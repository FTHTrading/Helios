// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title HeliosToken (HLS)
 * @notice ERC-20 token for the Helios Protocol — secondary issuance rail.
 *
 * Architecture:
 *   - XRPL remains the primary issuance rail.
 *   - This ERC-20 contract is a SECONDARY rail layered beside XRPL.
 *   - Only the MINTER_ROLE (backend Celery worker / admin) can mint.
 *   - Total supply is hard-capped at 100,000,000 HLS (8 decimals).
 *
 * Roles:
 *   DEFAULT_ADMIN_ROLE — can grant/revoke roles, pause/unpause.
 *   MINTER_ROLE        — can mint new tokens up to the cap.
 *   PAUSER_ROLE        — can pause/unpause transfers.
 *
 * @dev Inherits OpenZeppelin v5 contracts.
 */
contract HeliosToken is ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice Hard cap: 100,000,000 HLS with 8 decimals
    uint256 public constant CAP = 100_000_000 * 10 ** 8;

    constructor(address defaultAdmin) ERC20("Helios Token", "HLS") {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(MINTER_ROLE, defaultAdmin);
        _grantRole(PAUSER_ROLE, defaultAdmin);
    }

    /// @notice 8 decimals to match XRPL HLS token precision.
    function decimals() public pure override returns (uint8) {
        return 8;
    }

    /**
     * @notice Mint new HLS tokens to `to`.
     * @dev Only callable by MINTER_ROLE. Reverts if cap would be exceeded.
     * @param to   Recipient address.
     * @param amount Amount in smallest unit (10^-8 HLS).
     */
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        require(totalSupply() + amount <= CAP, "HeliosToken: cap exceeded");
        _mint(to, amount);
    }

    /// @notice Pause all token transfers. Only PAUSER_ROLE.
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /// @notice Unpause token transfers. Only PAUSER_ROLE.
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    // ── Required overrides ──────────────────────────────────────

    function _update(
        address from,
        address to,
        uint256 value
    ) internal override(ERC20, ERC20Pausable) {
        super._update(from, to, value);
    }
}
