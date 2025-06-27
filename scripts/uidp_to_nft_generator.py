#!/usr/bin/env python3
import os, hashlib, json
from datetime import datetime

UIDP_DIR = "./docs/contracts/uidp"
HASH_OUTPUT_DIR = os.path.join(UIDP_DIR, "hashes")
NFT_JSON_DIR = os.path.join(UIDP_DIR, "nft_payloads")

os.makedirs(HASH_OUTPUT_DIR, exist_ok=True)
os.makedirs(NFT_JSON_DIR, exist_ok=True)

def generate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def process_uidp_files():
    for fname in os.listdir(UIDP_DIR):
        if fname.endswith(".txt"):
            path = os.path.join(UIDP_DIR, fname)
            uidp_hash = generate_hash(path)

            metadata = {
                "uidp_license_file": fname,
                "sha256_hash": uidp_hash,
                "dao": "Strategickhaos DAO LLC",
                "issued_to": "ValorDrive Foundation",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "license_type": "UIDP NFT License",
                "dao_repo": "https://github.com/Me10101-01/Strategickhaos-DAO_Compliance"
            }

            with open(os.path.join(NFT_JSON_DIR, fname.replace(".txt", ".json")), "w") as f:
                json.dump(metadata, f, indent=2)

            with open(os.path.join(HASH_OUTPUT_DIR, fname + ".hash"), "w") as f:
                f.write(uidp_hash + "\n")

            print(f"✅ Processed: {fname}")

if __name__ == "__main__":
    process_uidp_files()
