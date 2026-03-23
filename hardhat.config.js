require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    // Local development
    hardhat: {},

    // Ethereum Sepolia testnet
    sepolia: {
      url: process.env.HELIOS_EVM_RPC_URL || "https://rpc.sepolia.org",
      chainId: 11155111,
      accounts: process.env.HELIOS_EVM_PRIVATE_KEY
        ? [process.env.HELIOS_EVM_PRIVATE_KEY]
        : [],
    },

    // Polygon Amoy testnet
    amoy: {
      url: process.env.HELIOS_EVM_RPC_URL || "https://rpc-amoy.polygon.technology",
      chainId: 80002,
      accounts: process.env.HELIOS_EVM_PRIVATE_KEY
        ? [process.env.HELIOS_EVM_PRIVATE_KEY]
        : [],
    },

    // Base Sepolia testnet
    baseSepolia: {
      url: process.env.HELIOS_EVM_RPC_URL || "https://sepolia.base.org",
      chainId: 84532,
      accounts: process.env.HELIOS_EVM_PRIVATE_KEY
        ? [process.env.HELIOS_EVM_PRIVATE_KEY]
        : [],
    },

    // Mainnet (use with caution)
    mainnet: {
      url: process.env.HELIOS_EVM_RPC_URL || "",
      chainId: Number(process.env.HELIOS_EVM_CHAIN_ID || "1"),
      accounts: process.env.HELIOS_EVM_PRIVATE_KEY
        ? [process.env.HELIOS_EVM_PRIVATE_KEY]
        : [],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || "",
  },
  paths: {
    sources: "./contracts",
    tests: "./test/contracts",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};
