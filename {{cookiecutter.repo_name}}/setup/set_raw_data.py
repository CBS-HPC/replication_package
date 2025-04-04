import os
import json
import argparse
import subprocess
from datetime import datetime
import pathlib

from utils import *
from readme_templates import *

# Change to project root directory
project_root = pathlib.Path(__file__).resolve().parent.parent
os.chdir(project_root)

def get_file_info(destination):
    files = [f for f in os.listdir(destination) if os.path.isfile(os.path.join(destination, f))]
    number_of_files = len(files)
    total_size = sum(os.path.getsize(os.path.join(destination, f)) for f in files) / (1024 * 1024)
    file_formats = set(os.path.splitext(f)[1].lower() for f in files)
    return number_of_files, total_size, file_formats

def add_to_json(json_file_path, entry):
    """
    Adds or updates an entry in the JSON file.

    Parameters:
        json_file_path (str): Path to the JSON file.
        entry (dict): The dataset metadata to add or update.
    """
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            datasets = json.load(json_file)
    else:
        datasets = []

    # Check if the dataset already exists
    if entry["hash"]:
        existing_entry = next((item for item in datasets if item["data_name"] == entry["data_name"] and item["destination"] == entry["destination"] and item["hash"] == entry["hash"]),None)
    else:
        existing_entry = next((item for item in datasets if item["data_name"] == entry["data_name"] and item["destination"] == entry["destination"]), None)
    
    if existing_entry:
        # Update the existing entry
        datasets[datasets.index(existing_entry)] = entry
        print(f"Updated existing dataset entry for {entry['data_name']}.")

    elif not existing_entry :
        # Add a new entry
        datasets.append(entry)
        print(f"Added new dataset entry for {entry['data_name']}.")

    # Write updated datasets to the JSON file
    with open(json_file_path, "w") as json_file:
        json.dump(datasets, json_file, indent=4)
    print(f"Metadata saved to {json_file_path}")

def set_dataset(data_name, destination, source:str = None, run_command:str = None,json_file_path:str = "./datasets.json" , doi:str = None,citation:str = None,license:str=None):
    """
    Executes a data download process and tracks created files in the specified path.

    Parameters:
        data_name (str): Name of the dataset.
        source (str): The remote URL or path to the dataset.
        run_command (str): A command for executing the download function/script.
                           The script will ensure {source} and {destination} are appended.
        destination (str): The path where the data will be stored. Defaults to './data/raw/data_name' if None.
    """

    os.makedirs(destination, exist_ok=True)

    initial_files = set(os.listdir(destination))

    if run_command:
        command_parts = run_command.split()
        command_list = command_parts + [source, destination]

        if is_installed(command_parts[0]):
            try:
                result = subprocess.run(command_list, check=True, text=True, capture_output=True)
                print(f"Command output:\n{result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                print(f"Command output:\n{e.output}")
                return
        else:
            raise FileNotFoundError(f"The executable '{command_parts[0]}' was not found in the PATH.")

        updated_files = set(os.listdir(destination))
        data_files = list(updated_files - initial_files)
    else:
        data_files = list(initial_files)

    number_of_files, total_size, file_formats = get_file_info(destination)

    if number_of_files > 1000: # FIX ME !!
        print("It is recommended to zip datasets with >1000 files when creating a replication package: https://aeadataeditor.github.io/aea-de-guidance/preparing-for-data-deposit.html#data-structure-of-a-replication-package")


    hash= get_git_hash(destination)

    new_entry = {
        "data_name": data_name,
        "destination": destination,
        "hash":hash,
        "number_of_files": number_of_files,
        "total_size_mb": int(total_size),
        "file_formats": list(file_formats),
        "data_files": data_files,
    
        "timestamp": datetime.now().isoformat(),
    }

    if hash:
        new_entry["hash"] = hash


    if source:
        new_entry["source"] = source

    if run_command:
        new_entry["run_command"] = " ".join(command_list)

    if doi:
        new_entry["DOI"] = doi

    if citation:
        new_entry["citation"] = citation
    
    if license:
        new_entry["license"] = license

    # Add or update the JSON metadata
    add_to_json(json_file_path, new_entry)

    try:
        markdown_table, full_table = generate_dataset_table(json_file_path)
        append_dataset_to_readme(markdown_table)

        with open("dataset_list.md", 'w') as markdown_file:
            markdown_file.write(full_table)
    except Exception as e:
        print(e)

@ensure_correct_kernel
def set_raw_data(data_name:str= None, source:str=None, run_command:str=None, destination:str=None, doi:str = None,citation:str = None,license:str=None):
    
    def sanitize_folder_name(name):
        return name.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
    
    def get_all_raw_files():
        # Get all files and folders in the './data/raw/' directory, excluding .git folders and .gitignore/.gitkeep files
        raw_data_dir = './data/raw/'
        
        # List files and directories, excluding .git folders and .gitignore/.gitkeep files
        return [
            f for f in os.listdir(raw_data_dir) 
            if os.path.isdir(os.path.join(raw_data_dir, f)) or 
            (os.path.isfile(os.path.join(raw_data_dir, f)) and not f.startswith(".git") and f not in [".gitignore", ".gitkeep"])
        ]

    # If all input parameters are None, gather all files and folders from './data/raw/'
    if all(param is None for param in [data_name, source, run_command, destination, doi, citation, license]):
        raw_files = get_all_raw_files()
        for file in raw_files:
            set_dataset(data_name=file, source=None, run_command=None, destination=f'./data/raw/{file}', doi=None, citation=None, license=None)
        return

    if destination is None:
        destination = f"./data/raw/{sanitize_folder_name(data_name)}"


    set_dataset(data_name = data_name,destination = destination, source=source, run_command=run_command,json_file_path="./datasets.json", doi=doi,citation=citation,license=license)

def save_datalist(full_table ,markdown_file_path="dataset_list.md"):

    # Save the markdown table to a file
    with open(markdown_file_path, 'w') as markdown_file:
            markdown_file.write(full_table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set data source and monitor file creation.")
    parser.add_argument("--name", default=None, help="Name of the dataset.")
    parser.add_argument("--source", default=None, help="Remote URL or path to the dataset.")
    parser.add_argument("--command", default=None, help="Command for executing the download function/script.")
    parser.add_argument("--destination", default=None, help="Path where data will be stored (optional).")
    parser.add_argument("--doi", default=None, help="DOI of the dataset (optional).")
    parser.add_argument("--citation", default=None, help="Citation of the dataset (optional).")
    parser.add_argument("--license", default=None, help="License of the dataset (optional).")
    args = parser.parse_args()

    set_raw_data(args.name, args.source, args.command, args.destination, args.doi, args.citation,args.license)


#python set_raw_data.py deic_dataset1 "https://sid.storage.deic.dk/cgi-sid/ls.py?share_id=CyOR8W3h2f" "./src/deic_storage_download.py"