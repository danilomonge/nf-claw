"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Sparkles, Boxes, Workflow, SlidersHorizontal, Puzzle } from "lucide-react";
import { Counter } from "@/components/ui/counter";
import type { RepoMeta } from "@/lib/types";
import { asset, formatDate } from "@/lib/utils";

const EASE = [0.16, 1, 0.3, 1] as const;

export function Hero({
  meta,
  latest,
}: {
  meta: RepoMeta;
  latest: { pipeline: string; version: string; date: string | null } | null;
}) {
  const reduce = useReducedMotion();
  const fade = (delay: number) => ({
    initial: reduce ? false : { opacity: 0, y: 24 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.9, ease: EASE, delay },
  });

  const stats = [
    { label: "Pipelines", value: meta.stats.pipelines, icon: Workflow },
    { label: "Agent skills", value: meta.stats.skills, icon: Boxes },
    { label: "Parameters", value: meta.stats.parameters, icon: SlidersHorizontal },
    { label: "nf-core modules", value: meta.stats.modules, icon: Puzzle },
  ];

  return (
    <section className="relative flex min-h-[100svh] flex-col items-center justify-center overflow-hidden px-6 pb-24 pt-28">
      {/* orbital rings behind logo */}
      <div aria-hidden className="pointer-events-none absolute left-1/2 top-[34%] -z-0 -translate-x-1/2 -translate-y-1/2">
        {[320, 520, 760].map((s, i) => (
          <motion.div
            key={s}
            className="absolute rounded-full border border-white/[0.05]"
            style={{ width: s, height: s, left: -s / 2, top: -s / 2 }}
            animate={reduce ? undefined : { rotate: i % 2 === 0 ? 360 : -360 }}
            transition={{ duration: 60 + i * 24, repeat: Infinity, ease: "linear" }}
          >
            <span
              className="absolute h-1.5 w-1.5 rounded-full bg-claw-400/70 shadow-[0_0_12px_2px_rgba(57,211,83,0.6)]"
              style={{ top: -3, left: "50%" }}
            />
          </motion.div>
        ))}
      </div>

      <div className="relative z-10 flex w-full max-w-4xl flex-col items-center text-center">
        {latest && (
          <motion.div {...fade(0)}>
            <Link
              href="/#releases"
              className="group mb-10 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] py-1.5 pl-1.5 pr-4 text-sm text-fog-muted backdrop-blur transition hover:border-claw-400/30"
            >
              <span className="inline-flex items-center gap-1.5 rounded-full bg-claw-500/15 px-2.5 py-1 text-xs font-medium text-claw-300">
                <Sparkles className="h-3 w-3" /> Latest
              </span>
              <span className="text-fog">
                {latest.pipeline} {latest.version}
              </span>
              {latest.date && (
                <span className="text-fog-dim">· {formatDate(latest.date)}</span>
              )}
              <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </motion.div>
        )}

        {/* brand mark */}
        <motion.div {...fade(0.05)} className="relative mb-9">
          <div className="absolute inset-0 -z-10 animate-pulse-ring rounded-3xl bg-claw-500/20 blur-2xl" />
          <div className="relative overflow-hidden rounded-[28px] ring-1 ring-white/10 shadow-glow">
            <Image
              src={asset("/nf-claw-logo.png")}
              alt="nf-claw"
              width={132}
              height={132}
              priority
              className="h-[112px] w-[112px] object-cover md:h-[132px] md:w-[132px]"
            />
          </div>
        </motion.div>

        <motion.p {...fade(0.1)} className="eyebrow mb-5">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-claw-400" />
          nf-claw
        </motion.p>

        <motion.h1
          {...fade(0.16)}
          className="text-balance text-5xl font-semibold leading-[1.02] tracking-tightest md:text-7xl"
        >
          <span className="gradient-text">{meta.tagline}</span>
        </motion.h1>

        <motion.p
          {...fade(0.24)}
          className="mt-7 max-w-2xl text-pretty text-lg leading-relaxed text-fog-muted md:text-xl"
        >
          {meta.description}
        </motion.p>

        <motion.div
          {...fade(0.32)}
          className="mt-10 flex flex-col items-center gap-3 sm:flex-row"
        >
          <Link
            href="/#pipelines"
            className="group inline-flex items-center gap-2 rounded-full bg-claw-500 px-7 py-3.5 text-sm font-semibold text-ink-950 transition hover:bg-claw-400 hover:shadow-[0_12px_40px_-12px_rgba(57,211,83,0.6)]"
          >
            Explore the universe
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            href="/#docs"
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-7 py-3.5 text-sm font-semibold text-fog transition hover:border-white/20 hover:bg-white/[0.06]"
          >
            Read the docs
          </Link>
        </motion.div>

        {/* stats */}
        <motion.div
          {...fade(0.42)}
          className="mt-16 grid w-full grid-cols-2 gap-3 sm:gap-4 md:grid-cols-4"
        >
          {stats.map((s) => (
            <div
              key={s.label}
              className="glass glass-hover flex flex-col items-center px-4 py-5"
            >
              <s.icon className="mb-3 h-5 w-5 text-claw-400/80" />
              <div className="text-3xl font-semibold tracking-tight text-fog md:text-4xl">
                <Counter value={s.value} />
              </div>
              <div className="mt-1 text-xs uppercase tracking-[0.16em] text-fog-dim">
                {s.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* scroll cue */}
      <motion.div
        aria-hidden
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 1 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <div className="flex h-9 w-5 items-start justify-center rounded-full border border-white/15 p-1.5">
          <motion.span
            className="h-1.5 w-1 rounded-full bg-claw-400"
            animate={reduce ? undefined : { y: [0, 8, 0] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
      </motion.div>
    </section>
  );
}
