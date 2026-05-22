---
name: cloud-vm-tag-maintenance
description: "Use when updating metadata/tags on cloud virtual machines without changing power state. Covers safe preflight, tag-only operations, verification, and provider-specific references such as Tencent Cloud CVM LastStoppedAt updates."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [devops, cloud, vm, tags, tencent-cloud, safety]
    related_skills: [ssh-host-access-probing]
---

# Cloud VM Tag Maintenance

## Overview

Use this skill for small cloud VM metadata changes where the user explicitly wants a tag or label updated and does not want the VM started, stopped, rebooted, resized, or otherwise mutated.

The main rule is to separate metadata APIs from lifecycle APIs. Read current state first, apply only the metadata/tag call, then verify both the tag value and the VM power state afterward.

Provider-specific command notes belong under `references/`; keep this SKILL.md focused on the cross-provider workflow.

## When to Use

- Updating a tag/label such as `LastStoppedAt`, `Owner`, `Team`, `Environment`, or `AutoShutdown`.
- Touching metadata on stopped cloud VMs while preserving STOPPED state.
- Auditing whether cloud resource tags match a table provided by the user.
- Repeating a safe, tag-only maintenance task across multiple cloud instances.

Do not use this for:

- Starting/stopping/rebooting VMs.
- OS-level changes inside the VM.
- Security group, network, disk, image, or instance-shape changes.
- Cost/reservation changes unless the governing provider-specific skill says so.

## Safety Workflow

1. Give a short upfront estimate if this is operational work for the user.
2. Identify the target provider, region, instance IDs, and desired tag key/value.
3. Compute dates with a tool; do not rely on mental current-date recall.
4. Verify the instances exist and record their current lifecycle state before changing anything.
5. Confirm the relevant tag key exists or choose the provider's add/update tag API intentionally.
6. Use only tag/metadata APIs. Avoid lifecycle verbs such as start, stop, reboot, reset, resize, reinstall, or terminate.
7. Verify after the update:
   - instance IDs/names match the requested targets
   - tag value is updated
   - lifecycle state remains unchanged, especially STOPPED when the user requested no power-on
8. Report concise before/after facts and any API request IDs if useful.

## Credential and Logging Hygiene

- Avoid commands that print full configured credentials, such as broad `configure list`, unless there is no safer alternative.
- Prefer targeted identity checks that return account/user identity without secret material.
- If a command accidentally prints credentials, do not repeat them in the final answer. Warn the user that local terminal/session logs may contain secret material and recommend rotation when appropriate.
- Do not save cloud SecretIds, SecretKeys, tokens, or account secrets into memory, skills, docs, or command transcripts.

## Provider References

- Tencent Cloud CVM tag updates: see `references/tencent-cloud-cvm-tags.md`.

## Common Pitfalls

1. Treating `LastStoppedAt` as a VM lifecycle field. In many setups it is a custom tag/label, not a provider-managed stop timestamp. Inspect tags first.
2. Using start/stop APIs just to refresh a date tag. If the user says not to power on the VM, update the metadata only.
3. Losing region/account context. Cloud instance IDs are not enough; include provider region and account/tenant in reads and writes.
4. Printing credentials during CLI discovery. Prefer `GetCallerIdentity`-style calls over full config dumps.
5. Reporting success after the update call only. Always re-read the instances to verify both metadata and power state.

## Verification Checklist

- [ ] Date/tag value was computed or confirmed with a tool.
- [ ] Targets were read before mutation and matched user-provided IDs/names.
- [ ] Only tag/metadata APIs were called.
- [ ] After read shows expected tag value.
- [ ] After read shows lifecycle state unchanged.
- [ ] Final response omits secrets and mentions any credential exposure risk if it occurred.
