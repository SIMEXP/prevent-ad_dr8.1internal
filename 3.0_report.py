from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nilearn.image import mean_img, math_img, concat_imgs
from nilearn.maskers import NiftiMasker
import numpy as np
from nilearn.plotting import plot_stat_map
from matplotlib.lines import Line2D

path_qc = Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/giga_auto_qc-0.3.4_scrub.5")
path_qc_agg = path_qc / "dataset-preventad81internal_task-rest_desc-cerebellum_report.tsv"
path_processed = Path("/scratch/hwang1/preventAD_processed-data")
path_pheno = Path("/scratch/hwang1/preventad-dr8.1internal/phenotype/pheno")
path_fmriprep = Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/fmriprep-20.2.8lts")

qc_rest = pd.read_csv(path_qc_agg, sep="\t")

# plot distributions of continuous metrics
plt.figure(figsize=(12, 8))
metrics = ['mean_fd_raw', 'mean_fd_scrubbed', 'proportion_kept', 'functional_dice', 'anatomical_dice', 'cerebellum_coverage']
for i, metric in enumerate(metrics, 1):
    plt.subplot(2, 3, i)
    sns.histplot(qc_rest[metric], kde=True)
    plt.title(f'Distribution of {metric}')
    plt.xlabel(metric)
    plt.ylabel('Number of scans')
plt.tight_layout()
plt.savefig(path_qc / "qc_metrics_distributions.png")
plt.close()

