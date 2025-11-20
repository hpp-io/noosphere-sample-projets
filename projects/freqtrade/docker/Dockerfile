# --- Build Stage ---
# This stage is for compiling dependencies like TA-Lib and python packages with C extensions.
FROM python:3.11-slim AS builder

# 1. Install build-time system dependencies in a separate layer for better caching
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
    wget \
    build-essential \
    dpkg-dev \
    automake \
    git && \
    rm -rf /var/lib/apt/lists/*

# 2. Install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -q -O - | tar -xz -C /tmp && \
    cd /tmp/ta-lib && \
    wget -q -O config.sub 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' && \
    wget -q -O config.guess 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    rm -rf /tmp/ta-lib

# 3. Create a virtual environment and install python dependencies
WORKDIR /app
COPY requirements.txt .
 RUN python -m venv /opt/venv && \
     /opt/venv/bin/pip install --upgrade pip

RUN /opt/venv/bin/pip install --no-cache-dir -v -r requirements.txt


# --- Final Stage ---
# This stage creates the final, lightweight production image.
FROM python:3.11-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the compiled TA-Lib library from the builder stage
COPY --from=builder /usr/lib/libta_lib.so.0 /usr/lib/libta_lib.so.0
COPY --from=builder /usr/lib/libta_lib.so.0.0.0 /usr/lib/libta_lib.so.0.0.0

# Set the working directory
WORKDIR /app
# Copy configuration and user_data (including ML models) into the image
COPY config_eth.json .
COPY user_data ./user_data/
COPY start.sh .
# Grant execute permissions to the start script
RUN chmod +x /app/start.sh
COPY src/app.py .

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8084

CMD ["/app/start.sh"]