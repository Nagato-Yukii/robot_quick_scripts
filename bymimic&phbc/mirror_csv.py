import numpy as np
import argparse
import os

"""
python motion_source/mirror_csv.py --input <输入文件> --output <输出文件> [--skip_last]
"""

def mirror_csv(input_file, output_file, skip_last=True):
    """
    将CSV文件进行镜像反转
    
    参数:
    input_file: 输入CSV文件路径
    output_file: 输出CSV文件路径  
    skip_last: 是否跳过最后一帧再反转（避免重复）
    """
    print(f"正在读取文件: {input_file}")
    
    # 读取CSV文件
    data = np.genfromtxt(input_file, delimiter=',')
    print(f"原始数据形状: {data.shape}")
    
    if len(data) == 0:
        print("错误：文件为空！")
        return
    
    # 创建镜像数据
    if skip_last:
        # 跳过最后一帧，避免重复：12345 -> 1234 + 321 = 1234321
        mirrored_data = data[:-1]  # 去掉最后一帧
        reversed_data = data[-2::-1]  # 从倒数第二帧开始反转
        print(f"镜像模式: 原始{len(data)}帧 -> 前{len(mirrored_data)}帧 + 反转{len(reversed_data)}帧")
    else:
        # 包含最后一帧：12345 -> 12345 + 54321 = 1234554321
        mirrored_data = data
        reversed_data = data[::-1]  # 完全反转
        print(f"完整镜像模式: 原始{len(data)}帧 + 完全反转{len(reversed_data)}帧")
    
    # 拼接原始数据和反转数据
    final_data = np.concatenate((mirrored_data, reversed_data), axis=0)
    
    print(f"最终数据形状: {final_data.shape}")
    print(f"总帧数: {len(data)} -> {len(final_data)}")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 保存为新的CSV文件
    np.savetxt(output_file, final_data, delimiter=',', fmt='%.6f')
    print(f"镜像数据已保存到: {output_file}")

def create_symmetric_motion(input_file, output_file, transition_frames=5):
    """
    创建对称运动（适用于运动数据）
    在原始数据和反转数据之间添加平滑过渡
    
    参数:
    input_file: 输入CSV文件路径
    output_file: 输出CSV文件路径
    transition_frames: 过渡帧数
    """
    print(f"正在创建对称运动: {input_file}")
    
    # 读取CSV文件
    data = np.genfromtxt(input_file, delimiter=',')
    print(f"原始数据形状: {data.shape}")
    
    if len(data) < transition_frames * 2:
        print(f"警告：数据帧数太少，无法创建{transition_frames}帧过渡")
        transition_frames = max(1, len(data) // 4)
    
    # 创建过渡序列
    start_frame = data[-1]  # 最后一帧
    end_frame = data[-2]    # 倒数第二帧（反转后的起始）
    
    # 线性插值创建过渡
    transition_data = []
    for i in range(transition_frames):
        ratio = (i + 1) / (transition_frames + 1)
        interpolated_frame = start_frame * (1 - ratio) + end_frame * ratio
        transition_data.append(interpolated_frame)
    
    transition_data = np.array(transition_data)
    
    # 创建反转数据（跳过最后一帧避免重复）
    reversed_data = data[-2::-1]
    
    # 拼接：原始数据 + 过渡数据 + 反转数据
    final_data = np.concatenate((data, transition_data, reversed_data), axis=0)
    
    print(f"对称运动: 原始{len(data)}帧 + 过渡{len(transition_data)}帧 + 反转{len(reversed_data)}帧")
    print(f"最终数据形状: {final_data.shape}")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 保存文件
    np.savetxt(output_file, final_data, delimiter=',', fmt='%.6f')
    print(f"对称运动数据已保存到: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将CSV运动文件进行镜像反转")
    parser.add_argument('--input', type=str, help="输入CSV文件路径", required=True)
    parser.add_argument('--output', type=str, help="输出CSV文件路径", required=True)
    parser.add_argument('--mode', type=str, choices=['simple', 'smooth'], 
                       default='simple', help="镜像模式：simple(简单镜像) 或 smooth(平滑过渡)")
    parser.add_argument('--skip_last', action='store_true', 
                       help="是否跳过最后一帧（避免重复）")
    parser.add_argument('--transition_frames', type=int, default=5,
                       help="平滑模式下的过渡帧数")
    
    args = parser.parse_args()
    
    if args.mode == 'simple':
        mirror_csv(args.input, args.output, args.skip_last)
    elif args.mode == 'smooth':
        create_symmetric_motion(args.input, args.output, args.transition_frames)