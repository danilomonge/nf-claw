// Lightweight, dependency-free parsing helpers for the generated markdown
// files (skill.md / reference.md). These read the exact tables the librarian
// emits, so the website never duplicates or hardcodes their content.

const PIPE_PLACEHOLDER = "__NFCLAW_ESCAPED_PIPE__";

export interface Frontmatter {
  data: Record<string, string | boolean>;
  content: string;
}

/**
 * Split YAML-style frontmatter from a generated markdown document. skill.md and
 * reference.md only ever use a flat block of `key: value` scalars (no nesting,
 * anchors or merge keys), so this small dedicated parser replaces a full YAML
 * dependency — and removes its transitive attack surface from the build.
 */
export function splitFrontmatter(raw: string): Frontmatter {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { data: {}, content: raw };
  const data: Record<string, string | boolean> = {};
  for (const line of m[1].split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf(":");
    if (idx === -1) continue;
    const key = trimmed.slice(0, idx).trim();
    let value = trimmed.slice(idx + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    data[key] = value === "true" || value === "false" ? value === "true" : value;
  }
  return { data, content: raw.slice(m[0].length) };
}

/** Split a markdown table row into trimmed cells, respecting escaped pipes. */
export function splitRow(line: string): string[] {
  const normalized = line.replace(/\\\|/g, PIPE_PLACEHOLDER);
  return normalized
    .replace(/^\s*\|/, "")
    .replace(/\|\s*$/, "")
    .split("|")
    .map((c) => c.replace(new RegExp(PIPE_PLACEHOLDER, "g"), "|").trim());
}

export interface MarkdownTable {
  headers: string[];
  rows: string[][];
}

/** Parse the first markdown table found within `lines` starting at `from`. */
export function parseTableAt(lines: string[], from: number): MarkdownTable | null {
  let i = from;
  while (i < lines.length && !lines[i].trim().startsWith("|")) i++;
  if (i >= lines.length) return null;
  const headers = splitRow(lines[i]);
  // separator row
  if (i + 1 >= lines.length || !/^[\s|:-]+$/.test(lines[i + 1])) return null;
  const rows: string[][] = [];
  let j = i + 2;
  while (j < lines.length && lines[j].trim().startsWith("|")) {
    rows.push(splitRow(lines[j]));
    j++;
  }
  return { headers, rows };
}

/** Find a section heading (## Title) and return the lines until the next heading. */
export function sectionLines(md: string, heading: string): string[] {
  const lines = md.split("\n");
  const wanted = heading.trim().toLowerCase();
  let start = -1;
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^#{1,6}\s+(.*)$/);
    if (m && m[1].trim().toLowerCase().startsWith(wanted)) {
      start = i + 1;
      break;
    }
  }
  if (start === -1) return [];
  const out: string[] = [];
  for (let i = start; i < lines.length; i++) {
    if (/^#{1,6}\s+/.test(lines[i])) break;
    out.push(lines[i]);
  }
  return out;
}

/** Parse the table under a given "## Heading" section. */
export function tableUnder(md: string, heading: string): MarkdownTable | null {
  const lines = sectionLines(md, heading);
  return parseTableAt(lines, 0);
}

/** Extract the first fenced code block under a "## Heading" section. */
export function codeBlockUnder(md: string, heading: string): string | null {
  const lines = sectionLines(md, heading);
  const out: string[] = [];
  let inBlock = false;
  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      if (inBlock) break;
      inBlock = true;
      continue;
    }
    if (inBlock) out.push(line);
  }
  return out.length ? out.join("\n") : null;
}

/** Plain prose under a "## Heading" (collapsed whitespace). */
export function proseUnder(md: string, heading: string): string {
  return sectionLines(md, heading)
    .filter((l) => !l.trim().startsWith("```"))
    .join("\n")
    .trim();
}

/**
 * Split an "allowed values" cell into a clean list. The librarian writes each value as its own code
 * span (`bac,arc`, `vst`) so a value containing a comma stays whole; a plain comma-separated cell
 * (older generated docs) is still read.
 */
export function splitAllowed(cell: string): string[] {
  if (!cell || !cell.trim()) return [];
  const spans = [...cell.matchAll(/`([^`]*)`/g)].map((m) => m[1].trim()).filter(Boolean);
  if (spans.length) return spans;
  return cell
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export function isYes(cell: string): boolean {
  const v = (cell || "").trim().toLowerCase();
  return v === "yes" || v === "true" || v === "✓" || v === "x";
}

/** Strip surrounding backticks from a cell value. */
export function unticked(cell: string): string {
  return (cell || "").replace(/`/g, "").trim();
}
