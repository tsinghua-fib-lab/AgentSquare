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
1. Set up OpenAI API key and store in environment variable ``OPENAI_API_KEY`` (see [here](https://help.openai.com/en/collections/3675931-api)). 

2. Install dependencies
```bash
conda create -n agentsquare python=3.9
pip install -r requirements.txt
```

3. If you want to run other tasks(such as webshop, etc), set up the corresponding environment. Install `webshop` environment following instructions [here](https://github.com/princeton-nlp/WebShop)


## Quick Start
An exemplar script combining different agent modules to solve the task of ALFworld:
```bash
export ALFWORLD_DATA=(Your path)/AgentSquare/alfworld
cd alfworld
sh run.sh or 
python3 alfworld_run.py \
    --planning deps\
    --reasoning cot\
    --tooluse none\
    --memory dilu\
    --model gpt-3.5-turbo-0125 \
```

## Contribute to AgentSquare
We kindly invite you to contribute to AgentSquare by standardizing your own LLM agents with our proposed I/O interfaces. Let's work together to offer a platform for fully exploiting the potential of successful agent designs and consolidating the collective efforts of LLM agent research community!

### Design New Modules
For guidance on standardizing the I/O interfaces of the four types of agent modules, please refer to `alfworld/reasoning(planning)_modules.py`, which provides a module template and some existing modules, along with a complete interface description available in `standard_module_interface.docx`. You can submit your standardized modules through this [link](https://cloud.tsinghua.edu.cn/u/d/698134791b1446cca0cc/). The .py file format is preferred, examples can be seen in the `module pool` folder. We will check your submission timely, once approved we will cite and acknowledge your works in this repository. 

### How to Add A New Task
You can refer to the `workflow.py` to integrate it with your encapsulated tasks, just like in `alfworld`.

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
