/**
 * Helios Token — Deployment Script
 * =================================
 * Deploys HeliosToken.sol and writes the contract address to .env.
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js --network sepolia
 */

const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log(`\n☀ Helios Token — Deploying with: ${deployer.address}`);
  console.log(`  Balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} ETH\n`);

  // Deploy
  const HeliosToken = await ethers.getContractFactory("HeliosToken");
  const token = await HeliosToken.deploy(deployer.address);
  await token.waitForDeployment();

  const contractAddress = await token.getAddress();
  console.log(`  ✓ HeliosToken deployed to: ${contractAddress}`);
  console.log(`  ✓ Name: ${await token.name()}`);
  console.log(`  ✓ Symbol: ${await token.symbol()}`);
  console.log(`  ✓ Decimals: ${await token.decimals()}`);
  console.log(`  ✓ Cap: ${ethers.formatUnits(await token.CAP(), 8)} HLS`);
  console.log(`  ✓ Admin: ${deployer.address}\n`);

  // Write deployment info
  const deployment = {
    contract: "HeliosToken",
    address: contractAddress,
    deployer: deployer.address,
    network: hre.network.name,
    chainId: (await ethers.provider.getNetwork()).chainId.toString(),
    deployedAt: new Date().toISOString(),
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const filename = `HeliosToken-${hre.network.name}-${Date.now()}.json`;
  fs.writeFileSync(
    path.join(deploymentsDir, filename),
    JSON.stringify(deployment, null, 2)
  );
  console.log(`  ✓ Deployment record saved: deployments/${filename}`);

  // Update .env hint
  console.log(`\n  Add to your .env:\n`);
  console.log(`    HELIOS_EVM_CONTRACT_ADDRESS=${contractAddress}`);
  console.log(`    HELIOS_EVM_CHAIN_ID=${deployment.chainId}\n`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
