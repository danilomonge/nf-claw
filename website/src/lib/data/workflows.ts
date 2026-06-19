import fs from "node:fs";
import { repoPath } from "./paths";
import type { Workflow } from "../types";

/**
 * Parse .github/workflows/*.yml heuristically (the files are small and simple,
 * so a dependency-free reader keeps the build lean and reflects them faithfully).
 */
export function getWorkflows(): Workflow[] {
  const dir = repoPath(".github", "workflows");
  let files: string[] = [];
  try {
    files = fs.readdirSync(dir).filter((f) => /\.ya?ml$/.test(f));
  } catch {
    return [];
  }

  return files
    .map((file): Workflow => {
      const raw = fs.readFileSync(`${dir}/${file}`, "utf8");
      const lines = raw.split("\n");

      const nameM = raw.match(/^name:\s*(.+)$/m);
      const name = nameM ? nameM[1].trim().replace(/^["']|["']$/g, "") : file.replace(/\.ya?ml$/, "");

      const triggers = new Set<string>();
      for (const t of ["push", "pull_request", "schedule", "workflow_dispatch", "release"]) {
        if (new RegExp(`\\b${t}\\b`).test(raw.split("jobs:")[0] ?? raw)) triggers.add(t);
      }

      const cronM = raw.match(/cron:\s*["']?([^"'\n#]+)["']?/);
      const schedule = cronM ? cronM[1].trim() : null;

      // Jobs are the 2-space-indented keys under `jobs:`.
      const jobs: string[] = [];
      let inJobs = false;
      for (const line of lines) {
        if (/^jobs:\s*$/.test(line)) {
          inJobs = true;
          continue;
        }
        if (inJobs) {
          if (/^\S/.test(line)) break;
          const m = line.match(/^ {2}([A-Za-z0-9_-]+):\s*$/);
          if (m) jobs.push(m[1]);
        }
      }

      return { file, name, triggers: [...triggers], schedule, jobs };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}
