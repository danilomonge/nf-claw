import Link from "next/link";
import { ArrowLeft, LayoutGrid } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { SearchButton } from "@/components/layout/search-button";

export default function NotFound() {
  return (
    <div className="container-site flex min-h-[80vh] flex-col items-center justify-center pt-16 text-center">
      <div className="relative">
        <div aria-hidden className="absolute inset-0 -z-10 animate-pulse-ring rounded-3xl bg-claw-500/20 blur-2xl" />
        <Logo size={64} />
      </div>
      <p className="eyebrow mt-8">404 · not in the repository</p>
      <h1 className="mt-4 text-balance text-4xl font-semibold tracking-tight md:text-5xl">
        <span className="gradient-text">This page isn’t in the repository.</span>
      </h1>
      <p className="mt-4 max-w-md text-pretty text-fog-muted">
        The site is generated from the nf-claw repository — if a page is missing, it isn’t in the source yet. Search for a
        pipeline or a doc instead.
      </p>
      <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row">
        <SearchButton className="inline-flex items-center gap-2 rounded-full bg-claw-500 px-6 py-3 text-sm font-semibold text-ink-950 transition hover:bg-claw-400">
          Search the library
        </SearchButton>
        <Link
          href="/pipelines/"
          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-6 py-3 text-sm font-semibold text-fog transition hover:border-white/20 hover:bg-white/[0.06]"
        >
          <LayoutGrid className="h-4 w-4" /> All pipelines
        </Link>
        <Link href="/" className="inline-flex items-center gap-2 px-4 py-3 text-sm text-fog-muted transition hover:text-fog">
          <ArrowLeft className="h-4 w-4" /> Back home
        </Link>
      </div>
    </div>
  );
}
