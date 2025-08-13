#!/bin/bash
CONTAINER_PATH="/lustre09/project/6003287/containers"
VERSION="20.2.8"
EMAIL=${SLACK_EMAIL_BOT}

module load apptainer/1.3.5
echo "Create fmriprep-slurm scripts for preventad"

DATASET_PATH="/lustre09/project/6003287/hwang1/prevent-ad/mri/wave1"
echo $DATASET_PATH
time=`date +%s`
OUTPUT_PATH="/scratch/hwang1/preventad_fmriprep-${VERSION}lts_${time}"

mkdir -p $OUTPUT_PATH

echo "run BIDS validator on the dataset"
# you only need this done once
apptainer exec -B ${DATASET_PATH}:/DATA \
    ${CONTAINER_PATH}/fmriprep-${VERSION}lts.sif bids-validator /DATA \
    > ${OUTPUT_PATH}/bids_validator.log

echo "run fmriprep-slurm"

# running the script from the current directory, reference
# fmriprep_slurm_singularity_run.bash from one level up
bash ./utils/fmriprep_slurm_singularity_run.bash \
    ${OUTPUT_PATH} \
    ${DATASET_PATH} \
    fmriprep-${VERSION}lts \
    --email=${EMAIL} \
    --time=36:00:00 \
    --mem-per-cpu=12288 \
    --cpus=1 \
    --container fmriprep-${VERSION}lts
