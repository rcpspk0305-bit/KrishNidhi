# Concepts

> Shared domain vocabulary for this project — entities, named processes, and status concepts with project-specific meaning. Seeded with core domain vocabulary, then accretes as ce-compound and ce-compound-refresh process learnings; direct edits are fine. Glossary only, not a spec or catch-all.

## Entities

### Microcontroller Node
A physical or simulated edge computing unit that interfaces directly with environmental sensors and relays.
*Avoid:* Client, worker

A Microcontroller Node is the sole physical master of attached actuators. It executes local safety policies independently of network connectivity, periodically transmits environmental observations, and polls for pending actuation requests.

### Plant Profile
The target environmental and physiological preferences assigned to a specific plant or crop.
*Avoid:* Preset, crop config

A Plant Profile defines the ideal ranges for ambient temperature, humidity, and soil hydration. The agronomic engine evaluates incoming telemetry against the active Plant Profile to determine stress levels and recommend corrective interventions.

### Telemetry Packet
A structured bundle of time-synchronized environmental and status observations emitted by a sensor node.
*Avoid:* Metric, event

Each packet captures ambient climate, soil moisture percentage, motion presence, and current actuation state. Telemetry Packets are immutable once recorded and form the basis for historical trend analysis and alert generation.

### Actuation Command
An explicit request dispatched to an edge node to transition an actuator to a target state.
*Avoid:* Instruction, remote call

Commands have a strict time-to-live after creation. If a node fails to retrieve and acknowledge a command before its expiration, the command transitions to expired without physical execution.

## Processes

### State Reconciliation
The two-phase synchronization mechanism guaranteeing that a remote user request corresponds to a physically executed hardware state.
*Avoid:* Command sync, round-trip

An actuation request first enters a pending state on the server. The node subsequently retrieves the request, evaluates local physical safety constraints, energizes the actuator, and returns an acknowledgment that transitions the server-side state to confirmed.

### Hardware Safeguard Watchdog
An edge-enforced execution limit that halts physical actuation regardless of network commands or software state.
*Avoid:* Relay timer, circuit breaker

The watchdog enforces maximum continuous runtime and mandatory rest intervals between actuations. It operates at the microcontroller level to prevent hardware burnout, soil over-saturation, and flooding.

### Agronomic Health Evaluation
The deterministic rule-based calculation that assesses plant vitality from real-time and historical microclimate telemetry.
*Avoid:* AI prediction, crop score

The evaluation balances moisture deficit, thermal stress, and transpiration demand against the active plant profile, producing an explainable vitality index and prioritized cultivation recommendations.

## Status Concepts

### Irrigation Mode
The operational policy governing actuator control on a microcontroller node.
*Avoid:* Operation type, pump mode

Nodes operate in one of three mutually exclusive modes: autonomous regulation based on calibrated moisture thresholds, direct manual control from buttons or web commands, or total safety lockout.

### Vapor Pressure Deficit (VPD)
The difference between the pressure exerted by water vapor inside saturated plant leaves and the ambient air.
*Avoid:* Leaf humidity, air dryness

VPD serves as the primary indicator of transpiration stress. Low values indicate stagnant transpiration and disease vulnerability, while elevated values indicate excessive moisture loss and stomatal closure.

### Telemetry Source
The designated origin providing observations to the operations dashboard.
*Avoid:* Data mode, stream mode

Observations may originate from an active physical microcontroller node transmitting over the local network or an in-memory virtual hardware simulator used for demonstration and testing.

## Flagged Ambiguities

- "Pump state" had been used for both requested intent and confirmed physical relay closure — these are distinct and separated into Requested State (pending) and Confirmed State (acknowledged).
- "Telemetry mode" was previously used to describe both hardware irrigation policies and frontend simulator feeds — "Irrigation Mode" now designates hardware behavior, while "Telemetry Source" designates the data feed origin.
