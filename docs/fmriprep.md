# 1. Notes on preprocessing with fMRIPrep

Rorqual `$SLURMTMP` is not big enough to save all intermediate files generated from preprocessing some subject, and I found out the hard way.

## 1.1_generate_slurm_script_full.sh

Generate script for preprocessing each subjects including all sessions.

## 1.2_generate_slurm_script_baseline_only.sh 

Generate script for preprocessing selected subject that were not completed in the first attempt.
Only preprocessing anatomical data and baseline.

## 1.3_generate_slurm_script_followup.sh 

Generate script for preprocessing follow up sessions from selected subject that were not completed in the first attempt.
