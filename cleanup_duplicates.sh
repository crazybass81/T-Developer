#!/bin/bash

echo "Cleaning up duplicate T-Developer processes..."

# Find and kill duplicate backend processes
echo "Checking for duplicate backend processes..."
BACKEND_PROCESSES=$(ps aux | grep "uvicorn main:app" | grep -v grep | wc -l)
if [ $BACKEND_PROCESSES -gt 1 ]; then
  echo "Found $BACKEND_PROCESSES backend processes. Cleaning up..."
  ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}' | xargs kill -9
  echo "All duplicate backend processes terminated."
else
  echo "No duplicate backend processes found."
fi

# Find and kill duplicate frontend processes
echo "Checking for duplicate frontend processes..."
FRONTEND_PROCESSES=$(ps aux | grep "node.*start" | grep -v grep | wc -l)
if [ $FRONTEND_PROCESSES -gt 1 ]; then
  echo "Found $FRONTEND_PROCESSES frontend processes. Cleaning up..."
  ps aux | grep "node.*start" | grep -v grep | awk '{print $2}' | xargs kill -9
  echo "All duplicate frontend processes terminated."
else
  echo "No duplicate frontend processes found."
fi

# Check for any processes using the common ports
echo "Checking for processes using common ports..."
for PORT in 3000 8000 8001 8080; do
  PROCESS=$(lsof -i:$PORT 2>/dev/null)
  if [ ! -z "$PROCESS" ]; then
    echo "Found process using port $PORT:"
    echo "$PROCESS"
    echo "Terminating process..."
    lsof -i:$PORT -t | xargs kill -9 2>/dev/null
    echo "Process on port $PORT terminated."
  else
    echo "No process found on port $PORT."
  fi
done

echo "Cleanup complete."