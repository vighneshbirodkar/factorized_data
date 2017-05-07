#!/bin/sh
#
#SBATCH --verbose
#SBATCH --job-name=$JOB_NAME
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --mem=16GB
#SBATCH --cpus-per-task=4
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=vnb222@nyu.edu


USER_NAME=$(whoami)

echo "Starting script.sh"
echo "Username = $USER_NAME"
echo "Command = $COMMAND"

module load mesa/intel/17.0.2
module load python3/intel/3.5.3
module load ffmpeg/intel

cd /scratch/$USER_NAME/code/factorized_data
eval "$COMMAND"