failed_cerebellum = qc_rest[qc_rest.cerebellum_coverage<0.7]
all_img = []
for _, row in failed_cerebellum.iterrows():
    prepro_bold = (
        path_fmriprep / f"sub-{row.participant_id}" / f"ses-{row.ses}" / 
        "func" / f"{row.identifier}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    )
    path_tsnr_scaled_img = Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/tsnr") / f"sub-{row.participant_id}" / f"ses-{row.ses}" / f"{row.identifier}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    if path_tsnr_scaled_img.is_file():
        all_img.append(str(path_tsnr_scaled_img))
        continue
    # calculate tsnr
    nii_mask = str(prepro_bold).replace("preproc_bold", "brain_mask")
    # smooth to improve tsnr
    masker = NiftiMasker(nii_mask, standardize=False, smoothing_fwhm=8)  # slice thickness = 4mm
    func_img = masker.fit_transform(prepro_bold)
    func_img = masker.inverse_transform(func_img)
    nii_mean = math_img("np.mean(img, axis=-1)", img=func_img)
    nii_std = math_img("np.std(img, axis=-1)", img=func_img)
    tsnr_img = math_img("mean / std", mean=nii_mean, std=nii_std)

    masker = NiftiMasker(nii_mask, standardize=False)
    tsnr_data = masker.fit_transform(tsnr_img)
    tsnr_data = (tsnr_data - np.min(tsnr_data)) / (np.max(tsnr_data) - np.min(tsnr_data)) # scale to 0-1 first
    tsnr_data *= 100
    tsnr_scaled_img = masker.inverse_transform(tsnr_data)
    path_tsnr_scaled_img.parent.mkdir(parents=True, exist_ok=True)
    tsnr_scaled_img.to_filename(path_tsnr_scaled_img)
    
    all_img.append(str(path_tsnr_scaled_img))
all_img = concat_imgs(all_img)
print(all_img.shape)
mean_tsnr_img = mean_img(all_img)
plt.figure()
plot_stat_map(mean_tsnr_img, display_mode="x", vmax=100, threshold=1, transparency=0.7,
              cut_coords=7, title="Average tSNR of failed cerebellum coverage (<70%) scans", 
              symmetric_cbar=True)
plt.savefig(Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/tsnr") / 'average_tsnr_lack_cerebellum.png')


failed_cerebellum = qc_rest[qc_rest.cerebellum_coverage>=0.7]
all_img = []
for _, row in failed_cerebellum.iterrows():
    prepro_bold = (
        path_fmriprep / f"sub-{row.participant_id}" / f"ses-{row.ses}" / 
        "func" / f"{row.identifier}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    )
    path_tsnr_scaled_img = Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/tsnr") / f"sub-{row.participant_id}" / f"ses-{row.ses}" / f"{row.identifier}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    if path_tsnr_scaled_img.is_file():
        all_img.append(str(path_tsnr_scaled_img))
        continue
    # calculate tsnr
    nii_mask = str(prepro_bold).replace("preproc_bold", "brain_mask")
    # smooth to improve tsnr
    masker = NiftiMasker(nii_mask, standardize=False, smoothing_fwhm=8)  # slice thickness = 4mm
    func_img = masker.fit_transform(prepro_bold)
    func_img = masker.inverse_transform(func_img)
    nii_mean = math_img("np.mean(img, axis=-1)", img=func_img)
    nii_std = math_img("np.std(img, axis=-1)", img=func_img)
    tsnr_img = math_img("mean / std", mean=nii_mean, std=nii_std)

    masker = NiftiMasker(nii_mask, standardize=False)
    tsnr_data = masker.fit_transform(tsnr_img)
    tsnr_data = (tsnr_data - np.min(tsnr_data)) / (np.max(tsnr_data) - np.min(tsnr_data)) # scale to 0-1 first
    tsnr_data *= 100
    tsnr_scaled_img = masker.inverse_transform(tsnr_data)
    path_tsnr_scaled_img.parent.mkdir(parents=True, exist_ok=True)
    tsnr_scaled_img.to_filename(path_tsnr_scaled_img)
    
    all_img.append(str(path_tsnr_scaled_img))
all_img = concat_imgs(all_img)
print(all_img.shape)
mean_tsnr_img = mean_img(all_img)
plt.figure()
plot_stat_map(mean_tsnr_img, display_mode="x", vmax=100, threshold=1, transparency=0.7,
              cut_coords=7, title="Average tSNR of good cerebellum coverage scans", 
              symmetric_cbar=True)
plt.savefig(Path("/scratch/hwang1/preventad-dr8.1internal/mri/wave1/tsnr") / 'average_tsnr_with_cerebellum.png')

failed_mean_fd= qc_rest[qc_rest.mean_fd_raw > 0.85].participant_id.unique()
print(f"Number of participants with mean fd > 0.55: {len(failed_mean_fd)}")
failed_motion = qc_rest[qc_rest.proportion_kept < 0.2].participant_id.unique()
print(f"Number of participants with more than 80% volumes with fd > 0.55: {len(failed_motion)}")


# Combine each scan with the demographics information

data_dict = pd.read_csv(path_pheno / "PREVENT-AD_internal_n387__Data_Dictionary.csv", sep=",", index_col=0)
table_w_age = data_dict[data_dict.variable == 'Candidate_Age']
demographic = pd.read_csv(path_pheno / "PREVENT-AD_internal_n387__Demographics.csv", sep=",")
demographic['participant_id'] = demographic.PSCID
# attach sex and age for each scan
qc_rest['ses'] = qc_rest.ses.str[:-1]  # remove the last character
qc_rest = qc_rest.merge(demographic[['participant_id', 'Sex']])

# compile age of each visits
# TODO use this format to check other variable per visit
df_age = pd.DataFrame()
for table_name in table_w_age.data_table.to_list():
    df = pd.read_csv(path_pheno / f"PREVENT-AD_internal_n387__{table_name}.csv", sep=",")
    age_visit = df[['PSCID', 'Visit_label', 'Candidate_Age']]
    # rename PSCID to participant_id
    age_visit = age_visit.rename(columns={'PSCID': 'participant_id'})
    df_age = pd.concat([df_age, age_visit], axis=0)

df_age = df_age.sort_values(['participant_id', 'Candidate_Age'])
df_age = df_age.drop_duplicates(subset=['participant_id', 'Visit_label'], keep='first')
df_age = df_age.reset_index(drop=True)

session_id_inorder = df_age.Visit_label.unique()
check_missing_session = df_age.pivot_table('Candidate_Age', 'participant_id', 'Visit_label')
check_missing_session.columns = session_id_inorder
plt.figure(figsize=(10, 13))
sns.heatmap(check_missing_session.isna(), cbar=False, yticklabels=False, cmap=['darkblue', 'lightgrey'])
custom_lines = [Line2D([0], [0], color='darkblue', lw=4),
                Line2D([0], [0], color='lightgrey', lw=4)]
plt.title('Missing Age Information Across Visits')
plt.xlabel('Visit Label')
plt.ylabel('Participants')
plt.legend(custom_lines, ['Present', 'Missing'], title='Age Info')
plt.savefig(path_qc / "missing_age_info_heatmap.png")
plt.close()

# add linked rsfmri sessions
pheno = pd.merge(
    left=qc_rest, 
    right=df_age,
    how='left',
    left_on=['participant_id', 'ses'],
    right_on=['participant_id', 'Visit_label'],
)
pheno = pheno.drop(columns=['Visit_label'])
pheno = pheno.sort_values(['participant_id', 'ses'])
pheno.to_csv(path_processed / "dataset-preventad81internal_desc-sexage_pheno.tsv", 
             sep='\t', index=False
            )

session_id_inorder = pheno.ses.unique()
check_missing_session = pheno.pivot_table('Candidate_Age', 'participant_id', 'ses')
check_missing_session.columns = session_id_inorder
check_missing_session = check_missing_session.sort_values('participant_id')
plt.figure(figsize=(10, 13))
sns.heatmap(check_missing_session.isna(), cbar=False, yticklabels=False, cmap=['darkblue', 'lightgrey'])
custom_lines = [Line2D([0], [0], color='darkblue', lw=4),
                Line2D([0], [0], color='lightgrey', lw=4)]
plt.title('Missing Visits')
plt.xlabel('Visit Label')
plt.ylabel('Participants')
plt.legend(custom_lines, ['Present', 'Missing'], title='fMRI session')
plt.savefig(path_qc / "missing_fmri_heatmap.png")
plt.close()
