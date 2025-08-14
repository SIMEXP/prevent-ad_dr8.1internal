
#!/usr/bin/env python
"""
Lazy check if the data has been preprocessed.
"""

from pathlib import Path
import pandas as pd

FMRIPREP_PATH = Path("prevent-ad/scratch/preventad-dr8.1internal/mri")
PREVENT_AD_PATH = Path("/lustre09/project/6003287/hwang1/prevent-ad/mri")

if __name__ == "__main__":
    logs = []
    for wave in ["wave1", "wave2"]:
        wave_path = PREVENT_AD_PATH / wave
        df_wave = pd.DataFrame()
        for filepath in wave_path.glob("sub-*/ses-*/func/*.nii.gz"):
            file_name = filepath.name
            entities = file_name.split(".nii.gz")[0].split("_")
            entry = {}
            for entity in entities:
                if "-" in entity:
                    key, value = entity.split("-")
                    entry[key] = [value]
                else:
                    entry["suffix"] = [entity]
            entry["run"] = entry.get("run", ["n/a"])
            df = pd.DataFrame.from_dict(entry)
            df_wave = pd.concat([df_wave, df], axis=0)

        df_wave = df_wave.sort_values(by=["sub", "ses"])
        df_wave = df_wave[["sub", "ses"]]
        df_wave['dataset'] = wave
        df_wave = df_wave.drop_duplicates()
        df_wave = df_wave.reset_index(drop=True)

        for i, row in df_wave.iterrows():
            if (FMRIPREP_PATH / wave / "fmriprep-20.2.8lts" / f"sub-{row['sub']}" / f"ses-{row['ses']}").is_dir():
                df_wave.loc[i, "fmriprep"] = "yes"
            else:
                df_wave.loc[i, "fmriprep"] = "no"
        logs.append(df_wave)

    logs = pd.concat(logs).sort_values(by=["sub", "ses", "dataset"])
    logs.to_csv(f"data/preprocess_log.tsv", sep="\t", index=False)
