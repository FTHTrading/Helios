"""
Ask Helios — The Voice
════════════════════════════════════════════════════════
Male. Calm. Grounded. Authoritative. Never salesy. Never defensive.
Explains money like a real person at a kitchen table.
"I'll explain it. You decide."

HELIOS PROTOCOL — Gold-Backed Smart Contract Allocation on Web3 Rails:
    Contract amounts: $100 / $250 / $500 / $1,000 / $5,000
    3 allocation channels: Direct Connection, Smart Contract Engine, Gold & Crypto
    Propagation formula: W_h = W_1 · r^(h-1) across full connection depth
    Treasury: Physical gold via APMEX, NFT certificates on XRPL + Stellar

TONE: Adult. Calm. Grounded. Kitchen-table money talk.
      Not hype. Not crypto jargon. Just math and facts.

COMPLIANCE: No income guarantees. No promises. Results depend on effort.
            Earnings shown are mathematical projections, not guarantees.
"""

import os
import hashlib
from datetime import datetime, timezone
from config import HeliosConfig
from ai.build_knowledge import build_context_block, build_grounded_fallback


# ═══ Knowledge Base — Gold-Backed Smart Contract Protocol ════════════

HELIOS_KNOWLEDGE = {

    # ─── What It Is ───────────────────────────────────────────────

    "what_is_helios": (
        "Helios is a gold-backed smart contract allocation protocol on Web3 rails.\n\n"
        "You select a contract — $100, $250, $500, $1,000, or $5,000. "
        "One payment. No recurring fees. No product to buy.\n\n"
        "Your activation fee enters a published pipeline. 45% goes into a "
        "smart contract allocation engine that distributes to everyone in your "
        "connection mesh based on a math formula. 15% buys physical gold through APMEX. "
        "20% funds the liquidity pool. The rest covers operations.\n\n"
        "You get a .helios identity, gold-backed NFT certificates on XRPL "
        "and Stellar, access to BTC, ETH, XRP, and stablecoins, and a "
        "smart contract mesh that allocates value every time someone joins.\n\n"
        "No ranks. No titles. No monthly quota. Just math, gold, and connections."
    ),

    "contracts": (
        "There are multiple contract amounts. One payment. No recurring fees.\n\n"
        "$100 contract — Signal weight: 1×. Allocation pool: $45. "
        "Direct connection allocation: $22.50 per member.\n\n"
        "$250 contract — Signal weight: 2.5×. Allocation pool: $112.50. "
        "Direct connection allocation: $56.25 per member.\n\n"
        "$500 contract — Signal weight: 5×. Allocation pool: $225. "
        "Direct connection allocation: $112.50 per member.\n\n"
        "$1,000 contract — Signal weight: 10×. Allocation pool: $450. "
        "Direct connection allocation: $225 per member.\n\n"
        "$5,000 contract — Signal weight: 50×. Allocation pool: $2,250. "
        "Direct connection allocation: $1,125 per member.\n\n"
        "Higher contract = bigger pool = bigger allocations at every depth. "
        "Same formula. Same structure. Just bigger numbers."
    ),

    "three_ways_to_earn": (
        "There are exactly three allocation channels in Helios.\n\n"
        "1. DIRECT CONNECTION ALLOCATION — every member you personally connect "
        "generates an immediate allocation. That's 50% of your allocation pool. "
        "At the $100 contract, that's $22.50. At $5,000, that's $1,125. Per member.\n\n"
        "2. THE SMART CONTRACT ENGINE — 45% of every activation in your "
        "connection mesh goes into a pool. That pool distributes across the full "
        "depth using a published formula. Depth 1 gets 50%, Depth 2 gets 25%, "
        "Depth 3 gets 12.5%, and so on. You receive allocations from members you never "
        "even met — because your connections connected them.\n\n"
        "3. GOLD, NFTs, AND CRYPTO — part of every activation buys "
        "physical gold. You get gold-backed NFT certificates. You can "
        "convert to BTC, ETH, XRP, stablecoins, or hold physical metal. "
        "Plus Staking rewards from 5% to 30%.\n\n"
        "No ranks. No quotas. No monthly. Just these three channels."
    ),

    # ─── Direct Connections ───────────────────────────────────────

    "direct_referral": (
        "The direct connection allocation is the simplest channel. You connect a member, "
        "you receive an allocation. That day.\n\n"
        "The allocation is 50% of your allocation pool — which is 45% of the "
        "activation fee. Here's what that looks like by contract:\n\n"
        "$100 contract → $22.50 per connection\n"
        "$250 contract → $56.25 per connection\n"
        "$500 contract → $112.50 per connection\n"
        "$1,000 contract → $225.00 per connection\n"
        "$5,000 contract → $1,125.00 per connection\n\n"
        "Connect a few members at the $100 contract and you've already received $100+. "
        "Connect members at the $5,000 contract and the numbers scale significantly.\n\n"
        "This is just Channel #1. The smart contract engine and gold/crypto "
        "are separate allocation channels on top of this."
    ),

    # ─── Smart Contract Engine ────────────────────────────────────

    "smart_contract_engine": (
        "The smart contract engine is where the real scale lives.\n\n"
        "Every activation sends 45% into an allocation pool. That pool "
        "gets distributed across the full connection depth using this formula:\n\n"
        "Weight at Depth h = W_1 · r^(h-1)\n\n"
        "Depth 1: 50.0% of the pool — that's your direct connections.\n"
        "Depth 2: 25.0%\n"
        "Depth 3: 12.5%\n"
        "Depth 4: 6.25%\n"
        "Depth 5: 3.125%\n"
        "Depth 6: 1.5625%\n"
        "Depth 7: 0.781%\n"
        "...and continues through the full mesh.\n\n"
        "The dollar amounts per member get smaller at deeper hops. "
        "But the number of members gets exponentially larger. "
        "Small per member × substantial volume = real allocations. That's the engine."
    ),

    "allocation_formula": (
        "The allocation formula is published and deterministic. Nobody decides "
        "who gets what — the math does.\n\n"
        "W_h = W_1 · r^(h-1)\n\n"
        "That means each depth gets half the weight of the depth above it. "
        "Depth 1 = 50%. Depth 2 = 25%. Depth 3 = 12.5%. And so on.\n\n"
        "The pool is 45% of the activation fee:\n"
        "$100 contract → $45 pool\n"
        "$250 contract → $112.50 pool\n"
        "$500 contract → $225 pool\n"
        "$1,000 contract → $450 pool\n"
        "$5,000 contract → $2,250 pool\n\n"
        "Each member's entry creates a new allocation event. "
        "The formula runs. Everyone in the connection chain gets their share. "
        "Automatically. No human decision involved."
    ),

    # ─── Smart Contract Propagation ───────────────────────────────

    "propagation": (
        "Think of smart contract propagation like signal flowing through a mesh.\n\n"
        "When someone activates a contract, the smart contract distributes "
        "allocations outward through the connection graph. Each hop reduces "
        "the allocation by a decay factor.\n\n"
        "Depth 1 gets 50%. Depth 2 gets 25%. Depth 3 gets 12.5%. And so on.\n\n"
        "The person who made the direct connection receives the largest allocation. "
        "Members further up the chain receive progressively smaller amounts — "
        "but they receive from every activation in their mesh, not just "
        "direct connections.\n\n"
        "Direct connectors earn the most per member. "
        "Upstream members earn less per member but from more activations. "
        "The formula is deterministic — W_h = W_1 · r^(h-1). "
        "No discretion. Pure math.\n\n"
        "The formula rewards the person doing the work — direct connectors "
        "always receive the largest share."
    ),

    "growth_scenario": (
        "Let me show you the math at scale.\n\n"
        "Direct connectors — closest to new activations — receive the "
        "largest allocations per member. Members further upstream receive "
        "smaller per-member amounts but from more total activations.\n\n"
        "With a growing mesh on the $100 contract:\n"
        "Direct connection allocations: $22.50 per member.\n"
        "Depth 2 allocations: $11.25 per member.\n"
        "Depth 3 allocations: $5.625 per member.\n\n"
        "As the mesh grows, volume compounds. The per-member amount "
        "decreases with depth, but the number of members increases "
        "exponentially.\n\n"
        "With higher contracts ($500, $1,000, $5,000), these numbers "
        "scale proportionally. The formula doesn't change. "
        "The structure doesn't change. Just bigger numbers.\n\n"
        "These are mathematical projections based on the formula. "
        "Results depend on the work you and your connections put in."
    ),

    # ─── Where Your Money Goes ────────────────────────────────────

    "allocation_split": (
        "Every activation fee splits the same way. Every contract. No exceptions.\n\n"
        "45% — Network Allocation. This is the smart contract engine. "
        "It's the pool that distributes to everyone in the connection mesh.\n\n"
        "20% — Liquidity Pool. Ensures certificates can always be redeemed. "
        "You want to cash out your gold certificates? This pool backs that.\n\n"
        "15% — Treasury. Physical gold purchases through APMEX. "
        "Real metal. Real receipts. Real vaults.\n\n"
        "10% — Infrastructure. Servers, compliance, operations, development.\n\n"
        "10% — Protocol Buffer. Emergency reserves.\n\n"
        "That's 100%. Every dollar accounted for. No slush fund. "
        "No mystery bucket. The math is published."
    ),

    # ─── Gold & Crypto ────────────────────────────────────────────

    "gold_backing": (
        "Part of every activation buys physical gold. Real metal. Not paper.\n\n"
        "15% of every fee goes to the treasury, which purchases gold through "
        "APMEX — one of the largest precious metals dealers in the world.\n\n"
        "As the protocol grows, gold purchases scale proportionally. "
        "Higher contracts scale that number significantly.\n\n"
        "Every purchase generates a Metal Vault Receipt — an NFT on XRPL "
        "recording the dealer, invoice, metal type, weight, and serial numbers. "
        "Evidence is pinned to IPFS. Anyone can verify every ounce.\n\n"
        "You receive gold-backed NFT certificates. These represent actual "
        "gold weight. You can redeem for physical gold, physical silver, "
        "or convert to stablecoins.\n\n"
        "Your wealth is backed by something you can hold in your hand."
    ),

    "crypto_access": (
        "Your allocations aren't stuck in one asset. You have options.\n\n"
        "BTC — Bitcoin. The original. Store of value.\n"
        "ETH — Ethereum. Smart contract backbone.\n"
        "XRP — Ripple. Fast cross-border settlement.\n"
        "XLM — Stellar. Low-cost transfers.\n"
        "USDC — Circle stablecoin. Pegged to the dollar.\n"
        "USDT — Tether stablecoin. Most liquid stablecoin.\n\n"
        "Plus physical gold (Au) and physical silver (Ag) through "
        "the treasury.\n\n"
        "You can convert your certificates into any of these. "
        "Build a portfolio across multiple asset classes. "
        "Diversify the way institutions do — not the way retail usually can.\n\n"
        "Helios runs on XRPL and Stellar. Two of the fastest, cheapest "
        "settlement networks in crypto. Your transactions settle in seconds."
    ),

    "certificate_staking": (
        "Staking lets you lock your certificates for Reward Allocations.\n\n"
        "30 days → +5% reward\n"
        "90 days → +12% reward\n"
        "180 days → +20% reward\n"
        "365 days → +30% reward\n\n"
        "You're not lending your certificates to anyone. You're locking them "
        "in the protocol and earning Reward Allocations on top of your "
        "existing allocations.\n\n"
        "Staking rewards compound on top of your base allocations. "
        "That 30% annual reward adds significant value over time.\n\n"
        "Staking is optional. Your certificates, your choice. "
        "But the math rewards patience."
    ),

    "nft_certificates": (
        "Helios Certificates are NFTs on XRPL, backed by physical gold.\n\n"
        "When you earn through the protocol or activate a contract, "
        "you receive certificates. Each one is a unique NFT with a "
        "deterministic ID — SHA256 of your identity, the amount, "
        "timestamp, and rate.\n\n"
        "What can you do with them?\n\n"
        "1. Hold — your certificate represents gold weight in the treasury.\n"
        "2. Redeem for gold — actual physical metal shipped to you.\n"
        "3. Redeem for silver — physical silver, same process.\n"
        "4. Convert to stablecoin — USDC or USDT equivalent.\n"
        "5. Convert to crypto — BTC, ETH, XRP, or XLM.\n"
        "6. Stake — lock for 30-365 days, earn Reward Allocations.\n\n"
        "They're not points. They're not credits. They're assets."
    ),

    # ─── Legitimacy & Structure ───────────────────────────────────

    "protocol_structure": (
        "Let me be direct about what Helios is.\n\n"
        "It's a smart contract allocation protocol. The formula distributes "
        "value across your connection mesh deterministically. The math is "
        "published. Anyone can verify it before they join.\n\n"
        "Here's the structure:\n\n"
        "No ranks. Nobody is a 'Diamond' or a 'Director.' There's no "
        "title system. The formula doesn't care about labels.\n\n"
        "No recurring fees. You pay once. That's it. There's no monthly "
        "qualifier. There's no re-enrollment.\n\n"
        "No product to push. There's no juice, supplements, or skincare. "
        "The protocol allocates gold and crypto. Real assets.\n\n"
        "No forced purchases. You don't buy inventory. You don't maintain "
        "a minimum. You don't qualify by spending.\n\n"
        "The math is published. The formula is on the site. Anyone can "
        "verify the allocations before they join.\n\n"
        "Smart contracts. Published math. Real assets."
    ),

    "protocol_integrity": (
        "Here's what Helios does NOT do:\n\n"
        "1. No ranks. No titles. No hierarchical labels.\n"
        "2. No recurring fees. One payment. Done.\n"
        "3. No product to push. No physical goods requirement.\n"
        "4. No re-qualifying. Your contract is your contract.\n"
        "5. No minimum volume requirements.\n"
        "6. No forced upgrades.\n"
        "7. No mandatory meetings or conventions.\n"
        "8. No hidden fees. The allocation formula is published.\n"
        "9. No promises. The math is real. Results depend on effort.\n\n"
        "One payment. Published math. Real assets. "
        "That's it. Everything else is noise."
    ),

    # ─── How to Join ──────────────────────────────────────────────

    "how_to_join": (
        "Joining takes about two minutes.\n\n"
        "Step 1 — Select your contract. $100, $250, $500, $1,000, or $5,000. "
        "Higher contract means bigger allocation pool and bigger connection "
        "allocations. All contracts get the same structure and access.\n\n"
        "Step 2 — Pay once. One transaction. No recurring charges. "
        "Your fee splits automatically: 45% to the smart contract engine, "
        "15% to gold treasury, 20% to liquidity, the rest to operations.\n\n"
        "Step 3 — Get your .helios identity. Something like nova.helios "
        "or king.helios. That's yours permanently.\n\n"
        "Step 4 — Receive your first certificate allocation and full "
        "protocol access including crypto tools and the AI guide.\n\n"
        "Step 5 — Share with your connections. "
        "Let the smart contracts handle the rest.\n\n"
        "No application. No approval process. No waiting period."
    ),

    "what_you_receive": (
        "When you activate any contract, here's what you get:\n\n"
        "1. Your .helios identity — a permanent namespace like yourname.helios. "
        "That's your on-chain identity in the protocol.\n\n"
        "2. Gold-backed NFT certificates — real digital assets backed by "
        "physical gold in the treasury. Redeemable.\n\n"
        "3. Smart contract mesh access — every member who joins through your "
        "connections generates allocations across the full depth automatically.\n\n"
        "4. Crypto tools — convert to BTC, ETH, XRP, XLM, USDC, USDT. "
        "Build your portfolio.\n\n"
        "5. Certificate staking — lock for 30 to 365 days, earn 5-30% "
        "Reward Allocations.\n\n"
        "6. Full protocol access — treasury verification, allocation model, "
        "AI advisory, AI guide, and live protocol metrics.\n\n"
        "7. The Helios AI — that's me. Available 24/7 to walk you through "
        "the math, the assets, or anything else.\n\n"
        "All contracts get full access. Higher contracts just get bigger numbers."
    ),

    # ─── Web3 / Technical ─────────────────────────────────────────

    "web3_rails": (
        "Helios runs on two blockchains: XRPL and Stellar.\n\n"
        "XRPL (XRP Ledger) — handles NFT certificates and Metal Vault "
        "Receipts. Fast settlement. Low fees. Battle-tested since 2012.\n\n"
        "Stellar — handles stablecoin operations and cross-asset settlement. "
        "Built for financial rails. Used by major institutions.\n\n"
        "Why two chains? Each does what it does best. XRPL for certificates "
        "and proof of reserves. Stellar for fast, cheap value transfer.\n\n"
        "Your allocations settle on-chain. Your certificates are verifiable. "
        "The treasury receipts are anchored with IPFS evidence bundles. "
        "Anyone can verify the gold holdings independently.\n\n"
        "This isn't 'we use blockchain.' The protocol actually lives on-chain."
    ),

    "treasury": (
        "The treasury is physical gold. Real metal in real vaults.\n\n"
        "15% of every activation fee goes to the treasury fund. "
        "That fund purchases gold through APMEX — one of the largest "
        "precious metals dealers in the United States.\n\n"
        "Every purchase creates a Metal Vault Receipt — an NFT on XRPL "
        "with the dealer name, invoice number, metal type, weight, "
        "serial numbers, and cost. Evidence bundles (invoices, photos) "
        "are pinned to IPFS.\n\n"
        "As the protocol grows, the treasury scales proportionally. "
        "With higher contracts ($250-$5,000), that number scales dramatically.\n\n"
        "Proof of reserves is public. Always. That's the deal.\n\n"
        "Your allocations aren't backed by promises. They're backed by metal."
    ),

    "verification": (
        "Everything in Helios is verifiable.\n\n"
        "The allocation formula is published: W_h = W_1 · r^(h-1). "
        "Anyone can run the math before they join.\n\n"
        "The fee split is published: 45% smart contract engine, 20% liquidity, "
        "15% treasury, 10% infrastructure, 10% buffer.\n\n"
        "The treasury receipts are on XRPL. Metal Vault Receipts are NFTs. "
        "Evidence is on IPFS. Anyone can verify every ounce of gold.\n\n"
        "Certificate IDs are deterministic — SHA256 hashes. "
        "You can independently verify your certificates.\n\n"
        "Protocol metrics are live and queryable.\n\n"
        "If someone tells you to 'just trust them,' walk away. "
        "In Helios, you verify. The math is public. The gold is real. "
        "The receipts are on-chain."
    ),

    # ─── Risk & Honesty ───────────────────────────────────────────

    "risks": (
        "I'll be straight with you because that's how this works.\n\n"
        "Your allocations depend on growing connections. If you join and don't "
        "connect anyone, you'll receive your certificates and gold allocation "
        "from your own activation, but the smart contract engine needs members.\n\n"
        "The numbers I show are mathematical projections based on the formula. "
        "Real results depend on how many members you connect, how well they "
        "duplicate, and what contracts they choose.\n\n"
        "Gold prices fluctuate. Crypto prices fluctuate. The protocol "
        "holds real assets, but asset values move.\n\n"
        "This isn't a savings account. It's not a guaranteed return. "
        "It's a protocol that rewards effort and math.\n\n"
        "The formula is real. The gold is real. But the work is on you."
    ),

    "why_not_rug": (
        "The treasury holds physical gold with receipts on XRPL. "
        "Anyone can verify every ounce independently.\n\n"
        "The allocation formula is published. No one decides allocations — "
        "the math does.\n\n"
        "There are no admin keys that let someone change the rules "
        "or drain the pools.\n\n"
        "The fee split is hardcoded: 45/20/15/10/10. "
        "It can't be altered after the fact.\n\n"
        "There's no token that can be dumped. No pre-mine. "
        "No insider allocation waiting to crash the price.\n\n"
        "The protocol is designed so that pulling the rug is architecturally "
        "impossible. Not 'we promise we won't.' The code won't let it happen.\n\n"
        "Verify the gold. Verify the math. That's all I ask."
    ),

    # ─── Token ────────────────────────────────────────────────────

    "what_token": (
        "HLS is the protocol token that powers Helios.\n\n"
        "Fixed supply: 100 million. No minting function. Nobody can create more.\n\n"
        "40% — locked in the settlement pool for protocol operations.\n"
        "35% — distribution as the protocol grows.\n"
        "15% — development, under 4-year vesting.\n"
        "10% — emergency reserve, locked 5 years.\n\n"
        "Founder tokens are locked 3 years. They can't touch them. "
        "They can't mint more. The contract doesn't have that function.\n\n"
        "The token facilitates protocol operations. It's not a speculation "
        "instrument. The value is in the protocol, the gold, and the certificates."
    ),

    # ─── Protocol Rules ───────────────────────────────────────────

    "protocol_rules": (
        "Helios runs on fixed rules. No exceptions. No overrides.\n\n"
        "ALLOCATION:\n"
        "- Contracts: $100 / $250 / $500 / $1,000 / $5,000\n"
        "- 45% of every fee enters the smart contract engine\n"
        "- Formula: W_h = W_1 · r^(h-1)\n"
        "- Propagation across full connection depth\n\n"
        "TREASURY:\n"
        "- 15% buys physical gold through APMEX\n"
        "- Metal Vault Receipts on XRPL\n"
        "- Proof of reserves is always public\n\n"
        "CERTIFICATES:\n"
        "- Gold-backed NFTs on XRPL\n"
        "- Redeemable for gold, silver, or stablecoins\n"
        "- Staking: 30d = +5%, 90d = +12%, 180d = +20%, 365d = +30%\n\n"
        "INTEGRITY:\n"
        "- No admin override keys\n"
        "- Conservation law: total in = total out\n"
        "- Published formula — anyone can verify before joining"
    ),

    "founders": (
        "The founders built the protocol. They don't control it.\n\n"
        "Their tokens are locked 3 years. They can't mint more — "
        "the contract doesn't have a minting function. They can't change "
        "the allocation formula. They can't access the pools.\n\n"
        "They hold a .helios identity like everyone else. "
        "They earn through the same formula as everyone else.\n\n"
        "If the founders disappeared tomorrow, the protocol keeps running. "
        "The formula keeps calculating. The treasury keeps holding gold. "
        "The certificates keep their value.\n\n"
        "That's the point. The system works because it doesn't need "
        "any one person to keep it running."
    ),

    # ─── Earning Comparisons ──────────────────────────────────────

    "earning_examples": (
        "Let me give you some real numbers. All based on the published formula.\n\n"
        "A FEW CONNECTIONS at $100 contract:\n"
        "Direct connection: each generates $22.50\n"
        "Depth 1 engine: $22.50 per member\n\n"
        "AS THE MESH GROWS at $100:\n"
        "You earn from Depth 1 AND Depth 2 connections.\n"
        "Depth 1: $22.50 per member. Depth 2: $11.25 per member.\n\n"
        "DEPTH 3 at $100:\n"
        "Depth 3: $5.625 per member\n\n"
        "It keeps going. The deeper the mesh gets, the more people there are, "
        "and even though per-person amounts get smaller, the volume "
        "makes up for it.\n\n"
        "Now imagine those people chose the $5,000 contract instead of $100..."
    ),

    "mixed_contract_math": (
        "When people in your mesh choose higher contracts, your numbers scale.\n\n"
        "At the $100 contract, your Depth 1 allocation per member is $22.50.\n"
        "At $5,000 contract, that same depth yields $1,125 per member.\n\n"
        "In a real protocol mesh, people choose different contracts. Some pick $100. "
        "Some go $1,000. A few go $5,000.\n\n"
        "With mixed contracts, allocations scale significantly. "
        "The formula doesn't change. The structure doesn't change. "
        "The only thing that changes is the dollar amounts flowing through it.\n\n"
        "Higher contracts don't get special treatment. They just put more money "
        "into the same engine."
    ),

    # ─── How It Compares ──────────────────────────────────────────

    "vs_traditional": (
        "Let me compare this to what most people know.\n\n"
        "SAVINGS ACCOUNT: 0.5% APY. $100 earns you 50 cents in a year.\n\n"
        "STOCK MARKET: Average 10% per year if you hold long enough. "
        "$100 becomes $110 after 12 months. Maybe.\n\n"
        "REAL ESTATE: Good returns, but you need $50K-$100K minimum. "
        "Plus maintenance, tenants, repairs.\n\n"
        "HELIOS: Smart contract allocations based on a published formula. "
        "The math scales with your connections and their contract amounts. "
        "Your initial activation: as low as $100.\n\n"
        "The catch? You have to grow connections. It's not passive. "
        "The math is real, but the work is real too.\n\n"
        "Nothing worth having comes without effort. But the math here "
        "is better than anything a bank will ever offer you."
    ),

    # ─── Token Offering & Launch ──────────────────────────────────

    "token_offering": (
        "The HLS token offering is the starting line. Three phases, clear dates.\n\n"
        "PHASE 1 — FOUNDING WINDOW (Feb 10 – Mar 31, 2026):\n"
        "Token price: $0.05 per HLS. "
        "Founding Member badge — permanent, on-chain. Priority .helios identity.\n\n"
        "PHASE 2 — BUILDER PHASE (Apr 1 – May 31, 2026):\n"
        "Token price: $0.25 per HLS. instant issuance. Smart contract engine activates. "
        "Liquidity pools funded. First NFT certificate minting.\n\n"
        "PHASE 3 — PUBLIC LAUNCH (Jun 1, 2026 →):\n"
        "Token price: $0.50 per HLS. Market rate. DEX listing. Full protocol live.\n\n"
        "$1,000 during Phase 1 = 20,000 HLS tokens. At public price that's $10,000 worth. "
        "10× your money before the smart contract engine even starts."
    ),

    "trustlines": (
        "A trustline is like opening a lane on the highway for a specific token.\n\n"
        "On XRPL, you set a TrustSet transaction to tell your wallet: "
        "'I'm willing to hold HLS tokens.' Costs about 2 XRP as a reserve — "
        "not a fee, it stays in your wallet.\n\n"
        "On Stellar, it's a ChangeTrust operation. Same idea — you authorize "
        "your wallet to hold HLS and stablecoins like USDC.\n\n"
        "You need trustlines set up before you can receive tokens. "
        "During Phase 1, we walk every founding member through the setup "
        "step by step. XUMM/Xaman for XRPL, Lobstr for Stellar. "
        "No technical experience required.\n\n"
        "Once your trustlines are set, tokens flow directly to your wallet. "
        "No middleman. No exchange. Wallet to wallet."
    ),

    "early_benefits": (
        "Here's what founding members get that nobody else will ever have:\n\n"
        "1. LOWEST PRICE EVER — $0.05/HLS. Phase 2 is $0.25. Public is $0.50. "
        "Your dollar goes 10× further than someone joining at launch.\n\n"
        "2. INSTANT ISSUANCE — Tokens delivered directly to your wallet. "
        "Drops to 10% in Phase 2. Zero at public launch.\n\n"
        "3. FOUNDING ACCESS — First to activate when the smart contract engine "
        "goes live. That access is permanent.\n\n"
        "4. FOUNDING MEMBER BADGE — Permanent, non-transferable, on-chain. "
        "You can't buy this later at any price.\n\n"
        "5. PRIORITY .HELIOS IDENTITY — First pick of names. "
        "gold.helios, king.helios — whatever you want.\n\n"
        "6. FIRST TRUSTLINE ACCESS — Your wallet is ready before "
        "everyone else's. When tokens flow, you're already connected."
    ),

    "launch_phases": (
        "Three phases. Each one raises the price and reduces the founding advantage.\n\n"
        "PHASE 1 — FOUNDING (Feb 10 – Mar 31, 2026):\n"
        "Register. Set up trustlines. Buy HLS at $0.05. Instant token issuance. "
        "First gold purchase with treasury allocation.\n\n"
        "PHASE 2 — BUILDER (Apr 1 – May 31, 2026):\n"
        "Token price goes to $0.25. Founding reward drops to 10%. "
        "Smart contract engine activates. Liquidity pools form. "
        "NFT certificates start minting. First proof of reserves.\n\n"
        "PHASE 3 — PUBLIC (Jun 1, 2026 →):\n"
        "Price hits $0.50. No more reward. Full protocol live. "
        "DEX listing. Staking. Certificate marketplace. "
        "Cross-chain settlement fully operational.\n\n"
        "Every week you wait in Phase 1, you're closer to paying "
        "2.5× more in Phase 2."
    ),

    "liquidity_pools": (
        "Liquidity pools are how HLS gets real trading depth.\n\n"
        "20% of every activation fee goes into the liquidity allocation. "
        "During Phase 2, that money funds HLS/USDC and HLS/XRP pools "
        "on decentralized exchanges.\n\n"
        "That means HLS isn't just a token you hold — it's a token "
        "you can trade. Real buyers, real sellers, real price discovery.\n\n"
        "The Phase 1 token offering is the starting fuel. "
        "Activation fees add to it continuously. "
        "As the protocol grows, the pools grow. "
        "More liquidity = tighter spreads = better for everyone.\n\n"
        "By Phase 3, when HLS lists on DEXes at $0.50, "
        "there's already real liquidity behind it — not just hype."
    ),

    "hls_token_details": (
        "100 million HLS tokens. Fixed supply. No minting function. "
        "Nobody can create more — not even founders.\n\n"
        "SETTLEMENT POOL — 40% (40M tokens):\n"
        "Powers the smart contract allocation engine.\n\n"
        "PROTOCOL DISTRIBUTION — 35% (35M tokens):\n"
        "Token offering, protocol rewards, Connection rewards.\n\n"
        "DEVELOPMENT — 15% (15M tokens):\n"
        "4-year linear vesting. Engineering, partnerships.\n\n"
        "EMERGENCY RESERVE — 10% (10M tokens):\n"
        "Locked 5 years. Black swan protection.\n\n"
        "Founder tokens locked 3 years. No admin minting keys. "
        "The contract is immutable. This isn't a promise — "
        "it's code on a blockchain."
    ),

    "flowline": (
        "The Flowline is the animated path on our site that shows how Helios works.\n\n"
        "It moves like electricity through a wire, lighting up each step as value \n"
        "flows through the system. Five steps:\n\n"
        "Step 1 — CONTRACT ACTIVATION: You select your contract and activate.\n"
        "Step 2 — FIAT TO STABLECOIN: Dollars convert to USDC/USDT.\n"
        "Step 3 — STABLECOIN TO GOLD: Stablecoins acquire physical gold.\n"
        "Step 4 — GOLD TO CERTIFICATES: Gold tokenizes into NFT certificates.\n"
        "Step 5 — SMART CONTRACT DISTRIBUTION: Certificates distribute through the mesh.\n\n"
        "When a new member activates, the Flowline shows the movement of value \n"
        "through the smart contract structure — step by step, depth by depth.\n\n"
        "It's a visual way to understand how Helios distributes value, issues \n"
        "gold-backed certificates, and triggers allocations across the protocol.\n\n"
        "Visit the homepage to watch the Flowline in action."
    ),

    # ─── Token Economics ──────────────────────────────────────────

    "burn_mechanics": (
        "HLS has a fixed supply of 100 million tokens. Burns permanently reduce "
        "that supply. Nobody can reverse a burn. Nobody can mint more.\n\n"
        "WHAT TRIGGERS A BURN:\n\n"
        "Contract Upgrade — when you upgrade, the difference between old and new contract "
        "token allocation is burned. Prevents double-dipping.\n\n"
        "Certificate Redemption — when you redeem a gold certificate for physical "
        "metal, the underlying token allocation is burned. Balances supply when "
        "gold leaves the treasury.\n\n"
        "Marketplace Fee — 20% of every internal marketplace transaction fee is burned. "
        "Buy a gold certificate with HLS? Part of the fee disappears forever.\n\n"
        "Conversion Fee — every HLS→stablecoin swap carries a 1% fee. 20% of that "
        "fee is burned. Every swap reduces supply.\n\n"
        "Early Staking Exit — if you break a staking lock, forfeited reward tokens "
        "are burned. 50-100% of accrued reward, depending on timing.\n\n"
        "Expired Identities — unclaimed .helios reserves are burned after 365 days.\n\n"
        "Supply can only go down. Never up. The burn address is public on XRPL."
    ),

    "penalties": (
        "Penalties protect long-term members from short-term exploiters. "
        "Every forfeited token is burned — benefiting everyone who stays.\n\n"
        "STAKING PENALTIES:\n"
        "Break lock within 7 days → 100% of accrued reward forfeited and burned.\n"
        "Break lock after 7 days → 50% of accrued reward forfeited and burned.\n\n"
        "RAPID CONVERSION PENALTY:\n"
        "Convert HLS→stablecoin within 48 hours of receiving tokens? "
        "2.5% conversion surcharge instead of the standard 1%. "
        "Discourages pump-and-dump behavior.\n\n"
        "DORMANT ACCOUNT:\n"
        "No activity for 730 days? Staking rewards pause. "
        "Reactivate anytime with any transaction. No tokens are lost.\n\n"
        "IMPORTANT: No penalty for simply holding. Your tokens, your certificates, "
        "your gold — they're yours. Penalties only apply to breaking commitments "
        "you voluntarily made."
    ),

    "internal_marketplace": (
        "The internal marketplace lets you spend HLS on real assets inside "
        "the protocol. This creates real demand for the token.\n\n"
        "WHAT YOU CAN BUY WITH HLS:\n\n"
        "Gold certificates — purchase additional gold-backed NFT certificates. "
        "Each one represents real gold in the treasury. Redeemable for physical metal.\n\n"
        "Silver certificates — same structure as gold. Real metal, real receipts.\n\n"
        ".helios identities — premium namespace identities like money.helios "
        "or crown.helios. On-chain. Permanent.\n\n"
        "Contract upgrades — use HLS to upgrade your contract instead of fiat. "
        "Go from $100 to $5,000 using accumulated tokens.\n\n"
        "Premium analytics — advanced protocol tools and propagation calculators.\n\n"
        "Every marketplace transaction carries a small fee. 20% of every fee "
        "is burned. More usage = more burns = more scarcity."
    ),

    "stablecoin_exchange": (
        "You can convert between HLS, certificates, and stablecoins on-chain. "
        "No intermediary. Wallet-to-wallet. Powered by XRPL DEX and Stellar anchors.\n\n"
        "CONVERSION ROUTES:\n\n"
        "HLS → USDC/USDT — sell HLS for stablecoins at market rate. 1% fee. "
        "20% of fee burned.\n\n"
        "USDC/USDT → HLS — buy HLS with stablecoins. 0.5% fee. Creates buy pressure.\n\n"
        "Certificates → Stablecoin — redeem gold certificates for USDC at current "
        "gold spot rate. Real gold price, real settlement.\n\n"
        "HLS → BTC/ETH/XRP — swap through XRPL DEX pathfinding. Multi-hop routing "
        "finds the best rate automatically.\n\n"
        "RAPID CONVERSION WARNING: If you convert HLS→stablecoin within 48 hours "
        "of receiving tokens, there's a 2.5% surcharge instead of 1%. "
        "This discourages short-term exploitation.\n\n"
        "Settlement in seconds. No exchange account needed. Just your wallet."
    ),

    "genesis_pool": (
        "The Genesis Pool is how Helios starts.\n\n"
        "10 members activate at the $5,000 contract. "
        "10 × $5,000 = $50,000 Genesis Value.\n\n"
        "That $50K splits: 45% ($22,500) allocation pool, 20% ($10,000) liquidity, "
        "15% ($7,500) gold purchase, 10% ($5,000) infrastructure, "
        "10% ($5,000) protocol buffer.\n\n"
        "Genesis Token Supply: 50,000 HLS. 1 token = $1 backing. Clean start.\n\n"
        "Then 10,000 members join at $100 each = $1,000,000 new value. "
        "Total backing becomes $1,050,000. Total supply: 1,050,000 tokens. "
        "Token price stays at $1.00 — but the backing is now massive.\n\n"
        "The Genesis 10 earn $20K–$225K each from the allocation pool alone, "
        "plus gold certificates, Staking rewards, and token allocations.\n\n"
        "The math compounds. The promises don't."
    ),

    "bonus_structure": (
        "Multiple reward channels reward different behaviors. All Rewards are funded "
        "from existing pools — never from new token creation.\n\n"
        "FOUNDING REWARD: Instant issuance on Phase 1 purchases. Drops to +10% Phase 2. "
        "Zero at public launch.\n\n"
        "Contract Upgrade Reward: Upgrade contracts and receive 10% transition reward on "
        "the price difference. $100→$1,000 = $900 × 10% = $90 in HLS.\n\n"
        "Staking Reward: 5-30% based on lock duration (30d/90d/180d/365d).\n\n"
        "LOYALTY MILESTONES: 6 months active = +2%. 12 months = +5%. "
        "24 months = +10%. These stack on top of staking.\n\n"
        "GROWTH MILESTONES: 100 connections = 500 HLS. 500 = 2,500 HLS. "
        "1,000 = 7,500 HLS. 5,000 = 25,000 HLS.\n\n"
        "GOLD ACCUMULATION: Every 10 oz of gold in treasury triggers 1% reward "
        "on your next certificate allocation.\n\n"
        "All formula-governed. All published. No discretion."
    ),

    "token_value_drivers": (
        "Token value isn't promised. It's engineered through mechanics.\n\n"
        "SUPPLY REDUCTION: Burns from upgrades, redemptions, marketplace fees, "
        "conversion fees, and staking penalties permanently reduce supply. "
        "100M is the ceiling. Actual circulating supply decreases over time.\n\n"
        "DEMAND CREATION: Marketplace purchases, contract upgrades, staking locks, "
        "and stablecoin→HLS conversions create buy pressure. Real utility = real demand.\n\n"
        "GOLD FLOOR: 15% of every activation buys physical gold. Certificates are "
        "redeemable at gold spot rate. Hard asset floor that rises with gold prices.\n\n"
        "CIRCULATING LOCK: Staked tokens, founder locks (3yr), emergency reserve (5yr), "
        "and development vesting (4yr) remove tokens from circulation. Less available "
        "supply = higher price potential.\n\n"
        "The token doesn't need hype. The mechanics do the work."
    ),

    "qr_code_sharing": (
        "Every Helios member gets a personal QR code page — your .helios identity, "
        "branded with Helios gold, downloadable as a high-res PNG.\n\n"
        "HOW IT WORKS: Go to helios5.netlify.app/qr/yourname. That page shows "
        "your branded QR code. When someone scans it, they land on your personal "
        "registration link. They connect through you.\n\n"
        "THE CHAIN: After they register, they get their OWN QR code page at "
        "/qr/theirname. They share that code. Their connections register. Those people "
        "get their own codes. The chain propagates through the smart contract mesh.\n\n"
        "Every connection is permanent. Your connector is always your connector. "
        "The allocation formula runs on every activation, automatically.\n\n"
        "SHARING: Download the QR as a PNG — print it, text it, post it, put it "
        "on a business card. Or tap Share to copy the link directly.\n\n"
        "No app required. No login to share. Just a code and a URL. "
        "The protocol grows one scan at a time."
    ),
}


