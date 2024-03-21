#!/bin/bash

########################################
############# CSCI 2951-O ##############
########################################
E_BADARGS=65
if [ $# -ne 1 ]
then
	echo "Usage: `basename $0` <input>"
	exit $E_BADARGS
fi
	
input=$1

# change this to point to your local installation
# CHANGE it back to this value before submitting
export DOCPLEX_COS_LOCATION=/C/Program\ Files/IBM/ILOG/CPLEX_Studio2211

# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/course/cs2951o/deps/python3.9/lib

source p3_venv/Scripts/activate

# run the solver
python src/main.py $input