import os 
from . import FileSafetyChecks
def read_file(file_path):
    checker = FileSafetyChecks.FileSafetyChecker(working_directory=os.getcwd(), target_file=file_path)
    checker.standard_checks()
    if not os.path.exists(file_path):
        raise ValueError("The provided file path does not exist")
    with open(file_path, "r") as f:
        content = f.read()
    content = content.strip()
    if not content:
        raise ValueError("The provided file is empty")
    return content

