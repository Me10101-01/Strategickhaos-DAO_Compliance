const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const contractAddress = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"; // ✅ Use latest deployed
  const uidp = await hre.ethers.getContractAt("StrategickhaosUIDP", contractAddress);

  const ipfsCID = "QmYourIPFSHashHere";  // replace with your actual IPFS CID or use placeholder
  const tx = await uidp.mintLicense(deployer.address, ipfsCID);
  await tx.wait();

  console.log("🧾 UIDP NFT License minted to:", deployer.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
