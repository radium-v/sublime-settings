Sublime Files
-------------

__A keyboard driven file navigation/opening plugin for Sublime Text 2__


Sublime Files works entirely through the command palette. By running the
Sublime Files Navigator, you can "cd" around directories similar to how
you would on a command line in order to open up files. New files will open up in new tabs.


Because Sublime Files actually navigates the file system by changing directories,
the navigator remembers and starts from last visited directory on subsequent uses.
To open the navigator, you can either just invoke the command pallette command or
use the keybinding ctrl+super+n 


Built with Mac OSX, but all the calls have been designed to be platform agnostic and thus should work regardless of system. However, this is untested on Windows.

----------

__Installation__

Sublime Files can be installed through Sublime Package Control.

----------

__Usage__

Sublime files an be activated with the command palette command: "Sublime Files: Open Navigator", or with the key command ctrl+super+n (or ctrl+alt+n for windows).
The first option will always show the current directory. Selecting another directory will nagivate to that directory and selecting a file will open that file.


There are a few notable options:


- Selecting "Directory actions" will pop up a small list of actions that can be applied onto the current directory. Mainly, a user can create new files, add the directory to the current project, and open a terminal at the directory.

- Selecting "~/" navigates to the home directory.

- Selecting "../" navigates to the parent directory.

- Selecting "To current View" navigates to the directory of the current file being editted.


----------

__Open Terminal__


For OSX/Linux systems, Sublime Files can open up a terminal at the current directory navigated to.
In order for this feature to work properly, you will have to modify the term\_command field in the 
SublimeFiles.sublime-settings text file
located in the SublimeFiles plugin directory. As a default, it is set to open up Terminal.app for OSX systems. 

For example, Gnome Terminal and iTerm2 users respectively will want to change term\_command in SublimeFiles.sublime-settings to: 

    - "term_command": "gnome-terminal --working-directory="
    - "term_command" : "open -a iTerm\ 2 "

