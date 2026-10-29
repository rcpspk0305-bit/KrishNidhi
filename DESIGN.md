# KrishiNidhi plant workspace

## Visual system
Operate mode: one quiet, botanical workspace for a single plant. Use an ivory application ground, forest-green navigation and controls, sage surfaces, clay temperature accents, and blue humidity accents. Preserve the KrishiNidhi name. Editorial serif headings sit above compact, readable Geist Sans controls; Geist fonts are served locally.

## Tokens
- Ground: `#f6f7f2`; rail: `#fdfdf9`; surface: `#fffefa`.
- Primary ink: `#263d31`; secondary ink: `#697367`; primary action: `#315b44`.
- Border: `#e3e7dd`; plant surface: `#eeefe3`; care surface: `#edf0e4`.
- Data: moisture `#3e705b`, temperature `#ad6c45`, humidity `#668a9b`.
- Panel radius: 12–14px; controls: 5–8px. Use borders instead of decorative shadows.
- Desktop rail: 222px; main inset: 42px; section gap: 22px. Below 1020px use an icon rail; below 540px use top navigation.

## Interaction
Current sensor values, plant condition, irrigation, history, and alerts are the core jobs. No simulated data or simulator is included in the primary workspace. Decorative botanical photography is not a camera feed. Preserve true loading, offline, missing, stale, pending, rejected, and unconfirmed command states. Never optimistically change a device-reported pump state.

## Implementation authority
`frontend/src/components/plant-monitor/PlantWorkspace.module.css` defines the scoped visual tokens and responsive rules. Existing companion routes retain their older styles. `/`, `/dashboard`, and `/plant-monitor` share one implementation. Accessible labels, keyboard focus, reduced-motion support, and non-color state text are required.
