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
pip install -r requirements.txt
```

3. Install ``alfworld`` following instructions [here](https://github.com/alfworld/alfworld).


## Quick Start
An exemplar script combining different agent modules to solve the task of ALFworld:
```bash
cd meta-agent-alfworld
sh run.sh or 
python3 alfworld_run.py \
    --planning deps\
    --reasoning cot\
    --tooluse none\
    --memory dilu\
    --model gpt-3.5-turbo-0125 \
```
## Contribute to AgentSquare
We kindly invite you to contribute to AgentSquare by standardizing your own LLM agents with our proposed IO interfaces. Let's work together to offer a platform for fully exploiting the potential of successful agent designs and consolidating the collective efforts of LLM agent research community!

For guidance on standardizing the I/O interfaces of the four types of agent modules, please refer to `standard_module_interface.docx`, and you can submit your standardized modules through this [link](https://cloud.tsinghua.edu.cn/d/c546f5360ca948ef9d3a/). The .py file format is preferred, examples can be seen in the `module pool` folder. 

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
