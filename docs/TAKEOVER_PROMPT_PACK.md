# Takeover Prompt Pack

These are the prompts the incoming team can use to get consistent help while building and launching Helios.

## 1. Choose the right route

Use this prompt:

> Review this repository and confirm whether we should use Route A, Route B, or Route C for launch. Assume we want the fastest path to a credible production launch with the lowest unnecessary complexity.

## 2. Set up GitHub correctly

Use this prompt:

> Apply the GitHub handoff checklist in this repository. Confirm the exact About description, website, topics, branch protections, and required CI settings we should use for the Helios launch repo.

## 3. Align the old Helios page with the repo

Use this prompt:

> Compare the original Helios institutional page with the current repository and rewrite the public-facing copy so it keeps the institutional tone but removes any unsupported live infrastructure claims.

## 4. Prepare the simple launch path

Use this prompt:

> Convert this repo into the Route B simplified launch path. Keep Stripe, Xaman, XRPL, Postgres, and Cloudflare. Defer Redis/Celery and any optional integrations unless they are required.

## 5. Configure environment variables

Use this prompt:

> Generate the exact production environment checklist for Route B using this repository’s `.env.example`, including Stripe, Xaman, XRPL, Postgres, watermark settings, and recommended safe defaults.

## 6. Verify build protection

Use this prompt:

> Check that the hidden build watermark protection is configured correctly. Confirm the build manifest, fingerprint behavior, response headers, and the recommended hidden watermark settings for launch.

## 7. Validate readiness before launch

Use this prompt:

> Run through the Helios readiness process and confirm what still blocks public launch. Use the readiness routes, funding routes, and wallet routes as the source of truth.

## 8. Review activation flow

Use this prompt:

> Review the user activation flow from `/join` to `/activate` to `/web3` to `/dashboard`. Identify anything that would block a first-time user from completing onboarding and recommend the smallest safe fixes.

## 9. Prepare stakeholder summary

Use this prompt:

> Write a short stakeholder-ready summary of Helios that explains what is live now, what is staged, what is deferred, and why the simplified launch route is the recommended default.

## 10. Prepare operator checklist

Use this prompt:

> Turn the operator handoff checklist into an execution plan for launch week. Group tasks into GitHub setup, environment setup, payment validation, wallet validation, and launch-day checks.

## 11. Rewrite page copy safely

Use this prompt:

> Rewrite this Helios marketing page copy so it sounds institutional and strong, but does not overclaim live mainnet, dual-chain, escrow, or operational metrics that are not verified by the current deployment.

## 12. Decide whether to add advanced infrastructure

Use this prompt:

> Based on this repository and the expected launch scope, tell us whether Redis/Celery should be added now or deferred. Focus on practical launch risk, transaction volume, and operational simplicity.

## 13. Final pre-launch review

Use this prompt:

> Perform a final launch-readiness review of this repository as if you were the incoming engineering lead. Identify the current source of truth, the safest launch route, unresolved risks, and the exact next seven actions.

## Recommended default prompts to run first

If the new team only runs three prompts, use these first:

1. route choice prompt
2. GitHub setup prompt
3. final pre-launch review prompt

## Best practice

The new team should use the repository docs in this order:

1. [docs/TAKEOVER_START_HERE.md](docs/TAKEOVER_START_HERE.md)
2. [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)
3. [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md)
4. [docs/TAKEOVER_PROMPT_PACK.md](docs/TAKEOVER_PROMPT_PACK.md)