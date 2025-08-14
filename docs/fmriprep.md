# Notes on preprocessing with fMRIPrep for `wave1`

Rorqual `$SLURMTMP` is not big enough to save all intermediate files generated from preprocessing some subject, and I found out the hard way.

## 0_index_all_sessions.py

Check if all subject are preprocessed. This is ran once in a while to check status.
Note: so far we are only doing `wave1`.

## 1.1_generate_slurm_script_full.sh

Generate script for preprocessing each subjects including all sessions.

## 1.2_generate_slurm_script_baseline_only.sh 

Generate script for preprocessing selected subject that were not completed in the first attempt.
Only preprocessing anatomical data and baseline.

## 1.3_generate_slurm_script_followup.sh 

Generate script for preprocessing follow up sessions from selected subject that were not completed in the first attempt.

## Notes on improving the workflow

If I were to redo the preprocessing:

1. run anatomical preprocessing first.
2. run functional with anatomical fast track option.
3. run just the standard MNI template.
