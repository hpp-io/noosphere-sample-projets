import hmac
import hashlib
import os
import logging
import math
import base64
from flask import Flask, request, jsonify, Response

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# MASTER_SECRET: 32-byte hex string from environment
MASTER_SECRET = bytes.fromhex(os.environ["MASTER_SECRET"])

# Epoch size: number of random values per epoch
EPOCH_SIZE = int(os.environ.get("EPOCH_SIZE", "1000"))


def get_node_seed(game_id: int) -> bytes:
    """Deterministic nodeSeed generation: HMAC-SHA256(MASTER_SECRET, game_id)"""
    return hmac.new(
        MASTER_SECRET,
        str(game_id).encode(),
        hashlib.sha256
    ).digest()


def keccak256(data: bytes) -> bytes:
    """Keccak-256 hash (Ethereum-compatible)"""
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()


def commutative_keccak256(a: bytes, b: bytes) -> bytes:
    """Commutative keccak256 matching OpenZeppelin Hashes.commutativeKeccak256.
    Sorts inputs so hash(a,b) == hash(b,a)."""
    if a <= b:
        return keccak256(a + b)
    else:
        return keccak256(b + a)


def build_merkle_tree(leaves: list[bytes]) -> list[list[bytes]]:
    """Build a Merkle tree from leaves, padding to next power-of-2 with bytes(32).
    Returns list of layers, layers[0] = leaves, layers[-1] = [root]."""
    n = len(leaves)
    # Pad to next power of 2
    next_pow2 = 1 << math.ceil(math.log2(n)) if n > 1 else 1
    padded = list(leaves) + [bytes(32)] * (next_pow2 - n)

    layers = [padded]
    current = padded
    while len(current) > 1:
        next_layer = []
        for i in range(0, len(current), 2):
            next_layer.append(commutative_keccak256(current[i], current[i + 1]))
        layers.append(next_layer)
        current = next_layer
    return layers


def get_merkle_proof(layers: list[list[bytes]], index: int) -> list[bytes]:
    """Extract sibling path (proof) for a given leaf index."""
    proof = []
    for layer in layers[:-1]:  # skip root layer
        if index % 2 == 0:
            sibling = index + 1
        else:
            sibling = index - 1
        if sibling < len(layer):
            proof.append(layer[sibling])
        else:
            proof.append(bytes(32))
        index //= 2
    return proof


def get_merkle_root(layers: list[list[bytes]]) -> bytes:
    """Return the Merkle root."""
    return layers[-1][0]


def build_epoch_tree(epoch: int, epoch_size: int) -> list[list[bytes]]:
    """Build a Merkle tree for a given epoch.
    Leaf = keccak256(abi.encodePacked(uint256(indexInEpoch), randomValue))
    This binds each random value to its position, preventing index manipulation."""
    start = epoch * epoch_size
    leaves = []
    for i in range(epoch_size):
        r_i = get_node_seed(start + i)
        # Match Solidity: keccak256(abi.encodePacked(uint256(i), bytes32(r_i)))
        # abi.encodePacked(uint256, bytes32) = 32 bytes + 32 bytes = 64 bytes
        leaf = keccak256(i.to_bytes(32, 'big') + r_i)
        leaves.append(leaf)
    return build_merkle_tree(leaves)


@app.route('/computation', methods=['POST'])
def computation():
    """
    Standard Noosphere /computation endpoint.

    Actions:
      - "init_epoch": Build Merkle tree for epoch, return root as "0x" + 64 hex chars
      - "reveal": Return randomValue + Merkle proof as packed hex
    """
    data = request.get_json()
    if not data or 'input' not in data:
        return jsonify({"error": "Missing 'input' in request body"}), 400

    inp = data['input']

    # Handle both string and dict input formats
    if isinstance(inp, str):
        import json
        try:
            inp = json.loads(inp)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid input format"}), 400

    action = inp.get('action', '')

    if action == 'init_epoch':
        epoch = int(inp.get('epoch', 0))
        epoch_size = int(inp.get('epoch_size', EPOCH_SIZE))

        layers = build_epoch_tree(epoch, epoch_size)
        root = get_merkle_root(layers)
        hex_value = "0x" + root.hex()

        logging.info(f"INIT_EPOCH epoch={epoch} size={epoch_size} root={hex_value}")
        return Response(hex_value, content_type='text/plain')

    elif action == 'reveal':
        game_id = int(inp.get('game_id', 0))

        # Determine epoch and index within epoch
        epoch = game_id // EPOCH_SIZE
        index = game_id % EPOCH_SIZE

        # Get random value
        r_i = get_node_seed(game_id)

        # Build epoch tree and get proof
        layers = build_epoch_tree(epoch, EPOCH_SIZE)
        proof = get_merkle_proof(layers, index)

        # Pack as raw bytes then base64-encode for text-safe transport.
        # Agent treats output as UTF-8 text, so raw binary gets corrupted.
        # Container returns base64(raw_bytes), agent wraps in data:;base64,<base64(...)>,
        # contract does double base64 decode to recover raw bytes.
        raw = r_i
        for sibling in proof:
            raw += sibling
        b64_raw = base64.b64encode(raw).decode('ascii')

        logging.info(f"REVEAL game_id={game_id} epoch={epoch} index={index} r_i=0x{r_i.hex()} proof_len={len(proof)} raw_len={len(raw)} b64_len={len(b64_raw)}")
        return Response(b64_raw, content_type='text/plain')

    else:
        return jsonify({"error": f"Unknown action: '{action}'. Expected 'init_epoch' or 'reveal'."}), 400


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "vrng"})


if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8085))
    logging.info(f"Starting VRNG container on port {port}")
    app.run(host='0.0.0.0', port=port)