# ═══ Topic Detection — Natural Language Mapping ══════════════════════

TOPIC_MAP = {
    "what_is_helios": ["what is", "what's helios", "explain helios", "about helios", "tell me about", "how does helios", "what does helios do"],
    "contracts": ["contract", "contracts", "$100", "$250", "$500", "$1000", "$5000", "which contract", "pick a contract", "activation", "contract amount"],
    "three_ways_to_earn": ["three ways", "3 ways", "how do i earn", "how do i make money", "how you earn", "ways to earn", "income streams", "revenue streams"],
    "direct_referral": ["direct connection", "connection allocation", "connect someone", "bring someone", "per person", "per member", "per connection", "Connection Reward"],
    "smart_contract_engine": ["smart contract", "contract engine", "allocation engine", "formula", "weight", "depth", "how many depths", "propagation"],
    "allocation_formula": ["formula", "w_h", "w_1", "decay", "weighting", "math behind", "calculation", "how is it calculated"],
    "propagation": ["propagation", "signal", "mesh", "how allocations flow", "flow through", "connection graph"],
    "growth_scenario": ["scenario", "projection", "how much can i make", "realistic", "example", "big numbers", "scale"],
    "allocation_split": ["where does my money go", "fee split", "45%", "20%", "15%", "allocation split", "how is the fee split", "where money goes"],
    "gold_backing": ["gold", "physical gold", "metal", "apmex", "vault", "gold backed", "gold backing", "bullion", "precious metal", "real gold"],
    "crypto_access": ["crypto", "bitcoin", "btc", "eth", "ethereum", "xrp", "xlm", "stellar", "usdc", "usdt", "stablecoin", "which crypto"],
    "certificate_staking": ["staking", "stake", "lock", "bonus", "30 day", "90 day", "180 day", "365 day", "Staking Reward", "lock certificate"],
    "nft_certificates": ["nft", "certificate", "certificates", "what do i get", "digital asset", "redeemable"],
    "protocol_structure": ["mlm", "pyramid", "ponzi", "scam", "scheme", "legit", "legitimate", "is this", "multilevel", "multi-level", "network marketing", "is it a"],
    "protocol_integrity": ["no bs", "no ranks", "no monthly", "what's the catch", "hidden fees", "monthly fee", "quota"],
    "how_to_join": ["join", "sign up", "register", "start", "get started", "create account", "how to join", "onboard", "activate", "how do i start"],
    "what_you_receive": ["what do i get", "receive", "what's included", "benefits", "member benefits", "what comes with", "access"],
    "web3_rails": ["xrpl", "stellar", "blockchain", "on chain", "on-chain", "web3", "which chain", "what chain"],
    "treasury": ["treasury", "reserves", "proof of reserves", "vault receipt", "mvr", "where is the gold"],
    "verification": ["verify", "audit", "check", "proof", "transparent", "trust", "verifiable", "published"],
    "risks": ["risk", "downside", "lose money", "what if", "guarantee", "guaranteed", "safe", "risky"],
    "why_not_rug": ["rug", "rug pull", "run away", "steal", "disappear", "trust you"],
    "what_token": ["token", "coin", "hls", "supply", "tokenomics"],
    "protocol_rules": ["rules", "limits", "restrictions", "protocol", "parameters", "how it works technically"],
    "founders": ["founder", "team", "who built", "who made", "creator", "behind helios", "who runs"],
    "earning_examples": ["example", "show me the math", "break it down", "real numbers", "small network"],
    "mixed_contract_math": ["mixed contract", "higher contract", "bigger numbers", "what if $5000", "multiply"],
    "vs_traditional": ["compare", "savings", "bank", "stock market", "real estate", "better than", "vs", "compared to"],
    "token_offering": ["token offering", "offering", "presale", "pre-sale", "token sale", "buy tokens", "buy hls", "get tokens", "founding window", "get the party started"],
    "trustlines": ["trustline", "trustlines", "trust line", "trustset", "changetrust", "xumm", "xaman", "lobstr", "wallet setup", "set up wallet"],
    "early_benefits": ["early", "register early", "why now", "why join now", "founding member", "founding", "early registration", "early bird", "first mover", "benefits of joining early"],
    "launch_phases": ["phase 1", "phase 2", "phase 3", "phases", "roadmap", "timeline", "when", "dates", "launch date", "when does it start", "launch schedule"],
    "liquidity_pools": ["liquidity", "liquidity pool", "lp", "trading", "dex", "exchange", "trade hls", "pool"],
    "hls_token_details": ["supply", "total supply", "100 million", "token pool", "settlement pool", "distribution", "emergency reserve", "issuance", "token issuance", "how many tokens", "tokenomics"],
    "flowline": ["flowline", "flow line", "animation", "how it works visually", "the line", "electricity", "glowing line", "activation flow", "show me how it works"],
    "burn_mechanics": ["burn", "burning", "deflationary", "reduce supply", "token burn", "burned", "burn mechanism", "supply reduction"],
    "penalties": ["penalty", "penalties", "penalize", "forfeit", "forfeited", "early exit", "break lock", "punishment", "surcharge", "rapid conversion", "dormant"],
    "internal_marketplace": ["marketplace", "buy with hls", "spend hls", "internal market", "buy gold with tokens", "buy certificates", "purchase with hls", "use tokens"],
    "stablecoin_exchange": ["convert", "conversion", "swap", "exchange", "hls to usdc", "hls to usdt", "stablecoin exchange", "cash out", "sell tokens", "sell hls", "convert to dollars"],
    "genesis_pool": ["genesis", "genesis pool", "genesis contract", "first 10", "seed", "initial", "50000", "$50,000", "founding pool", "starting pool", "how it starts"],
    "bonus_structure": ["bonus", "bonuses", "loyalty", "milestone", "growth bonus", "upgrade bonus", "Contract Upgrade Reward", "gold accumulation", "compound"],
    "token_value_drivers": ["value driver", "what drives value", "why go up", "price increase", "appreciation", "token value", "supply and demand", "scarcity", "deflationary pressure"],
    "qr_code_sharing": ["qr", "qr code", "share code", "share link", "scan", "my code", "my qr", "network code", "how do i share", "share helios", "send my link", "business card", "invite link", "personal link", "registration link"],
}


