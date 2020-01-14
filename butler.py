#!/usr/bin/env python3
"""
|------------------------------------------------------------
| butler.py
|------------------------------------------------------------
| This script takes the database backups of multiple Laravel
| apps as SQL files. Define the project root and depth in
| .env file and run the script as a cron job.
| 
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
import sys


def backup_database(project_root, project_depth):
    """
    Run mysqldump and backup database as SQL file.
    """
    # Validate project directory
    try:
        ROOT_DIRECTORY = Path(project_root)
        if not os.path.exists(ROOT_DIRECTORY):
            raise IOError('Error! Project directory not found, aborting...')
    except IOError as error:
        print(str(error))
        sys.exit(0)
    
    # The glob for searching
    TARGET_LARAVEL_DIRECTORY = '*' * int(project_depth) + '/*storage/app'
    
    # Search and get the Laravel projects, in this case, we are
    # targeting directories which has /storage/app subdirectory,
    # i.e. where user uploaded files reside.
    print('Searching for directories...\n')
    PUBLIC_PATH = ROOT_DIRECTORY.glob(TARGET_LARAVEL_DIRECTORY)
    count = 0
    for public_directory in PUBLIC_PATH:
        # Check if it's not a directory, mainly for safekeeping
        if not public_directory.is_dir():
            continue
        
        try:
            # Load the .env variables as a dictionary
            env_file = public_directory.parent.parent / '.env'
            env = dotenv_values(dotenv_path=env_file)
            
            # Get necessary keys from .env file
            dbname = env['DB_NAME']
            user = env['DB_USER']
            password = env['DB_PASSWORD']
            now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
            
            # We will be keeping the backups into a directory named backup inside the app directory
            backup_directory = public_directory.joinpath('backup')
            if not os.path.exists(backup_directory):
                os.mkdir(backup_directory)
            # Filename consists of the database name and current timestamp as human readable format
            filename = dbname + '_' + now + '.sql'
            # The backup file path
            filepath = backup_directory.joinpath(filename)
            # The command to run, note that the command is a native mysql command that will run in
            # shell, it has nothing to do with Python, hence we cannot catch an error here.
            print('\nRunning mysqldump on %s...' % dbname)
            cmd = "mysqldump -u{} -p{} {} > {}".format(user, password, dbname, filepath)
            os.system(cmd)
            count += 1
            print('Success!')
        except Exception as error:
            print('Error occurred: ' + str(error))
    
    print('\nBackup generated for %d projects.' % count)
    print('\nExecution finished at: ' + str(datetime.now()))


def run():
    """
    Initializes environment variables and runs main program.
    """
    try:
        valid_depths = (1, 2)
        print('Reading environment variables from .env file...\n')
        project_root = os.environ['PROJECT_ROOT']
        project_depth = os.environ['PROJECT_DEPTH']
        
        if not project_root:
            raise ValueError("Error! Project root is not defined. You must set a project root in .env file.")
        
        if int(project_depth) not in valid_depths:
            raise ValueError(
                "Error! Invalid value defined for depth, value must be between 1 and 2.")
        
        backup_database(project_root, project_depth)
        return
    except ValueError as error:
        print(error)
    except KeyError as error:
        print('Error! Please define necessary keys in .env file.')


if __name__ == "__main__":
    run()