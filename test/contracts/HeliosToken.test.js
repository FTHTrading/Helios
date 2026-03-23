/**
 * HeliosToken Contract Tests
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("HeliosToken", function () {
  let token, owner, minter, user1, user2;
  const CAP = ethers.parseUnits("100000000", 8); // 100M with 8 decimals

  beforeEach(async function () {
    [owner, minter, user1, user2] = await ethers.getSigners();
    const HeliosToken = await ethers.getContractFactory("HeliosToken");
    token = await HeliosToken.deploy(owner.address);
    await token.waitForDeployment();
  });

  describe("Deployment", function () {
    it("should set the correct name and symbol", async function () {
      expect(await token.name()).to.equal("Helios Token");
      expect(await token.symbol()).to.equal("HLS");
    });

    it("should use 8 decimals", async function () {
      expect(await token.decimals()).to.equal(8);
    });

    it("should have a cap of 100M HLS", async function () {
      expect(await token.CAP()).to.equal(CAP);
    });

    it("should assign all roles to deployer", async function () {
      const MINTER = await token.MINTER_ROLE();
      const PAUSER = await token.PAUSER_ROLE();
      const ADMIN = await token.DEFAULT_ADMIN_ROLE();

      expect(await token.hasRole(ADMIN, owner.address)).to.be.true;
      expect(await token.hasRole(MINTER, owner.address)).to.be.true;
      expect(await token.hasRole(PAUSER, owner.address)).to.be.true;
    });

    it("should start with zero supply", async function () {
      expect(await token.totalSupply()).to.equal(0);
    });
  });

  describe("Minting", function () {
    it("should allow MINTER_ROLE to mint tokens", async function () {
      const amount = ethers.parseUnits("1000", 8);
      await token.mint(user1.address, amount);
      expect(await token.balanceOf(user1.address)).to.equal(amount);
    });

    it("should reject minting by non-minters", async function () {
      const amount = ethers.parseUnits("1000", 8);
      await expect(
        token.connect(user1).mint(user2.address, amount)
      ).to.be.reverted;
    });

    it("should reject minting beyond the cap", async function () {
      await expect(
        token.mint(user1.address, CAP + 1n)
      ).to.be.revertedWith("HeliosToken: cap exceeded");
    });

    it("should allow minting up to exactly the cap", async function () {
      await token.mint(user1.address, CAP);
      expect(await token.totalSupply()).to.equal(CAP);
    });

    it("should allow granting MINTER_ROLE to another address", async function () {
      const MINTER = await token.MINTER_ROLE();
      await token.grantRole(MINTER, minter.address);
      
      const amount = ethers.parseUnits("500", 8);
      await token.connect(minter).mint(user1.address, amount);
      expect(await token.balanceOf(user1.address)).to.equal(amount);
    });
  });

  describe("Pausing", function () {
    it("should allow PAUSER_ROLE to pause", async function () {
      await token.pause();
      expect(await token.paused()).to.be.true;
    });

    it("should block transfers when paused", async function () {
      const amount = ethers.parseUnits("100", 8);
      await token.mint(user1.address, amount);
      await token.pause();

      await expect(
        token.connect(user1).transfer(user2.address, amount)
      ).to.be.reverted;
    });

    it("should allow transfers after unpause", async function () {
      const amount = ethers.parseUnits("100", 8);
      await token.mint(user1.address, amount);
      await token.pause();
      await token.unpause();

      await token.connect(user1).transfer(user2.address, amount);
      expect(await token.balanceOf(user2.address)).to.equal(amount);
    });
  });

  describe("Burning", function () {
    it("should allow holders to burn their tokens", async function () {
      const amount = ethers.parseUnits("1000", 8);
      await token.mint(user1.address, amount);

      const burnAmount = ethers.parseUnits("300", 8);
      await token.connect(user1).burn(burnAmount);
      expect(await token.balanceOf(user1.address)).to.equal(
        amount - burnAmount
      );
    });
  });

  describe("Transfers", function () {
    it("should allow standard ERC-20 transfers", async function () {
      const amount = ethers.parseUnits("500", 8);
      await token.mint(user1.address, amount);

      const transferAmount = ethers.parseUnits("200", 8);
      await token.connect(user1).transfer(user2.address, transferAmount);

      expect(await token.balanceOf(user1.address)).to.equal(
        amount - transferAmount
      );
      expect(await token.balanceOf(user2.address)).to.equal(transferAmount);
    });
  });
});
