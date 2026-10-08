"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { DocHeading } from "@/lib/doc-meta";
import { cn } from "@/lib/utils";

/** "On this page": the document's headings, with the one being read marked as you scroll. */
export function DocToc({ headings }: { headings: DocHeading[] }) {
  const [active, setActive] = useState<string | null>(headings[0]?.id ?? null);
  const reduce = useReducedMotion();

  useEffect(() => {
    const els = headings.map((h) => document.getElementById(h.id)).filter((e): e is HTMLElement => Boolean(e));
    if (!els.length) return;
    // The active heading is the last one scrolled past the top third of the viewport.
    const update = () => {
      const line = window.innerHeight * 0.3;
      let current = els[0].id;
      for (const el of els) {
        if (el.getBoundingClientRect().top <= line) current = el.id;
        else break;
      }
      setActive(current);
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [headings]);

  if (!headings.length) return null;

  return (
    <nav aria-label="On this page">
      <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-fog-dim">On this page</p>
      <ul className="relative space-y-0.5 border-l border-white/[0.07]">
        {headings.map((h) => {
          const on = h.id === active;
          return (
            <li key={h.id} className="relative">
              {on && (
                <motion.span
                  layoutId="toc-active"
                  className="absolute -left-px top-1 bottom-1 w-px bg-claw-400"
                  transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 500, damping: 40 }}
                />
              )}
              <a
                href={`#${h.id}`}
                aria-current={on ? "location" : undefined}
                className={cn(
                  "block py-1 text-[13px] leading-snug transition-colors",
                  h.depth === 3 ? "pl-6" : "pl-3.5",
                  on ? "text-fog" : "text-fog-dim hover:text-fog-muted",
                )}
              >
                {h.text}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
