#!/bin/bash

########################################
############# CSCI 2951-O ##############
########################################

# Update this file with instructions on how to compile your code
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/course/cs2951o/deps/python3.9/lib
/course/cs2951o/deps/python3.9/bin/python3.9 -m venv p3_venv
source p3_venv/bin/activate
pip3 install -r requirements.txt