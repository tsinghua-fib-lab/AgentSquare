# Detailed Procedure to Test New Modules

A step-by-step guide for testing a new module on the ALFWorld task:

1. Design a new module based on the detailed instructions in the modules folder, for example, name it `ReasoningNew`.

2. Add `ReasoningNew` to `tasks/alfworld/module_map.py` and `reasoning_modules.py`

3. Update the `--reasoning` argument in `run.sh`, then execute `sh run.sh`.
