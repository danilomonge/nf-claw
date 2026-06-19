"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  ArrowUpRight,
  GitBranch,
  LayoutGrid,
  Orbit,
  Plus,
  Search,
  SlidersHorizontal,
  Puzzle,
  X,
  Check,
} from "lucide-react";
import type { PipelineSummary } from "@/lib/derive";
import { cn, formatDate } from "@/lib/utils";

const CATEGORY_COLOR: Record<string, string> = {
  Transcriptomics: "#39D353",
  "Single-cell": "#5FDD86",
  "Variant calling": "#EFE6B8",
  "Data retrieval": "#94EBB0",
  Epigenomics: "#28BA47",
  Metagenomics: "#C9F5D6",
  Proteomics: "#D8C98A",
  Genomics: "#39D353",
};

function colorFor(cat: string) {
  return CATEGORY_COLOR[cat] ?? "#39D353";
}

type SortKey = "name" | "parameters" | "modules" | "newest";

function ringLayout(n: number, w: number, h: number) {
  const cx = w / 2;
  const cy = h / 2;
  const positions: { x: number; y: number }[] = [];
  const baseR = Math.min(w, h) * 0.17;
  const gap = Math.min(w, h) * 0.15;
  let placed = 0;
  let ring = 1;
  while (placed < n) {
    const cap = ring * 6;
    const count = Math.min(cap, n - placed);
    const r = baseR + (ring - 1) * gap;
    for (let k = 0; k < count; k++) {
      const angle = (k / count) * Math.PI * 2 + ring * 0.6 - Math.PI / 2;
      positions.push({ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) });
    }
    placed += count;
    ring++;
  }
  return { cx, cy, positions };
}

