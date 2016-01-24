# multicmd

A simple Python + Tkinter program to execute long running commands in parallel and track their progress.

Should work on every platform, tested on Linux, FreeBSD and Windows.

## Usage

1. Import a TSV (tab separated values) file by pressing  the "Open" button
2. Write the command to be executed into the text box
3. Choose the number of parallel processes with the spinner
4. Click "Start" and wait for the commands to complete
5. The "Result" column will contain the exit code of every command

You can stop and restart as needed, rows with results will not be run again.

## Command line

The command line will be passed onto a shell so you can write the command line just like you would write commands into a shell.

Prior to being passed onto a shell, the command line will be formatted using standard Python `str.format()`, once for every imported row.

Hint: because the command line is passed to a shell, you can use the standard ">" operator to send the command's output to a file.

## Input file

A standard TSV (tab separated values) file with headers on the first row

## Store commands

You can store commands by pressing Ctrl + S (or from the menus), they will be loaded at startup from a JSON-based settings file. Stored commands can be used from the dropdown menu.
You can forget stored commands by pressing Ctrl + F (or from the menus).

## Dealing with results

Rows with results in them will not be run again. Therefore, if you want to re-run all of your commands, you need to use the Reset (Ctrl + E) functionality.

Of course, you might also need to re-run commands because some of them failed with a non-zero exit code. In that case, you can use the Prune (Ctrl + R) functionality. It will remove all rows with exit code 0 and clear all the rest. This way you can gradually work through your commands until all of them have succeeded.


## Usage example

Suppose you have 10 directories you need to sync with rsync.

First, create a TSV file with headers, such as:

src | dst | log
--- | --- | ---
/mnt/disk1/dir1 | /mnt/disk2/dir1 | /logs/dir1.log
/mnt/disk1/dir2 | /mnt/disk2/dir2 | /logs/dir2.log
/mnt/disk1/dir3 | /mnt/disk2/dir3 | /logs/dir3.log
/mnt/disk1/dir4 | /mnt/disk2/dir4 | /logs/dir4.log
/mnt/disk1/dir5 | /mnt/disk2/dir5 | /logs/dir5.log
/mnt/disk1/dir6 | /mnt/disk2/dir6 | /logs/dir6.log
/mnt/disk1/dir7 | /mnt/disk2/dir7 | /logs/dir7.log
/mnt/disk1/dir8 | /mnt/disk2/dir8 | /logs/dir8.log
/mnt/disk1/dir9 | /mnt/disk2/dir9 | /logs/dir9.log
/mnt/disk1/dir10 | /mnt/disk2/dir10 | /logs/dir10.log

Then write the command line:

    rsync -avh "{0}" "{1}" > "{2}"

Finally, define the number of parallel executions and hit "Start".

## Dependencies

My `jsonconfig` library.
