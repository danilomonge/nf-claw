"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { Tag, Rocket, Sparkles } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";

export interface TimelineItem {
  id: string;
  kind: "release" | "tag" | "milestone";
  title: string;
  subtitle: string;
  date: string | null;
  version?: string;
  pipeline?: string;
  accent: string;
}

export function ReleaseTimeline({ items }: { items: TimelineItem[] }) {
  const reduce = useReducedMotion();
  const [filter, setFilter] = useState<"all" | "release" | "tag">("all");

  const hasTags = items.some((i) => i.kind === "tag");
  const filtered = useMemo(
    () => items.filter((i) => filter === "all" || i.kind === filter),
    [items, filter],
  );

  return (
    <div className="mt-12">
      {hasTags && (
        <div className="mb-8 flex gap-2">
          {(["all", "release", "tag"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-full border px-4 py-2 text-xs font-medium capitalize transition",
                filter === f
                  ? "border-claw-400/40 bg-claw-500/15 text-claw-200"
                  : "border-white/10 bg-white/[0.02] text-fog-muted hover:text-fog",
              )}
            >
              {f === "all" ? "All" : `${f}s`}
            </button>
          ))}
        </div>
      )}

      <div className="relative">
        {/* center spine */}
        <div className="absolute left-4 top-0 h-full w-px bg-gradient-to-b from-claw-400/40 via-white/10 to-transparent md:left-1/2" />

        <div className="space-y-8">
          {filtered.map((item, i) => {
            const side = i % 2 === 0;
            return (
              <motion.div
                key={item.id}
                initial={reduce ? false : { opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                className={cn(
                  "relative pl-12 md:w-1/2 md:pl-0",
                  side ? "md:pr-12 md:text-right" : "md:ml-auto md:pl-12",
                )}
              >
                {/* node */}
                <span
                  className={cn(
                    "absolute top-5 z-10 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-ink-900",
                    "left-0 md:left-auto",
                    side ? "md:-right-4" : "md:-left-4",
                  )}
                  style={{ boxShadow: `0 0 0 4px rgba(7,8,10,1), 0 0 18px ${item.accent}55` }}
                >
                  {item.kind === "release" ? (
                    <Rocket className="h-3.5 w-3.5" style={{ color: item.accent }} />
                  ) : item.kind === "tag" ? (
                    <Tag className="h-3.5 w-3.5" style={{ color: item.accent }} />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5" style={{ color: item.accent }} />
                  )}
                </span>

                <div className="glass glass-hover p-5">
                  <div
                    className={cn(
                      "flex items-center gap-2",
                      side ? "md:justify-end" : "",
                    )}
                  >
                    <span
                      className="rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                      style={{ background: `${item.accent}1a`, color: item.accent }}
                    >
                      {item.date ? formatDate(item.date) : "unreleased"}
                    </span>
                    <span className="text-[11px] uppercase tracking-wider text-fog-dim">
                      {item.kind}
                    </span>
                  </div>
                  <h3 className="mt-2 font-mono text-base font-semibold text-fog">
                    {item.pipeline ? (
                      <Link href={`/pipelines/${item.pipeline}`} className="hover:text-claw-300">
                        {item.title}
                      </Link>
                    ) : (
                      item.title
                    )}
                  </h3>
                  <p className={cn("mt-1.5 text-sm leading-relaxed text-fog-muted", side && "md:ml-auto")}>
                    {item.subtitle}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
