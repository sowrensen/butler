import os
import json
import datetime as dt
import subprocess
from send2trash import send2trash


def remove_older(path, days, prefix=None):
    """Remove files older than N days."""
    
    # Delta time to remove files
    delta = ((dt.datetime.today() - dt.timedelta(days=days)) -
             dt.datetime.utcfromtimestamp(0)).total_seconds()
    found_files = []
    
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            filepath = '/'.join([dirpath, filename])
            if not os.path.isfile(filepath):
                continue
            # Last modified time of file
            mtime = os.path.getmtime(filepath)
            # Select file to delete if file is older than delta
            if delta >= mtime:
                # If a prefix is defined only delete files with names start with prefix
                if not prefix is None and filename.startswith(prefix):
                    found_files.append(filepath)
                # Move all found files to trash if no prefix is defined
                if prefix is None:
                    found_files.append(filepath)
    
    print("\nRemoving files older than {} days from {}...".format(days, prefix))
    if len(found_files) > 0:
        for file in found_files:
            print("Removing {}...".format(file))
            send2trash(file)
    else:
        print("No files older than {} days has been found!".format(days))


def run_telescope_pruner(path, hours):
    """
    Run telescope:prune command for requested path.

    For now, the php path is hardcoded, in future it will be
    made dynamic to automatically locate binary executable.
    """
    if not is_package_installed('laravel/telescope', path.joinpath('composer.json')):
        return
    try:
        print("Running telescope:prune...")
        php = "/usr/bin/php"
        subprocess.run([php, str(path.joinpath('artisan')), 'telescope:prune', '--hours={}'.format(hours)], check=True)
    except subprocess.CalledProcessError as error:
        print(error.output)


def is_package_installed(package, composer_file_path):
    """
    Check if specified package is installed in a Laravel project.
    :param package: Name of the package
    :param composer_file_path: composer.json file path
    :return: bool
    """
    if not os.path.exists(composer_file_path):
        return False
    with open(composer_file_path) as file:
        composer = json.load(file)
    file.close()
    return package in composer['require'] or package in composer['require-dev']
