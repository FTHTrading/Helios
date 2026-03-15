# Helios AI Knowledge System

## Purpose

Ask Helios should answer from the actual build, not from generic marketing copy.

## Source priority

The AI system should prioritize:

1. mirrored handoff documents
2. operator and runbook documents
3. review rebuttal and coverage docs
4. selected build files and API routes
5. model synthesis only after source context is loaded

## Current answer sources

The current build-aware AI system is designed to use:

- `START.md`
- white paper and operator docs
- tokenomics guide
- review rebuttal docs
- launch blueprint and runbook
- selected build files such as `app.py`, `api/routes.py`, `config.py`, and `core/handoff.py`
- GitHub repository references

## Operator rule

Do not store live model credentials in code.

Set them through environment variables only.

## Recommended environment

- `HELIOS_AI_API_KEY`
- `HELIOS_AI_MODEL`

## What a good answer looks like

A good Ask Helios answer should:

- answer the question directly
- stay aligned to the current build
- separate what exists from what is pending
- reference source docs or code paths when possible
- avoid hype and unsupported certainty

## Final position

The AI system is part of the operator and stakeholder support layer. Its job is not to invent a story. Its job is to explain the current Helios build accurately.
