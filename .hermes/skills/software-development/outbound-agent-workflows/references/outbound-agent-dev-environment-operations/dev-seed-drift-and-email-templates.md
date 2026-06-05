# Dev seed drift and Email Template verification

## When to use

Use this reference when an Outbound Agent dev environment looks healthy after migration/deploy, but a demo object is missing from the UI. The main lesson is that migration-only does not apply seed fixtures.

## Observed incident pattern

On dev-seoul, `/login` and authenticated `/sales-demo/home` were healthy, migrations and schema checks were successful, and the app was deployed to the latest image. The user still could not see `Email Template` data.

DB inspection showed:

```text
EmailTemplate         0
EmailTemplateVersion  0
User                  present
Team                  present
Campaign              present
```

This meant the environment had partial/older seed data, not a UI rendering bug.

## Correct investigation sequence

1. SSH to the Tencent VM.
2. Query VM-local PostgreSQL in the `outbound-agent-postgres` container.
3. Count both the primary table and version/detail table for the reported domain object.
4. Inspect team ownership, because many demo records are team-scoped.
5. Only after confirming seed drift, run reset+seed through the migration workflow with `reset_database=true`.
6. Re-check DB counts and authenticated pages after reset.

## Useful SQL for Email Templates

```sql
select 'EmailTemplate' as table_name, count(*)::text as count from "EmailTemplate"
union all select 'EmailTemplateVersion', count(*)::text from "EmailTemplateVersion"
union all select 'Team', count(*)::text from "Team"
union all select 'Campaign', count(*)::text from "Campaign";

select t.name, t.category, t.status::text, tm.slug as team_slug, count(v.id)::text as versions
from "EmailTemplate" t
left join "Team" tm on tm.id=t."teamId"
left join "EmailTemplateVersion" v on v."emailTemplateId"=t.id
group by t.id, tm.slug
order by tm.slug, t.name;

select u.username, tm.slug as team_slug, m.role::text
from "TeamMembership" m
join "User" u on u.id=m."userId"
join "Team" tm on tm.id=m."teamId"
order by u.username, tm.slug;
```

## Expected seeded Email Template shape

After a correct reset+seed:

```text
EmailTemplate         9
EmailTemplateVersion  9
Team                  6
Campaign              3
```

Templates are scoped as:

- `querypie-jp`: Japanese event, ACP launch, Lingo launch templates
- `querypie-kr`: Korean event, ACP launch, Lingo launch templates
- `querypie-us`: English event, ACP launch, Lingo launch templates

`/sales-demo/email-templates` may legitimately show 0 templates because `sales-demo` is the personal team. Confirm the QueryPie team pages:

```text
/querypie-jp/email-templates
/querypie-kr/email-templates
/querypie-us/email-templates
```

## Reset verification

After reset+seed and deploy alignment, verify:

- `/opt/outbound-agent/deployments/current-revision`
- `/opt/outbound-agent/deployments/current-image`
- `/opt/outbound-agent/repo/.deployed-revision`
- `systemctl is-active outbound-front`
- `systemctl is-active nginx`
- `curl https://outbound-seoul.dev.querypie.io/login`
- authenticated QueryPie team `email-templates` pages contain the expected template names

## Reporting nuance

If the user reports “Email Template is missing,” distinguish these cases explicitly:

- seed data missing: `EmailTemplate`/`EmailTemplateVersion` count is 0 across all teams
- team-scope confusion: templates exist under `querypie-*` teams but not under `sales-demo`
- UI/navigation bug: DB rows exist for the current team, but the route does not render them
