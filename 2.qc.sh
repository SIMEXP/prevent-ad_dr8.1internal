#!/bin/bash
#SBATCH --account=rrg-pbellec
#SBATCH --job-name=preventad_qc
#SBATCH --output=/scratch/hwang1/logs/%x_%A.out
#SBATCH --error=/scratch/hwang1/logs/%x_%A.out
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G

module load apptainer

FMRIPREP_DIR=/scratch/$USER/preventad-dr8.1internal/mri/wave1/fmriprep-20.2.8lts
GIGA_AUTO_QC_CONTAINER=/lustre09/project/6003287/containers/giga_auto_qc-0.3.4.sif
QC_OUTPUT=/scratch/$USER/preventad-dr8.1internal/mri/wave1/giga_auto_qc-0.3.4_scrub.5
QC_PARAMS=/lustre09/project/6003287/$USER/prevent-ad_dr8.1internal/utils/qc_params_scrub5.json

mkdir -p $QC_OUTPUT

echo "Running QC"

apptainer run --cleanenv -B ${QC_PARAMS} -B ${FMRIPREP_DIR}:/inputs -B ${QC_OUTPUT}:/outputs ${GIGA_AUTO_QC_CONTAINER} --reindex-bids /inputs /outputs --quality_control_parameters ${QC_PARAMS} group