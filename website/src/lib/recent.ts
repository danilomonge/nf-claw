"use client";

// Pipelines this reader opened lately, newest first — a per-browser convenience for the command
// palette. Storage can be unavailable (private mode, blocked site data), so every access is guarded.

const KEY = "nfclaw:recent-pipelines";
const MAX = 5;

export function readRecent(): string[] {
  try {
    const v = JSON.parse(window.localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string").slice(0, MAX) : [];
  } catch {
    return [];
  }
}

export function rememberPipeline(name: string): void {
  try {
    const next = [name, ...readRecent().filter((n) => n !== name)].slice(0, MAX);
    window.localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    /* storage unavailable: nothing to remember */
  }
}
