const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("🛠 Deployer address:", deployer.address);

  const StrategickhaosUIDP = await hre.ethers.getContractFactory("StrategickhaosUIDP");
  const contract = await StrategickhaosUIDP.deploy("ipfs://base_uri/", deployer.address);
  await contract.waitForDeployment();  // ✅ replaces .deployed()

  const contractAddress = await contract.getAddress(); // safer than contract.address directly
  console.log("✅ StrategickhaosUIDP deployed at:", contractAddress);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
