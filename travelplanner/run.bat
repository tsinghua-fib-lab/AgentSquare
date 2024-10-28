@echo off

REM 导出环境变量
set OUTPUT_DIR=C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\output_plan\output_plan16
set MODEL_NAME=gpt-3.5-turbo-0125
set OPENAI_API_KEY=sk-4iQVFio5D3ef906N4hC-K9AbCX887_U5kU1S4fcqT5T3BlbkFJJa2AtlZUKv3STlHEoVqhHdX7MMvYU1OYHXw09gBG0A
set SET_TYPE=validation
set STRATEGY=direct
REM MODE in ['two-stage', 'sole-planning']
set MODE=two-stage
set TMP_DIR=C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\temp\temp16
set SUBMISSION_DIR=C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\submission\submission16

REM 切换到 postprocess 目录并执行 parsing.py 脚本
cd ..\postprocess
echo run parsing.py
python parsing.py --set_type %SET_TYPE% --output_dir %OUTPUT_DIR% --model_name %MODEL_NAME% --strategy %STRATEGY% --mode %MODE% --tmp_dir %TMP_DIR%

REM 执行 element_extraction.py 脚本
echo run element_extraction.py
python element_extraction.py --set_type %SET_TYPE% --output_dir %OUTPUT_DIR% --model_name %MODEL_NAME% --strategy %STRATEGY% --mode %MODE% --tmp_dir %TMP_DIR%

REM 执行 combination.py 脚本，合并计划文件用于评估
echo run combination.py
python combination.py --set_type %SET_TYPE% --output_dir %OUTPUT_DIR% --model_name %MODEL_NAME% --strategy %STRATEGY% --mode %MODE% --submission_file_dir %SUBMISSION_DIR%

REM 导出评估文件路径
set EVALUATION_FILE_PATH=C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\submission\submission16\validation_gpt-3.5-turbo-0125_two-stage_submission.jsonl

REM 切换到 evaluation 目录并执行 eval.py 脚本
cd ..\evaluation
echo run eval.py
python eval.py --set_type %SET_TYPE% --evaluation_file_path %EVALUATION_FILE_PATH%

@echo COMPLETE
