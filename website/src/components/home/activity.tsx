import {
  Activity,
  CalendarClock,
  CircleDot,
  GitCommitHorizontal,
  PlayCircle,
  ShieldCheck,
  Workflow as WorkflowIcon,
} from "lucide-react";
import { Reveal } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Commit, Workflow } from "@/lib/types";
import type { LiveRun } from "@/lib/data/github";
import { commitTone, humanizeCron, TONE_CLASS } from "@/lib/format";
import { timeAgo, cn } from "@/lib/utils";

export function LiveStatus({
  commits,
  workflows,
  liveRuns,
  lastUpdate,
}: {
  commits: Commit[];
  workflows: Workflow[];
  liveRuns: LiveRun[] | null;
  lastUpdate: string | null;
}) {
  const autoUpdate = workflows.find((w) => w.schedule);
  const cron = humanizeCron(autoUpdate?.schedule ?? null);

  return (
    <section id="activity" className="container-site scroll-mt-24 py-24 md:py-32">
      <SectionHeading
        eyebrow="Always in sync"
        title="Live repository status"
        description="Commits, automation and release activity — read straight from git and GitHub Actions. When the repository changes, this view changes with it."
      />

      {/* status strip */}
      <Reveal className="mt-10">
        <div className="grid gap-3 sm:grid-cols-3">
          <StatusTile
            icon={<CalendarClock className="h-4 w-4" />}
            label="Auto-update"
            value={cron ?? "On demand"}
            sub={autoUpdate ? autoUpdate.name : "scheduled workflow"}
            live
          />
          <StatusTile
            icon={<ShieldCheck className="h-4 w-4" />}
            label="Drift gate"
            value={workflows.some((w) => /drift/i.test(w.name)) ? "Enforced on every PR" : "Configured"}
            sub="context matches the pinned submodule"
            live
          />
          <StatusTile
            icon={<Activity className="h-4 w-4" />}
            label="Last update"
            value={lastUpdate ? timeAgo(lastUpdate) : "—"}
            sub="most recent commit"
            live
          />
        </div>
      </Reveal>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        {/* commit feed */}
        <Reveal>
          <div className="glass h-full p-6">
            <div className="mb-5 flex items-center gap-2">
              <GitCommitHorizontal className="h-4 w-4 text-claw-400" />
              <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-fog-dim">
                Update history
              </h3>
            </div>
            <ol className="relative space-y-1 before:absolute before:left-[5px] before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-white/[0.07]">
              {commits.map((c) => (
                <li key={c.hash} className="relative flex gap-4 py-2.5 pl-6">
                  <span className="absolute left-0 top-3.5 h-2.5 w-2.5 rounded-full border-2 border-ink-900 bg-claw-500/80" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      {c.type && (
                        <span
                          className={cn(
                            "rounded-md border px-1.5 py-0.5 text-[10px] font-medium",
                            TONE_CLASS[commitTone(c.type)],
                          )}
                        >
                          {c.type}
                          {c.scope ? `(${c.scope})` : ""}
                        </span>
                      )}
                      <span className="truncate text-sm text-fog">{stripPrefix(c.subject)}</span>
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-xs text-fog-dim">
                      <span className="font-mono">{c.hash}</span>
                      <span>·</span>
                      <span>{c.author}</span>
                      <span>·</span>
                      <span>{timeAgo(c.date)}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </Reveal>

        {/* automation + runs */}
        <div className="flex flex-col gap-6">
          <Reveal delay={0.05}>
            <div className="glass p-6">
              <div className="mb-5 flex items-center gap-2">
                <WorkflowIcon className="h-4 w-4 text-claw-400" />
                <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-fog-dim">
                  CI / CD workflows
                </h3>
              </div>
              <div className="space-y-3">
                {workflows.map((w) => (
                  <div
                    key={w.file}
                    className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 font-mono text-sm text-fog">
                        <CircleDot className="h-3.5 w-3.5 text-claw-400" />
                        {w.name}
                      </span>
                      <span className="text-[11px] text-fog-dim">{w.jobs.length} job{w.jobs.length !== 1 ? "s" : ""}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {w.triggers.map((t) => (
                        <span key={t} className="chip text-[10px]">
                          {t.replace(/_/g, " ")}
                        </span>
                      ))}
                      {w.schedule && (
                        <span className="chip text-[10px] text-cream">
                          {humanizeCron(w.schedule)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>

          {liveRuns && liveRuns.length > 0 && (
            <Reveal delay={0.1}>
              <div className="glass p-6">
                <div className="mb-5 flex items-center gap-2">
                  <PlayCircle className="h-4 w-4 text-claw-400" />
                  <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-fog-dim">
                    Recent runs
                  </h3>
                </div>
                <div className="space-y-2">
                  {liveRuns.map((r, i) => (
                    <a
                      key={i}
                      href={r.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2.5 text-sm transition hover:border-white/15"
                    >
                      <span className="flex items-center gap-2 text-fog">
                        <RunDot conclusion={r.conclusion} status={r.status} />
                        {r.name}
                      </span>
                      <span className="text-xs text-fog-dim">{timeAgo(r.date)}</span>
                    </a>
                  ))}
                </div>
              </div>
            </Reveal>
          )}
        </div>
      </div>
    </section>
  );
}

function StatusTile({
  icon,
  label,
  value,
  sub,
  live,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub: string;
  live?: boolean;
}) {
  return (
    <div className="glass glass-hover p-5">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-fog-dim">
          {icon}
          {label}
        </span>
        {live && (
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-claw-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-claw-400" />
          </span>
        )}
      </div>
      <div className="mt-3 text-lg font-semibold text-fog">{value}</div>
      <div className="mt-0.5 text-xs text-fog-dim">{sub}</div>
    </div>
  );
}

function RunDot({ conclusion, status }: { conclusion: string | null; status: string }) {
  const ok = conclusion === "success";
  const fail = conclusion === "failure" || conclusion === "cancelled";
  const running = status === "in_progress" || status === "queued";
  const color = ok ? "bg-claw-400" : fail ? "bg-red-400" : running ? "bg-cream" : "bg-fog-dim";
  return <span className={cn("h-2.5 w-2.5 rounded-full", color)} />;
}

function stripPrefix(subject: string) {
  return subject.replace(/^(\w+)(\([^)]+\))?!?:\s*/, "");
}
