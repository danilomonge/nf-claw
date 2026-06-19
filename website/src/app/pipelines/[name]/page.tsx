import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import {
  ArrowLeft,
  BookOpen,
  Boxes,
  Calendar,
  GitCommitHorizontal,
  Github,
  Layers,
  Puzzle,
  SlidersHorizontal,
  Table2,
  Terminal,
} from "lucide-react";
import { getPipeline, pipelineNames } from "@/lib/data";
import { toSkill, categorize, colorForCategory } from "@/lib/derive";
import { CodeBlock } from "@/components/ui/code-block";
import { ParameterExplorer } from "@/components/pipeline/parameter-explorer";
import { Reveal } from "@/components/ui/reveal";
import { formatDate, humanize } from "@/lib/utils";

export function generateStaticParams() {
  return pipelineNames().map((name) => ({ name }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ name: string }>;
}): Promise<Metadata> {
  const { name } = await params;
  const p = getPipeline(name);
  if (!p) return { title: "Pipeline not found" };
  return {
    title: `${p.name} ${p.version}`,
    description: p.description,
  };
}

function schemaUrl(url: string, version: string): string | null {
  const m = url.match(/github\.com[:/](.+?)(?:\.git)?$/);
  if (!m) return null;
  return `https://github.com/${m[1]}/blob/${version}/nextflow_schema.json`;
}

function repoUrl(url: string, version: string): string | null {
  const m = url.match(/github\.com[:/](.+?)(?:\.git)?$/);
  if (!m) return null;
  return `https://github.com/${m[1]}/tree/${version}`;
}

