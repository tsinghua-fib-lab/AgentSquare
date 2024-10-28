# 获取传递的参数
planning=$1
planning_OPTION=$2
reasoning=$3
reasoning_OPTION=$4
memory=$5
memory_OPTION=$6
tooluse=$7
tooluse_OPTION=$8

# 输出收到的参数（仅供调试）
echo "planning: $planning, Option: $planning_OPTION"
echo "reasoning: $reasoning, Option: $reasoning_OPTION"
echo "memory: $memory, Option: $memory_OPTION"
echo "tooluse: $tooluse, Option: $tooluse_OPTION"


python3 agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks pddl \
    --model gpt-3.5-turbo-0125 \
    --wandb \
    --log_path ./results/gpt-3.5-turbo-0125 \
    --project_name evaluate-gpt-35-turbo-0125 \
    --baseline_dir ./data/baseline_results \
     $planning $planning_OPTION $reasoning $reasoning_OPTION $memory $memory_OPTION $tooluse $tooluse_OPTION
