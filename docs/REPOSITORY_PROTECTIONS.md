# Repository Protections

Recommended GitHub settings for `Helios-launch`:

## Branch protection for `main`

- require pull requests before merge
- require 1 approving review
- dismiss stale approvals on new commits
- require status checks to pass
- require branches to be up to date
- restrict direct pushes to admins only
- require signed commits if available
- enable secret scanning
- enable push protection
- enable dependency alerts

## Repository settings

- default branch: `main`
- squash merge: enabled
- auto-delete head branches: enabled
- issues: enabled
- discussions: optional
- wiki: disabled unless used operationally

## Required status checks

- `ci / smoke`

## Release hygiene

- tag staging and production releases
- attach launch notes
- record env changes separately from code changes
