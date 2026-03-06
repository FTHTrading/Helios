# Push to Helios-launch

## Option A — reuse this repository as the source

From the current repository root:

1. Commit the launch hardening files.
2. Add the new remote.
3. Push `main`.

Suggested sequence:
- `git add .`
- `git commit -m "Prepare Helios launch repo"`
- `git remote add launch https://github.com/FTHTrading/Helios-launch.git`
- `git push -u launch main`

## Option B — mirror into a fresh clone

- create a fresh local folder named `Helios-launch`
- copy this codebase into it
- initialize git
- push to `https://github.com/FTHTrading/Helios-launch.git`

## After push

Enable:
- branch protection
- secret scanning
- Dependabot
- required CI checks
- CODEOWNERS review flow

Then update the repository description to:

`XRPL-first launch repo for Helios onboarding, funding, wallet activation, and production infrastructure.`
