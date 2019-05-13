#!/bin/bash

set -exu

CONFIG_DIR=$1

# Create boxplot for assignments.
python -m src.plot.boxplot_quants $CONFIG_DIR

exit