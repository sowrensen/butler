# Butler

This script takes the **mysql** or **mariadb** database backups of multiple **Laravel** apps as SQL 
files. Define the project `root` and `depth` in .env file and run the script as a cron job.

Changelog
------

#### Version 1.4
 
 - Improved process management.
 - Now `telescope:prune` command will only run when it is applicable, i.e. `telescope` is installed.
 - Code refactoring.

#### Version 1.3
 
 - Added `laravel-telescope` data pruning support.
 - Improved code structure.
 - Fixed documentation.

#### Version 1.2

 - Added option to remove older backups.
 - Now optional keys need not have to be specified in `.env` file.  
 - Improved visual feedback.

#### Version 1.1

 - Added option to enable or disable generated file compression.

#### Version 1.0

 - Initial release

Usage
------

### Setup

Run following commands in your terminal to copy this repository and for primary setup. I assume 
that **mysql** or **mariadb** is installed on your machine, cause the script uses `mysqldump` 
under the hood to take the backup. You will need [Pipenv](https://github.com/pypa/pipenv) 
to use this script however.

```shell
git clone https://github.com/sowrensen/butler.git
cd butler
pipenv install
cp .env.example .env
```

### Enviroment Variables

Before you can run the script, you have to declare some environment variables in a 
`.env` file. An example `.env` file has been added for your consistency. Just copy
the `.env.example` file as `.env` and define the values for the following keys.


 - **PROJECT_ROOT** (required): This will be the directory where all of your Laravel projects 
 reside, e.g. `/home/<user>/projects`, or `/var/www`, or `/usr/share/nginx`. 
 Note that, if you keep your projects into some place which is in `root` directory, 
 you have to run the script as root. You know how Linux works, right?
 
 - **PROJECT_DEPTH** (required): This value defines the searching depths for directories.
 The value should be either 1 or 2. If you have subdirectories in your root 
 directory, you have to put 2, else put 1. For example, suppose this is the file
 structure inside your `PROJECT_ROOT`:
 
   ```
   App-1/
    - App_1_Instance_1/
    - App_1_Instance_2/
   App-2/
    - App_2_Instance_1/
    - App_2_Instance_2/
   ``` 
   
   In the above case, you have to put depth value 2. If there is only one
   level of application directory, you can put 1.

 - **COMPRESS_OUTPUT** (optional, default=1): Self explanatory. By default compression is enabled. 
 If you want to disable compression and prefer raw SQL output, set the value to anything other than 1.
 
 - **REMOVE_OLDER_FILES** (optional, default=0): This key takes number of days as input. By default it 
 is disabled. If you specify any other number, the script will remove files generated before specified 
 number of days. So if you specify 10, it will delete all backups generated before 10 days from next run.
 
 - **PRUNE_TELESCOPE_DATA** (optional, default=-1): If you're using Laravel Telescope in
 your project, this option might come handy. Specify any number (starting from 0) as value
 of this key and butler will run `php artisan telescope:prue --hours=number` for your project.
 By default it is disabled. _Note that, if telescope is not installed in some of your project
 it will show an error - `There are no commands defined in the "telescope" namespace.` - which
 has no impact on the execution of the main program._

Output
------
The script will read the database credentials from each of your projects `.env` file and will use it
to generate compressed SQL files along with all of your schemas and data for each of your projects.
You will get the generated SQL file inside each of your projects `storage/app/backup` directory. 
_Note that, these files will not be replaced in the next run, instead a new backup will be 
generated and stored_. The default file naming format is:

```
<dbname>_2020-01-14_13_45_06.[gz|sql]
```

You can use these SQL files to restore data anytime.

Cron Example
------------

You can run the file directly from cron job. However, if you face difficulties to run pipenv from 
cron, better you create a bash script like this.

```
#!/bin/sh

PYTHON="/path/to/pipenv/python"
BUTLER="/path/to/butler"
PIPENV="/path/to/pipenv"
SCRIPT="butler.py"

cd "${BUTLER}" && "${PIPENV}" run "${PYTHON}" "${SCRIPT}"
```

Make the bash script executable by running:

```shell
chmod +x butler.sh
```

Now run the bash script as cron job. This following cron job will run on every **two days** at **03:30 AM** 
and write the log into the defined log file.

```
30 3 */2 * * /path/to/bash/butler.sh > /path/to/butler_output.log
```

If you do not want a log file:

```
30 3 */2 * * /path/to/bash/butler.sh >/dev/null 2>&1
```
