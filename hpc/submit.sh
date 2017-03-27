JOB_NAME=$1
shift
export COMMAND="$@"
export JOB_NAME=$JOB_NAME


echo "Job name = $JOB_NAME"
echo "Command = $COMMAND"

USER_NAME=$(whoami)

mkdir -p ../logs/$JOB_NAME

sbatch --job-name $JOB_NAME --output ../logs/$JOB_NAME/std.out --error ../logs/$JOB_NAME/std.err script.sh
