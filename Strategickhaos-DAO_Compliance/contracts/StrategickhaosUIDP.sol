// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StrategickhaosUIDP is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;
    string public baseURI;

    constructor(string memory _baseURI) ERC721("Strategickhaos UIDP License", "UIDP") {
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
