import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Reveal } from "./reveal";

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "left",
  className,
  action,
}: {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
  className?: string;
  action?: ReactNode;
}) {
  return (
    <div
      className={cn(
        "flex flex-col gap-6",
        align === "center" ? "items-center text-center" : "items-start",
        action ? "md:flex-row md:items-end md:justify-between" : "",
        className,
      )}
    >
      <Reveal className={align === "center" ? "max-w-2xl" : "max-w-3xl"}>
        <p className="eyebrow mb-4">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-claw-400" />
          {eyebrow}
        </p>
        <h2 className="text-balance text-4xl font-semibold tracking-tighter md:text-5xl">
          <span className="gradient-text">{title}</span>
        </h2>
        {description && (
          <p className="mt-5 text-pretty text-lg leading-relaxed text-fog-muted">
            {description}
          </p>
        )}
      </Reveal>
      {action && <Reveal delay={0.1}>{action}</Reveal>}
    </div>
  );
}
