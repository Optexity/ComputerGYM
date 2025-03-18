#!/bin/zsh

# Check if required arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <storage_file> <task_name> <url> [proxy_server]"
    echo "Example: $0 auth.json aws_login us-east-1.console.aws.amazon.com"
    exit 1
fi

# Get arguments
STORAGE_FILE=$1
TASK_NAME=$2
URL=$3

# Generate timestamp in yyyy-mm-dd-hh-mm-ss format
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")
OUTPUT_FILE="${TASK_NAME}_${TIMESTAMP}.py"

# Add proxy server if provided
if [ -n "$PROXY_SERVER" ]; then
    CMD="$CMD --proxy-server=\"$PROXY_SERVER\""
fi

# Execute the command
echo "Generating script for task: $TASK_NAME"
echo "Using storage file: $STORAGE_FILE"
echo "Target URL: $URL"
echo "Generating code to to $OUTPUT_FILE"

playwright codegen $URL --output=$OUTPUT_FILE --load-storage=$STORAGE_FILE --save-storage=$STORAGE_FILE --proxy-server="http://38.154.227.167:5868"

echo "Done! Generated code saved to $OUTPUT_FILE"
