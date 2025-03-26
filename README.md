# Optexity: Foundation Model Training Using Human Demonstrations

## Overview
Optexity enables training foundation models using human demonstrations of computer tasks. This framework allows for recording, processing, and using demonstrations to train AI agents to complete web-based tasks.

## Setup

### 1. Repository Setup
Clone the necessary repositories:
```bash
mkdir optexity
cd optexity
git clone https://github.com/Optexity/ComputerGYM.git
git clone https://github.com/Optexity/AgentAI.git
git clone https://github.com/Optexity/playwright.git
```

### 2. Environment Setup
Create and activate a Conda environment with the required Python and Node.js versions:
```bash
conda create -n optexity python=3.10 nodejs
conda activate optexity
```

### 3. Installing Dependencies
Install the required packages and build the Playwright framework:
```bash
pip install -e ComputerGym
pip install -e AgentAI
cd playwright
git checkout playwright_optexity
npm install
npm run build
playwright install
```

## Workflow

### 1. Recording Demonstrations
Record human demonstrations by creating a configuration file and running the demonstration script:
```bash
cd ComputerGYM/computergym/demonstrations
./demonstrate.sh dummy.yaml
```
> Note: Create your own `dummy.yaml` configuration file before running this script.

### 2. Processing Demonstrations
Process the recorded demonstrations to prepare them for training:
```bash
python process_demonstration.py --yaml dummy.yaml --seed 5
```

### 3. Generating Training Data
Convert processed demonstrations into a format suitable for model training:
```bash
cd AgentAI/agentai/sft
python prepare_training_data.py --agent_config ../train_configs/hubspot_agent.yaml
```

### 4. Training the Model
Train your model using LLamaFactory with the prepared demonstration data.

### 5. Testing the Trained Agent
Test your trained agent on specific web tasks:
```bash
cd AgentAI/agentai
python main.py --url "https://app.hubspot.com" --port 8000 --log_to_console --goal "change currency to SGD"
```

## Documentation
For more details on configuration options and advanced usage, refer to the documentation in each repository.