"use client";

import { useEffect, useRef } from "react";

/**
 * Ambient page backdrop: a faint grid, two slow-breathing brand glows and a
 * subtle pointer-follow light. Purely decorative, fixed behind all content.
 */
export function BackgroundFX() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    const onMove = (e: PointerEvent) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty("--mx", `${e.clientX}px`);
        el.style.setProperty("--my", `${e.clientY}px`);
      });
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* base wash */}
      <div className="absolute inset-0 bg-ink" />
      {/* grid */}
      <div className="absolute inset-0 bg-grid-faint [background-size:64px_64px] opacity-60 mask-fade-b" />
      {/* brand glows */}
      <div className="absolute -top-40 left-1/2 h-[640px] w-[900px] -translate-x-1/2 rounded-full bg-claw-500/[0.07] blur-[140px] animate-float" />
      <div className="absolute bottom-0 right-[-10%] h-[520px] w-[620px] rounded-full bg-claw-700/[0.06] blur-[150px]" />
      <div className="absolute left-[-8%] top-1/3 h-[420px] w-[420px] rounded-full bg-cream/[0.03] blur-[150px]" />
      {/* pointer light */}
      <div
        ref={ref}
        className="absolute inset-0 opacity-70 transition-opacity"
        style={{
          background:
            "radial-gradient(420px circle at var(--mx, 50%) var(--my, 30%), rgba(57,211,83,0.06), transparent 70%)",
        }}
      />
      {/* film grain */}
      <div className="noise absolute inset-0 opacity-[0.025] mix-blend-soft-light" />
      {/* vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_55%,rgba(0,0,0,0.55))]" />
    </div>
  );
}
