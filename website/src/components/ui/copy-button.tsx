"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

/** Copy text to the clipboard; `copied` stays true for a moment afterwards. */
export function useCopy(timeout = 1600) {
  const [copied, setCopied] = useState(false);
  const timer = useRef<number | undefined>(undefined);
  useEffect(() => () => window.clearTimeout(timer.current), []);
  const copy = useCallback(
    async (text: string) => {
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        // Clipboard API unavailable (insecure context): fall back to a hidden selection.
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try {
          document.execCommand("copy");
        } finally {
          ta.remove();
        }
      }
      setCopied(true);
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setCopied(false), timeout);
    },
    [timeout],
  );
  return { copied, copy };
}

/** An icon-and-label copy control whose icon swaps to a check once copied. */
export function CopyButton({
  text,
  label = "Copy",
  className,
  iconOnly = false,
}: {
  text: string;
  label?: string;
  className?: string;
  iconOnly?: boolean;
}) {
  const { copied, copy } = useCopy();
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        void copy(text);
      }}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-fog-dim transition hover:bg-white/5 hover:text-fog",
        className,
      )}
      aria-label={copied ? "Copied" : `${label}: ${text}`}
      title={copied ? "Copied" : label}
    >
      <span className="relative inline-flex h-3.5 w-3.5">
        <AnimatePresence initial={false} mode="popLayout">
          {copied ? (
            <motion.span
              key="ok"
              initial={{ scale: 0.4, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.4, opacity: 0 }}
              transition={{ duration: 0.18 }}
              className="absolute inset-0"
            >
              <Check className="h-3.5 w-3.5 text-claw-400" />
            </motion.span>
          ) : (
            <motion.span
              key="copy"
              initial={{ scale: 0.4, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.4, opacity: 0 }}
              transition={{ duration: 0.18 }}
              className="absolute inset-0"
            >
              <Copy className="h-3.5 w-3.5" />
            </motion.span>
          )}
        </AnimatePresence>
      </span>
      {!iconOnly && <span aria-live="polite">{copied ? "Copied" : label}</span>}
    </button>
  );
}