export default async function PipelinePage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = await params;
  const pipeline = getPipeline(name);
  if (!pipeline) notFound();

  const skill = toSkill(pipeline);
  const category = categorize(pipeline);
  const accent = colorForCategory(category);
  const schema = schemaUrl(pipeline.url, pipeline.version);
  const upstream = repoUrl(pipeline.url, pipeline.version);
  const csvHeader = pipeline.samplesheet.map((c) => c.column).join(",");

  const facts = [
    { icon: SlidersHorizontal, label: "Parameters", value: String(pipeline.parameterCount) },
    { icon: Layers, label: "Groups", value: String(pipeline.groups.length) },
    { icon: Puzzle, label: "nf-core modules", value: String(pipeline.moduleCount) },
    { icon: Table2, label: "Samplesheet cols", value: String(pipeline.samplesheet.length) },
  ];

  return (
    <div className="container-site pt-28">
      <Link
        href="/#pipelines"
        className="inline-flex items-center gap-2 text-sm text-fog-muted transition hover:text-fog"
      >
        <ArrowLeft className="h-4 w-4" /> All pipelines
      </Link>

      {/* header */}
      <Reveal className="mt-8">
        <div className="relative overflow-hidden rounded-4xl border border-white/[0.07] p-8 md:p-12">
          <div
            className="absolute -right-20 -top-20 h-72 w-72 rounded-full blur-[120px]"
            style={{ background: `${accent}22` }}
          />
          <div className="relative">
            <div className="flex flex-wrap items-center gap-3">
              <span
                className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium"
                style={{ background: `${accent}1a`, color: accent }}
              >
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: accent }} />
                {category}
              </span>
              <span className="chip">{pipeline.policy || "pinned release"}</span>
            </div>

            <h1 className="mt-5 font-mono text-5xl font-semibold tracking-tight text-fog md:text-6xl">
              {pipeline.name}
            </h1>
            <p className="mt-2 text-sm text-fog-dim">{pipeline.pipeline}</p>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-fog-muted">
              {pipeline.description}
            </p>

            <div className="mt-7 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm">
                <span className="text-fog-dim">version</span>
                <span className="font-mono font-semibold text-fog">{pipeline.version}</span>
              </span>
              <span className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm">
                <GitCommitHorizontal className="h-4 w-4 text-fog-dim" />
                <span className="font-mono text-fog">{pipeline.commit.slice(0, 10)}</span>
              </span>
              {pipeline.releaseDate && (
                <span className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm">
                  <Calendar className="h-4 w-4 text-fog-dim" />
                  <span className="text-fog">{formatDate(pipeline.releaseDate)}</span>
                </span>
              )}
              {upstream && (
                <a
                  href={upstream}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-fog transition hover:border-claw-400/30"
                >
                  <Github className="h-4 w-4" /> Upstream
                </a>
              )}
              {pipeline.usageUrl && (
                <a
                  href={pipeline.usageUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-fog transition hover:border-claw-400/30"
                >
                  <BookOpen className="h-4 w-4" /> Usage docs
                </a>
              )}
            </div>
          </div>
        </div>
      </Reveal>

      {/* facts */}
      <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        {facts.map((f) => (
          <div key={f.label} className="glass p-5">
            <f.icon className="h-5 w-5 text-claw-400/80" />
            <div className="mt-3 text-3xl font-semibold text-fog">{f.value}</div>
            <div className="text-xs uppercase tracking-[0.14em] text-fog-dim">{f.label}</div>
          </div>
        ))}
      </div>

      {/* run it */}
      <section className="mt-16">
        <h2 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-fog">
          <Terminal className="h-5 w-5 text-claw-400" /> Run it
        </h2>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <CodeBlock code={pipeline.runCommand} label="nfclaw" />
          <CodeBlock code={pipeline.rawCommand} label="raw nextflow" />
        </div>
        {pipeline.demoCommand && (
          <div className="mt-4">
            <CodeBlock code={pipeline.demoCommand} label="demo (test profile)" />
          </div>
        )}
      </section>

      {/* samplesheet */}
      {pipeline.samplesheet.length > 0 && (
        <section className="mt-16">
          <h2 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-fog">
            <Table2 className="h-5 w-5 text-claw-400" /> Samplesheet
          </h2>
          <p className="mt-2 text-sm text-fog-muted">
            A CSV with this exact header. Fill each value per the constraints below.
          </p>
          <div className="mt-5">
            <CodeBlock code={csvHeader} label="samplesheet.csv header" />
          </div>
          <div className="glass mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[0.07] text-left text-xs uppercase tracking-wider text-fog-dim">
                  <th className="px-5 py-3 font-medium">Column</th>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Required</th>
                  <th className="px-5 py-3 font-medium">Allowed / constraints</th>
                </tr>
              </thead>
              <tbody>
                {pipeline.samplesheet.map((c) => (
                  <tr key={c.column} className="border-b border-white/[0.04] last:border-0">
                    <td className="px-5 py-3">
                      <code className="font-mono text-fog">{c.column}</code>
                    </td>
                    <td className="px-5 py-3 text-fog-muted">{c.type}</td>
                    <td className="px-5 py-3">
                      {c.required ? (
                        <span className="rounded-md border border-claw-400/20 bg-claw-500/15 px-1.5 py-0.5 text-[11px] text-claw-300">
                          required
                        </span>
                      ) : (
                        <span className="text-fog-dim">optional</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-fog-muted">
                      {c.allowed.length > 0 && (
                        <span className="mr-2 flex flex-wrap gap-1">
                          {c.allowed.map((a) => (
                            <code key={a} className="rounded bg-white/[0.05] px-1.5 py-0.5 font-mono text-[11px]">
                              {a}
                            </code>
                          ))}
                        </span>
                      )}
                      {c.constraints && <span className="text-xs text-fog-dim">{c.constraints}</span>}
                      {!c.allowed.length && !c.constraints && <span className="text-fog-dim">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* required params */}
      {pipeline.requiredParams.length > 0 && (
        <section className="mt-16">
          <h2 className="text-2xl font-semibold tracking-tight text-fog">Required parameters</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {pipeline.requiredParams.map((r) => (
              <div key={r.name} className="glass p-5">
                <div className="flex items-center gap-2">
                  <code className="font-mono text-sm font-semibold text-claw-300">{r.name}</code>
                  <span className="chip text-[10px]">{r.type}</span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-fog-muted">{r.description}</p>
                {r.constraints && (
                  <p className="mt-2 text-xs text-fog-dim">Constraint · {r.constraints}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* parameter explorer */}
      <section className="mt-16">
        <div className="flex items-end justify-between">
          <h2 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-fog">
            <Boxes className="h-5 w-5 text-claw-400" /> Parameter explorer
          </h2>
          <span className="text-sm text-fog-dim">
            {pipeline.parameterCount} parameters · {pipeline.groups.length} groups
          </span>
        </div>
        <p className="mt-2 max-w-2xl text-sm text-fog-muted">
          Every parameter from the pinned <code className="font-mono">nextflow_schema.json</code>,
          validated by nf-schema at runtime. Search, filter by group, and expand any parameter for
          its type, default, allowed values and constraints.
        </p>
        <div className="mt-6">
          <ParameterExplorer params={skill.params} groups={skill.groups} schemaUrl={schema} />
        </div>
      </section>

      {/* outputs */}
      {pipeline.outputs && (
        <section className="mt-16">
          <h2 className="text-2xl font-semibold tracking-tight text-fog">Outputs</h2>
          <div className="glass mt-5 p-6">
            <p className="text-pretty leading-relaxed text-fog-muted">{pipeline.outputs}</p>
          </div>
        </section>
      )}

      {/* group overview */}
      <section className="mt-16">
        <h2 className="text-2xl font-semibold tracking-tight text-fog">Parameter groups</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {pipeline.groups.map((g) => (
            <span key={g.name} className="chip text-sm">
              {humanize(g.name)}
              <span className="text-fog-dim">{g.parameters.length}</span>
            </span>
          ))}
        </div>
      </section>

      <div className="h-10" />
    </div>
  );
}
