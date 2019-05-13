#!/bin/bash

set -exu

CONFIG=$1

# Run FairFlow formulation of paper matching.
python -m src.exp.fairflow $CONFIG

exit