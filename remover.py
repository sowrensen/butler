import os
import datetime as dt
from send2trash import send2trash


def remove_older(path, days, prefix=None):
    """Remove files older than N days."""
    
    # Delta time to remove files
    delta = ((dt.datetime.today() - dt.timedelta(days=days)) - dt.datetime.utcfromtimestamp(0)).total_seconds()
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
    
    if len(found_files) > 0:
        for file in found_files:
            print('Removing %s...' % file)
            send2trash(file)
    else:
        print('No files older than %d days has been found!' % days)
