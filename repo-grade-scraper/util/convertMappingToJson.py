import json
import argparse
import os

def convert_to_json(module_number):
    output_path = f"./json-files/module-{module_number}.json"

    data = []
    with open(f"./text-files/module-{module_number}.txt", 'r') as infile: # ZACHHHHHHH: TEXT FILES MUST BE IN THIS DIRECTORY AND IN THIS FORMAT
        for line in infile:
            # Correctly split the line into module and TA username parts
            parts = line.strip().split(':')
            if len(parts) > 2:  # Ensure there are at least 3 parts (including empty ones)
                module = parts[1]  # Get the module name, assuming it's between the first two colons
                ta_username = parts[2].split(',')[1]  # Get the TA username, assuming it follows the module name and ends with a comma
                data.append({"repo": module, "grader": ta_username})
            else:
                print(f"Skipping malformed line: {line}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the JSON data to the file
    with open(output_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    print(f"Conversion to JSON completed successfully. Output file: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert a text file to JSON format with keys "Module" and "TA Username".')
    parser.add_argument('module_number', help='Module number of the text file (as recieved from Prof. Sproull). The file must be named "module-<module_number>.txt"')
    args = parser.parse_args()
    convert_to_json(args.module_number)

if __name__ == "__main__":
    main()
