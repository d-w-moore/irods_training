#!/bin/bash

set -e 

# $1 is full path to any executable with a leading '#!' line

SBATCH_OPTIONS="-o /tmp/slurm-%j.out"

SCRIPT="$1" 
shift

/usr/local/bin/sbatch $SBATCH_OPTIONS "$SCRIPT" "$@" 2>&1 

