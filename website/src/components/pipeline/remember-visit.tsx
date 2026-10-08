"use client";

import { useEffect } from "react";
import { rememberPipeline } from "@/lib/recent";

/** Records a pipeline page visit so the command palette can offer it again. Renders nothing. */
export function RememberVisit({ name }: { name: string }) {
  useEffect(() => rememberPipeline(name), [name]);
  return null;
}
