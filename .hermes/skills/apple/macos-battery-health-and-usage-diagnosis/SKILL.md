---
name: macos-battery-health-and-usage-diagnosis
description: Diagnose macOS laptop battery health, compare current capacity to normal, estimate realistic runtime, and inspect recent battery/power history around a requested time window.
---

# macOS Battery Health and Usage Diagnosis

Use when the user asks:
- whether their MacBook battery is healthy,
- how much capacity has degraded versus normal,
- how many hours of use remain,
- whether a recent drain pattern is normal,
- or to inspect battery/power history around a specific time.

This workflow is for live macOS inspection using built-in power tools plus Apple model specs.

## Goal
Produce a grounded battery assessment with:
1. current battery health,
2. degradation versus design capacity,
3. practical runtime expectations,
4. judgment on whether a reported drain rate is normal,
5. and a timeline of recent power/battery events for a requested period.

## Core commands

### 1) Current high-level health
Run:
```bash
pmset -g batt
system_profiler SPPowerDataType
system_profiler SPHardwareDataType
```
Key fields:
- `State of Charge (%)`
- `Condition`
- `Maximum Capacity`
- `Cycle Count`
- model identifier and chip

### 2) Raw battery telemetry
Run:
```bash
ioreg -r -c AppleSmartBattery
```
Important fields to read from the output:
- `DesignCapacity`
- `AppleRawMaxCapacity`
- `AppleRawCurrentCapacity`
- `CycleCount`
- `Voltage`
- `Amperage`
- `TimeRemaining`

Do not rely on `ioreg -a | plutil -convert json` here; it can fail with:
- `Invalid object in plist for JSON format`

Use the plain-text `ioreg -r -c AppleSmartBattery` output instead.

## Capacity and degradation calculations
Use both views and explain the distinction:

### User-facing health
From `system_profiler SPPowerDataType`:
- `Maximum Capacity: 89%`
This is usually the main user-facing answer for “how much has it degraded?”

### Raw ratio cross-check
Compute:
```text
raw_health = AppleRawMaxCapacity / DesignCapacity * 100
raw_loss = 100 - raw_health
```
This can differ slightly from the macOS health percentage because Apple applies calibration and smoothing.

When reporting:
- Treat `Maximum Capacity` as the main answer.
- Mention the raw ratio as a cross-check if it materially differs.

## Model-rated runtime baseline
Identify the exact Mac model from `system_profiler SPHardwareDataType`, then fetch Apple’s spec page if needed.

Example pattern:
```bash
curl -L -A 'Mozilla/5.0' https://support.apple.com/kb/<spec-page> -o /tmp/spec.html
```
Then search the HTML for battery claims such as:
- `Up to 11 hours wireless web`
- `Up to 17 hours Apple TV app movie playback`

For the 14-inch MacBook Pro M1 Pro / MacBookPro18,3 (Apple page SP854), the page lists:
- `Up to 17 hours Apple TV app movie playback`
- `Up to 11 hours wireless web`
- `70-watt-hour lithium-polymer battery`

## Runtime estimation
Estimate realistic full-charge runtime by scaling Apple’s rated runtime by health percentage:
```text
estimated_full_runtime = rated_runtime * health_fraction
```
Estimate current remaining runtime from current charge as:
```text
estimated_now_runtime = rated_runtime * health_fraction * charge_fraction
```
Present these as rough expectations, not guarantees.

Recommended wording:
- light web/doc work: near the scaled wireless-web figure
- video playback: near the scaled playback figure
- development/video calls/high brightness: often significantly lower

## Judging whether an observed drain rate is normal
If the user says something like “80% to 68% in 1 hour”, calculate:
```text
drain_per_hour = 12%
projected_full_runtime = 100 / 12 = 8.33 hours
```
Compare that to the health-adjusted light-use baseline.

Interpretation guidance:
- If projected full runtime is only modestly below the scaled web baseline, it is usually normal for real-world use.
- Meeting/travel conditions commonly increase drain because of:
  - high brightness
  - unstable Wi‑Fi / hotspot use
  - Zoom / Meet / Slack / Telegram
  - Bluetooth audio
  - browser media and transient CPU load

A result around 8.3 hours on a machine whose health-adjusted light baseline is around 9.8 hours is usually still normal for mobile meeting use.

## Inspecting recent battery/power history
For a requested time window, use:
```bash
pmset -g log | grep -E 'YYYY-MM-DD 1[2-4]:'
```
and, if needed, narrower filters like:
```bash
pmset -g log | grep 'YYYY-MM-DD 13:' | grep 'Using Batt'
```
Useful markers:
- `Using Batt(Charge: X)`
- `Using AC(Charge: X)`
- `Sleep Entering Sleep state`
- `Wake`
- `Display is turned off`
- `Display is turned on`
- assertion summaries from `coreaudiod`, `Google Chrome`, etc.

You can also try unified logs:
```bash
log show --style compact --start 'YYYY-MM-DD HH:MM:SS' --end 'YYYY-MM-DD HH:MM:SS' --predicate '(process == "powerd") || (eventMessage CONTAINS[c] "Battery") || (eventMessage CONTAINS[c] "Wake") || (eventMessage CONTAINS[c] "Sleep")' --info
```
But `pmset -g log` is often the more directly useful source.

## How to interpret history
Normal patterns include:
- battery use followed by display off,
- idle sleep on battery,
- wake due to user activity,
- later connection to AC power,
- `coreaudiod` assertions during calls/media,
- brief Chrome `Video Wake Lock` events.

These do not by themselves indicate abnormal battery drain.

## Important limitations
- `pmset -g log` does not give a perfect minute-by-minute battery percentage trace.
- You may be able to confirm power-source transitions and sampled charge values, but not reconstruct every exact drop such as `80 -> 68` unless the relevant percentages were logged.
- Be explicit when the logs support the usage pattern but do not fully reconstruct the claimed percentage change.

## Suggested reporting format
1. Current status
   - charge, charging/discharging, condition, cycle count, maximum capacity
2. Degradation vs normal
   - main answer from `Maximum Capacity`
   - optional raw-capacity cross-check
3. Expected runtime
   - full-charge estimate
   - current-charge estimate
4. Judgment on reported drain rate
   - normal / somewhat heavy but plausible / clearly abnormal
5. Time-window history
   - concise timeline of batt/AC, sleep/wake, and notable assertions
6. Caveats
   - whether the exact percentage progression was reconstructable

## Pitfalls
- Do not answer from memory; always inspect live system state.
- Do not trust only one source; use both `system_profiler` and `ioreg`.
- Do not overstate `TimeRemaining` while charging; it may refer to time to full, not discharge runtime.
- Do not claim exact historical percentage drops unless the logs explicitly show them.
- Do not treat media/audio/browser wake locks as abnormal by default; they are often the expected explanation.
- `pmset -g pslog` may hang or time out; prefer `pmset -g log` for history unless continuous live sampling is specifically needed.
