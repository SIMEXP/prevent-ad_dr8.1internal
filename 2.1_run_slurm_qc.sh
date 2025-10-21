#!/bin/bash
#SBATCH --account=rrg-pbellec
#SBATCH --job-name=preventad_qc
#SBATCH --output=/scratch/hwang1/logs/%x_%A-%a.out
#SBATCH --error=/scratch/hwang1/logs/%x_%A-%a.err
#SBATCH --time=36:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --array=0-381

# SUBJECTS=($(ls -d $FMRIPREP_DIR/sub-*/))
# echo $((${#SUBJECTS[@]}-1))

module load apptainer

FMRIPREP_DIR=/scratch/$USER/preventad-dr8.1internal/mri/wave1/fmriprep-20.2.8lts
GIGA_AUTO_QC_CONTAINER=/lustre09/project/6003287/containers/giga_auto_qc-0.3.4.sif
QC_OUTPUT=/scratch/$USER/preventad-dr8.1internal/mri/wave1/giga_auto_qc-0.3.4_scrub.5
QC_PARAMS=/lustre09/project/6003287/$USER/prevent-ad_dr8.1internal/utils/qc_params_scrub5.json


SUBJECTS=($(ls -d $FMRIPREP_DIR/sub-*/))
subject_dir=${SUBJECTS[$SLURM_ARRAY_TASK_ID]}

# Check if the directory contains .html files and skip it if it does
if [[ -n $(find "$subject_dir" -maxdepth 1 -type f -name "*.html") ]]; then
    echo "Skipping subject directory with .html files: $subject_dir"
    continue
fi

subject_label=$(basename $subject_dir)
subject_label=${subject_label#sub-}  # Remove "sub-"

echo "Processing subject: $subject_label"

# Create a directory for the current subject
subject_output_dir="$QC_OUTPUT/sub-$subject_label"
mkdir -p "$subject_output_dir"

# run qc if the directory does not contain .tsv files
if [[ -n $(find "$subject_output_dir" -maxdepth 1 -type f -name "*rest*.tsv") ]]; then
    echo "Skipping subject directory with .tsv files: $subject_output_dir"
    exit 0
fi

apptainer run --cleanenv -B ${QC_PARAMS} -B ${FMRIPREP_DIR}:/inputs -B ${subject_output_dir}:/outputs \
    ${GIGA_AUTO_QC_CONTAINER} /inputs /outputs participant \
    --quality_control_parameters ${QC_PARAMS}  \
    --participant_label $subject_label \
    --task rest