// Resolve the links inside a rendered repository document (README, CONTRIBUTING, docs/*.md).
// Those files link to each other by repository-relative path (`docs/known-issues.md`, or
// `compatibility.md` from inside docs/). Rendered as-is on the site, every one of them resolved under
// the current page — `/docs/readme/docs/known-issues.md` — and 404'd. Pure and dependency-free so the
// client-side Markdown renderer can use it.

export interface LinkContext {
  /** The document's repository-relative path, e.g. "docs/known-issues.md". */
  source: string;
  /** Repository-relative path -> slug, for every document the site renders under /docs/<slug>/. */
  docs: Record<string, string>;
  /** Where any other repository file is shown, e.g. "https://github.com/owner/repo/blob/main". */
  repoBlobBase: string | null;
}

export interface ResolvedLink {
  href: string;
  /** True for a page of this site (rendered with next/link, which adds the base path). */
  internal: boolean;
}

/** Normalise a repository-relative POSIX path; null if it climbs above the repository root. */
function normalize(path: string): string | null {
  const out: string[] = [];
  for (const part of path.split("/")) {
    if (!part || part === ".") continue;
    if (part === "..") {
      if (!out.length) return null;
      out.pop();
    } else {
      out.push(part);
    }
  }
  return out.join("/");
}

export function resolveDocLink(href: string | undefined, ctx: LinkContext): ResolvedLink | null {
  if (!href) return null;
  // Absolute URLs (any scheme), in-page anchors and root-relative paths are already correct.
  if (/^[a-z][a-z0-9+.-]*:/i.test(href) || /^[#/]/.test(href)) {
    return { href, internal: false };
  }
  const [, pathPart, suffix] = href.match(/^([^?#]*)(.*)$/) ?? ["", href, ""];
  const dir = ctx.source.includes("/") ? ctx.source.slice(0, ctx.source.lastIndexOf("/")) : "";
  const target = normalize(dir ? `${dir}/${pathPart}` : pathPart);
  if (!target) return { href, internal: false };
  const slug = ctx.docs[target];
  if (slug) return { href: `/docs/${slug}/${suffix}`, internal: true };
  if (ctx.repoBlobBase) return { href: `${ctx.repoBlobBase}/${target}${suffix}`, internal: false };
  return { href, internal: false };
}
