#!/bin/bash
CONTAINER_PATH="/lustre09/project/6003287/containers"
VERSION="20.2.8"
EMAIL=${SLACK_EMAIL_BOT}

echo "Create fmriprep-slurm scripts for preventad"
DATASET_PATH="/lustre09/project/6003287/hwang1/prevent-ad/mri/wave1"
OUTPUT_PATH="/scratch/hwang1/preventad_fmriprep-20.2.8lts_1754943288"

echo "run fmriprep-slurm"
PARTICIPANTS="MTL0051 MTL0054 MTL0057 MTL0060 MTL0062 MTL0064 MTL0065 MTL0069 \
        MTL0078 MTL0079 MTL0080 MTL0081 MTL0082 MTL0085 MTL0086 MTL0091 \
        MTL0092 MTL0093 MTL0094 MTL0101 MTL0103 MTL0104 MTL0106 MTL0107 \
        MTL0108 MTL0110 MTL0111 MTL0112 MTL0113 MTL0122 MTL0124 MTL0125"

bash ./utils/fmriprep_slurm_singularity_run.bash \
    ${OUTPUT_PATH} \
    ${DATASET_PATH} \
    fmriprep-${VERSION}lts \
    --email=${EMAIL} \
    --time=3:00:00 \
    --mem-per-cpu=12288 \
    --cpus=1 \
    --container fmriprep-${VERSION}lts \
    --prepro func \
    --participant-label ${PARTICIPANTS}

