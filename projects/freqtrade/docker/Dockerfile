
# --- Build Stage ---
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
    wget \
    build-essential \
    dpkg-dev \
    automake \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -q -O - | tar -xz -C /tmp && \
    cd /tmp/ta-lib && \
    wget -q -O config.sub 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' && \
    wget -q -O config.guess 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    rm -rf /tmp/ta-lib

# Set up Python environment
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install all requirements at once - let pip resolve dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Apply patches if files exist
RUN if [ -f /opt/venv/lib/python3.11/site-packages/freqtrade/rpc/rpc.py ]; then \
        sed -i 's/NAN/nan/g' /opt/venv/lib/python3.11/site-packages/freqtrade/rpc/rpc.py; \
    fi

# Force upgrade ccxt to a version compatible with the latest freqtrade
# RUN pip install --upgrade "ccxt"

# --- Final Stage ---
FROM python:3.11-slim

# Copy virtual environment and libraries
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/lib/libta_lib.so.0 /usr/lib/libta_lib.so.0
COPY --from=builder /usr/lib/libta_lib.so.0.0.0 /usr/lib/libta_lib.so.0.0.0

# Set working directory and environment
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY config_eth.json .
COPY user_data ./user_data/
COPY start.sh .
COPY src/app.py .

RUN chmod +x /app/start.sh

EXPOSE 8084

CMD ["/app/start.sh"]