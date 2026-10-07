"use client";

import { useEffect, useState } from "react";
import { useReducedMotion } from "framer-motion";
import { ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * A quiet "back to top" control that appears once the reader is well into a long page. It lives in
 * the layout, so it hides on every navigation: it is shown/hidden with CSS, not unmounted through an
 * exit animation (one cut short by a route change left an invisible button over the page).
 */
export function BackToTop() {
  const [show, setShow] = useState(false);
  const reduce = useReducedMotion();

  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > window.innerHeight * 1.5);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" })}
      aria-label="Back to top"
      tabIndex={show ? 0 : -1}
      aria-hidden={!show}
      className={cn(
        "fixed bottom-5 right-5 z-40 inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-ink-900/80 text-fog-muted shadow-[0_12px_40px_-12px_rgba(0,0,0,0.8)] backdrop-blur-xl transition-[opacity,transform,visibility,color,border-color] duration-300 ease-out hover:border-claw-400/30 hover:text-claw-300 md:bottom-8 md:right-8",
        show ? "visible translate-y-0 scale-100 opacity-100" : "pointer-events-none invisible translate-y-3 scale-90 opacity-0",
      )}
    >
      <ArrowUp className="h-4 w-4" />
    </button>
  );
}
