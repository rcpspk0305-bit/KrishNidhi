# Focused plant workspace redesign

User request: recreate the UI and website with only the important features. Scope and visual choices below are implementation assumptions under the user's instruction to state reasonable assumptions and proceed.

## Design
Use the existing Next.js, TypeScript, Lucide, and Recharts stack. Replace the portal with one plant workspace shared by `/`, `/dashboard`, and `/plant-monitor`. Use warm ivory, forest green, muted terracotta, editorial serif headings, readable sans-serif UI, and generous spacing. The layout has a compact navigation rail, plant overview, three core measurements, irrigation controls, recent history, and a compact care/alerts area. Botanical imagery is decorative, not a camera feed.

## Implementation
1. Add a shared workspace and CSS module; preserve unrelated pages and legacy styles.
2. Use existing REST APIs and a stable SSE subscription, with polling fallback and explicit empty/error/stale states.
3. Preserve device-authoritative pump state. Track pending commands by ID, recognize matching applied/rejected events, show expiry as unconfirmed, and prevent new conflicting requests while waiting.
4. Offer history metric and time-range filters, alert acknowledgment, refresh, and a collapsible connection/help panel.
5. Verify TypeScript, production build, and browser rendering and key interactions when local infrastructure permits. Do not treat simulator or API fixtures as physical-hardware proof.
