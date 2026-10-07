"use client";

import { useEffect, useState } from "react";
import { formatDate, timeAgo } from "@/lib/utils";

/**
 * A "5h ago" that stays true. The site is a static export, so a relative time computed at build
 * froze there ("6m ago" for as long as the build was served). This renders the absolute date on the
 * server — identical on the client's first render, so hydration matches — then switches to the
 * relative form once mounted and keeps it current.
 */
export function RelativeTime({ date, className }: { date: string | null; className?: string }) {
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    setNow(Date.now());
    const id = window.setInterval(() => setNow(Date.now()), 60_000);
    return () => window.clearInterval(id);
  }, []);

  if (!date) return null;
  return (
    <time dateTime={date} title={new Date(date).toUTCString()} className={className} suppressHydrationWarning>
      {now === null ? formatDate(date) : timeAgo(date, now)}
    </time>
  );
}
