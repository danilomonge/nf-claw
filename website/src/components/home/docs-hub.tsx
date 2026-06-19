import Link from "next/link";
import { ArrowUpRight, FileText } from "lucide-react";
import { Reveal, StaggerGroup, StaggerItem } from "@/components/ui/reveal";
import { SectionHeading } from "@/components/ui/section-heading";
import type { DocPage } from "@/lib/types";

function preview(md: string): string {
  const text = md
    .replace(/^---[\s\S]*?---/m, "") // frontmatter
    .replace(/<[^>]+>/g, "") // html
    .replace(/```[\s\S]*?```/g, "") // code blocks
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "") // images
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1") // links
    .replace(/[#>*`_|-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return text.slice(0, 180) + (text.length > 180 ? "…" : "");
}

function readingTime(md: string): string {
  const words = md.split(/\s+/).filter(Boolean).length;
  const mins = Math.max(1, Math.round(words / 200));
  return `${mins} min read`;
}

export function DocsHub({ docs }: { docs: DocPage[] }) {
  return (
    <section id="docs" className="container-site scroll-mt-24 py-24 md:py-32">
      <SectionHeading
        eyebrow="Single source of truth"
        title="Documentation hub"
        description="Every page here is rendered directly from the repository — README, architecture notes, contributor guides and more. Nothing is maintained by hand; update the markdown and this hub updates itself."
      />

      <StaggerGroup className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {docs.map((doc) => (
          <StaggerItem key={doc.slug}>
            <Link href={`/docs/${doc.slug}`} className="group block h-full">
              <article className="glass glass-hover flex h-full flex-col p-6">
                <div className="flex items-center justify-between">
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-claw-400">
                    <FileText className="h-5 w-5" />
                  </span>
                  <ArrowUpRight className="h-5 w-5 text-fog-dim transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-claw-300" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-fog">{doc.title}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-fog-muted">
                  {preview(doc.content)}
                </p>
                <div className="mt-5 flex items-center gap-2 text-xs text-fog-dim">
                  <code className="font-mono">{doc.source}</code>
                  <span>·</span>
                  <span>{readingTime(doc.content)}</span>
                </div>
              </article>
            </Link>
          </StaggerItem>
        ))}
      </StaggerGroup>
    </section>
  );
}
