"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

export interface SectionLink {
  id: string;
  label: string;
  count?: number;
}

/**
 * A sticky "on this page" bar: one chip per section, the one being read highlighted as you scroll,
 * and a click scrolls there. It sits just under the site header and scrolls sideways on a phone.
 */
export function SectionNav({ sections, className }: { sections: SectionLink[]; className?: string }) {
  const [active, setActive] = useState<string>(sections[0]?.id ?? "");
  const [stuck, setStuck] = useState(false);
  const barRef = useRef<HTMLDivElement>(null);
  const sentinel = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    const seen = new Map<string, boolean>();
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) seen.set(e.target.id, e.isIntersecting);
        const current = sections.find((s) => seen.get(s.id));
        if (current) setActive(current.id);
      },
      { rootMargin: "-120px 0px -60% 0px" },
    );
    for (const s of sections) {
      const el = document.getElementById(s.id);
      if (el) io.observe(el);
    }
    return () => io.disconnect();
  }, [sections]);

  // Detect when the bar is pinned, to give it a backdrop only then.
  useEffect(() => {
    const el = sentinel.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setStuck(!e.isIntersecting), { rootMargin: "-65px 0px 0px 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  // Keep the active chip in view inside the horizontally scrolling bar.
  useEffect(() => {
    barRef.current
      ?.querySelector<HTMLElement>(`[data-section="${active}"]`)
      ?.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reduce ? "auto" : "smooth" });
  }, [active, reduce]);

  const go = (id: string) => {
    setActive(id);
    document.getElementById(id)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    history.replaceState(null, "", `#${id}`);
  };

  return (
    <>
      <div ref={sentinel} aria-hidden className="h-px" />
      <nav
        aria-label="On this page"
        className={cn(
          "sticky top-16 z-30 -mx-5 border-b px-5 py-2.5 transition-[background-color,border-color] duration-300 sm:-mx-6 sm:px-6 md:-mx-10 md:px-10",
          stuck ? "border-white/[0.06] bg-ink-950/80 backdrop-blur-xl" : "border-transparent",
          className,
        )}
      >
        <div ref={barRef} className="scrollbar-none flex gap-1 overflow-x-auto">
          {sections.map((s) => {
            const on = s.id === active;
            return (
              <a
                key={s.id}
                href={`#${s.id}`}
                data-section={s.id}
                onClick={(e) => {
                  e.preventDefault();
                  go(s.id);
                }}
                aria-current={on ? "location" : undefined}
                className={cn(
                  "relative isolate shrink-0 whitespace-nowrap rounded-full px-3.5 py-1.5 text-sm transition-colors",
                  on ? "text-fog" : "text-fog-dim hover:text-fog",
                )}
              >
                {on && (
                  <motion.span
                    layoutId="section-pill"
                    className="absolute inset-0 -z-10 rounded-full border border-white/[0.08] bg-white/[0.06]"
                    transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 420, damping: 36 }}
                  />
                )}
                {s.label}
                {s.count !== undefined && <span className="ml-1.5 text-xs text-fog-dim">{s.count}</span>}
              </a>
            );
          })}
        </div>
      </nav>
    </>
  );
}
