#!/bin/bash

set -exu

CONFIG=$1

# Run FairIR formulation of paper matching.
python -m src.exp.fairir $CONFIG

exit