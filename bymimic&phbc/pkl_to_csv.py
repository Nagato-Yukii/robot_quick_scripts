import numpy as np
import joblib
import argparse
import os

def convert_back(pkl_filepath, output_csv_path):
    """
    Reads a PKL file created by the original script and converts it back to a CSV file.
    """
    # 1. Load the data from the PKL file
    print(f"Loading data from: {pkl_filepath}")
    loaded_data = joblib.load(pkl_filepath)

    # The original script saves the data in a dictionary like {'filename': data_dict}.
    # We need to get the actual data dictionary, which is the first value.
    if not isinstance(loaded_data, dict) or not loaded_data:
        raise ValueError("The PKL file does not contain the expected dictionary format.")
    
    # Get the inner dictionary containing all the motion data
    data_dump = list(loaded_data.values())[0]

    # 2. Extract the core components needed to reconstruct the original CSV
    root_trans = data_dump['root_trans_offset']
    root_qua = data_dump['root_rot']
    dof_new = data_dump['dof'] # This is the MODIFIED dof array

    print(f"Found {root_trans.shape[0]} frames of data.")
    
    # --- The CRITICAL step: Reconstructing the original 'dof' array ---
    # The original script did: dof_new = np.concatenate((dof[:, :19], dof[:, 22:26]), axis=1)
    # This means it DISCARDED 3 columns (index 19, 20, 21) from the original 'dof'.
    # We cannot recover this lost data. The best we can do is insert placeholders (e.g., zeros).
    
    # Create an array of zeros for the missing columns
    num_frames = dof_new.shape[0]
    missing_dof_columns = np.zeros((num_frames, 3), dtype=np.float32)

    # Re-insert the missing columns at the correct position (after the 19th column)
    dof_reconstructed = np.concatenate(
        (dof_new[:, :19], missing_dof_columns, dof_new[:, 19:]), 
        axis=1
    )

    # 3. Concatenate all parts back into a single flat array, mimicking the original CSV structure
    # Original structure was: [root_trans, root_qua, dof]
    reconstructed_data = np.concatenate(
        (root_trans, root_qua, dof_reconstructed), 
        axis=1
    )

    print(f"Reconstructed data shape: {reconstructed_data.shape}")

    # 4. Save the reconstructed data to a new CSV file
    print(f"Saving reconstructed data to: {output_csv_path}")
    np.savetxt(output_csv_path, reconstructed_data, delimiter=',', fmt='%.8f')
    print("Conversion complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a motion PKL file back to a CSV file.")
    parser.add_argument('--pklfile', type=str, help="Path to the input .pkl file", required=True)
    parser.add_argument('--output', type=str, help="Path for the output .csv file (optional)")
    args = parser.parse_args()

    # Determine the output file path
    if args.output:
        output_filepath = args.output
    else:
        # If no output is specified, create a default name next to the input file
        base_dir = os.path.dirname(args.pklfile)
        filename = os.path.basename(args.pklfile)
        output_filename = os.path.splitext(filename)[0] + '_reconstructed.csv'
        output_filepath = os.path.join(base_dir, output_filename)

    convert_back(args.pklfile, output_filepath)