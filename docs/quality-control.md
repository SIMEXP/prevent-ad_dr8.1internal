# Quality control

## 2.1_run_slurm_qc.sh

We are running giga auto qc version 0.3.4.

## 2.2_add_cerebellum_coverage.py

As some target analysis uses brain parcellation that covers cerebellum, we need to get some stats with coverage.
Based on visual inspection, data with less than 70% of cerebellum coverage will not be usable for such analysis.

