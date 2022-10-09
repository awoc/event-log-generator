# Event Log Processor

This project contains Python scripts used to convert and process event log files 
to the distributed event log format used in other projects.

## Content

- The `cpee/` module contains the script used to merge multiple .yaml files in the CPEE format 
to a single .xes event log.
The script requires all message templates located in `correlator/message-templates`
which are by default not checked in to Git.
The message templates are generated using the `data-generation` project.

- The `colliery/` module contains the script used 
to convert the [colliery validation dataset](https://bitbucket.org/proslabteam/colliery_validation/src/master/).

Requires at least Python version 3.10.
