"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowUpRight,
  BookOpen,
  ChevronDown,
  GitCommitHorizontal,
  Layers,
  Puzzle,
  Search,
  SlidersHorizontal,
  Table2,
} from "lucide-react";
import type { SkillSummary } from "@/lib/derive";
import { CodeBlock } from "@/components/ui/code-block";
import { cn, formatDate, humanize } from "@/lib/utils";

export function SkillsExplorer({ skills }: { skills: SkillSummary[] }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");

  const categories = useMemo(
    () => ["All", ...[...new Set(skills.map((s) => s.category))].sort()],
    [skills],
  );

  const q = query.trim().toLowerCase();

  const results = useMemo(() => {
    return skills
      .filter((s) => category === "All" || s.category === category)
      .map((s) => {
        const matchedParams = q
          ? s.params.filter(
              (p) => p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q),
            )
          : [];
        const textMatch =
          !q ||
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.category.toLowerCase().includes(q);
        return { skill: s, matchedParams, visible: textMatch || matchedParams.length > 0 };
      })
      .filter((r) => r.visible);
  }, [skills, category, q]);

  return (
    <div className="mt-12">
      <div className="glass flex flex-col gap-3 p-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search skills, descriptions and parameters (e.g. “aligner”, “strandedness”)…"
            className="w-full rounded-xl border border-white/10 bg-ink-900/60 py-3 pl-11 pr-4 text-sm text-fog outline-none transition placeholder:text-fog-dim focus:border-claw-400/40 focus:bg-ink-900"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={cn(
                "rounded-full border px-3.5 py-2 text-xs font-medium transition",
                category === c
                  ? "border-claw-400/40 bg-claw-500/15 text-claw-200"
                  : "border-white/10 bg-white/[0.02] text-fog-muted hover:text-fog",
              )}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        {results.map(({ skill, matchedParams }) => (
          <SkillCard key={skill.name} skill={skill} matchedParams={matchedParams} query={q} />
        ))}
      </div>
      {results.length === 0 && (
        <p className="py-16 text-center text-sm text-fog-dim">No skills match your search.</p>
      )}
    </div>
  );
}

function SkillCard({
  skill,
  matchedParams,
  query,
}: {
  skill: SkillSummary;
  matchedParams: SkillSummary["params"];
  query: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="glass glass-hover flex flex-col p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Link
              href={`/pipelines/${skill.name}`}
              className="font-mono text-lg font-semibold text-fog transition hover:text-claw-300"
            >
              {skill.name}
            </Link>
            <span className="chip text-[10px]">{skill.category}</span>
          </div>
          <p className="mt-0.5 text-xs text-fog-dim">{skill.pipeline}</p>
        </div>
        <div className="text-right">
          <div className="font-mono text-sm text-fog">{skill.version}</div>
          {skill.releaseDate && (
            <div className="text-[11px] text-fog-dim">{formatDate(skill.releaseDate)}</div>
          )}
        </div>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-fog-muted">{skill.description}</p>

      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <Stat icon={<SlidersHorizontal className="h-3.5 w-3.5" />}>{skill.parameterCount} params</Stat>
        <Stat icon={<Layers className="h-3.5 w-3.5" />}>{skill.groups.length} groups</Stat>
        <Stat icon={<Puzzle className="h-3.5 w-3.5" />}>{skill.moduleCount} modules</Stat>
        {skill.hasSamplesheet && (
          <Stat icon={<Table2 className="h-3.5 w-3.5" />}>{skill.samplesheetCount}-col sheet</Stat>
        )}
        <Stat icon={<GitCommitHorizontal className="h-3.5 w-3.5" />}>
          <span className="font-mono">{skill.commit.slice(0, 7)}</span>
        </Stat>
      </div>

      {matchedParams.length > 0 && (
        <div className="mt-4 rounded-xl border border-claw-400/15 bg-claw-500/[0.05] p-3">
          <p className="mb-2 text-[11px] uppercase tracking-wider text-claw-300/80">
            {matchedParams.length} matching parameter{matchedParams.length !== 1 ? "s" : ""}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {matchedParams.slice(0, 8).map((p) => (
              <code
                key={p.name}
                className="rounded bg-white/[0.05] px-1.5 py-0.5 font-mono text-[11px] text-fog"
                title={p.description}
              >
                {p.name}
              </code>
            ))}
            {matchedParams.length > 8 && (
              <span className="text-[11px] text-fog-dim">+{matchedParams.length - 8} more</span>
            )}
          </div>
        </div>
      )}

      <div className="mt-4">
        <CodeBlock code={skill.runCommand} label="run it" />
      </div>

      <button
        onClick={() => setOpen((v) => !v)}
        className="mt-4 inline-flex items-center gap-1.5 self-start text-xs font-medium text-fog-muted transition hover:text-fog"
      >
        <ChevronDown className={cn("h-4 w-4 transition-transform", open && "rotate-180")} />
        {open ? "Hide details" : "Required params, groups & outputs"}
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="space-y-5 pt-4">
              {skill.required.length > 0 && (
                <div>
                  <h5 className="mb-2 text-[11px] uppercase tracking-wider text-fog-dim">
                    Required parameters
                  </h5>
                  <div className="space-y-1.5">
                    {skill.required.map((r) => (
                      <div key={r.name} className="flex items-baseline gap-2 text-sm">
                        <code className="font-mono text-claw-300">{r.name}</code>
                        <span className="text-fog-dim">·</span>
                        <span className="truncate text-fog-muted">{r.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h5 className="mb-2 text-[11px] uppercase tracking-wider text-fog-dim">
                  Parameter groups
                </h5>
                <div className="flex flex-wrap gap-1.5">
                  {skill.groups.map((g) => (
                    <span key={g.name} className="chip">
                      {humanize(g.name)}
                      <span className="text-fog-dim">{g.count}</span>
                    </span>
                  ))}
                </div>
              </div>

              {skill.outputs && (
                <div>
                  <h5 className="mb-2 text-[11px] uppercase tracking-wider text-fog-dim">Outputs</h5>
                  <p className="text-sm leading-relaxed text-fog-muted line-clamp-4">
                    {skill.outputs}
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-5 flex items-center gap-3 border-t border-white/[0.05] pt-4">
        <Link
          href={`/pipelines/${skill.name}`}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-claw-300 transition hover:text-claw-200"
        >
          Full parameter explorer <ArrowUpRight className="h-4 w-4" />
        </Link>
        {skill.usageUrl && (
          <a
            href={skill.usageUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-fog-dim transition hover:text-fog"
          >
            <BookOpen className="h-4 w-4" /> Upstream docs
          </a>
        )}
      </div>
    </div>
  );
}

function Stat({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-white/[0.02] px-2.5 py-1 text-fog-muted">
      <span className="text-claw-400/70">{icon}</span>
      {children}
    </span>
  );
}
