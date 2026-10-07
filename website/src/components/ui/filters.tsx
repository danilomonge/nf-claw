"use client";

import { Search, X } from "lucide-react";
import { colorForCategory } from "@/lib/derive";
import { cn } from "@/lib/utils";

/** The search box every explorer uses: icon, Escape to clear, and a clear button once typed in. */
export function SearchField({
  value,
  onChange,
  placeholder,
  label,
  className,
  onFocus,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  className?: string;
  onFocus?: () => void;
}) {
  return (
    <div className={cn("relative", className)}>
      <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Escape" && onChange("")}
        onFocus={onFocus}
        placeholder={placeholder}
        aria-label={label}
        className="field"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-3 top-1/2 inline-flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-md text-fog-dim transition hover:bg-white/5 hover:text-fog"
          aria-label="Clear search"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}

/**
 * A row of research-domain filter pills ("All" first). It scrolls sideways on small screens and
 * wraps from `wrapFrom` up. Clicking the active domain again returns to "All".
 */
export function DomainChips({
  domains,
  total,
  value,
  onChange,
  onHover,
  wrapFrom = "md",
}: {
  domains: { name: string; count: number }[];
  total: number;
  value: string;
  onChange: (domain: string) => void;
  onHover?: (domain: string | null) => void;
  wrapFrom?: "md" | "lg";
}) {
  return (
    <div
      className={cn(
        "mask-fade-r scrollbar-none -mx-1 flex gap-2 overflow-x-auto px-1 py-0.5",
        wrapFrom === "md" ? "md:mask-none md:flex-wrap md:overflow-visible" : "lg:mask-none lg:flex-wrap lg:overflow-visible",
      )}
    >
      {[{ name: "All", count: total }, ...domains].map((d) => {
        const on = value === d.name;
        return (
          <button
            key={d.name}
            onClick={() => onChange(on && d.name !== "All" ? "All" : d.name)}
            onMouseEnter={onHover && d.name !== "All" ? () => onHover(d.name) : undefined}
            onMouseLeave={onHover ? () => onHover(null) : undefined}
            aria-pressed={on}
            className={cn("pill", on ? "pill-on" : "pill-off")}
          >
            {d.name !== "All" && <span className="h-2 w-2 rounded-full" style={{ background: colorForCategory(d.name) }} />}
            {d.name}
            <span className={cn("tabular-nums", on ? "text-claw-200/70" : "text-fog-dim")}>{d.count}</span>
          </button>
        );
      })}
    </div>
  );
}
