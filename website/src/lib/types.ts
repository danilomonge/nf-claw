// Data model for the nf-claw living interface.
// Every type here is derived from repository files — nothing is hand-authored.

export interface Parameter {
  name: string; // e.g. "--aligner"
  type: string; // e.g. "string", "boolean", "integer"
  required: boolean;
  hidden: boolean;
  allowed: string[];
  constraints: string;
  default: string;
  description: string;
  group: string;
}

export interface ParameterGroup {
  name: string; // e.g. "alignment_options"
  title: string; // e.g. "Alignment options"
  parameters: Parameter[];
}

export interface SamplesheetColumn {
  column: string;
  type: string;
  required: boolean;
  allowed: string[];
  constraints: string;
}

export interface RequiredParam {
  name: string;
  type: string;
  allowed: string[];
  constraints: string;
  description: string;
}

export interface Pipeline {
  name: string; // "rnaseq"
  pipeline: string; // "nf-core/rnaseq"
  version: string;
  commit: string;
  description: string;
  hasSamplesheet: boolean;
  url: string; // upstream git url
  policy: string; // version policy (sources.tsv)
  runCommand: string;
  rawCommand: string;
  demoCommand: string | null;
  samplesheet: SamplesheetColumn[];
  requiredParams: RequiredParam[];
  groups: ParameterGroup[];
  parameterCount: number;
  outputs: string;
  usageUrl: string | null;
  releaseDate: string | null; // date of the pinned release commit
  moduleCount: number; // distinct nf-core modules in the upstream
}

export interface Commit {
  hash: string;
  author: string;
  date: string;
  subject: string;
  type: string | null; // conventional-commit type
  scope: string | null;
}

export interface Workflow {
  file: string;
  name: string;
  triggers: string[];
  schedule: string | null;
  jobs: string[];
}

export interface DocPage {
  slug: string;
  title: string;
  source: string; // relative path in the repo
  content: string; // raw markdown
}

export interface TimelineEntry {
  id: string;
  kind: "release" | "tag" | "milestone";
  title: string;
  subtitle: string;
  date: string | null;
  pipeline?: string;
  version?: string;
}

export interface RepoStats {
  pipelines: number;
  skills: number;
  parameters: number;
  modules: number;
  commits: number;
  latestUpdate: string | null;
}

export interface RepoMeta {
  name: string;
  tagline: string;
  description: string;
  stats: RepoStats;
  remote: string | null; // GitHub "owner/repo" if a remote is configured
  defaultBranch: string;
  live: boolean; // whether live GitHub data augmented the build
}
