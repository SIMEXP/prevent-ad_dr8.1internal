"""
Check cerebellum coverage of all resting state functional scans.

https://github.com/diedrichsenlab/cerebellar_atlases
"""
from nilearn import image
from nilearn.plotting import plot_roi
import matplotlib.pyplot as plt 
import numpy as np
from pathlib import Path
import pandas as pd


def create_cerebellum_mask():
    """Create a cerebellum mask in MNI space."""
    path_cerebellum = "data/tpl-MNI152NLin6AsymC_desc-cerebliberal_mask.nii"
    path_cerebellum_atlas = "data/atl-Anatom_space-MNI_dseg.nii"
    a424_atlas = "data/A424+2mm.nii.gz"
    a424_atlas = image.load_img(a424_atlas)
    cerebellum = image.load_img(path_cerebellum_atlas)
    cerebellum = image.binarize_img(cerebellum, 0, copy_header=True)
    cerebellum = image.smooth_img(cerebellum, fwhm=1)  # smooth it slightly
    cerebellum = image.binarize_img(cerebellum, 0, copy_header=True)

    plot_roi(a424_atlas, title="A424", draw_cross=False)
    plt.savefig("A424_roi.png")
    plt.close()

    plot_roi(cerebellum, title="Cerebellum ROI", draw_cross=False)
    plt.savefig("cerebellum_roi.png")
    plt.close()
    cerebellum.to_filename(path_cerebellum)
    return path_cerebellum


def cerebellum_coverage(processed_img, cerebellum_mask):
    # make sure the inputs are 3d
    processed_img = image.load_img(processed_img)
    cerebellum_mask = image.load_img(cerebellum_mask)

    # resample template to processed image
    if (cerebellum_mask.affine != processed_img.affine).any():
        cerebellum_mask = image.resample_to_img(
            cerebellum_mask, processed_img, interpolation="nearest"
        )

    # check space, resample target to source space
    processed_img = processed_img.get_fdata().astype(bool)
    cerebellum_mask = cerebellum_mask.get_fdata().astype(bool)
    intersection = np.sum(np.logical_and(processed_img, cerebellum_mask))
    total_elements = np.sum(cerebellum_mask)
    return intersection / total_elements


if __name__ == "__main__":

    path_qc = Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/giga_auto_qc-0.3.4_scrub.5")
    path_qc_agg = path_qc / "dataset-preventad81internal_task-rest_desc-cerebellum_report.tsv"
    qc_rest = pd.DataFrame()
    for p in path_qc.glob("sub-*/*rest*.tsv"):
        df = pd.read_csv(p, sep="\t")
        qc_rest = pd.concat([qc_rest, df], ignore_index=True)
    qc_rest.set_index('identifier', inplace=True)

    cerebellum_nii = create_cerebellum_mask()
    # get the list of epi scan and brain mask
    a424_atlas_path = "data/A424+2mm.nii.gz"
    a424_atlas = image.load_img(a424_atlas_path)

    a424_atlas = image.binarize_img(a424_atlas, 0, copy_header=True)
    fmriprep_path = Path("prevent-ad/scratch/preventad-dr8.1internal/mri/wave1/fmriprep-20.2.8lts")
    epi_scans = fmriprep_path.rglob("*task-rest_*_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
    
    for epi in epi_scans:
        cerebe_coverage = cerebellum_coverage(epi, cerebellum_nii)
        a424_coverage = cerebellum_coverage(epi, a424_atlas)
        identifier = epi.name.split("_space")[0]
        qc_rest.loc[identifier, ["cerebellum_coverage", "a424_coverage"]] = [cerebe_coverage, a424_coverage]
        # if cerebe_coverage < 0.8:
        #     img = str(epi).replace("_desc-brain_mask", "_boldref")
        #     a424_atlas = image.resample_to_img(
        #         a424_atlas_path, img, interpolation="nearest"
        #     )
        #     plt.figure()
        #     plot_roi(a424_atlas, bg_img=img, title=f"{identifier}\nCoverage: {cerebe_coverage:.2f}", draw_cross=False)
        #     plt.savefig(f"{identifier}_cerebellum_coverage.png")
        #     plt.close()
    metric = qc_rest.drop(columns=["pass_func_qc", "pass_anat_qc", "pass_all_qc"], errors='ignore')
    metric.to_csv(path_qc_agg, sep="\t")
