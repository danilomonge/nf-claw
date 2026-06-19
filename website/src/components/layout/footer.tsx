import Link from "next/link";
import { Github } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import type { Pipeline } from "@/lib/types";

export function Footer({
  repo,
  pipelines,
}: {
  repo: string | null;
  pipelines: Pipeline[];
}) {
  const githubUrl = repo ? `https://github.com/${repo}` : "https://github.com";
  const year = new Date().getFullYear();

  return (
    <footer className="relative mt-32 border-t border-white/[0.06]">
      <div className="container-site grid gap-12 py-16 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div>
          <Logo size={40} withText />
          <p className="mt-5 max-w-xs text-sm leading-relaxed text-fog-muted">
            A self-maintaining, token-minimal library of nf-core pipelines for AI
            agents. The repository is the single source of truth — this interface
            regenerates itself from it.
          </p>
          <a
            href={githubUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-fog transition hover:border-claw-400/30"
          >
            <Github className="h-4 w-4" /> View on GitHub
          </a>
        </div>

        <FooterCol title="Pipelines">
          {pipelines.slice(0, 6).map((p) => (
            <FooterLink key={p.name} href={`/pipelines/${p.name}`}>
              {p.name}
            </FooterLink>
          ))}
        </FooterCol>

        <FooterCol title="Explore">
          <FooterLink href="/#pipelines">Pipeline universe</FooterLink>
          <FooterLink href="/#skills">Skills explorer</FooterLink>
          <FooterLink href="/#activity">Live activity</FooterLink>
          <FooterLink href="/#releases">Release timeline</FooterLink>
          <FooterLink href="/#docs">Documentation</FooterLink>
        </FooterCol>

        <FooterCol title="Resources">
          <FooterLink href="https://nf-co.re" external>
            nf-core
          </FooterLink>
          <FooterLink href="https://www.nextflow.io" external>
            Nextflow
          </FooterLink>
          <FooterLink href="/docs/readme">README</FooterLink>
          <FooterLink href="/docs/architecture">Architecture</FooterLink>
        </FooterCol>
      </div>

      <div className="border-t border-white/[0.06]">
        <div className="container-site flex flex-col items-center justify-between gap-3 py-6 text-xs text-fog-dim md:flex-row">
          <p>© {year} nf-claw · MIT licensed · Pipelines © the nf-core community.</p>
          <p className="font-mono">Generated live from the repository.</p>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="mb-4 text-xs font-semibold uppercase tracking-[0.18em] text-fog-dim">
        {title}
      </h4>
      <ul className="space-y-2.5">{children}</ul>
    </div>
  );
}

function FooterLink({
  href,
  children,
  external,
}: {
  href: string;
  children: React.ReactNode;
  external?: boolean;
}) {
  if (external) {
    return (
      <li>
        <a
          href={href}
          target="_blank"
          rel="noreferrer"
          className="text-sm text-fog-muted transition hover:text-claw-300"
        >
          {children}
        </a>
      </li>
    );
  }
  return (
    <li>
      <Link href={href} className="text-sm text-fog-muted transition hover:text-claw-300">
        {children}
      </Link>
    </li>
  );
}
