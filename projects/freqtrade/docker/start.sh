#!/bin/bash

# Activate the virtual environment
. /opt/venv/bin/activate

# Start the freqtrade bot in the background
echo "Starting freqtrade bot in the background..."
freqtrade trade --strategy TCLStrategy_3R --dry-run --config config_eth.json &
 
# Wait for the prediction file to be created before starting the API
echo "Waiting for freqtrade to generate the first prediction file..."
while [ ! -f /app/pred.txt ]; do
  sleep 2
done
 
echo "Prediction file found. Proceeding to start API server."
 
# Start the Flask API server in the foreground
echo "Starting Flask API server..."
python /app/app.py