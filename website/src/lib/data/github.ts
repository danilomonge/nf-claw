// Optional live-data adapter. The site is local-first: it is fully driven by
// repository files and local git. When a GitHub remote AND a token are present
// (GITHUB_TOKEN / GH_TOKEN), this augments the build with live Actions runs and
// releases via the REST API. With no remote (the current setup), it no-ops and
// the UI uses the local equivalents (git tags, workflow definitions, git log).

import { getRemote } from "./repo";

export interface LiveRun {
  name: string;
  status: string;
  conclusion: string | null;
  branch: string;
  url: string;
  date: string;
}

export interface LiveRelease {
  name: string;
  tag: string;
  date: string;
  url: string;
}

export function liveEnabled(): boolean {
  return Boolean(getRemote() && (process.env.GITHUB_TOKEN || process.env.GH_TOKEN));
}

async function gh<T>(repo: string, endpoint: string): Promise<T | null> {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  if (!token) return null;
  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/${endpoint}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
      },
      // Revalidate hourly so the static build stays live without rebuilds.
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function getLiveRuns(limit = 6): Promise<LiveRun[] | null> {
  const repo = getRemote();
  if (!repo || !liveEnabled()) return null;
  const data = await gh<{ workflow_runs: Record<string, unknown>[] }>(
    repo,
    `actions/runs?per_page=${limit}`,
  );
  if (!data?.workflow_runs) return null;
  return data.workflow_runs.map((r) => ({
    name: String(r.name ?? r.display_title ?? "run"),
    status: String(r.status ?? ""),
    conclusion: r.conclusion ? String(r.conclusion) : null,
    branch: String(r.head_branch ?? ""),
    url: String(r.html_url ?? ""),
    date: String(r.created_at ?? ""),
  }));
}

export async function getLiveReleases(limit = 10): Promise<LiveRelease[] | null> {
  const repo = getRemote();
  if (!repo || !liveEnabled()) return null;
  const data = await gh<Record<string, unknown>[]>(repo, `releases?per_page=${limit}`);
  if (!Array.isArray(data)) return null;
  return data.map((r) => ({
    name: String(r.name ?? r.tag_name ?? ""),
    tag: String(r.tag_name ?? ""),
    date: String(r.published_at ?? r.created_at ?? ""),
    url: String(r.html_url ?? ""),
  }));
}
