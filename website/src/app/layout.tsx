import type { Metadata, Viewport } from "next";
import "./globals.css";
import { BackgroundFX } from "@/components/ui/background-fx";
import { Nav } from "@/components/layout/nav";
import { Footer } from "@/components/layout/footer";
import { getRepoMeta, getPipelines } from "@/lib/data";

const meta = getRepoMeta();

// Hosting context: under a project path (e.g. GitHub Pages "/<repo>") assets
// live under the base path, and the canonical origin comes from the deploy URL.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "nf-claw — nf-core pipelines for AI agents",
    template: "%s · nf-claw",
  },
  description: meta.tagline,
  applicationName: "nf-claw",
  keywords: [
    "nf-core",
    "nextflow",
    "bioinformatics",
    "pipelines",
    "AI agents",
    "nf-claw",
  ],
  openGraph: {
    title: "nf-claw",
    description: meta.tagline,
    type: "website",
    images: [`${basePath}/nf-claw-logo-with-text.png`],
  },
  icons: { icon: `${basePath}/nf-claw-logo.png` },
};

export const viewport: Viewport = {
  themeColor: "#07080a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const repo = getRepoMeta();
  const pipelines = getPipelines();

  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <BackgroundFX />
        <Nav repo={repo.remote} />
        <main className="relative">{children}</main>
        <Footer repo={repo.remote} pipelines={pipelines} />
      </body>
    </html>
  );
}
