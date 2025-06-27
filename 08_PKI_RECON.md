🛡️ Trust:
- GPG key pair generated for DAO validator node
- Public key stored in /keys/dao_validator.pub
- Private key encrypted and stored in cold vault

🔎 Verify:
- DAO scripts (deploy_onboard.sh, vault_engine.py) check signature of issuing terminal
- Reject execution if signature does not match DAO-verified public key
- Set up pre-commit hook: git commit requires GPG signature from allowed key

🧠 Signal:
- Push /keys/authorized_signatures.json to IPFS + GitHub
- Update README_LAW_PROOF.md with PKI enforcement clause
- Run: `gpg --verify deploy_onboard.sh.sig deploy_onboard.sh`

🎯 Target Timeframe: Day 14–Day 17
