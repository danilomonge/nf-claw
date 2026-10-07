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
  as: Heading = "h2",
}: {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
  className?: string;
  action?: ReactNode;
  /** h1 when the heading opens its own page, h2 inside the home page. */
  as?: "h1" | "h2";
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
        <Heading className="text-balance text-[2rem] font-semibold leading-[1.08] tracking-tighter sm:text-4xl md:text-5xl">
          <span className="gradient-text">{title}</span>
        </Heading>
        {description && (
          <p className="mt-5 text-pretty text-base leading-relaxed text-fog-muted sm:text-lg">{description}</p>
        )}
      </Reveal>
      {action && <Reveal delay={0.1}>{action}</Reveal>}
    </div>
  );
}
