# backend/ml/dataset_loader.py

import zipfile
import glob
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from collections import Counter


class OnetDatasetLoader:
    """
    Loads the O*NET database from a ZIP file.

    The O*NET ZIP contains three files we care about:
    - Occupation Data.txt   → job titles and descriptions
    - Skills.txt            → soft skills (importance-weighted)
    - Technology Skills.txt → hard/tech skills

    We join all three into one DataFrame where each row is a job title.
    """

    def __init__(self, zip_path: str, extract_path: str):
        self.zip_path = zip_path
        self.extract_path = extract_path
        self._df: Optional[pd.DataFrame] = None
        self.skill_market_demand: Dict[str, float] = {}

    def load(self) -> pd.DataFrame:
        """Load and return the dataset. Uses cache after first call."""
        if self._df is not None:
            return self._df
        self._extract_zip()
        self._df = self._build_dataset()
        print(f"✅ O*NET loaded: {len(self._df)} job profiles")
        return self._df

    def _extract_zip(self):
        # Check if data is already extracted
        db_folders = glob.glob(f"{self.extract_path}/db_*")
        if db_folders:
            print("📦 O*NET data already extracted")
            return
        
        # Try to extract from ZIP if available
        if self.zip_path and Path(self.zip_path).exists():
            print("📦 Extracting O*NET dataset...")
            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(self.extract_path)
        else:
            print("⚠️  No ZIP file available, expecting pre-extracted data")

    def _build_dataset(self) -> pd.DataFrame:
        # Find the extracted O*NET folder dynamically
        db_folders = glob.glob(f"{self.extract_path}/db_*")
        if not db_folders:
            raise FileNotFoundError(f"No O*NET database folder found in {self.extract_path}. Expected pattern: db_*")
        base = db_folders[0]
        print(f"📂 Using O*NET database folder: {base}")

        occ    = pd.read_csv(f"{base}/Occupation Data.txt",   sep="\t")
        skills = pd.read_csv(f"{base}/Skills.txt",            sep="\t")
        tech   = pd.read_csv(f"{base}/Technology Skills.txt", sep="\t")

        # Filter soft skills: only importance-rated ("IM" scale) above 3/5
        soft = (
            skills[(skills["Scale ID"] == "IM") & (skills["Data Value"] > 3.0)]
            [["O*NET-SOC Code", "Element Name", "Data Value"]]
            .rename(columns={"Element Name": "soft_skill", "Data Value": "soft_skill_importance"})
        )

        hard = (
            tech[["O*NET-SOC Code", "Example", "Commodity Title"]]
            .rename(columns={"Example": "tech_skill", "Commodity Title": "skill_category"})
        )

        df = occ.merge(soft, on="O*NET-SOC Code", how="left")
        df = df.merge(hard, on="O*NET-SOC Code", how="left")

        def agg_skills(x):
            return list(set([
                str(i).lower().strip()
                for i in x if pd.notnull(i) and str(i).strip()
            ]))

        final = df.groupby("Title").agg(
            job_description=("Description", "first"),
            tech_skills=("tech_skill", agg_skills),
            soft_skills=("soft_skill", agg_skills),
        ).reset_index()

        final.columns = ["job_title", "job_description", "tech_skills", "soft_skills"]
        final["all_skills"] = final["tech_skills"] + final["soft_skills"]

        # Build market demand: what fraction of jobs need each skill?
        all_skills_flat = final["tech_skills"].explode().dropna()
        skill_freq = Counter(all_skills_flat)
        total_jobs = len(final)
        self.skill_market_demand = {
            skill: count / total_jobs
            for skill, count in skill_freq.items()
        }

        return final

    def get_job_profile(self, title: str):
        """Find a job profile by title. Returns the row as a Series, or None."""
        df = self.load()
        title_lower = title.lower()

        exact = df[df["job_title"].str.lower() == title_lower]
        if not exact.empty:
            return exact.iloc[0]

        # Partial match fallback (e.g., "data scientist" matches "Data Scientists")
        partial = df[df["job_title"].str.lower().str.contains(title_lower, na=False)]
        if not partial.empty:
            print(f"⚠️  Using closest match: {partial.iloc[0]['job_title']}")
            return partial.iloc[0]

        return None

    def get_all_tech_skills(self) -> List[str]:
        """Get the complete list of tech skills across all jobs. Used to build the extractor."""
        df = self.load()
        return list(set(df["tech_skills"].explode().dropna().tolist()))