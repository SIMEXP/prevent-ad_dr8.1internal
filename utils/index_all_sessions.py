from pathlib import Path
import pandas as pd

FMRIPREP_PATH = Path("scratch/preventad_fmriprep-20.2.8lts_1754712947/wave1/fmriprep-20.2.8lts")

if __name__ == "__main__":
    PREVENT_AD_PATH = Path("/lustre09/project/6003287/hwang1/prevent-ad/mri")
    
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

        df_wave = df_wave.sort_values(by=["sub", "ses", "task", "run"])
        df_wave = df_wave[["sub", "ses"]]
        df_wave = df_wave.drop_duplicates()
        df_wave = df_wave.reset_index(drop=True)

        for i, row in df_wave.iterrows():
            if (FMRIPREP_PATH / f"sub-{row['sub']}" / f"ses-{row['ses']}").is_dir():
                df_wave.loc[i, "fmriprep"] = "yes"
            else:
                df_wave.loc[i, "fmriprep"] = "no"
        df_wave.to_csv(f"data/{wave}.tsv", sep="\t", index=False)
