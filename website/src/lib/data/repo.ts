import fs from "node:fs";
import { execFileSync } from "node:child_process";
import { repoRoot, repoPath, readText } from "./paths";
import { getPipelines, allParameters } from "./pipelines";
import type { Commit, DocPage, RepoMeta, TimelineEntry } from "../types";

function git(args: string[]): string {
  try {
    return execFileSync("git", ["-C", repoRoot(), ...args], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return "";
  }
}

const CONVENTIONAL = /^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$/;

export function getCommits(limit = 20): Commit[] {
  const out = git(["log", `-${limit}`, "--pretty=format:%H%x1f%an%x1f%cI%x1f%s"]);
  if (!out) return [];
  return out.split("\n").map((line) => {
    const [hash, author, date, subject] = line.split("\x1f");
    const m = subject?.match(CONVENTIONAL);
    return {
      hash: (hash ?? "").slice(0, 7),
      author: author ?? "",
      date: date ?? "",
      subject: subject ?? "",
      type: m ? m[1] : null,
      scope: m && m[2] ? m[2] : null,
    };
  });
}

export function getCommitCount(): number {
  const out = git(["rev-list", "--count", "HEAD"]);
  const n = parseInt(out, 10);
  return Number.isNaN(n) ? 0 : n;
}

export function getTags(): { name: string; date: string | null }[] {
  const out = git(["tag", "--sort=-creatordate", "--format=%(refname:short)%x1f%(creatordate:iso-strict)"]);
  if (!out) return [];
  return out
    .split("\n")
    .filter(Boolean)
    .map((line) => {
      const [name, date] = line.split("\x1f");
      return { name, date: date || null };
    });
}

export function getRemote(): string | null {
  const url = git(["config", "--get", "remote.origin.url"]);
  if (!url) return null;
  const m = url.match(/github\.com[:/](.+?)(?:\.git)?$/);
  return m ? m[1] : null;
}

export function getDefaultBranch(): string {
  return git(["rev-parse", "--abbrev-ref", "HEAD"]) || "main";
}

/** README + everything under docs/ (excluding images and ignored superpowers). */
export function getDocs(): DocPage[] {
  const docs: DocPage[] = [];

  const readme = readText("README.md");
  if (readme) {
    docs.push({ slug: "readme", title: "README", source: "README.md", content: readme });
  }

  const extras = ["CONTRIBUTING.md", "AGENTS.md", "NOTICE"];
  for (const f of extras) {
    const content = readText(f);
    if (content) {
      docs.push({
        slug: f.toLowerCase().replace(/\.md$/, "").replace(/[^a-z0-9]+/g, "-"),
        title: f.replace(/\.md$/, ""),
        source: f,
        content,
      });
    }
  }

  const docsDir = repoPath("docs");
  try {
    for (const f of fs.readdirSync(docsDir)) {
      if (!f.endsWith(".md")) continue;
      const content = readText("docs", f);
      if (!content) continue;
      const slug = f.replace(/\.md$/, "");
      const titleM = content.match(/^#\s+(.+)$/m);
      docs.push({
        slug,
        title: titleM ? titleM[1].trim() : slug.replace(/[-_]/g, " "),
        source: `docs/${f}`,
        content,
      });
    }
  } catch {
    /* no docs dir */
  }

  return docs;
}

export function getDoc(slug: string): DocPage | undefined {
  return getDocs().find((d) => d.slug === slug);
}

/** A unified timeline: each pinned pipeline release + repo tags as milestones. */
export function getTimeline(): TimelineEntry[] {
  const entries: TimelineEntry[] = [];

  for (const p of getPipelines()) {
    entries.push({
      id: `release-${p.name}`,
      kind: "release",
      title: `${p.pipeline} ${p.version}`,
      subtitle: p.description,
      date: p.releaseDate,
      pipeline: p.name,
      version: p.version,
    });
  }

  for (const tag of getTags()) {
    entries.push({
      id: `tag-${tag.name}`,
      kind: "tag",
      title: tag.name,
      subtitle: "nf-claw release tag",
      date: tag.date,
    });
  }

  return entries.sort((a, b) => {
    const da = a.date ? new Date(a.date).getTime() : 0;
    const db = b.date ? new Date(b.date).getTime() : 0;
    return db - da;
  });
}

function extractTagline(): { tagline: string; description: string } {
  const readme = readText("README.md") ?? "";
  // First non-empty paragraph after the H1.
  const afterH1 = readme.split(/^#\s+nf-claw\s*$/m)[1] ?? readme;
  const para = afterH1
    .split("\n\n")
    .map((s) => s.trim())
    .find((s) => s && !s.startsWith("#") && !s.startsWith("<") && !s.startsWith("-"));
  const clean = (para ?? "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
  // The headline tagline is the first sentence of the README's lead paragraph.
  const firstSentence = clean.match(/^.*?[.!?](?=\s|$)/)?.[0] ?? clean;
  return {
    tagline:
      firstSentence ||
      "A self-maintaining library of nf-core pipelines for AI agents.",
    description: clean,
  };
}

export function getRepoMeta(): RepoMeta {
  const pipelines = getPipelines();
  const modules = new Set<string>();
  let moduleTotal = 0;
  for (const p of pipelines) moduleTotal += p.moduleCount;
  // distinct module estimate isn't reconstructable from counts, so report total.
  void modules;

  const { tagline, description } = extractTagline();
  const remote = getRemote();
  const commits = getCommitCount();
  const lastCommit = getCommits(1)[0];

  return {
    name: "nf-claw",
    tagline,
    description,
    remote,
    defaultBranch: getDefaultBranch(),
    live: false,
    stats: {
      pipelines: pipelines.length,
      skills: pipelines.length, // each pipeline ships one agent skill (skill.md)
      parameters: allParameters().length,
      modules: moduleTotal,
      commits,
      latestUpdate: lastCommit?.date ?? null,
    },
  };
}
