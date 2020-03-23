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
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
from remover import remove_older, run_telescope_pruner


def is_compression_enabled():
    """Check if compression is enabled. Default is True."""
    try:
        return True if int(os.environ['COMPRESS_OUTPUT']) == 1 else False
    except KeyError as error:
        return True


def remove_older_files():
    """
    Check if removing older files is enabled. Default is 0 which depicts false.
    :return int The number of days
    """
    try:
        return int(os.environ['REMOVE_OLDER_FILES'])
    except KeyError as error:
        return 0


def prune_telescope_data():
    """
    Check if telescope data pruning is enabled. Default is -1 which depicts false.
    :return int The number of hours
    """
    try:
        return int(os.environ['PRUNE_TELESCOPE_DATA'])
    except KeyError as error:
        return -1


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
    
    # Get output compression setting
    compress_output = is_compression_enabled()
    
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
            dbname = env['DB_DATABASE']
            user = env['DB_USERNAME']
            password = env['DB_PASSWORD']
            
            # We will be keeping the backups into a directory named backup inside the app directory
            backup_directory = public_directory.joinpath('backup')
            os.makedirs(backup_directory, exist_ok=True)
            
            print('\n------------------ [%s] ------------------' % dbname)
            # Run telescope data pruner if enabled
            if prune_telescope_data() > -1:
                run_telescope_pruner(public_directory.parent.parent, prune_telescope_data())
            
            # Run actual mysqldump process
            run(user, password, dbname, backup_directory)
            count += 1
            print('Success!')
            
            # Remove older backups if feature is enabled
            if remove_older_files() > 0 and backup_directory.exists():
                remove_older(str(backup_directory), remove_older_files(), dbname)
            
            print('---------------- //[%s]// ----------------' % dbname)
        except Exception as error:
            print('Error occurred: ' + str(error))
    
    print('\nBackup generated for %d projects.' % count)
    print('\nExecution finished at: ' + str(datetime.now()))


def generate_file_name(dbname, backup_directory):
    """
    Generate file name
    :param dbname: The database name
    :param backup_directory: Location of backup directory
    :return: str
    """
    now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    # Filename consists of the database name and current timestamp as human readable format
    filename = dbname + '_' + now + ('.gz' if is_compression_enabled() else '.sql')
    return backup_directory.joinpath(filename)


def run(user, password, dbname, backup_directory):
    """
    Run mysqldump process
    :param user: Database username
    :param password: Database password
    :param dbname: Database name
    :param backup_directory: Location of backup directory
    """
    compress_output = is_compression_enabled()
    print("Running mysqldump on {}...".format(dbname))
    args = ['mysqldump', '-u{}'.format(user), '-p{}'.format(password), dbname]
    with open(generate_file_name(dbname, backup_directory), 'wb') as backup:
        process1 = subprocess.Popen(args, stdout=subprocess.PIPE if compress_output else backup)
        if compress_output:
            # If compression is enabled, open a second process and compress the output
            process2 = subprocess.Popen('gzip', stdin=process1.stdout, stdout=backup)
            process1.stdout.close()
    backup.close()


def start():
    """
    Initializes environment variables and runs main program.
    """
    try:
        valid_depths = (1, 2)
        print('Reading environment variables from .env file...')
        project_root = os.environ['PROJECT_ROOT']
        project_depth = os.environ['PROJECT_DEPTH']
        
        if not project_root:
            raise ValueError("Error! Project root is not defined. You must set a project root in .env file.")
        
        if int(project_depth) not in valid_depths:
            raise ValueError(
                "Error! Invalid value defined for depth, value must be between 1 and 2.")
        
        print("""
        Project Root:           %s
        Project Depth:          %s
        """ % (project_root, project_depth))
        backup_database(project_root, project_depth)
        return
    except ValueError as error:
        print(error)
    except KeyError as error:
        print('\nError! Please define necessary keys in .env file.')


if __name__ == "__main__":
    start()
