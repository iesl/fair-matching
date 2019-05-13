#!/usr/bin/env bash

export MATCH_ROOT=`pwd`

export PYTHON_EXEC=python
export PYTHONPATH=$MATCH_ROOT/src:$PYTHONPATH

if [ ! -f $MATCH_ROOT/.gitignore ]; then
    echo ".gitignore" > $MATCH_ROOT/.gitignore
    echo "target" >> $MATCH_ROOT/.gitignore
    echo ".idea" >> $MATCH_ROOT/.gitignore
    echo "__pycache__" >> $MATCH_ROOT/.gitignore
    echo "dep" >> $MATCH_ROOT/.gitignore
    echo "data" >> $MATCH_ROOT/.gitignore
    echo "test_out" >> $MATCH_ROOT/.gitignore
    echo "exp_out" >> $MATCH_ROOT/.gitignore
    echo ".DS_STORE" >> $MATCH_ROOT/.gitignore
    echo "*.iml" >> $MATCH_ROOT/.gitignore
    echo "*gurobi.log*" >> $MATCH_ROOT/.gitignore
fi