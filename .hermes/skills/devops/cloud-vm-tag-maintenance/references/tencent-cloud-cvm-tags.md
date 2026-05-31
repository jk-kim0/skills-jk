# Tencent Cloud CVM tag updates

Use this reference when the user asks to update Tencent Cloud CVM tags/metadata while preserving VM power state.

## Preflight

Prefer targeted checks that do not print configured secrets:

```bash
# Current date for tag values when the user says "today".
date +%F

# Confirm identity/account without printing SecretKey.
tccli sts GetCallerIdentity

# Confirm target instances and current state.
tccli cvm DescribeInstances \
  --region ap-seoul \
  --InstanceIds '["ins-...","ins-..."]'
```

Avoid `tccli configure list` for routine discovery because it can print SecretId and SecretKey.

## Adding missing tags

Tencent Cloud `tag TagResources` can associate new tag keys with a CVM resource. In the current `tccli` version used on the user's workstation, `--cli-input-json` must point to a `file://` JSON document; inline JSON is rejected.

```bash
cat >/tmp/cvm-tags.json <<'JSON'
{
  "ResourceList": [
    "qcs::cvm:ap-seoul::instance/ins-..."
  ],
  "Tags": [
    {"TagKey": "AutoShutdown", "TagValue": "false"},
    {"TagKey": "Environment", "TagValue": "dev-seoul"},
    {"TagKey": "Owner", "TagValue": "Jk"},
    {"TagKey": "LastUpdatedAt", "TagValue": "2026-05-30T05:20:01Z"}
  ]
}
JSON

tccli tag TagResources \
  --region ap-seoul \
  --cli-input-json file:///tmp/cvm-tags.json
```

If a key is already present and only the value changes, prefer `UpdateResourceTagValue` below.

Observed Tencent reserved tag-key pitfall: `Project` and `project` were rejected with `InvalidParameter.ReservedTagKey` in the outbound-agent Tencent Cloud account. Do not assume those keys are usable; verify before documenting or applying them.

## Updating an existing tag value

Tencent Cloud `tag UpdateResourceTagValue` updates a tag key already associated with a resource. The resource parameter is a QCS six-segment resource string:

```bash
ACCOUNT_ID=<AccountId from tccli sts GetCallerIdentity>
REGION=ap-seoul
TAG_KEY=LastStoppedAt
TAG_VALUE=2026.05.22

for id in ins-6imdjii9 ins-9bxjgppx ins-d3faf5wf ins-7pjaif5l; do
  tccli tag UpdateResourceTagValue \
    --region "$REGION" \
    --TagKey "$TAG_KEY" \
    --TagValue "$TAG_VALUE" \
    --Resource "qcs::cvm:${REGION}:uin/${ACCOUNT_ID}:instance/${id}"
done
```

Notes:

- `AccountId` from `sts GetCallerIdentity` worked for the `uin/<id>` segment in this setup.
- The API returns only a request ID; it does not prove the visible instance state/tag without a follow-up read.
- If the tag key may not exist, use the provider's tag association API intentionally instead of assuming `UpdateResourceTagValue` will create it.

## Post-update verification

Re-read CVM instances and inspect both the tag and lifecycle state:

```bash
tccli cvm DescribeInstances \
  --region ap-seoul \
  --InstanceIds '["ins-6imdjii9","ins-9bxjgppx","ins-d3faf5wf","ins-7pjaif5l"]'
```

Verify for each instance:

- `InstanceId` and `InstanceName` match the request.
- `InstanceState` remains `STOPPED` when the user asked not to power on VMs.
- `Tags` contains the desired `LastStoppedAt` value.

## Reporting

Keep the final response short and operational:

- Region used.
- Tag key/value changed.
- Per-instance state and tag confirmation.
- Credential hygiene note only if a command exposed local credentials during the session; do not quote the secret values.
