"""
Download and extract the O*NET 30.2 database.

Run this once after cloning:
    python scripts/setup_data.py

The dataset is ~50MB compressed. Without it the backend runs in FALLBACK MODE
with hardcoded skill profiles (see FallbackIntelligenceCore).

A 50-occupation sample is bundled in backend/data/sample/ so the app works
immediately after a fresh clone. The full dataset unlocks all 1,000+ occupations.
"""

from __future__ import annotations
import hashlib
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

ONET_URL     = "https://www.onetcenter.org/dl_files/database/db_30_2_text.zip"
ONET_SHA256  = ""          # leave empty to skip hash check (O*NET doesn't publish hashes)
DEST_DIR     = Path(__file__).parent.parent / "backend" / "data"
ZIP_PATH     = DEST_DIR / "onet_30_2.zip"
EXTRACT_PATH = DEST_DIR / "db_30_2_text"


def _progress(count: int, block_size: int, total: int) -> None:
    pct = min(int(count * block_size * 100 / total), 100) if total > 0 else 0
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    sys.stdout.write(f"\r  [{bar}] {pct:3d}%")
    sys.stdout.flush()


def download(url: str, dest: Path) -> None:
    print(f"\nDownloading O*NET database from:\n  {url}\n")
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest, reporthook=_progress)
    print(f"\n  Saved to {dest}  ({dest.stat().st_size / 1_000_000:.1f} MB)")


def verify_hash(path: Path, expected: str) -> None:
    if not expected:
        return   # no hash to check
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != expected:
        raise ValueError(f"SHA-256 mismatch.\n  Expected: {expected}\n  Got:      {sha}")
    print("  SHA-256 verified ✓")


def extract(zip_path: Path, dest: Path) -> None:
    print(f"\nExtracting to {dest}...")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        members = zf.namelist()
        for i, member in enumerate(members, 1):
            zf.extract(member, dest)
            sys.stdout.write(f"\r  {i}/{len(members)} files extracted")
            sys.stdout.flush()
    print(f"\n  Done. {len(members)} files extracted.")


def main() -> None:
    if EXTRACT_PATH.exists() and any(EXTRACT_PATH.iterdir()):
        print(f"O*NET data already present at {EXTRACT_PATH}")
        print("Delete the directory and re-run to re-download.")
        return

    if not ZIP_PATH.exists():
        download(ONET_URL, ZIP_PATH)
    else:
        print(f"Using cached zip at {ZIP_PATH}")

    verify_hash(ZIP_PATH, ONET_SHA256)
    extract(ZIP_PATH, EXTRACT_PATH)

    print(f"\n✓ O*NET data ready at {EXTRACT_PATH}")
    print("  Set ONET_EXTRACT_PATH in backend/.env to point here, then restart the server.")


if __name__ == "__main__":
    main()
