# Optexity: Foundation Model training using human demonstrations

## Setup
### Cloning the repository
```bash
mkdir optexity
cd optexity
git clone https://github.com/Optexity/ComputerGYM.git
git clone https://github.com/Optexity/AgentAI.git
git clone https://github.com/Optexity/playwright.git
```

### Environment Setup
```bash
conda create -n optexity python=3.10 nodejs
conda activate optexity
```
### Installing dependencies
```bash
pip install -e ComputerGym
pip install -e AgentAI
cd playwright
git checkout playwright_optexity
npm install
npm run build
playwright install
```

## Recording Demonstrations
Create your own `dummy.yaml` file and run the script
```bash
cd ComputerGYM/computergym/demonstrations
./demonstrate.sh dummy.yaml
```

## Processing the Demonstrations
```bash
python process_demonstration.py --yaml dummy.yaml --seed 5
```

## Generating Training Data
```bash
cd AgentAI/agentai/sft
python prepare_training_data.py --agent_config ../train_configs/hubspot_agent.yaml
```

## Training using LLamaFactory

## Testing 
```bash
cd AgentAI/agentai
python main.py --url "https://app.hubspot.com" --port 8000 --log_to_console --goal "change currency to SGD"
```