import argparse
import os

def executor(directory_name: str):
    # Sorted list of all files in the directory
    file_names = sorted(f for f in os.listdir(directory_name) if os.path.isfile(os.path.join(directory_name, f)))
    
    # Initialize an array to store file contents
    file_contents = []
    
    # Iterate over the sorted file names and read their contents
    for file_name in file_names:
        file_path = os.path.join(directory_name, file_name)
        with open(file_path, 'r') as file:
            file_contents.append(file.read())
    
    print(file_contents)

def main():
    parser = argparse.ArgumentParser(description="Process a directory name.")
    parser.add_argument("directory", type=str, help="Path to the directory")
    args = parser.parse_args()
    directory_name = args.directory
    
    if not os.path.isdir(directory_name):
        print(f"The provided path is not a valid directory: {directory_name}")
        exit(0)
    else:
        executor(directory_name)

if __name__ == "__main__":
    main()
