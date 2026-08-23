import pandas as pd
import subprocess
from pathlib import Path
import shutil
import gzip

# Input
id_file = "IDgenome_list.tsv"
base_dir = Path("/Thesis/Exp")
flat_fasta_dir = base_dir / "Exp_seq"
flat_fasta_dir.mkdir(parents=True, exist_ok=True)

# Load genome IDs
genome_ids = pd.read_csv(id_file, header=None)[0].astype(str).tolist()

for gid in genome_ids:
    print(f"Downloading {gid}")

    subprocess.run([
        "ncbi-genome-download",
        "bacteria",
        "--section", "refseq",
        "--assembly-accessions", gid,
        "--formats", "fasta",
        "--output-folder", str(base_dir)
    ], check=True)

# Flatten FASTA files
for fna in base_dir.rglob("*.fna*"):
    shutil.copy(fna, flat_fasta_dir / fna.name)

# Unzip and convert to fa
input_dir = Path("/Users/tranthihongnhung/Desktop/MasterThesis/Exp/Exp_seq")

for gz_file in input_dir.glob("*.fna.gz"):
    # Define output file path (.fa)
    fa_file = gz_file.with_suffix("").with_suffix(".fa")

    # Unzip and write to .fa
    with gzip.open(gz_file, "rb") as f_in, open(fa_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    # remove compressed file after done
    gz_file.unlink()
