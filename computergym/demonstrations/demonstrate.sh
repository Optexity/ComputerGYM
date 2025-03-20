#!/bin/zsh

# Check if yaml file exists
if [ ! -f "dummy.yaml" ]; then
    echo "Error: dummy.yaml not found"
    exit 1
fi

# Install yq if not already installed
if ! command -v yq &> /dev/null; then
    echo "yq is not installed. Please install it first:"
    echo "brew install yq  # for MacOS"
    echo "or"
    echo "wget https://github.com/mikefarah/yq/releases/download/v4.40.5/yq_linux_amd64 -O /usr/bin/yq && chmod +x /usr/bin/yq  # for Linux"
    exit 1
fi

# Read global variables from yaml
SAVE_DIR=$(yq -r '.save_dir' dummy.yaml)
GENERATED_CODE=$(yq -r '.generated_code' dummy.yaml)
RECORDER_DIR=$(yq -r '.recorder_dir' dummy.yaml)
PROCESSED_OUTPUT_DIR=$(yq -r '.processed_output_dir' dummy.yaml)

mkdir -p "$SAVE_DIR"

# Storage file for playwright
STORAGE_FILE="auth.json"

# Process each task
TASK_COUNT=$(yq -r '.tasks | length' dummy.yaml)
for ((i=0; i<$TASK_COUNT; i++)); do
    TASK_NAME=$(yq -r ".tasks[$i].task_name" dummy.yaml)
    URL=$(yq -r ".tasks[$i].url" dummy.yaml)
    
    # Create task-specific directory structure
    TASK_DIR="$SAVE_DIR/$TASK_NAME"
    mkdir -p "$TASK_DIR"
    mkdir -p "$TASK_DIR/$RECORDER_DIR"
    mkdir -p "$TASK_DIR/$PROCESSED_OUTPUT_DIR"
    
    # Set output file path
    OUTPUT_FILE="$TASK_DIR/$GENERATED_CODE"
    
    echo "Processing task: $TASK_NAME"
    echo "Target URL: $URL"
    echo "Generating code to: $OUTPUT_FILE"
    
    # Execute playwright codegen command
    npx --prefix /Users/shivamgoyal/work/Reinforce-Align-AI/playwright/ playwright codegen "$URL" \
        --output="$OUTPUT_FILE" \
        --content-dir="$TASK_DIR/$RECORDER_DIR" \
        --target=python
    
    echo "Done! Generated code saved to $OUTPUT_FILE"
    echo "----------------------------------------"
done

echo "All tasks completed!"
