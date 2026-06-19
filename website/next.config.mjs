/** @type {import('next').NextConfig} */

// Base path for project-site hosting (e.g. GitHub Pages serves a project repo
// under "/<repo>"). Set NEXT_PUBLIC_BASE_PATH in CI; left empty for local dev
// so the site runs at the root.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig = {
  reactStrictMode: true,
  // Emit a fully static site (HTML/CSS/JS) into `out/` — no server needed, so
  // it can be hosted on GitHub Pages. The data layer still reads repository
  // files and local git at build time.
  output: "export",
  // Pretty, host-agnostic URLs: each route becomes <route>/index.html.
  trailingSlash: true,
  basePath,
  assetPrefix: basePath || undefined,
  // GitHub Pages has no image-optimization server.
  images: { unoptimized: true },
  // The data layer reads files from the repository root (one level up). Allow
  // tracing those files so the build can bundle them when needed.
  outputFileTracingRoot: process.cwd() + "/..",
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
};

export default nextConfig;
