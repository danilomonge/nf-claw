"use client";

import { useState } from "react";
import { Check, Copy, TerminalSquare } from "lucide-react";
import { cn } from "@/lib/utils";

/** Minimal shell-flavoured syntax accents for command strings. */
function highlight(line: string) {
  if (!line.trim()) return <span>&nbsp;</span>;
  const comment = line.match(/^(\s*#.*)$/);
  if (comment) return <span className="text-fog-dim italic">{line}</span>;

  const tokens = line.split(/(\s+)/);
  return tokens.map((tok, i) => {
    if (/^\s+$/.test(tok)) return <span key={i}>{tok}</span>;
    if (i === 0) return <span key={i} className="text-claw-300">{tok}</span>;
    if (tok.startsWith("--") || tok.startsWith("-"))
      return <span key={i} className="text-cream">{tok}</span>;
    if (["run", "list"].includes(tok))
      return <span key={i} className="text-white">{tok}</span>;
    return <span key={i} className="text-fog-muted">{tok}</span>;
  });
}

export function CodeBlock({
  code,
  label = "shell",
  className,
}: {
  code: string;
  label?: string;
  className?: string;
}) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className={cn("group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-ink-950/80", className)}>
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2.5">
        <span className="flex items-center gap-2 text-xs font-medium text-fog-dim">
          <TerminalSquare className="h-3.5 w-3.5" />
          {label}
        </span>
        <button
          onClick={copy}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-fog-dim transition hover:bg-white/5 hover:text-fog"
          aria-label="Copy to clipboard"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-claw-400" /> Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" /> Copy
            </>
          )}
        </button>
      </div>
      <pre className="overflow-x-auto px-4 py-3.5 font-mono text-[13px] leading-relaxed">
        <code>
          {code.split("\n").map((line, i) => (
            <div key={i}>{highlight(line)}</div>
          ))}
        </code>
      </pre>
    </div>
  );
}
