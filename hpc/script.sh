#!/bin/sh
#
#SBATCH --verbose
#SBATCH --job-name=$JOB_NAME
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --mem=16GB
#SBATCH --ntasks-per-node=8
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=vnb222@nyu.edu


USER_NAME=$(whoami)

echo "Starting script.sh"
echo "Username = $USER_NAME"
echo "Command = $COMMAND"

module load pytorch/intel/20170226

cd /scratch/$USER_NAME/code/factor
eval "$COMMAND"