class AskHelios:
    """
    The Voice of HELIOS.
    Male. Calm. Grounded. Kitchen-table money talk.
    Explains gold, crypto, and the smart contract math like a real person.
    Never sells. Never hypes. Shows the math and lets you decide.
    """

    def __init__(self, db_session=None):
        self.db = db_session
        self.conversation_history = []

    # ═══ Main Interface ══════════════════════════════════════════

    def ask(self, question: str, member_id: str = None) -> dict:
        """Answer any question about HELIOS. Knowledge base first, AI fallback."""
        question_lower = question.lower().strip()

        self.conversation_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        grounded_context, grounded_sources = build_context_block(question)

        if grounded_sources:
            response = self._ask_ai(question, member_id, grounded_context, grounded_sources)
        else:
            # Knowledge base first (instant, no API call)
            kb_answer = self._search_knowledge_base(question_lower)
            if kb_answer:
                response = {
                    "answer": kb_answer,
                    "source": "knowledge_base",
                    "confidence": "high",
                    "follow_up": self._suggest_follow_up(question_lower),
                    "references": []
                }
            else:
                response = self._ask_ai(question, member_id)

        if grounded_sources and "references" not in response:
            response = {
                **response,
                "references": [
                    {
                        "title": source["title"],
                        "path": source["path"],
                        "github_url": source["github_url"],
                    }
                    for source in grounded_sources
                ]
            }

        if member_id and self.db:
            response["personal_context"] = self._get_member_context(member_id)

        self.conversation_history.append({
            "role": "assistant",
            "content": response["answer"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return response

    def get_quick_answers(self) -> list:
        """Pre-built questions for the interface."""
        return [
            {"question": "How does the token offering work?", "icon": "🚀"},
            {"question": "Why should I register early?", "icon": "⏰"},
            {"question": "What are trustlines?", "icon": "🔗"},
            {"question": "What is Helios?", "icon": "☀️"},
            {"question": "How do I earn?", "icon": "💰"},
            {"question": "What are the contract options?", "icon": "📊"},
            {"question": "How does propagation work?", "icon": "📈"},
            {"question": "How is the protocol structured?", "icon": "🔍"},
            {"question": "How does the smart contract engine work?", "icon": "⚙️"},
            {"question": "Show me the growth math", "icon": "💵"},
            {"question": "How does the gold backing work?", "icon": "🏆"},
            {"question": "How do token burns work?", "icon": "🔥"},
            {"question": "What are the penalties?", "icon": "⚠️"},
            {"question": "How does the internal marketplace work?", "icon": "🏪"},
            {"question": "How do I convert to stablecoins?", "icon": "💱"},
            {"question": "What is the genesis pool?", "icon": "🌱"},
            {"question": "What about the liquidity pools?", "icon": "🌊"},
            {"question": "How do I share my QR code?", "icon": "📱"},
        ]

    # ═══ Knowledge Base Search ═══════════════════════════════════

    def _search_knowledge_base(self, question: str) -> str:
        best_match = None
        best_score = 0

        for topic, keywords in TOPIC_MAP.items():
            score = sum(1 for kw in keywords if kw in question)
            if score > best_score:
                best_score = score
                best_match = topic

        if best_match and best_score > 0:
            return HELIOS_KNOWLEDGE[best_match]
        return None

    # ═══ AI Fallback ═════════════════════════════════════════════

    def _ask_ai(self, question: str, member_id: str = None, grounded_context: str = "", grounded_sources: list | None = None) -> dict:
        api_key = HeliosConfig.AI_API_KEY
        grounded_sources = grounded_sources or []

        if not api_key:
            grounded = build_grounded_fallback(question)
            if grounded:
                return {
                    "answer": grounded["answer"],
                    "source": "grounded_fallback",
                    "confidence": grounded["confidence"],
                    "follow_up": self._suggest_follow_up(question.lower()),
                    "references": grounded["references"],
                }
            return {
                "answer": self._smart_fallback(question),
                "source": "fallback",
                "confidence": "medium",
                "follow_up": self._suggest_follow_up(question.lower()),
                "references": [],
            }

        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            system_prompt = self._build_system_prompt(member_id, grounded_context)
            messages = [{"role": "system", "content": system_prompt}]

            for msg in self.conversation_history[-HeliosConfig.AI_MAX_CONTEXT_TURNS:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            response = client.chat.completions.create(
                model=HeliosConfig.AI_MODEL,
                messages=messages,
                temperature=HeliosConfig.AI_TEMPERATURE,
                max_tokens=500
            )

            return {
                "answer": response.choices[0].message.content.strip(),
                "source": "ai",
                "confidence": "high",
                "follow_up": self._suggest_follow_up(question.lower()),
                "references": [
                    {
                        "title": source["title"],
                        "path": source["path"],
                        "github_url": source["github_url"],
                    }
                    for source in grounded_sources
                ],
            }

        except Exception:
            grounded = build_grounded_fallback(question)
            if grounded:
                return {
                    "answer": grounded["answer"],
                    "source": "grounded_fallback",
                    "confidence": grounded["confidence"],
                    "follow_up": self._suggest_follow_up(question.lower()),
                    "references": grounded["references"],
                    "note": "AI unavailable. Using build-aware source context.",
                }
            return {
                "answer": self._smart_fallback(question),
                "source": "fallback",
                "confidence": "medium",
                "follow_up": self._suggest_follow_up(question.lower()),
                "references": [],
                "note": "AI unavailable. Using protocol knowledge base."
            }

    def _build_system_prompt(self, member_id: str = None, grounded_context: str = "") -> str:
        """System prompt with smart contract protocol context and voice rules."""
        context = (
            "You are Helios — the voice of the protocol. "
            "Male. Calm. Grounded. Authoritative. Like a smart friend "
            "explaining money at a kitchen table.\n\n"
            "WHAT HELIOS IS:\n"
            "An XRPL-first activation, wallet, treasury, and certificate platform with a simplified recommended launch route. "
            "The current source of truth is the repository, mirrored docs, rebuttal documents, and build-aware handoff portal.\n\n"
            "VOICE RULES:\n"
            "- Talk like a real person explaining money to another adult\n"
            "- Use plain language. No crypto jargon unless asked.\n"
            "- Be direct. Be honest. No hype.\n"
            "- Distinguish clearly between what exists now, what is hybrid, and what is still pending\n"
            "- Never guarantee income, performance, valuation, or launch timing\n"
            "- If the build is not proven live for a claim, say that directly\n"
            "- Prefer the simplified route unless there is a strong reason otherwise\n\n"
            "PROTOCOL FACTS:\n"
            f"- Token: {HeliosConfig.TOKEN_NAME} ({HeliosConfig.TOKEN_SYMBOL})\n"
            f"- Total supply: {HeliosConfig.TOKEN_TOTAL_SUPPLY:,} (FIXED)\n"
            f"- Recommended chain posture: XRPL-first\n"
            f"- Treasury path: receipts, evidence, and anchoring workflows exist\n"
            f"- Certificates: XRPL XLS-20 posture in launch docs\n"
            f"- Default route: simplified\n"
        )
        if grounded_context:
            context += (
                "\nCURRENT BUILD CONTEXT — USE THIS AS THE PRIMARY SOURCE OF TRUTH:\n"
                f"{grounded_context}\n\n"
                "When answering, use the supplied context first. If something in older messaging conflicts with the context, follow the current build context."
            )
        if member_id:
            context += f"\nThe person asking holds identity: {member_id}\n"
        return context

    def _smart_fallback(self, question: str) -> str:
        """Fallback when AI is unavailable."""
        grounded = build_grounded_fallback(question)
        if grounded:
            return grounded["answer"]

        q = question.lower()

        if any(w in q for w in ["price", "worth", "value", "market"]):
            return (
                "Helios doesn't make price projections. The protocol holds "
                "physical gold, issues certificates backed by real assets, "
                "and allocates through a published smart contract formula. "
                "Value comes from the protocol and the gold — not speculation."
            )

        if any(w in q for w in ["how much", "earn", "money", "make", "income", "paid"]):
            return (
                "Your allocations depend on your contract and your connections. "
                "At the $100 contract, you receive $22.50 per direct connection. "
                "The smart contract engine distributes allocations from everyone in your mesh — "
                "across the full connection depth. "
                "Results depend on effort and connection growth."
            )

        if any(w in q for w in ["safe", "secure", "security", "trust"]):
            return (
                "The treasury holds physical gold with receipts on XRPL. "
                "The allocation formula is published — anyone can verify. "
                "There are no admin override keys. The fee split is hardcoded. "
                "No one can change the rules or drain the pools. "
                "Verify the gold. Verify the math. That's all I ask."
            )

        if any(w in q for w in ["help", "support", "problem", "issue"]):
            return (
                "I can explain the contracts, the 3 allocation channels, "
                "the smart contract propagation, the formula, the gold backing, "
                "the crypto access, staking, or how to get started. "
                "What would you like to know?"
            )

        if any(w in q for w in ["gold", "metal", "treasury"]):
            return (
                "15% of every activation fee buys physical gold through APMEX. "
                "As the protocol grows, gold purchases scale proportionally. "
                "Metal Vault Receipts are NFTs on XRPL. "
                "Proof of reserves is always public.\n\n"
                "Want to know more about the certificates or crypto access?"
            )

        return (
            "Helios is currently best understood as an XRPL-first launch repository with onboarding, funding, wallet, treasury, handoff, and build-verification rails.\n\n"
            "Could you ask that one more specifically? I can answer from the current docs, rebuttal material, operator guides, and build files."
        )

    # ═══ Helpers ═════════════════════════════════════════════════

    def _suggest_follow_up(self, question: str) -> list:
        if any(w in question for w in ["offering", "presale", "token sale", "buy tokens", "founding window"]):
            return ["Why should I register early?", "How do burns work?"]
        elif any(w in question for w in ["burn", "deflationary", "supply reduction"]):
            return ["What are the penalties?", "What drives token value?"]
        elif any(w in question for w in ["penalty", "forfeit", "surcharge"]):
            return ["How does staking work?", "How do burns work?"]
        elif any(w in question for w in ["marketplace", "buy with hls", "spend"]):
            return ["How does the stablecoin exchange work?", "How do burns work?"]
        elif any(w in question for w in ["convert", "swap", "exchange", "cash out", "sell"]):
            return ["What about the internal marketplace?", "What are the penalties?"]
        elif any(w in question for w in ["genesis", "seed", "first 10", "founding pool"]):
            return ["How does the token offering work?", "What drives token value?"]
        elif any(w in question for w in ["trustline", "wallet", "xumm", "lobstr"]):
            return ["How does the token offering work?", "What are the contracts?"]
        elif any(w in question for w in ["early", "founding", "register early", "why now", "benefits"]):
            return ["How does the token offering work?", "How does propagation work?"]
        elif any(w in question for w in ["phase", "roadmap", "timeline", "dates", "when"]):
            return ["Why should I register early?", "What about the liquidity pools?"]
        elif any(w in question for w in ["liquidity", "pool", "dex", "trade"]):
            return ["How does the token offering work?", "Show me the growth math"]
        elif any(w in question for w in ["join", "start", "sign", "activate", "entry"]):
            return ["How does the token offering work?", "What are the contracts?"]
        elif any(w in question for w in ["contract", "$100", "$250", "$500", "$1000", "$5000"]):
            return ["How do I earn?", "Why should I register early?"]
        elif any(w in question for w in ["earn", "paid", "money", "income"]):
            return ["How does propagation work?", "Show me the growth math"]
        elif any(w in question for w in ["propagation", "signal", "mesh", "structure"]):
            return ["Show me the growth math", "How does the smart contract engine work?"]
        elif any(w in question for w in ["mlm", "scam", "pyramid", "trust", "rug", "legit"]):
            return ["What's the protocol integrity?", "How does the gold backing work?"]
        elif any(w in question for w in ["gold", "metal", "treasury", "vault"]):
            return ["What crypto can I access?", "How does staking work?"]
        elif any(w in question for w in ["crypto", "btc", "eth", "xrp", "stablecoin"]):
            return ["How does staking work?", "How does the gold backing work?"]
        elif any(w in question for w in ["staking", "stake", "lock", "bonus"]):
            return ["Show me the growth math", "How do I join?"]
        elif any(w in question for w in ["certificate", "nft"]):
            return ["How does the gold backing work?", "How does staking work?"]
        elif any(w in question for w in ["formula", "depth", "engine", "smart contract"]):
            return ["How does propagation work?", "What are the contracts?"]
        elif any(w in question for w in ["scenario", "projection"]):
            return ["How does staking work?", "What about mixed contracts?"]
        elif any(w in question for w in ["token", "supply", "hls", "issuance"]):
            return ["How does the token offering work?", "What about the liquidity pools?"]
        elif any(w in question for w in ["founder", "team", "who"]):
            return ["What are the protocol rules?", "How does verification work?"]
        else:
            return ["How does the token offering work?", "What are the contracts?"]

    def _get_member_context(self, member_id: str) -> dict:
        try:
            from models.member import Member
            member = self.db.query(Member).filter_by(helios_id=member_id).first()
            if member:
                return {
                    "member_since": member.created_at.isoformat(),
                    "display_name": member.display_name,
                    "node_state": member.node_state,
                    "bond_count": member.bond_count
                }
        except Exception:
            pass
        return {}
