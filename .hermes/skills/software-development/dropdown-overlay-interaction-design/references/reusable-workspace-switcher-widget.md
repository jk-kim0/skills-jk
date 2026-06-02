# Reusable Workspace Switcher widget adaptation

Use this reference when a user asks to adopt the shadcnui-blocks `Workspace Switcher` not just as inline markup, but as a reusable UI widget.

## Key lesson

Do not leave the Workspace Switcher pattern embedded directly in `AppShell` or another page/component when the user asks for a widget.
Extract a reusable client component and let product surfaces pass domain data into it.

## Recommended component contract

Keep the visual pattern close to the upstream block:

- `DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`
- `Avatar` + `AvatarFallback`
- primary name and secondary metadata in the trigger
- `ChevronsUpDown` on the trigger
- item rows with avatar/fallback, primary/secondary text, and a right-aligned `Check` for the selected item

But make product behavior configurable:

```tsx
export type WorkspaceSwitcherItem = {
  id: string;
  name: string;
  description: string;
};

type WorkspaceSwitcherProps = {
  actionHref?: string;
  actionLabel?: string;
  actionInputName?: string;
  ariaLabel: string;
  emptyLabel?: string;
  selectedWorkspaceId?: string;
  switchWorkspaceAction?: (formData: FormData) => void | Promise<void>;
  workspaces: WorkspaceSwitcherItem[];
};
```

For a Team switcher, map Team data into generic workspace-shaped items in the caller:

```tsx
<WorkspaceSwitcher
  actionHref="/teams/new"
  actionInputName="teamId"
  actionLabel="Create Team"
  ariaLabel={`Team switcher: ${currentTeam?.name ?? "No Team"}`}
  emptyLabel="No active Team"
  selectedWorkspaceId={currentTeam?.id}
  switchWorkspaceAction={switchTeamAction}
  workspaces={memberships.map((membership) => ({
    id: membership.teamId,
    name: membership.team.name,
    description: `${membership.role} · ${membership.team.slug}`,
  }))}
/>
```

## Testing checklist

Add source-level tests that assert:

- the reusable component file exists and is a client component;
- the caller imports and renders `WorkspaceSwitcher`;
- the caller no longer contains row-level implementation classes/markup;
- `WorkspaceSwitcher` contains `Avatar`, `ChevronsUpDown`, `Check`, `selectedWorkspaceId`, and the action prop;
- removed menu labels/actions remain absent from the caller.

When rebasing onto main, preserve unrelated tests that landed on main (for example other dropdown tests) while adding widget-specific assertions.
