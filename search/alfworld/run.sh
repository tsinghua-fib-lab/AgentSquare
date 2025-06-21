#!/bin/bash
tooluse=None
planning=none
reasoning=io
memory=tp
n=50
python3 alfworld_run.py \
    --planning $planning \
    --reasoning $reasoning \
    --tooluse $tooluse \
    --memory $memory \
    --n $n \
    --model deepseek-chat \
     
