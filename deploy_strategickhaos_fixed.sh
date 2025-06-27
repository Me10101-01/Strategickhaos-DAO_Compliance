#!/bin/bash

echo "🧠 Setting up StrategickhaosUIDP..."

mkdir -p contracts scripts

# ✅ Contract with fixed constructor
cat << 'SOL' > contracts/StrategickhaosUIDP.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StrategickhaosUIDP is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;
    string public baseURI;

    constructor(string memory _baseURI, address initialOwner)
        ERC721("Strategickhaos UIDP License", "UIDP")
        Ownable(initialOwner)
    {
        baseURI = _baseURI;
    }

    function mintLicense(address to, string memory ipfsCID) external onlyOwner {
        uint256 tokenId = nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, string(abi.encodePacked(baseURI, ipfsCID)));
    }

    function updateBaseURI(string memory newBaseURI) external onlyOwner {
        baseURI = newBaseURI;
    }
}
SOL

# ✅ Deploy script
cat << 'JS' > scripts/deploy.js
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("🛠 Deployer address:", deployer.address);

  const StrategickhaosUIDP = await hre.ethers.getContractFactory("StrategickhaosUIDP");
  const contract = await StrategickhaosUIDP.deploy("ipfs://base_uri/", deployer.address);
  await contract.deployed();

  console.log("✅ StrategickhaosUIDP deployed at:", contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
JS

# Compile
echo "📦 Compiling contract..."
npx hardhat compile

# Deploy
echo "🚀 Deploying..."
npx hardhat run scripts/deploy.js --network localhost
