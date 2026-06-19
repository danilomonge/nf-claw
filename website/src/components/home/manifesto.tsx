"use client";

import { motion, useReducedMotion } from "framer-motion";
import { GitBranch, RefreshCw, ShieldCheck } from "lucide-react";
import type { PipelineSummary } from "@/lib/derive";
import { colorForCategory } from "@/lib/derive";

const PRINCIPLES = [
  {
    icon: GitBranch,
    title: "Pinned, unmodified",
    body: "Every pipeline is an nf-core release pinned as a git submodule — wrapped, never forked.",
  },
  {
    icon: RefreshCw,
    title: "Generated context",
    body: "skill.md and the full parameter reference are generated from the pinned schema, not written by hand.",
  },
  {
    icon: ShieldCheck,
    title: "Drift-gated",
    body: "A CI gate guarantees the published context always matches the pinned submodule — this site included.",
  },
];

export function Manifesto({ pipelines }: { pipelines: PipelineSummary[] }) {
  const reduce = useReducedMotion();
  const track = [...pipelines, ...pipelines];

  return (
    <section className="relative border-y border-white/[0.06] py-16">
      {/* marquee of pipeline names */}
      <div className="mask-fade-x relative overflow-hidden">
        <div
          className="flex w-max gap-8 will-change-transform"
          style={reduce ? undefined : { animation: "marquee 36s linear infinite" }}
        >
          {track.map((p, i) => (
            <span key={`${p.name}-${i}`} className="flex items-center gap-3 whitespace-nowrap">
              <span
                className="h-2 w-2 rounded-full"
                style={{ background: colorForCategory(p.category) }}
              />
              <span className="font-mono text-2xl font-semibold text-fog/70">{p.name}</span>
              <span className="text-sm text-fog-dim">{p.category}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="container-site mt-14 grid gap-5 md:grid-cols-3">
        {PRINCIPLES.map((p, i) => (
          <motion.div
            key={p.title}
            initial={reduce ? false : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.6, delay: i * 0.08 }}
            className="flex gap-4"
          >
            <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-claw-400">
              <p.icon className="h-5 w-5" />
            </span>
            <div>
              <h3 className="text-sm font-semibold text-fog">{p.title}</h3>
              <p className="mt-1 text-sm leading-relaxed text-fog-muted">{p.body}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
