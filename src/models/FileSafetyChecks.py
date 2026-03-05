import os
class OutsideWorkingDirectoryError(ValueError):
    def __init__(self, target_file):
        message = f'"{target_file}" as it is outside the permitted working directory'
        super().__init__(message)
class TargetFileDoesNotExistError(ValueError):
    def __init__(self, target_file):
        message = f'Error: The {"directory" if os.path.isdir(target_file) else "file"} "{target_file}" does not exist.'
        super().__init__(message)
        
class FileSafetyChecker:
    def __init__(self, working_directory,target_file, content=None):
        self.working_directory = working_directory  
        self.target_file = target_file
        self.abs_working_directory = os.path.abspath(working_directory)   
        self.abs_target_file = os.path.join(self.abs_working_directory, target_file) if not os.path.isabs(target_file) else os.path.abspath(target_file)
        self.content = content

    def standard_checks(self):
        if not os.path.exists(self.abs_working_directory):
            raise ValueError(f'Error: The working directory "{self.working_directory}" does not exist.')
        elif not self.abs_target_file.startswith(self.abs_working_directory+os.sep):
            raise OutsideWorkingDirectoryError(self.target_file)
        elif not os.path.exists(self.abs_target_file):
            raise TargetFileDoesNotExistError(self.target_file)
        else: 
            pass