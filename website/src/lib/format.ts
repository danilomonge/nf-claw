/** Humanize a 5-field cron expression for the common cases the repo uses. */
export function humanizeCron(cron: string | null): string | null {
  if (!cron) return null;
  const parts = cron.trim().split(/\s+/);
  if (parts.length < 5) return cron;
  const [min, hour, dom, mon, dow] = parts;
  const time =
    hour !== "*" && min !== "*"
      ? `${hour.padStart(2, "0")}:${min.padStart(2, "0")} UTC`
      : null;
  if (dom === "*" && mon === "*" && dow === "*") {
    return time ? `Daily at ${time}` : "Every minute";
  }
  if (dow !== "*") {
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const d = days[Number(dow)] ?? dow;
    return time ? `Weekly · ${d} ${time}` : `Weekly on ${d}`;
  }
  return time ? `Scheduled · ${time}` : cron;
}

export type CommitTone = "feat" | "fix" | "chore" | "docs" | "refactor" | "test" | "other";

export function commitTone(type: string | null): CommitTone {
  switch (type) {
    case "feat":
      return "feat";
    case "fix":
      return "fix";
    case "refactor":
    case "perf":
      return "refactor";
    case "docs":
      return "docs";
    case "test":
      return "test";
    case "chore":
    case "build":
    case "ci":
    case "style":
      return "chore";
    default:
      return "other";
  }
}

export const TONE_CLASS: Record<CommitTone, string> = {
  feat: "bg-claw-500/15 text-claw-300 border-claw-400/20",
  fix: "bg-cream/10 text-cream border-cream/20",
  refactor: "bg-white/[0.05] text-fog-muted border-white/10",
  docs: "bg-white/[0.04] text-fog-dim border-white/10",
  test: "bg-white/[0.04] text-fog-dim border-white/10",
  chore: "bg-white/[0.03] text-fog-dim border-white/10",
  other: "bg-white/[0.03] text-fog-dim border-white/10",
};
