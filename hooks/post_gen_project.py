import subprocess
import sys

# Add the directory to sys.path
script_dir = "setup"
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Run the script
subprocess.run(["python", "setup/create.py"])
