import os

def find_missing_files(directory, total_files = 181):
    # 存储缺失的文件序号
    missing_files = []
    
    # 遍历所有可能的文件序号
    for i in range(1,total_files):
        # 构建文件名
        file_name = f"generated_plan_{i}.json"
        # 检查文件是否存在
        if not os.path.exists(os.path.join(directory, file_name)):
            missing_files.append(i)
    
    return missing_files

# 文件夹路径和总文件数
directory_path = r"C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\output_plan\output_plan0\validation"  # 替换为你的文件夹路径
total_files = 181  # 应该有0到180，共181个文件

# 查找缺失的文件
missing_files = find_missing_files(directory_path, total_files)

# 打印缺失的文件序号
if missing_files:
    print(f"总共缺失{len(missing_files)}个文件\n"+f"缺失的文件序号: {missing_files}")
else:
    print("所有文件都存在。")

print(len(os.listdir(r"C:\Users\kyzhao\Desktop\Study\LLMAgent\TravelPlanner\output_plan\output_plan0\validation")))
# validation_directory = os.path.join(args.output_dir, "validation")
# print(len(os.listdir(validation_directory)))