/**
 * The events a GitHub workflow runs on: the keys of its top-level `on:` block, or its inline form
 * (`on: push`, `on: [push, pull_request]`). Only that block is read — matching event names anywhere
 * before `jobs:` also matched the words in comments ("a push made with that token", "per-release CI"),
 * which listed triggers the workflows do not have.
 */
export function workflowTriggers(raw: string): string[] {
  const lines = raw.split("\n");
  const start = lines.findIndex((l) => /^["']?on["']?\s*:/.test(l));
  if (start === -1) return [];
  const inline = lines[start]
    .replace(/^["']?on["']?\s*:/, "")
    .replace(/\s+#.*$/, "")
    .trim();
  if (inline) {
    return inline
      .replace(/^\[|\]$/g, "")
      .split(",")
      .map((s) => s.trim().replace(/^["']|["']$/g, ""))
      .filter(Boolean);
  }
  const out: string[] = [];
  for (const line of lines.slice(start + 1)) {
    if (/^\s*(#.*)?$/.test(line)) continue; // blank or comment
    if (/^\S/.test(line)) break; // the next top-level key ends the block
    const m = line.match(/^ {2}(?:-\s+)?([A-Za-z_]+)\s*(?::|$)/); // events sit at two spaces
    if (m) out.push(m[1]);
  }
  return out;
}
