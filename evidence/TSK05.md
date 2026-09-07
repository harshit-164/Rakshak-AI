# TSK05 — Hosted baseline and grounding evidence

State: in progress; adapter contract passes, live Gemini smoke call is pending.

Implemented paths include the replaceable adapter contract, Gemini Interactions adapter,
versioned prompt, curated reference bundle, and immutable hosted manifest. The manifest
SHA-256 is `894d9bee803278d590cc289912007d8e1052b47a7215750d9b3247354e6927e4`.

Verified locally:

- The model receives normalized narrative and optional activity only; site, date, source
  outcome, and server-owned metadata are excluded.
- Tests inspect the hosted request, validate structured output, reject fabricated quotes and
  passage IDs, map validated output to the full API result, and preserve provider failure as
  job failure.
- Prompt SHA-256: `c0506c9714afa05555b134e64ae65f95bc52040e135f904af4923fe4a2ca5440`.
- Reference bundle SHA-256: `c251c9dfd7b7bf488d793a08cacf7a583ab2af7c4b67eb72a39f3ad93b2bc4ef`.

Acceptance not yet met:

- No `GEMINI_API_KEY` was supplied, so no live provider response, latency, token usage, or
  provider-side schema compatibility has been claimed.
