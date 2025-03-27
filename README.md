<p align="center">
  <img src="assets/logo_optexity.svg" alt="Optexity Logo" width="300"/>
</p>

<p align="center">
  <a href="https://optexity.com">Visit our website: optexity.com</a>
</p>

<div align="center">
  <a href="https://www.youtube.com/watch?v=Nudl0JcezUg" target="_blank">
    <div style="position: relative; display: inline-block;">
      <img src="https://img.youtube.com/vi/Nudl0JcezUg/maxresdefault.jpg" alt="Optexity Demo Video" width="800" height="450" style="border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" />
      <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: rgba(0, 0, 255, 0.8); border-radius: 50%; width: 80px; height: 80px; display: flex; justify-content: center; align-items: center;">
        <div style="width: 0; height: 0; border-top: 20px solid transparent; border-left: 35px solid white; border-bottom: 20px solid transparent; margin-left: 8px;"></div>
      </div>
    </div>
  </a>
  <p>
    <strong>▶️ Optexity Demo: Trained Llama 3-8B Beats Gemini 2.0 Flash & GPT-4o on Software Automation</strong>
  </p>
</div>

# Optexity: Foundation Model Training Using Human Demonstrations

## Overview
Optexity enables training foundation models using human demonstrations of computer tasks. This framework allows for recording, processing, and using demonstrations to train AI agents to complete web-based tasks. We will be adding training using self exploration using reinforement learning, training from software documentations and training using youtube videos in future.

## Detailed Tutorial Videos
Explore our step-by-step video guides to get started with Optexity:

1. [**Optexity Tutorial Part 1 | Introduction and State of Browser Agents for Software Use**](https://www.youtube.com/watch?v=5gsb4z5FAAE)
2. [**Optexity Tutorial Part 2 | Training AI with Human Demonstrations**](https://www.youtube.com/watch?v=CMreOrcN7bc)
3. [**Optexity Tutorial Part 3 | AI Agent in Action!**](https://www.youtube.com/watch?v=0eq9rY2Su5E)

## Setup

1. **Repository Setup**
   Clone the necessary repositories:
   ```bash
   mkdir optexity
   cd optexity
   git clone https://github.com/Optexity/ComputerGYM.git
   git clone https://github.com/Optexity/AgentAI.git
   git clone https://github.com/Optexity/playwright.git
   ```

2. **Environment Setup**
   Create and activate a Conda environment with the required Python and Node.js versions:
   ```bash
   conda create -n optexity python=3.10 nodejs
   conda activate optexity
   ```

3. **Installing Dependencies**
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

1. **Recording Demonstrations**
   Record human demonstrations by creating a configuration file and running the demonstration script:
   ```bash
   ./ComputerGYM/computergym/demonstrations/demonstrate.sh ComputerGYM/computergym/demonstrations/demonstration_config.yaml
   ```
   > Note: Create your own `demonstration_config.yaml` configuration file before running this script.

2. **Processing Demonstrations**
   Process the recorded demonstrations to prepare them for training:
   ```bash
   python ComputerGYM/computergym/demonstrations/process_demonstration.py --yaml ComputerGYM/computergym/demonstrations/demonstration_config.yaml --seed 5
   ```

3. **Generating Training Data**
   Convert processed demonstrations into a format suitable for model training:
   ```bash
   python AgentAI/agentai/sft/prepare_training_data.py --agent_config AgentAI/agentai/train_configs/hubspot_agent.yaml
   ```

4. **Training the Model**
   Our data preparation scripts generate JSON data in a format compatible with [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory). The generated training and inference configurations are stored in the `train_data` directory. Please refer to the LLaMA-Factory documentation for detailed instructions on model training.

5. **Evaluating the Trained Agent**
   After training your model, deploy it as an inference service on `http://localhost:8000`. By default, our framework is configured to work with the vLLM serving capability provided by LLaMA-Factory. If you're using an alternative serving method, you'll need to modify the appropriate scripts.

   To evaluate your trained agent on a specific web task, execute:
   ```bash
   python AgentAI/agentai/main.py --url "https://app.hubspot.com" --port 8000 --log_to_console --goal "change currency to SGD" --storage_state cache_dir/auth.json --model vllm
   ```

## Documentation
For comprehensive information on configuration options and advanced usage patterns, please refer to the detailed documentation available in each repository:

- **ComputerGYM**: Environment setup, demonstration recording, and processing
- **AgentAI**: Model training configurations, inference settings, and evaluation metrics
- **Playwright Integration**: Custom extensions and modifications for web automation

### Configuration References
- Demonstration configuration: See `ComputerGYM/computergym/demonstrations/demonstration_config_example.yaml`
- Training parameters: See `AgentAI/agentai/train_configs/README.md`

## Acknowledgements
This project builds upon and extends the work of:
- [BrowserGym](https://github.com/ServiceNow/BrowserGym) - For the browser automation environment foundation
- [Playwright](https://playwright.dev/) - For reliable web testing and automation capabilities
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) - For efficient foundation model fine-tuning



## Community & Support
- Report issues on [GitHub](https://github.com/Optexity/ComputerGYM/issues)
- Follow us on [Twitter](https://twitter.com/optexity) for the latest updates
