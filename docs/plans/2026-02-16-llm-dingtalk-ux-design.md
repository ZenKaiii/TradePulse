# TradePulse LLM + DingTalk UX Design

## Context

Users reported two primary issues: DingTalk was rendering markdown as plain text, and event analysis was still rule-template output instead of real LLM reasoning.

## Goals

- Use DingTalk markdown payload for readable output.
- Enable true LLM-generated Chinese analysis.
- Support Bailian primary and Gemini fallback.
- Support configurable model/base URL/temperature/timeout via GitHub Variables.
- Apply mixed detail strategy: top 5 detailed, next 5 brief.

## Non-Goals

- No deep article extraction in this phase.
- No trading signal engine.

## Key Decisions

- Keep rule-based scoring as fallback when LLM fails.
- Add structured JSON prompt/parse for deterministic integration.
- Add beginner-friendly phrasing and lightweight emoji markers.

## Data/Provider Notes

- Bailian via OpenAI-compatible endpoint.
- Gemini via generateContent endpoint.
- Provider selection: forced config or auto (Bailian -> Gemini).
