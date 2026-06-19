import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { getPipelines } from "@/lib/data";
import { toSummary, colorForCategory } from "@/lib/derive";
import { SectionHeading } from "@/components/ui/section-heading";
import { StaggerGroup, StaggerItem } from "@/components/ui/reveal";
import { formatDate } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Pipelines",
  description: "Every nf-core pipeline in the nf-claw library.",
};

export default function PipelinesIndexPage() {
  const pipelines = getPipelines().map(toSummary);

  return (
    <div className="container-site pt-28">
      <SectionHeading
        eyebrow="The collection"
        title="All pipelines"
        description={`${pipelines.length} nf-core pipelines, each pinned to a release and documented from source.`}
      />

      <StaggerGroup className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {pipelines.map((p) => {
          const accent = colorForCategory(p.category);
          return (
            <StaggerItem key={p.name}>
              <Link href={`/pipelines/${p.name}`} className="group block h-full">
                <article className="glass glass-hover relative flex h-full flex-col overflow-hidden p-6">
                  <div
                    className="absolute -right-12 -top-12 h-32 w-32 rounded-full blur-3xl"
                    style={{ background: `${accent}22` }}
                  />
                  <div className="relative flex items-center justify-between">
                    <span className="inline-flex items-center gap-2 font-mono text-lg font-semibold text-fog">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ background: accent }} />
                      {p.name}
                    </span>
                    <ArrowUpRight className="h-5 w-5 text-fog-dim transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-claw-300" />
                  </div>
                  <p className="relative mt-1 text-xs text-fog-dim">{p.pipeline}</p>
                  <p className="relative mt-3 flex-1 text-sm leading-relaxed text-fog-muted">
                    {p.description}
                  </p>
                  <div className="relative mt-5 flex items-center justify-between border-t border-white/[0.05] pt-4 text-xs text-fog-dim">
                    <span className="chip text-[10px]">{p.category}</span>
                    <span className="flex items-center gap-3">
                      <span>{p.parameterCount} params</span>
                      <span className="font-mono text-fog-muted">{p.version}</span>
                    </span>
                  </div>
                  {p.releaseDate && (
                    <p className="relative mt-2 text-[11px] text-fog-dim">
                      Pinned {formatDate(p.releaseDate)}
                    </p>
                  )}
                </article>
              </Link>
            </StaggerItem>
          );
        })}
      </StaggerGroup>

      <div className="h-20" />
    </div>
  );
}
