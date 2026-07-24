"""O*NET dataset loader and query functionality."""

from __future__ import annotations
import logging
import zipfile
import glob as _glob
import pandas as pd
from pathlib import Path
from collections import Counter
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class OnetDatasetLoader:
    def __init__(self, zip_path: str, extract_path: str):
        self.zip_path     = zip_path
        self.extract_path = extract_path
        self._df: Optional[pd.DataFrame] = None
        self.skill_market_demand: Dict[str, float] = {}

    def load(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        self._extract_zip()
        self._df = self._build_dataset()
        logger.info(f"Dataset loaded: {len(self._df)} job profiles")
        return self._df

    def _extract_zip(self):
        if _glob.glob(f"{self.extract_path}/db_*"):
            logger.info("Dataset already extracted")
            return
        if self.zip_path and Path(self.zip_path).exists():
            logger.info("Extracting dataset...")
            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(self.extract_path)
        else:
            logger.info("No ZIP file found — expecting pre-extracted db_* folder")

    @staticmethod
    def _agg_skills(series) -> List[str]:
        return list({
            str(v).lower().strip()
            for v in series
            if pd.notnull(v) and str(v).strip()
        })

    def _build_dataset(self) -> pd.DataFrame:
        folders = _glob.glob(f"{self.extract_path}/db_*")
        if not folders:
            raise FileNotFoundError(
                f"No db_* folder found in '{self.extract_path}'. "
                "Provide the dataset ZIP or pre-extracted folder."
            )
        base = sorted(folders)[-1]
        logger.info(f"Using folder: {base}")

        occ    = pd.read_csv(f"{base}/Occupation Data.txt",   sep="\t")
        skills = pd.read_csv(f"{base}/Skills.txt",            sep="\t")
        tech   = pd.read_csv(f"{base}/Technology Skills.txt", sep="\t")

        soft = (
            skills[(skills["Scale ID"] == "IM") & (skills["Data Value"] > 3.0)]
            [["O*NET-SOC Code", "Element Name", "Data Value"]]
            .rename(columns={"Element Name": "soft_skill",
                             "Data Value":   "soft_skill_importance"})
        )
        hard = (
            tech[["O*NET-SOC Code", "Example", "Commodity Title"]]
            .rename(columns={"Example":        "tech_skill",
                             "Commodity Title": "skill_category"})
        )

        df    = occ.merge(soft, on="O*NET-SOC Code", how="left")
        df    = df.merge(hard, on="O*NET-SOC Code", how="left")
        final = df.groupby("Title").agg(
            job_description=("Description", "first"),
            tech_skills=    ("tech_skill",  self._agg_skills),
            soft_skills=    ("soft_skill",  self._agg_skills),
        ).reset_index()
        final.columns  = ["job_title", "job_description", "tech_skills", "soft_skills"]
        final["all_skills"] = final["tech_skills"] + final["soft_skills"]

        total     = max(len(final), 1)
        tech_flat = final["tech_skills"].explode().dropna()
        soft_flat = final["soft_skills"].explode().dropna()
        tech_freq = Counter(tech_flat)
        soft_freq = Counter(soft_flat)
        self.skill_market_demand = {
            s: (tech_freq.get(s, 0) + 0.5 * soft_freq.get(s, 0)) / total
            for s in set(tech_freq) | set(soft_freq)
        }
        return final

    def get_job_profile(self, title: str):
        df = self.load()
        t  = title.lower().strip()
        exact = df[df["job_title"].str.lower() == t]
        if not exact.empty:
            return exact.iloc[0]
        # regex=False prevents injection from user-controlled strings
        partial = df[df["job_title"].str.lower().str.contains(t, na=False, regex=False)]
        if not partial.empty:
            # Return closest by title-length distance, not first alphabetically
            partial = partial.copy()
            partial["_dist"] = partial["job_title"].str.len().sub(len(t)).abs()
            row = partial.sort_values("_dist").iloc[0]
            logger.info(f"Closest match: '{row['job_title']}'")
            return row
        return None

    def get_all_tech_skills(self) -> List[str]:
        df = self.load()
        return list({s for s in df["tech_skills"].explode().dropna() if s})
