#!/bin/bash

echo "🧠 Compiling StrategickhaosUIDP..."
npx hardhat compile

echo "🚀 Deploying StrategickhaosUIDP..."
cat << 'JS' > scripts/deploy.js
const hre = require("hardhat");

async function main() {
  const StrategickhaosUIDP = await hre.ethers.getContractFactory("StrategickhaosUIDP");
  const contract = await StrategickhaosUIDP.deploy("ipfs://base_uri/");
  await contract.deployed();
  console.log("✅ Deployed StrategickhaosUIDP at:", contract.address);
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
JS

DEPLOY_OUTPUT=$(npx hardhat run scripts/deploy.js --network localhost)
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep 'Deployed StrategickhaosUIDP at:' | awk '{print $NF}')

echo "📦 Contract deployed at: $CONTRACT_ADDRESS"

echo "🔐 Creating mint script..."
cat << MINTJS > scripts/mint_uidp.js
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const uidp = await hre.ethers.getContractAt("StrategickhaosUIDP", "$CONTRACT_ADDRESS");

  const recipient = deployer.address;
  const ipfsCID = "QmYourRealIPFSCIDHere"; // Replace if needed

  const tx = await uidp.mintLicense(recipient, ipfsCID);
  await tx.wait();
  console.log(\`✅ UIDP NFT minted to: \${recipient}\`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
MINTJS

echo "🧾 Minting UIDP NFT..."
npx hardhat run scripts/mint_uidp.js --network localhost
