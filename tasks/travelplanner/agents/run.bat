@echo off

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

REM 切换到 evaluation 目录并执行 eval.py 脚本
cd ..\evaluation
echo run eval.py
python eval.py --set_type %SET_TYPE% --evaluation_file_path %EVALUATION_FILE_PATH%

cd ..\agents

@echo COMPLETE