export function PipelineUniverse({ pipelines }: { pipelines: PipelineSummary[] }) {
  const reduce = useReducedMotion();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("All");
  const [sort, setSort] = useState<SortKey>("name");
  const [view, setView] = useState<"orbit" | "grid">("orbit");
  const [selected, setSelected] = useState<string | null>(pipelines[0]?.name ?? null);
  const [compare, setCompare] = useState<string[]>([]);

  const categories = useMemo(() => {
    const set = new Set(pipelines.map((p) => p.category));
    return ["All", ...[...set].sort()];
  }, [pipelines]);

  const sorted = useMemo(() => {
    const arr = [...pipelines];
    arr.sort((a, b) => {
      switch (sort) {
        case "parameters":
          return b.parameterCount - a.parameterCount;
        case "modules":
          return b.moduleCount - a.moduleCount;
        case "newest":
          return (
            (b.releaseDate ? +new Date(b.releaseDate) : 0) -
            (a.releaseDate ? +new Date(a.releaseDate) : 0)
          );
        default:
          return a.name.localeCompare(b.name);
      }
    });
    return arr;
  }, [pipelines, sort]);

  const matches = (p: PipelineSummary) => {
    const q = query.trim().toLowerCase();
    const inQuery =
      !q ||
      p.name.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q);
    const inCat = category === "All" || p.category === category;
    return inQuery && inCat;
  };

  const filtered = sorted.filter(matches);
  const selectedPipeline = pipelines.find((p) => p.name === selected) ?? null;

  const toggleCompare = (name: string) =>
    setCompare((c) =>
      c.includes(name) ? c.filter((n) => n !== name) : c.length >= 4 ? c : [...c, name],
    );

  const W = 760;
  const H = 560;
  const { cx, cy, positions } = useMemo(() => ringLayout(sorted.length, W, H), [sorted.length]);

  return (
    <div className="mt-12">
      {/* toolbar */}
      <div className="glass flex flex-col gap-4 p-4 md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search pipelines…"
            className="w-full rounded-xl border border-white/10 bg-ink-900/60 py-3 pl-11 pr-4 text-sm text-fog outline-none transition placeholder:text-fog-dim focus:border-claw-400/40 focus:bg-ink-900"
          />
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortKey)}
              className="appearance-none rounded-xl border border-white/10 bg-ink-900/60 py-3 pl-4 pr-9 text-sm text-fog-muted outline-none transition focus:border-claw-400/40"
            >
              <option value="name">Sort: Name</option>
              <option value="parameters">Sort: Parameters</option>
              <option value="modules">Sort: Modules</option>
              <option value="newest">Sort: Newest</option>
            </select>
            <SlidersHorizontal className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
          </div>
          <div className="flex rounded-xl border border-white/10 bg-ink-900/60 p-1">
            <ViewBtn active={view === "orbit"} onClick={() => setView("orbit")} label="Orbit">
              <Orbit className="h-4 w-4" />
            </ViewBtn>
            <ViewBtn active={view === "grid"} onClick={() => setView("grid")} label="Grid">
              <LayoutGrid className="h-4 w-4" />
            </ViewBtn>
          </div>
        </div>
      </div>

      {/* category chips */}
      <div className="mt-4 flex flex-wrap gap-2">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={cn(
              "rounded-full border px-3.5 py-1.5 text-xs font-medium transition",
              category === c
                ? "border-claw-400/40 bg-claw-500/15 text-claw-200"
                : "border-white/10 bg-white/[0.02] text-fog-muted hover:border-white/20 hover:text-fog",
            )}
          >
            {c}
            {c !== "All" && (
              <span className="ml-1.5 text-fog-dim">
                {pipelines.filter((p) => p.category === c).length}
              </span>
            )}
          </button>
        ))}
        <span className="ml-auto self-center text-xs text-fog-dim">
          {filtered.length} of {pipelines.length} shown
        </span>
      </div>

      {/* main */}
      <div className="mt-6 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        {/* visualization */}
        <div className="glass relative overflow-hidden p-2 sm:p-4">
          {view === "orbit" ? (
            <div className="relative">
              <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full">
                {/* connection lines */}
                {sorted.map((p, i) => {
                  const pos = positions[i];
                  const dim = !matches(p);
                  const isSel = p.name === selected;
                  return (
                    <motion.line
                      key={`l-${p.name}`}
                      x1={cx}
                      y1={cy}
                      x2={pos.x}
                      y2={pos.y}
                      stroke={isSel ? colorFor(p.category) : "#ffffff"}
                      strokeOpacity={dim ? 0.03 : isSel ? 0.4 : 0.07}
                      strokeWidth={isSel ? 1.4 : 1}
                      initial={reduce ? false : { pathLength: 0, opacity: 0 }}
                      whileInView={{ pathLength: 1, opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: 0.2 + i * 0.04 }}
                    />
                  );
                })}

                {/* center hub */}
                <g>
                  <circle cx={cx} cy={cy} r={34} fill="#0A0B0E" stroke="rgba(57,211,83,0.4)" strokeWidth={1} />
                  <circle cx={cx} cy={cy} r={34} fill="url(#hubGlow)" />
                  <text x={cx} y={cy - 2} textAnchor="middle" className="fill-fog font-mono" fontSize="12" fontWeight="600">
                    nf-claw
                  </text>
                  <text x={cx} y={cy + 13} textAnchor="middle" className="fill-current text-fog-dim" fontSize="9">
                    {pipelines.length} pipelines
                  </text>
                </g>
                <defs>
                  <radialGradient id="hubGlow">
                    <stop offset="0%" stopColor="rgba(57,211,83,0.25)" />
                    <stop offset="100%" stopColor="transparent" />
                  </radialGradient>
                </defs>

                {/* nodes */}
                {sorted.map((p, i) => {
                  const pos = positions[i];
                  const dim = !matches(p);
                  const isSel = p.name === selected;
                  const color = colorFor(p.category);
                  const r = sorted.length > 24 ? 7 : sorted.length > 12 ? 9 : 12;
                  return (
                    <motion.g
                      key={p.name}
                      style={{ cursor: "pointer" }}
                      onClick={() => setSelected(p.name)}
                      initial={reduce ? false : { scale: 0, opacity: 0 }}
                      whileInView={{ scale: 1, opacity: dim ? 0.25 : 1 }}
                      animate={{ opacity: dim ? 0.25 : 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.6, delay: 0.3 + i * 0.05, ease: [0.16, 1, 0.3, 1] }}
                      whileHover={{ scale: 1.25 }}
                    >
                      {isSel && (
                        <motion.circle
                          cx={pos.x}
                          cy={pos.y}
                          r={r + 6}
                          fill="none"
                          stroke={color}
                          strokeOpacity={0.5}
                          animate={reduce ? undefined : { r: [r + 4, r + 12], opacity: [0.5, 0] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                      )}
                      <circle cx={pos.x} cy={pos.y} r={r + 4} fill={color} opacity={0.12} />
                      <circle
                        cx={pos.x}
                        cy={pos.y}
                        r={r}
                        fill={color}
                        stroke={isSel ? "#fff" : "rgba(255,255,255,0.4)"}
                        strokeWidth={isSel ? 2 : 1}
                      />
                      {(sorted.length <= 16 || isSel) && (
                        <text
                          x={pos.x}
                          y={pos.y + r + 15}
                          textAnchor="middle"
                          className="fill-current font-mono"
                          fontSize="11"
                          fill={dim ? "#646B76" : "#F4F5F6"}
                        >
                          {p.name}
                        </text>
                      )}
                    </motion.g>
                  );
                })}
              </svg>
            </div>
          ) : (
            <div className="grid max-h-[560px] gap-3 overflow-y-auto p-1 sm:grid-cols-2">
              {filtered.map((p) => (
                <button
                  key={p.name}
                  onClick={() => setSelected(p.name)}
                  className={cn(
                    "group rounded-2xl border p-4 text-left transition",
                    p.name === selected
                      ? "border-claw-400/40 bg-claw-500/[0.06]"
                      : "border-white/[0.07] bg-white/[0.02] hover:border-white/20",
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-2 font-mono text-sm font-semibold text-fog">
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{ background: colorFor(p.category) }}
                      />
                      {p.name}
                    </span>
                    <span className="text-xs text-fog-dim">{p.version}</span>
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-fog-muted">
                    {p.description}
                  </p>
                  <div className="mt-3 flex gap-3 text-[11px] text-fog-dim">
                    <span>{p.parameterCount} params</span>
                    <span>{p.moduleCount} modules</span>
                  </div>
                </button>
              ))}
              {filtered.length === 0 && (
                <p className="col-span-full py-12 text-center text-sm text-fog-dim">
                  No pipelines match your search.
                </p>
              )}
            </div>
          )}
        </div>

        {/* inspector */}
        <div className="glass flex flex-col p-6">
          <AnimatePresence mode="wait">
            {selectedPipeline ? (
              <motion.div
                key={selectedPipeline.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="flex h-full flex-col"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ background: colorFor(selectedPipeline.category) }}
                  />
                  <span className="chip">{selectedPipeline.category}</span>
                  <span className="ml-auto font-mono text-sm text-fog-dim">
                    {selectedPipeline.version}
                  </span>
                </div>
                <h3 className="mt-4 font-mono text-2xl font-semibold text-fog">
                  {selectedPipeline.name}
                </h3>
                <p className="mt-1 text-xs text-fog-dim">{selectedPipeline.pipeline}</p>
                <p className="mt-4 text-sm leading-relaxed text-fog-muted">
                  {selectedPipeline.description}
                </p>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <Metric icon={<SlidersHorizontal className="h-4 w-4" />} value={selectedPipeline.parameterCount} label="parameters" />
                  <Metric icon={<Puzzle className="h-4 w-4" />} value={selectedPipeline.moduleCount} label="nf-core modules" />
                  <Metric icon={<GitBranch className="h-4 w-4" />} value={selectedPipeline.groupCount} label="param groups" />
                  <Metric icon={<Check className="h-4 w-4" />} value={selectedPipeline.requiredCount} label="required" />
                </div>

                {selectedPipeline.releaseDate && (
                  <p className="mt-4 text-xs text-fog-dim">
                    Pinned release · {formatDate(selectedPipeline.releaseDate)}
                    {selectedPipeline.policy && ` · ${selectedPipeline.policy}`}
                  </p>
                )}

                <div className="mt-auto flex flex-col gap-2 pt-6">
                  <Link
                    href={`/pipelines/${selectedPipeline.name}`}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-claw-500 px-4 py-3 text-sm font-semibold text-ink-950 transition hover:bg-claw-400"
                  >
                    Inspect pipeline
                    <ArrowUpRight className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => toggleCompare(selectedPipeline.name)}
                    className={cn(
                      "inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium transition",
                      compare.includes(selectedPipeline.name)
                        ? "border-claw-400/40 bg-claw-500/10 text-claw-200"
                        : "border-white/10 bg-white/[0.02] text-fog-muted hover:text-fog",
                    )}
                  >
                    {compare.includes(selectedPipeline.name) ? (
                      <>
                        <Check className="h-4 w-4" /> In comparison
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4" /> Add to compare
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            ) : (
              <p className="m-auto text-sm text-fog-dim">Select a pipeline to inspect.</p>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* compare tray */}
      <AnimatePresence>
        {compare.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="glass mt-6 overflow-hidden p-5"
          >
            <div className="mb-4 flex items-center justify-between">
              <h4 className="text-sm font-semibold text-fog">
                Comparing {compare.length} pipeline{compare.length > 1 ? "s" : ""}
              </h4>
              <button
                onClick={() => setCompare([])}
                className="inline-flex items-center gap-1 text-xs text-fog-dim hover:text-fog"
              >
                <X className="h-3.5 w-3.5" /> Clear
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wider text-fog-dim">
                    <th className="py-2 pr-4 font-medium">Metric</th>
                    {compare.map((name) => (
                      <th key={name} className="py-2 pr-4 font-mono font-medium text-fog">
                        {name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-fog-muted">
                  {(
                    [
                      ["Category", (p: PipelineSummary) => p.category],
                      ["Version", (p: PipelineSummary) => p.version],
                      ["Parameters", (p: PipelineSummary) => p.parameterCount],
                      ["Param groups", (p: PipelineSummary) => p.groupCount],
                      ["nf-core modules", (p: PipelineSummary) => p.moduleCount],
                      ["Required params", (p: PipelineSummary) => p.requiredCount],
                      ["Samplesheet cols", (p: PipelineSummary) => p.samplesheetCount],
                    ] as const
                  ).map(([label, accessor]) => (
                    <tr key={label} className="border-t border-white/[0.05]">
                      <td className="py-2.5 pr-4 text-fog-dim">{label}</td>
                      {compare.map((name) => {
                        const p = pipelines.find((x) => x.name === name)!;
                        return (
                          <td key={name} className="py-2.5 pr-4 text-fog">
                            {accessor(p)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ViewBtn({
  active,
  onClick,
  label,
  children,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition",
        active ? "bg-white/10 text-fog" : "text-fog-dim hover:text-fog",
      )}
    >
      {children}
    </button>
  );
}

function Metric({
  icon,
  value,
  label,
}: {
  icon: React.ReactNode;
  value: number;
  label: string;
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="flex items-center gap-2 text-claw-400/80">{icon}</div>
      <div className="mt-2 text-2xl font-semibold text-fog">{value}</div>
      <div className="text-[11px] text-fog-dim">{label}</div>
    </div>
  );
}
