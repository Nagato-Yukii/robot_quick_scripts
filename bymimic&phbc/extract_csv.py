import numpy as np
import argparse
import os

"""
python motion_source/extract_csv.py --input <输入文件> --output <输出文件> --start <起始帧> --end <结束帧>
"""
def extract_frames_csv(input_file, output_file, start_frame, end_frame):
    """
    从CSV文件中提取指定帧范围的数据
    
    参数:
    input_file: 输入CSV文件路径
    output_file: 输出CSV文件路径  
    start_frame: 起始帧
    end_frame: 结束帧
    """
    print(f"正在读取文件: {input_file}")
    
    # 读取CSV文件
    data = np.genfromtxt(input_file, delimiter=',')
    print(f"原始数据形状: {data.shape}")
    
    # 检查帧范围是否有效
    total_frames = data.shape[0]
    if start_frame < 0:
        start_frame = 0
    if end_frame > total_frames or end_frame == -1:
        end_frame = total_frames
        
    print(f"提取帧范围: {start_frame} 到 {end_frame}")
    
    # 提取指定帧范围的数据
    extracted_data = data[start_frame:end_frame, :]
    print(f"提取后数据形状: {extracted_data.shape}")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 保存为新的CSV文件
    np.savetxt(output_file, extracted_data, delimiter=',', fmt='%.6f')
    print(f"数据已保存到: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从CSV运动文件中提取指定帧范围")
    parser.add_argument('--input', type=str, help="输入CSV文件路径", required=True)
    parser.add_argument('--output', type=str, help="输出CSV文件路径", required=True)
    parser.add_argument('--start', type=int, help="起始帧", default=0)
    parser.add_argument('--end', type=int, help="结束帧(-1表示到最后)", default=-1)
    
    args = parser.parse_args()
    
    extract_frames_csv(args.input, args.output, args.start, args.end)