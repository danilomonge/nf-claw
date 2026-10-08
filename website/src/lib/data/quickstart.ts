import { readText } from "./paths";
import { getPipelines } from "./pipelines";
import { splitFrontmatter } from "./markdown";

/**
 * The three steps an agent takes (AGENTS.md "To run a pipeline"), filled with real repository
 * content for one example pipeline: the catalog lines a grep returns, an excerpt of its skill.md,
 * and its run and demo commands. Nothing here is written by hand.
 */
export interface Quickstart {
  name: string;
  catalogLines: string[];
  skillLines: string[];
  runCommand: string;
  demoCommand: string | null;
}

export function getQuickstart(preferred = "rnaseq"): Quickstart | null {
  const pipelines = getPipelines();
  const p = pipelines.find((x) => x.name === preferred) ?? pipelines[0];
  if (!p) return null;

  const catalog = readText("catalog.md") ?? "";
  const catalogLines = catalog
    .split("\n")
    .filter((l) => l.toLowerCase().includes(p.name.toLowerCase()) && l.trim().startsWith("|"))
    .slice(0, 3);

  const body = splitFrontmatter(readText("pipelines", p.name, "skill.md") ?? "").content.split("\n");
  const at = (heading: string) => body.findIndex((l) => l.trim().toLowerCase() === heading);
  const skillLines: string[] = [];
  const title = body.find((l) => l.startsWith("# "));
  if (title) skillLines.push(title, "");
  const run = at("## run it");
  if (run !== -1) {
    // the heading and its fenced block, as written
    let i = run;
    skillLines.push(body[i++]);
    while (i < body.length && !body[i].startsWith("```")) i++;
    skillLines.push(body[i++] ?? "```");
    while (i < body.length && !body[i].startsWith("```")) skillLines.push(body[i++]);
    skillLines.push("```", "");
  }
  const inputs = at("## inputs");
  if (inputs !== -1) {
    skillLines.push(body[inputs]);
    const table = body.slice(inputs + 1).filter((l) => l.startsWith("|"));
    skillLines.push(...table.slice(0, 3));
  }

  return { name: p.name, catalogLines, skillLines, runCommand: p.runCommand, demoCommand: p.demoCommand };
}
