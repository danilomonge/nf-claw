import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { ArrowLeft, FileText } from "lucide-react";
import { getDoc, getDocs } from "@/lib/data";
import { Markdown } from "@/components/ui/markdown";
import { Reveal } from "@/components/ui/reveal";

export function generateStaticParams() {
  return getDocs().map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDoc(slug);
  if (!doc) return { title: "Document not found" };
  return { title: doc.title };
}

function clean(md: string): string {
  const base = md
    .replace(/^---[\s\S]*?---\s*/m, "") // frontmatter
    .replace(/<!--[\s\S]*?-->/g, "") // comments
    .replace(/^<p[\s\S]*?<\/p>\s*/i, "") // leading centered logo block
    .trim();

  // Plain-text files (e.g. NOTICE) use long runs of "=" as section dividers.
  // A run directly under a text line is a setext heading underline (keep it so
  // the heading still renders); a standalone run is a divider → make it a real
  // <hr> instead of an 80-character string that overflows the column.
  const lines = base.split("\n");
  const out: string[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^={3,}\s*$/.test(line)) {
      const prev = i > 0 ? lines[i - 1] : "";
      const isSetextUnderline = prev.trim() !== "" && !/^[=_*\s-]+$/.test(prev);
      if (!isSetextUnderline) {
        out.push("", "---", "");
        continue;
      }
    }
    out.push(line);
  }
  return out.join("\n");
}

export default async function DocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const doc = getDoc(slug);
  if (!doc) notFound();

  const others = getDocs().filter((d) => d.slug !== slug);

  return (
    <div className="container-site pt-28">
      <Link
        href="/#docs"
        className="inline-flex items-center gap-2 text-sm text-fog-muted transition hover:text-fog"
      >
        <ArrowLeft className="h-4 w-4" /> Documentation hub
      </Link>

      <div className="mt-8 grid gap-12 lg:grid-cols-[1fr_240px]">
        <article className="min-w-0">
          <Reveal>
            <div className="mb-8 flex items-center gap-3">
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-claw-400">
                <FileText className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-fog-dim">Generated from</p>
                <code className="font-mono text-sm text-fog">{doc.source}</code>
              </div>
            </div>
            <div className="glass max-w-prose overflow-hidden p-8 md:p-10">
              <Markdown content={clean(doc.content)} />
            </div>
          </Reveal>
        </article>

        <aside className="hidden lg:block">
          <div className="sticky top-24">
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-fog-dim">
              More docs
            </p>
            <nav className="space-y-1">
              {others.map((d) => (
                <Link
                  key={d.slug}
                  href={`/docs/${d.slug}`}
                  className="block rounded-xl px-3 py-2 text-sm text-fog-muted transition hover:bg-white/[0.04] hover:text-fog"
                >
                  {d.title}
                </Link>
              ))}
            </nav>
          </div>
        </aside>
      </div>

      <div className="h-10" />
    </div>
  );
}
