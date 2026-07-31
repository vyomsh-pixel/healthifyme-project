# Health.io Project Context

This document summarizes the current state, recent fixes, and architectural decisions made for the Health.io project. It is intended to serve as a high-level context briefing for AI collaborators (like Kimi) joining the project.

## 1. Core Architecture & Migration State
- **Backend Framework**: Python (FastAPI).
- **Frontend Framework**: React (Vite).
- **Database**: Migrated from ephemeral SQLite to **PostgreSQL (Supabase)** to survive Render's server sleep cycles.
  - Required updating ~30 raw SQL queries (`?` -> `%s`).
  - Auto-incrementing IDs updated to `SERIAL`.
  - SQLite `lastrowid` logic replaced with Postgres `RETURNING id`.
- **Authentication**: Bearer tokens + `localStorage` (chosen over `httpOnly` cookies due to complexity overhead vs actual XSS risk, which is actively managed in the markdown rendering).

## 2. Completed Backend Features & Fixes
- **Rate Limiter Hardening**: 
  - Fixed a fail-open silent bug where the `rate_limits` table was missing from `initialise_database()`.
  - Corrected key derivation so limits apply correctly per-user rather than globally.
  - *Known Caveat*: The in-memory rate limiter strategy works perfectly for a 1-worker setup on Render, but will partition if uvicorn spawns >1 worker. Documented for project grading.
- **Security & Schema Validation**:
  - Implemented strong password complexity (min 8 chars, 1 digit, 1 special character) strictly on `RegisterRequest`, deliberately avoiding `LoginRequest` to prevent locking out existing legacy users.
  - Enforced maximum string length limits on Base64 image payload uploads.
- **5-Tier BMI Logic**:
  - Expanded standard BMI ranges to include extreme underweight checks (`< 16` and `< 18.5`).
  - Added strict Pydantic bounds (`weight_kg` `ge=20` to `le=400`, `height_cm` `ge=80` to `le=250`) directly on `BMIRequest` to mirror frontend HTML5 constraints.
  - Added copy text to explicitly flag extreme low BMI results (`< 16`) as potential data-entry typos to prevent medical alarmism over bad inputs.

## 3. Completed Frontend Polish
- **BMI Dashboard UI**: 
  - Status badges ("Moderate Risk", "High Risk") redesigned with a neon glow effect, bright white text, and explicitly constrained using `white-space: nowrap; flex-shrink: 0; width: max-content;` to prevent text-wrapping bugs in flex containers.
  - Implemented a "Stale Result Indicator": If a user modifies their inputs *after* saving a BMI, the result card instantly dims (`opacity: 0.4`) and clears the success notice, preventing screenshots of mismatching data.
- **Mobile Responsiveness**: 
  - Audited existing breakpoints (`max-width: 850px` and `480px`).
  - Replaced native browser number spinners (up/down arrows) with custom CSS.
  - Expanded touch tap-targets (e.g. `padding: 0.9rem 1rem`) across all inputs and dropdowns to meet the 44px mobile usability minimum.

## 4. AI Vision Integration (Food & Skin Scanners)
- Uses **Gemini 2.5 Flash** for image processing.
- **Fixed Hardcoded MIME Types**: The backend originally hardcoded `mime_type="image/jpeg"` for all uploads. We rewrote this to dynamically parse the actual MIME type (e.g., `image/png`, `image/webp`) from the `data:image/...;base64,` prefix payload sent by the frontend's `FileReader`.
- **Enforced JSON Mode**: 
  - Previously relied on brittle Markdown regex stripping to parse AI outputs.
  - We updated both `analyze_food_image` and `analyze_skin_image` to explicitly use `types.GenerateContentConfig(response_mime_type="application/json")`, forcing the model to output strict JSON.
- **Strict Endpoint Validation**: 
  - Upgraded the `/analyze-skin` route to strictly validate that the AI response dictionary contains both `{"concerns", "summary"}` using an `issubset` check. This prevents silent frontend rendering failures if the AI omits keys, mirroring the exact strictness of the `/analyze-food` route.

## Next Steps
- Testing the end-to-end flow of the **Food Scanner** and **Skin Scan** on the live deployment.
- Moving on to wiring the **Analytics & History** data visualizations, ensuring they effectively stitch together the activity from the AI planners and scanners.
