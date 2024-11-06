<div align="center">
<img src="pics/logo1.png" style="width: 20%;height: 10%">
<h1> AgentSquare: Automatic LLM Agent Search In Modular Design Space </h1>
</div>

<div align="center">
  <!-- <a href="#model">Model</a> • -->
  🌐 <a href="https://tsinghua-fib-lab.github.io/AgentSquare_website">Website</a> |
  📃 <a href="https://arxiv.org/abs/2410.06153">Paper</a> |
</div>

# AgentSquare
The official implementation for paper [AgentSquare: Automatic LLM Agent Search in Modular Design Space](https://arxiv.org/abs/2410.06153) with code, prompts and results.

![intro](pics/intro.png)


## Setup
1. Set up OpenAI API key and store in environment.
```bash
export OPENAI_API_KEY=<YOUR KEY HERE>
```
2. Install dependencies
```bash
git clone https://github.com/tsinghua-fib-lab/AgentSquare.git
conda create -n agentsquare python=3.9
conda activate agentsquare
cd AgentSquare
pip install -r requirements.txt
```

## Quick Start
An exemplar script combining different agent modules to solve the task of ALFworld:
```bash
export ALFWORLD_DATA=<Your path>/AgentSquare/tasks/alfworld
cd tasks/alfworld
sh run.sh or 
python3 alfworld_run.py \
    --planning deps\
    --reasoning cot\
    --tooluse none\
    --memory dilu\
    --model gpt-3.5-turbo-0125 \
```

## Other Tasks
```bash
cd tasks
pip install -r requirements.txt
```

### webshop
Install `webshop` environment following instructions [here](https://github.com/princeton-nlp/WebShop) and launch the `WebShop` webpage.
```bash
cd tasks/webshop
sh run.sh
```

### M3Tooleval
```bash
cd tasks/m3tooleval
sh run.sh
```

## Modular Design Challenge
We kindly invite you to participate in the modular design challenge by standardizing your LLM agents with our recommended I/O interfaces.  Let's work together to offer a platform for fully exploiting the potential of successful agent designs and consolidating the collective efforts of LLM agent research community! 

### Contribute New Modules
For guidance on standardizing the I/O interfaces of the four types of agent modules, please refer to [module pools](modules), which provides some existing modules, along with a complete interface description available in [module interface description](modules/readme.md). [Click here](modules/test_new_modules.md) for a detailed procedure. You can submit your standardized modules through this [link](https://drive.google.com/drive/folders/1CrtW_s3n0-tCJRtUDzaKFWrBid7MuF9v?usp=sharing). The .py file format is preferred, examples can be seen in the `modules` folder. We will check your submission timely, once approved we will cite and acknowledge your works in this repository. 

## How to Add Your Own Task
You can refer to the `workflow.py` to integrate it with your encapsulated tasks, just like in `tasks/alfworld`.

## Citations
Please considering citing our paper and staring this repo if you use AgentSquare and find it useful, thanks! Feel free to contact fenglixu@tsinghua.edu.cn or open an issue if you have any question.

```bibtex
@misc{shang2024agentsquare,
      title={AgentSquare: Automatic LLM Agent Search in Modular Design Space}, 
      author={Yu Shang and Yu Li and Keyu Zhao and Likai Ma and Jiahe Liu and Fengli Xu and Yong Li},
      year={2024},
      eprint={2410.06153},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
}
```
