import type { Pipeline } from "./types";

/** Shared category accent colors (brand greens + cream), used across views. */
export const CATEGORY_COLOR: Record<string, string> = {
  Transcriptomics: "#39D353",
  "Single-cell": "#5FDD86",
  "Variant calling": "#EFE6B8",
  "Data retrieval": "#94EBB0",
  Epigenomics: "#28BA47",
  Metagenomics: "#C9F5D6",
  Proteomics: "#D8C98A",
  Genomics: "#39D353",
};

export function colorForCategory(cat: string): string {
  return CATEGORY_COLOR[cat] ?? "#39D353";
}

/**
 * Derive a coarse topic for a pipeline from its name + description. Heuristic
 * but data-driven (no per-pipeline hardcoding) and degrades to "Genomics".
 */
export function categorize(p: { name: string; description: string }): string {
  const t = `${p.name} ${p.description}`.toLowerCase();
  if (/(single.?cell|scrna|10x|10 genomics)/.test(t)) return "Single-cell";
  if (/(variant|germline|somatic|mutation|sarek|wgs|wes)/.test(t)) return "Variant calling";
  if (/(fetch|download|retriev|databas|sra|ena|public)/.test(t)) return "Data retrieval";
  if (/(rna|transcript|isoform|expression|gene)/.test(t)) return "Transcriptomics";
  if (/(methyl|epigen|chip|atac)/.test(t)) return "Epigenomics";
  if (/(metagenom|microbi|taxonom|amplicon|16s)/.test(t)) return "Metagenomics";
  if (/(protein|mass.?spec|proteom)/.test(t)) return "Proteomics";
  return "Genomics";
}

/** A serialisable, lightweight summary passed to client components. */
export interface PipelineSummary {
  name: string;
  pipeline: string;
  version: string;
  description: string;
  category: string;
  parameterCount: number;
  groupCount: number;
  moduleCount: number;
  requiredCount: number;
  samplesheetCount: number;
  hasSamplesheet: boolean;
  releaseDate: string | null;
  policy: string;
  runCommand: string;
}

/** Compact parameter shape for the client-side skills/parameter explorer. */
export interface ParamLite {
  name: string;
  type: string;
  group: string;
  required: boolean;
  hidden: boolean;
  allowed: string[];
  constraints: string;
  default: string;
  description: string;
}

export interface SkillGroupLite {
  name: string;
  title: string;
  count: number;
}

/** A "skill" == one pipeline's generated skill.md (what an agent reads). */
export interface SkillSummary {
  name: string;
  pipeline: string;
  version: string;
  commit: string;
  description: string;
  category: string;
  runCommand: string;
  demoCommand: string | null;
  usageUrl: string | null;
  outputs: string;
  releaseDate: string | null;
  policy: string;
  parameterCount: number;
  moduleCount: number;
  samplesheetCount: number;
  hasSamplesheet: boolean;
  groups: SkillGroupLite[];
  required: { name: string; type: string; description: string }[];
  params: ParamLite[];
}

export function toSkill(p: Pipeline): SkillSummary {
  return {
    name: p.name,
    pipeline: p.pipeline,
    version: p.version,
    commit: p.commit,
    description: p.description,
    category: categorize(p),
    runCommand: p.runCommand,
    demoCommand: p.demoCommand,
    usageUrl: p.usageUrl,
    outputs: p.outputs,
    releaseDate: p.releaseDate,
    policy: p.policy,
    parameterCount: p.parameterCount,
    moduleCount: p.moduleCount,
    samplesheetCount: p.samplesheet.length,
    hasSamplesheet: p.hasSamplesheet,
    groups: p.groups.map((g) => ({
      name: g.name,
      title: g.title,
      count: g.parameters.length,
    })),
    required: p.requiredParams.map((r) => ({
      name: r.name,
      type: r.type,
      description: r.description,
    })),
    params: p.groups.flatMap((g) =>
      g.parameters.map((param) => ({
        name: param.name,
        type: param.type,
        group: g.name,
        required: param.required,
        hidden: param.hidden,
        allowed: param.allowed,
        constraints: param.constraints,
        default: param.default,
        description: param.description,
      })),
    ),
  };
}

export function toSummary(p: Pipeline): PipelineSummary {
  return {
    name: p.name,
    pipeline: p.pipeline,
    version: p.version,
    description: p.description,
    category: categorize(p),
    parameterCount: p.parameterCount,
    groupCount: p.groups.length,
    moduleCount: p.moduleCount,
    requiredCount: p.requiredParams.length,
    samplesheetCount: p.samplesheet.length,
    hasSamplesheet: p.hasSamplesheet,
    releaseDate: p.releaseDate,
    policy: p.policy,
    runCommand: p.runCommand,
  };
}
