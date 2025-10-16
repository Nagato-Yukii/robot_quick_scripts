import pandas as pd
import argparse

def add_zero_columns(input_file, output_file):
    """
    Reads a CSV file, appends 3 columns of zeros to the end, and saves the new CSV.

    Args:
        input_file (str): Path to the input CSV file (k rows, 33 columns).
        output_file (str): Path to save the new CSV file (k rows, 36 columns).
    """
    try:
        # 1. 使用 Pandas 读取 CSV 文件
        # header=None 表示文件没有标题行，第一行就是数据
        print(f"Reading data from: {input_file}")
        df = pd.read_csv(input_file, header=None)
        
        # 打印原始形状以供确认
        print(f"Original data shape: {df.shape}")
        
        if df.shape[1] != 33:
            print(f"Warning: The input file has {df.shape[1]} columns, not 33. Proceeding anyway.")

        # 2. 在DataFrame的末尾添加三列新的、值为0的列
        # 我们需要给新列起名字，否则无法添加。这里用临时名字，保存时不会写入。
        df[33] = 0
        df[34] = 0
        df[35] = 0
        
        # 打印新形状以供确认
        print(f"New data shape: {df.shape}")

        # 3. 将修改后的DataFrame保存为新的CSV文件
        # header=False 表示不保存列名（0, 1, 2...）
        # index=False 表示不保存行索引（0, 1, 2...）
        print(f"Saving modified data to: {output_file}")
        df.to_csv(output_file, header=False, index=False)
        
        print("Successfully added 3 zero columns.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add 3 zero columns to a CSV file.")
    parser.add_argument('--input', type=str, required=True, help="Path to the input CSV file (k, 33).")
    parser.add_argument('--output', type=str, required=True, help="Path for the output CSV file (k, 36).")
    
    args = parser.parse_args()
    
    add_zero_columns(args.input, args.output)