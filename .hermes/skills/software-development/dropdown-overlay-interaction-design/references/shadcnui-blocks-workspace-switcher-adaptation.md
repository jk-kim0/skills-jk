# shadcnui-blocks Workspace Switcher adaptation

Use this reference when adapting a team/workspace switcher to the shadcnui-blocks Dropdown Menu example named `Workspace Switcher` from `https://www.shadcnui-blocks.com/components/dropdown-menu`.

## Upstream example shape

The example is a client component that imports:

- `Check` and `ChevronsUpDown` from `lucide-react`
- `useState` from React
- `Avatar` and `AvatarFallback`
- `DropdownMenu`, `DropdownMenuContent`, `DropdownMenuItem`, `DropdownMenuLabel`, `DropdownMenuTrigger`

It uses local sample data:

```tsx
const workspaces = [
  { id: 1, name: "Workspace 1", createdBy: "abc@example.com" },
  { id: 2, name: "Workspace 2", createdBy: "def@example.com" },
  { id: 3, name: "Workspace 3", createdBy: "ghi@example.com" },
];
```

The trigger pattern:

```tsx
<DropdownMenuTrigger className="flex items-center gap-2 rounded-lg bg-accent px-3 py-2.5">
  <Avatar className="h-8 w-8 rounded-lg">
    <AvatarFallback className="rounded-lg bg-primary text-primary-foreground">
      {selectedWorkspace.name[0]}
    </AvatarFallback>
  </Avatar>
  <div className="flex flex-col gap-1 text-start leading-none">
    <span className="max-w-[17ch] truncate font-semibold text-sm leading-none">
      {selectedWorkspace.name}
    </span>
    <span className="max-w-[20ch] truncate text-muted-foreground text-xs">
      {selectedWorkspace.createdBy}
    </span>
  </div>
  <ChevronsUpDown className="ml-6 h-4 w-4 text-muted-foreground" />
</DropdownMenuTrigger>
```

The content pattern:

```tsx
<DropdownMenuContent align="start" className="w-52">
  <DropdownMenuLabel>Workspaces</DropdownMenuLabel>
  {workspaces.map((workspace) => (
    <DropdownMenuItem key={workspace.id} onClick={() => setSelectedWorkspace(workspace)}>
      <div className="flex items-center gap-2">
        <Avatar className="h-8 w-8 rounded-md">
          <AvatarFallback className="rounded-md bg-primary/10 text-foreground">
            {workspace.name[0]}
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <span>{workspace.name}</span>
          <span className="text-muted-foreground text-xs">{workspace.createdBy}</span>
        </div>
      </div>
      {selectedWorkspace.id === workspace.id && <Check className="ml-auto" />}
    </DropdownMenuItem>
  ))}
</DropdownMenuContent>
```

## Adaptation rules for real app team switchers

1. Preserve the shadcn/Radix DropdownMenu structure, but do not blindly copy `useState` selection when the app has server-side routing or server actions.
2. Map `Workspace` to the domain concept the app actually uses, e.g. `Team`.
3. Map `createdBy` to useful secondary metadata, e.g. `role · slug`, owner email, region, or another stable team descriptor.
4. Keep real switching behavior authoritative:
   - If the app already uses a server action/form submit to switch teams, keep that mechanism.
   - Use `DropdownMenuItem asChild` around a submit button or link when needed.
   - Do not replace server-side selection with client-only `useState` unless the product explicitly only needs local selection.
5. Render the current team in the trigger with an avatar/fallback, truncated primary name, truncated secondary text, and a `ChevronsUpDown` affordance.
   - If the requested current state is a blank team/profile image, keep the fallback blank/neutral rather than substituting initials or a made-up logo.
6. Render team rows with avatar/fallback, team name, secondary metadata, and a `Check` icon for the current team.
7. Prefer `DropdownMenuItem` for current and selectable rows. If the current row is not clickable, use `disabled` or an item-shaped row rather than a visually unrelated `<span>`.
8. Do not keep grouping labels or demo action sections when the product menu does not need them. Remove labels such as `Workspaces`, `Switch Team`, and `Team actions` when the user asks for a single flat menu.
9. Prune menu actions literally. If the user asks to leave only `Create Team`, remove `Manage Team`, `Team settings`, and related tests/assertions that still expect them.
10. If the repo does not already have shadcn `Avatar`, add or implement it consistently before importing it.

## Pitfalls

- Do not treat a visual switcher block as a full product flow. Its demo `useState` is placeholder behavior.
- Do not lose existing server-action semantics, redirects, session persistence, or route invalidation when adopting the block.
- Do not keep a plain text-only menu if the user explicitly asks to use the Workspace Switcher visual/interaction pattern.
