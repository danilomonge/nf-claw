"use client";

import { Search } from "lucide-react";
import { OPEN_PALETTE_EVENT } from "@/components/layout/command-palette";
import { cn } from "@/lib/utils";

/** Opens the site-wide command palette. */
export function SearchButton({ className, children }: { className?: string; children?: React.ReactNode }) {
  return (
    <button type="button" onClick={() => window.dispatchEvent(new Event(OPEN_PALETTE_EVENT))} className={cn(className)}>
      <Search className="h-4 w-4" />
      {children ?? "Search"}
    </button>
  );
}
