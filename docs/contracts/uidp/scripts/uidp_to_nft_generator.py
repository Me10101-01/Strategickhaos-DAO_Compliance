#!/usr/bin/env python3

"""
Strategickhaos UIDP-to-NFT Generator
Hashes UIDP contracts into NFT-mintable JSON payloads.
"""

import os
import hashlib
import json
from datetime import datetime

# Paths
UIDP_DIR = "./docs/contracts/uidp"
HASH_OUTPUT_DIR = "./docs/contracts/uidp/hashes"
NFT_JSON_DIR = "./docs/contracts/uidp/nft_payloads"

# Ensure directories exist
os.makedirs(HASH_OUTPUT_DIR, exist_ok=True)
os.makedirs(NFT_JSON_DIR, exist_ok=True)

def generate_hash(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
        return hashlib.sha256(content).hexdigest()

def create_nft_metadata(file_name, uidp_hash):
    metadata = {
        "uidp_license_file": file_name,
        "sha256_hash": uidp_hash,
        "dao": "Strategickhaos DAO LLC",
        "issued_to": "ValorDrive Foundation",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "license_type": "UIDP NFT License",
        "dao_repo": "https://github.com/Me10101-01/Strategickhaos-DAO_Compliance"
    }
    return metadata

def process_uidp_files():
    for fname in os.listdir(UIDP_DIR):
        if fname.endswith(".md") and not fname.startswith("README"):
            file_path = os.path.join(UIDP_DIR, fname)
            uidp_hash = generate_hash(file_path)

            # Write hash
            hash_file = os.path.join(HASH_OUTPUT_DIR, f"{fname}.sha256")
            with open(hash_file, "w") as hf:
                hf.write(uidp_hash)

            # Write NFT JSON metadata
            metadata = create_nft_metadata(fname, uidp_hash)
            json_path = os.path.join(NFT_JSON_DIR, f"{fname}.json")
            with open(json_path, "w") as jf:
                json.dump(metadata, jf, indent=4)

            print(f"✅ Processed: {fname}")

if __name__ == "__main__":
    process_uidp_files()
