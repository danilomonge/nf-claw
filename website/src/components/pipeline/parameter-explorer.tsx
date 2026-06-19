"use client";

import { useMemo, useState } from "react";
import { ChevronDown, Code2, Eye, EyeOff, Search, Star } from "lucide-react";
import type { ParamLite, SkillGroupLite } from "@/lib/derive";
import { cn, humanize } from "@/lib/utils";

export function ParameterExplorer({
  params,
  groups,
  schemaUrl,
  initialQuery = "",
  compact = false,
}: {
  params: ParamLite[];
  groups: SkillGroupLite[];
  schemaUrl: string | null;
  initialQuery?: string;
  compact?: boolean;
}) {
  const [query, setQuery] = useState(initialQuery);
  const [group, setGroup] = useState("All");
  const [requiredOnly, setRequiredOnly] = useState(false);
  const [showHidden, setShowHidden] = useState(false);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return params.filter((p) => {
      if (!showHidden && p.hidden) return false;
      if (requiredOnly && !p.required) return false;
      if (group !== "All" && p.group !== group) return false;
      if (!q) return true;
      return (
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.allowed.join(" ").toLowerCase().includes(q) ||
        p.group.toLowerCase().includes(q)
      );
    });
  }, [params, query, group, requiredOnly, showHidden]);

  const hiddenCount = params.filter((p) => p.hidden).length;

  return (
    <div>
      <div className="glass flex flex-col gap-3 p-4 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search parameters, values, descriptions…"
            className="w-full rounded-xl border border-white/10 bg-ink-900/60 py-3 pl-11 pr-4 text-sm text-fog outline-none transition placeholder:text-fog-dim focus:border-claw-400/40 focus:bg-ink-900"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <select
              value={group}
              onChange={(e) => setGroup(e.target.value)}
              className="max-w-[200px] appearance-none rounded-xl border border-white/10 bg-ink-900/60 py-3 pl-4 pr-9 text-sm text-fog-muted outline-none transition focus:border-claw-400/40"
            >
              <option value="All">All groups</option>
              {groups.map((g) => (
                <option key={g.name} value={g.name}>
                  {g.title} ({g.count})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-fog-dim" />
          </div>
          <Toggle active={requiredOnly} onClick={() => setRequiredOnly((v) => !v)}>
            <Star className="h-3.5 w-3.5" /> Required
          </Toggle>
          {hiddenCount > 0 && (
            <Toggle active={showHidden} onClick={() => setShowHidden((v) => !v)}>
              {showHidden ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
              Hidden
            </Toggle>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between px-1 text-xs text-fog-dim">
        <span>
          {filtered.length} parameter{filtered.length !== 1 ? "s" : ""}
          {!showHidden && hiddenCount > 0 && ` · ${hiddenCount} hidden`}
        </span>
        {schemaUrl && (
          <a
            href={schemaUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-fog-dim transition hover:text-claw-300"
          >
            <Code2 className="h-3.5 w-3.5" /> nextflow_schema.json
          </a>
        )}
      </div>

      <div className={cn("mt-3 space-y-2", compact && "max-h-[520px] overflow-y-auto pr-1")}>
        {filtered.map((p) => (
          <ParamRow key={`${p.group}-${p.name}`} param={p} />
        ))}
        {filtered.length === 0 && (
          <p className="py-12 text-center text-sm text-fog-dim">No parameters match.</p>
        )}
      </div>
    </div>
  );
}

function ParamRow({ param }: { param: ParamLite }) {
  const [open, setOpen] = useState(false);
  const expandable = Boolean(param.description || param.allowed.length || param.constraints || param.default);
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] transition hover:border-white/12">
      <button
        onClick={() => expandable && setOpen((v) => !v)}
        className="flex w-full items-start gap-3 p-4 text-left"
      >
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <code className="font-mono text-sm font-medium text-fog">{param.name}</code>
            <span className="chip text-[10px]">{param.type}</span>
            {param.required && (
              <span className="rounded-md border border-claw-400/20 bg-claw-500/15 px-1.5 py-0.5 text-[10px] font-medium text-claw-300">
                required
              </span>
            )}
            {param.hidden && (
              <span className="rounded-md border border-white/10 bg-white/[0.03] px-1.5 py-0.5 text-[10px] text-fog-dim">
                hidden
              </span>
            )}
            <span className="ml-1 text-[10px] uppercase tracking-wider text-fog-dim">
              {humanize(param.group)}
            </span>
          </div>
          {param.description && (
            <p className={cn("mt-1.5 text-sm leading-relaxed text-fog-muted", !open && "line-clamp-1")}>
              {param.description}
            </p>
          )}
        </div>
        {expandable && (
          <ChevronDown
            className={cn("mt-1 h-4 w-4 shrink-0 text-fog-dim transition-transform", open && "rotate-180")}
          />
        )}
      </button>
      {open && (
        <div className="grid gap-3 border-t border-white/[0.05] px-4 py-3.5 text-xs sm:grid-cols-3">
          <Field label="Default">
            {param.default ? (
              <code className="font-mono text-cream">{param.default}</code>
            ) : (
              <span className="text-fog-dim">—</span>
            )}
          </Field>
          <Field label="Constraints">
            {param.constraints ? (
              <span className="text-fog-muted">{param.constraints}</span>
            ) : (
              <span className="text-fog-dim">—</span>
            )}
          </Field>
          <Field label="Allowed values">
            {param.allowed.length ? (
              <span className="flex flex-wrap gap-1">
                {param.allowed.map((a) => (
                  <code
                    key={a}
                    className="rounded bg-white/[0.05] px-1.5 py-0.5 font-mono text-[11px] text-fog"
                  >
                    {a}
                  </code>
                ))}
              </span>
            ) : (
              <span className="text-fog-dim">any</span>
            )}
          </Field>
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1 text-[10px] uppercase tracking-wider text-fog-dim">{label}</div>
      <div>{children}</div>
    </div>
  );
}

function Toggle({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-xl border px-3 py-2.5 text-xs font-medium transition",
        active
          ? "border-claw-400/40 bg-claw-500/15 text-claw-200"
          : "border-white/10 bg-ink-900/60 text-fog-muted hover:text-fog",
      )}
    >
      {children}
    </button>
  );
}
