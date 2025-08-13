#!/bin/bash

set -- "${1%/}" "${2%/}" "${@:3}" # trick to remove last path char from first arg (dataset path)
PROJECT_PATH="/lustre03/project/6003287"
FMRIPREP_SLURM_PATH="$PROJECT_PATH/$USER/prevent-ad_dr8.1internal/fmriprep-slurm"
DATASET_PATH=$2
DATASET_FOLDER="${DATASET_PATH%/*}"
DATASET_NAME=${DATASET_PATH##*/}
OUTPUT_ROOT=$1
OUTPUT_DIR=$OUTPUT_ROOT/$DATASET_NAME
TEMPLATEFLOW_DIR=/home/$USER/.cache/templateflow
PYTHON_CMD="python /fmriprep-slurm/fmriprep-slurm/main.py "${@:2}" --output-path "$OUTPUT_DIR

echo "###"
echo "singularity_run.bash "$@
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
module load singularity/3.8

echo "Creating templateflow directory in "$TEMPLATEFLOW_DIR
mkdir -p $TEMPLATEFLOW_DIR

echo "Running fmriprep-slurm inside singularity with the following command"
echo $PYTHON_CMD
mkdir -p $OUTPUT_DIR
echo $PYTHON_CMD | xargs singularity exec -B $FMRIPREP_SLURM_PATH:/fmriprep-slurm \
  -B $DATASET_FOLDER:/DATA \
  -B /etc/pki:/etc/pki \
  -B $TEMPLATEFLOW_DIR:/templateflow \
  -B $OUTPUT_DIR:/OUTPUT \
  $PROJECT_PATH/containers/fmriprep-20.2.7lts.sif

echo ""
echo "Finished!"
echo ""
echo "Please review your slurm scripts in "$OUTPUT_DIR" before submitting them with:"
echo "find "$OUTPUT_DIR"/.slurm/smriprep_sub-*.sh -type f | while read file; do sbatch \"\$file\"; done"
echo "###"
