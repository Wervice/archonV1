# Archon Backup
Archon is the open source backup solution that will help you protect your files from damage and restore destructed files easily. Archon Backup Utility supports FTP, FTPS and Windows Network Paths. Archon compresses your backups with modern compression algorithms. It's fully written in Python, HTML, CSS and JavaScript. The fresh and easy backup reports will show you the results of any backup task.

First of all, I want to say thanks to the developers of termcolor. I use termcolor as a module in my applicatioon to style the output. Termcolor is licensed under the MIT License. You can find the license text of it under legal/termcolor.txt. I also want to say Thank You to all the other developers of the oher python-included libraries I used.
## How to install Archon?
### Run Archon
To use Archon, you just have to download the archon folder and execute the python script in it from the command-line.  
For example: `python3 .\__main__.py`.

### Commands
The are the commands to use archon.
### `backup`
This command backups a single file to a location.  
`python3 .\__main__.py backup [file_path] [destination_path]`
### `fbackup`
This command backups one folder and compresses the backup.  
`python3 .\__main__.py fbackup [folder_path] [backup_location]`  
> ⚠ You allways have to use the full path and the path has to end with \
> Correct Example: C:\users\starred\MyPhotos\\  
> Wrong Example: C:\users\starred\MyPhotos
### `restore`
This command restores your files from and backup.  
`python3 .\__main__.py restore [backup_path] [broken_folder_path]`

### The Reports
When Archon has finished an backup, it will popup a report with some information about the backup.  
The report also contains a backup history.
You can also find the history under the assets in the archon base folder as a .csv file.


----
> ‼ __Warning: Archon comes with absolutely no guaranty. If something goes wrong and your files are destroyed or can't be restored, I can't be held responsible for this. Archon is used at your own risk.__
