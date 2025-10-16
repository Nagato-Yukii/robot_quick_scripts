import joblib
import os
import argparse

def reverse_process(motion_data):
    """
    Removes the keys added by the count_pkl_contact_mask.py script.
    """
    keys_to_remove = ['contact_mask', 'smpl_joints', 'pose_aa']
    
    for key in keys_to_remove:
        if key in motion_data:
            del motion_data[key]
            print(f"Removed key: '{key}'")
            
    # 注意：原始的 'dof' 数据可能已被23-DoF版本覆盖，这一步是不可逆的。
    # 我们无法从这个文件中恢复被丢弃的6个手腕自由度。
    if 'dof' in motion_data:
        print("Note: The 'dof' key is present but may have been reduced to 23 DoF. This change cannot be reverted.")

    return motion_data

def main(args):
    input_folder = args.input_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    if not os.path.isdir(input_folder):
        print(f"Error: Input folder not found at '{input_folder}'")
        return

    print(f"Scanning for files in '{input_folder}'...")
    for filename in os.listdir(input_folder):
        if filename.endswith(".pkl"):
            input_file_path = os.path.join(input_folder, filename)
            
            try:
                # 1. 加载包含 contact_mask 的 pkl 文件
                data_with_mask = joblib.load(input_file_path)
                
                # 假设数据结构是 {'some_key': motion_dict}
                data_keys = list(data_with_mask.keys())
                if not data_keys:
                    print(f"Warning: Skipping empty pkl file: {filename}")
                    continue
                
                motion_key = data_keys[0]
                motion_dict = data_with_mask[motion_key]
                
                # 2. 调用逆向处理函数，移除添加的键
                cleaned_motion_dict = reverse_process(motion_dict)
                
                # 3. 准备保存的数据
                save_data = {motion_key: cleaned_motion_dict}
                
                # 4. 定义输出文件名并保存
                output_filename = filename.replace('_cont_mask', '') # 尝试恢复原始名称
                output_file_path = os.path.join(output_folder, output_filename)
                
                joblib.dump(save_data, output_file_path)
                print(f"Processed '{filename}' -> Saved to '{output_filename}'")

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove contact mask and other added data from motion pkl files.")
    parser.add_argument('--input_folder', type=str, required=True, help="Folder containing the pkl files with contact masks.")
    parser.add_argument('--output_folder', type=str, required=True, help="Folder to save the cleaned pkl files.")
    
    args = parser.parse_args()
    main(args)