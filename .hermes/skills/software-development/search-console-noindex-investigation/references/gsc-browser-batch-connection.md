# GSC browser batch connection notes

Use this when maintaining or operating `bin/gsc validate-index-issues --browser` for Search Console Page indexing issue validation.

## Durable lesson

Repeatedly spawning a browser helper per GSC property causes repeated Chrome DevTools attach attempts. On recent Chrome/macOS setups this can surface as repeated permission/approval prompts, delayed WebSocket handshakes, or intermittent `Timed out connecting to Chrome DevTools WebSocket` / `WebSocket error: unknown` failures.

Prefer a single browser-helper process that attaches to Chrome once, then processes multiple `--site` values sequentially over the same browser-level CDP connection.

## Recommended CLI shape

- Let the low-level browser helper accept repeatable `--site` arguments in `--index-issues` mode.
- Add `--site-delay-ms` for spacing between properties inside that one helper process.
- Have the wrapper (`bin/gsc validate-index-issues --browser`) pass all selected properties to one helper invocation rather than looping with one subprocess per property.
- Keep a long enough `--connect-timeout-ms` because Chrome may wait for a one-time remote-debugging approval prompt before opening the WebSocket.
- Keep a separate `--batch-timeout-ms` at the wrapper level for the whole run.

## Operational pattern

1. Start the batch run once.
2. If Chrome shows a DevTools/remote-debugging approval prompt, approve it once.
3. Do not restart the CLI for each property; let the same helper continue through the selected sites.
4. If the WebSocket does not open, verify `DevToolsActivePort`, the listener, and the actual WebSocket handshake before changing GSC validation logic.

## Regression tests to keep

- The browser helper documents repeatable `--site` and `--connect-timeout-ms`.
- The wrapper builds a single browser batch command with multiple `--site` arguments.
- The wrapper exposes both per-site and batch timeouts.
- The process still returns non-zero if any site/issue fails inside the batch.
