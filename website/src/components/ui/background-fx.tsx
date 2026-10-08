"use client";

import { useEffect, useRef } from "react";

/**
 * Ambient page backdrop: a faint grid, slow-breathing brand glows and a subtle pointer-follow
 * light. Purely decorative, fixed behind all content. The same pointer listener feeds the
 * card spotlight: it sets --sx/--sy on the `.glass-hover` card under the pointer.
 */
export function BackgroundFX() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (!window.matchMedia("(pointer: fine)").matches) return;
    let raf = 0;
    let last: PointerEvent | null = null;
    const frame = () => {
      raf = 0;
      if (!last) return;
      const e = last;
      el.style.setProperty("--mx", `${e.clientX}px`);
      el.style.setProperty("--my", `${e.clientY}px`);
      const card = (e.target as Element | null)?.closest?.(".glass-hover") as HTMLElement | null;
      if (card) {
        const r = card.getBoundingClientRect();
        card.style.setProperty("--sx", `${e.clientX - r.left}px`);
        card.style.setProperty("--sy", `${e.clientY - r.top}px`);
      }
    };
    const onMove = (e: PointerEvent) => {
      last = e;
      if (!raf) raf = requestAnimationFrame(frame);
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
      <div className="mask-fade-b absolute inset-0 bg-grid-faint opacity-60 [background-size:64px_64px]" />
      {/* brand glows */}
      <div className="absolute -top-40 left-1/2 h-[640px] w-[900px] -translate-x-1/2 animate-float rounded-full bg-claw-500/[0.07] blur-[140px]" />
      <div className="absolute bottom-0 right-[-10%] h-[520px] w-[620px] rounded-full bg-claw-700/[0.06] blur-[150px]" />
      <div className="absolute left-[-8%] top-1/3 h-[420px] w-[420px] rounded-full bg-cream/[0.03] blur-[150px]" />
      {/* pointer light */}
      <div
        ref={ref}
        className="absolute inset-0 opacity-70"
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
