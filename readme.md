# Butler

This script takes the **mysql** or **mariadb** database backups of multiple **Laravel** apps as SQL 
files. Define the project `root` and `depth` in .env file and run the script as a cron job.

Changelog
------

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

Before you can run the script, you have to declare two environment variables 
in `.env` file. An example file has been added for your consistency. Just copy
the `.env.example` file as `.env` and define the values for the following two 
keys.

 - **PROJECT_ROOT**: This will be the directory where all of your Laravel projects 
 reside, e.g. `/home/<user>/projects`, or `/var/www`, or `/usr/share/nginx`. 
 Note that, if you keep your projects into some place which is in `root` directory, 
 you have to run the script as root. You know how Linux works, right?
 
 - **PROJECT_DEPTH**: This value defines the searching depths for directories.
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

 - **COMPRESS_OUTPUT**: Self explanatory. By default compression is enabled. If you want to disable 
 compression and prefer raw SQL output, set the value to anything other than 1.

Output
------
The script will read the database credentials from each of your projects `.env` file and will use it
to generate compressed SQL files along with all of your schemas and data for each of your projects.
You will get the generated SQL file inside each of your projects `storage/app/backup` directory. 
_Note that, these files will not be replaced in the next run, instead a new backup will be 
generated and stored_. The default file naming format is:

```
<dbname>_2020-01-14_13_45_06.[gz|sql|
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
30 3 2 * * /path/to/bash/butler.sh > /path/to/butler_output.log
```

If you do not want a log file:

```
30 3 2 * * /path/to/bash/butler.sh >/dev/null 2>&1
```
