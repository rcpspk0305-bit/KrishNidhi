# Plant workspace verification

The primary interface is shared by `/`, `/dashboard`, and `/plant-monitor`. Existing secondary pages are retained outside the main navigation.

## Evidence
- TypeScript check passed.
- Production webpack build passed, including static generation of all routes. The restricted sandbox initially blocked generated build-directory creation; the build passed with normal filesystem access.
- Scoped ESLint checks passed before final review.
- Three Node regression tests passed for UTC parsing, freshness boundaries, and merging persisted history with newer live samples, including an India-local timezone.
- Browser inspection at the default desktop viewport (1280px) and a 390px mobile viewport showed no horizontal overflow.
- Real offline state: empty readings, unavailable pump state, disabled controls, connection help, and working chart filters.
- Isolated API-fixture checks: populated charts, mode command pending and applied, pump pending and confirmed, rejected mode preserves the confirmed mode, missing acknowledgment becomes unconfirmed at expiry, alert acknowledgment, and foreign-device SSE events ignored.
- Review regressions: an acknowledgment arriving before the command POST response is retained; newer SSE readings survive a delayed older poll; failed history requests show an unavailable/retry state; a cold load with repeated SSE events during delayed REST calls still initializes device status and historical records.

`desktop.png` shows the final local preview against the existing backend, with the device offline and no sensor readings. Files with `fixture` in their names use the explicit browser-test API in `frontend/tests/fixtures/plant-api.mjs`; those screenshots are not live sensor or physical-hardware evidence. The fixture writes no database and actuates no hardware.

## Commands
From `frontend/`:

```powershell
rtk proxy node --experimental-strip-types --test tests/plant-state.test.mjs
rtk proxy node node_modules/typescript/bin/tsc --noEmit
rtk proxy node node_modules/next/dist/bin/next build --webpack
rtk npm run dev
```

The fixture is never imported by the app. It defaults to loopback port 8000 and accepts `PLANT_TEST_API_PORT` for isolation. If a real backend is running, use another port and a separate frontend with `NEXT_PUBLIC_API_URL` pointing to the fixture and `NEXT_BUILD_DIR=.next-fixture`; never send fixture control scenarios to a real backend. Stop the fixture after testing. Final cold-start verification used fixture port 8001 and frontend port 3003; both were stopped afterward.

## Limits
No physical ESP8266, relay, water-flow, or production-authentication validation was performed. Existing backend/firmware security, history-query sampling, and pump safety behavior remain separate from this frontend redesign. Existing history API responses are capped at 500 samples and do not constitute a complete archive.
