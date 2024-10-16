import csv
import argparse

import os

def convert_to_csv(input_path, output_path=None):
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '.csv'
    
    with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['Module', 'TA Username'])
        
        for line in infile:
            # Correctly split the line into module and TA username parts
            parts = line.strip().split(':')
            if len(parts) > 2:  # Ensure there are at least 3 parts (including empty ones)
                print(parts)
                module = parts[1]  # Get the module name, assuming it's between the first two colons
                ta_username = parts[2].split(',')[1]  # Get the TA username, assuming it follows the module name and ends with a comma
                csv_writer.writerow([module, ta_username])
            else:
                print(f"Skipping malformed line: {line}")

    print(f"Conversion to CSV completed successfully. Output file: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert a text file to CSV format with columns "Module" and "TA Username".')
    parser.add_argument('input_path', help='Path to the input text file')
    parser.add_argument('-o', '--output', help='Path to the output CSV file. If not provided, the output file name is derived from the input file name with a .csv extension.', default=None)
    
    args = parser.parse_args()
    convert_to_csv(args.input_path, args.output)

if __name__ == "__main__":
    main()

