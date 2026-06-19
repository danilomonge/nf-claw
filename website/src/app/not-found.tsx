import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Logo } from "@/components/ui/logo";

export default function NotFound() {
  return (
    <div className="container-site flex min-h-[80vh] flex-col items-center justify-center text-center">
      <Logo size={56} />
      <p className="eyebrow mt-8">404</p>
      <h1 className="mt-4 text-balance text-4xl font-semibold tracking-tight md:text-5xl">
        <span className="gradient-text">This page isn’t in the repository.</span>
      </h1>
      <p className="mt-4 max-w-md text-fog-muted">
        The site is generated from the nf-claw repository — if a page is missing, it isn’t in the
        source yet.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex items-center gap-2 rounded-full bg-claw-500 px-6 py-3 text-sm font-semibold text-ink-950 transition hover:bg-claw-400"
      >
        <ArrowLeft className="h-4 w-4" /> Back home
      </Link>
    </div>
  );
}
