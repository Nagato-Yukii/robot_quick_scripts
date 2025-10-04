import numpy as np
import joblib
import argparse
import os

def revert(input_pkl_path, output_csv_path):
    """
    读取处理后的 .pkl 文件，并将其转换回近似原始的 .csv 格式。

    注意：原始转换过程丢弃了3列dof数据，
    此逆向过程会在相应位置用0填充，因此输出的CSV与最原始的输入不会完全相同。

    参数:
    input_pkl_path (str): 输入的 .pkl 文件路径。
    output_csv_path (str): 输出的 .csv 文件路径。

    示例:
    python revert.py --filepath Charleston_dance.pkl --output reverted_Charleston_dance.csv
    """
    print(f"--- 开始逆向转换 ---")
    print(f"正在加载文件: {input_pkl_path}")

    # 1. 从 .pkl 文件加载数据
    try:
        all_data = joblib.load(input_pkl_path)
    except FileNotFoundError:
        print(f"错误：文件 {input_pkl_path} 不存在！")
        return

    # pkl文件里只有一个主键（文件名），我们获取其对应的值
    # list(all_data.keys())[0] 是获取字典中第一个键的稳定方法
    file_key = list(all_data.keys())[0]
    data_dump = all_data[file_key]
    
    print(f"成功加载数据，文件主键为: '{file_key}'")

    # 2. 从字典中提取核心数据
    # 根节点位移 (x,y,z)
    root_trans = data_dump['root_trans_offset']
    # 根节点旋转四元数 (w,x,y,z)
    root_qua = data_dump['root_rot']
    # 经过筛选的关节角度
    dof_new = data_dump['dof']
        # ----> 添加这些诊断代码 <----
    print("--- 诊断信息 ---")
    print(f"data_dump 中包含的键: {data_dump.keys()}")
    if 'root_trans_offset' in data_dump:
        print(f"root_trans 的形状: {data_dump['root_trans_offset'].shape}")
    if 'root_rot' in data_dump:
        print(f"root_qua 的形状: {data_dump['root_rot'].shape}")
    if 'dof' in data_dump:
        print(f"dof_new 的形状: {data_dump['dof'].shape}")
    print("--------------------")
    # ---------------------------
    # 获取动画的帧数
    num_frames = root_trans.shape[0]
    print(f"数据包含 {num_frames} 帧。")

    # 3. 重建丢失的 dof 列
    # 原始脚本丢弃了原 dof 的第 19, 20, 21 列
    # 我们需要在 dof_new 的第 19 列之后插入 3 列 0
    
    # 取出 dof_new 的第一部分（前19列）
    dof_part1 = dof_new[:, :19]
    # 创建一个形状为 (帧数, 3) 的零矩阵来填充丢失的数据
    missing_dof_cols = np.zeros((num_frames, 3), dtype=np.float32)
    # 取出 dof_new 的第二部分（剩下的列）
    dof_part2 = dof_new[:, 19:]

    # 将三部分拼接起来，恢复 dof 的原始形状
    dof_reconstructed = np.concatenate((dof_part1, missing_dof_cols, dof_part2), axis=1)

    print(f"原始dof形状: {dof_new.shape}")
    print(f"重建后dof形状: {dof_reconstructed.shape}")

    # 4. 将所有数据部分按原始顺序拼接
    # 顺序是: root_trans (3列), root_qua (4列), dof_reconstructed (...)
    final_data = np.concatenate((root_trans, root_qua, dof_reconstructed), axis=1)

    print(f"最终合并后数据形状: {final_data.shape}")

    # 5. 将最终的数组保存为 CSV 文件
    np.savetxt(output_csv_path, final_data, delimiter=',', fmt='%.8f')
    
    print(f"转换完成！数据已保存至: {output_csv_path}")
    print(f"--- 转换结束 ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将处理后的pkl文件逆向转换回csv格式。")
    parser.add_argument('--filepath', type=str, help="输入的 .pkl 文件路径", required=True)
    parser.add_argument('--output', type=str, help="输出的 .csv 文件路径 (可选)")
    args = parser.parse_args()

    input_path = args.filepath
    
    # 如果用户没有指定输出路径，我们就自动生成一个
    if args.output:
        output_path = args.output
    else:
        # 基于输入文件名创建一个默认的输出文件名
        # 例如: 'lafan_pkl/walk_0_100.pkl' -> 'walk_0_100_reverted.csv'
        base_name = os.path.basename(input_path)  # 获取文件名 'walk_0_100.pkl'
        name_without_ext = os.path.splitext(base_name)[0] # 去掉扩展名 'walk_0_100'
        output_path = f"{name_without_ext}_reverted.csv"

    # 调用核心函数执行转换
    revert(input_path, output_path)
    print(f"save as {output_path}")
