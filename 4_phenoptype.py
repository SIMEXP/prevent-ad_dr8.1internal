"""Compile phenotypic targets for subjects at baseline visit or use the first available visit if no baseline visit."""

import pandas as pd
from pathlib import Path

base_columns = ["PSCID"]
base_path = "prevent-ad/scratch/dataset-preventad_version-8.1internal_pipeline-gigapreprocess2/phenotype/pheno"
phenotype_dict = {
    "Demographics": {
        "file": "PREVENT-AD_internal_n387__Demographics.csv",
        "columns": ["Sex"]
    },
    "AD8": {
        "file": "PREVENT-AD_internal_n387__AD8.csv",
        "columns": ["AD8_total_score", "Visit_label", "Candidate_Age"]
    },
    "APS": {
        "file": "PREVENT-AD_internal_n387__APS.csv",
        "columns": ["APS_score", "Visit_label"]
    },
    "CSFproteins": {
        "file": "PREVENT-AD_internal_n387__CSF_proteins.csv",
        "columns": ["tau","ptau","Amyloid_beta_1_42", "Visit_label"]
    },
    "PET": {
        "file": "PREVENT-AD_internal_n387__PET_NAV_SUVR_ref-cerebellumCortex.csv",
        "columns": ["amyloid_index_SUVR", "centiloid_s0_WhlCbl"],
    },  # add new phenotypes between here and the MCI phenotype
    "MCI": {
        "file": "PREVENT-AD_internal_n387__MCI.csv",
        "columns": ["initial_MCI_visit_Candidate_Age", "initial_MCI_visit_label"]
    }
}

def load_phenotype_data() -> pd.DataFrame:
    data_frames = []
    for phenotype, info in phenotype_dict.items():
        file_path = Path(base_path) / info["file"]
        df = pd.read_csv(file_path)
        selected_columns = base_columns.copy() + info["columns"]
        df = df[selected_columns]
        df = df.rename(columns={"PSCID": "participant_id"})
        if phenotype == 'MCI':
            df = df.drop_duplicates()
            df['clinical_trial'] = [1 if 'NAP' in vl else 0 for vl in df["initial_MCI_visit_label"]]
            df['initial_MCI_visit_label'] = df["initial_MCI_visit_label"].str.replace('NAP', '')
            df['initial_MCI_visit_label'] = df['initial_MCI_visit_label'].str.replace('PRE', '')
            df = df.rename(columns={"initial_MCI_visit_Candidate_Age": "MCI_onset_age"})
        if 'Visit_label' in df.columns:
            df.set_index(['participant_id', 'Visit_label'], inplace=True)
        else:
            df.set_index('participant_id', inplace=True)
        data_frames.append(df)
    return data_frames

if __name__ == "__main__":
    combined_df = load_phenotype_data()
    pheno_info = pd.concat([combined_df[0], combined_df[-1]], axis=1)
    for df in combined_df[1:-1]:
        if 'Visit_label' not in df.columns:
            pheno_info = pd.merge(pheno_info, df, left_index=True, right_index=True, how='left')
            continue
        bl_mask = df.index.get_level_values('Visit_label') == 'BL00'
        bl = df[bl_mask].droplevel('Visit_label')
        # if the subject has no baseline session, use the first available session
        no_bl_ids = df.index.levels[0].difference(bl.index)
        first_sessions = df.loc[no_bl_ids, :].reset_index().sort_values(['participant_id', 'Visit_label'])
        first_sessions = first_sessions.drop_duplicates(subset=['participant_id'], keep='first').set_index('participant_id')
        first_sessions = first_sessions.drop(columns=['Visit_label'])
        bl = pd.concat([bl, first_sessions], axis=0)
        pheno_info = pd.merge(pheno_info, bl, left_index=True, right_index=True, how='left')
    pheno_info = pheno_info.fillna("n/a")
    pheno_info.to_csv('prevent-ad/scratch/dataset-preventad_version-8.1internal_pipeline-gigapreprocess2/dataset-preventad81internal_desc-subjlvltargets_pheno.tsv', sep='\t')
