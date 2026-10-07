// Where the site is served: origin + base path (GitHub Pages serves a project site under /<repo>).
export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "";
export const SITE_ORIGIN = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

/** Absolute URL of a site path, e.g. siteUrl("/pipelines/rnaseq/"). */
export function siteUrl(path: string): string {
  return `${SITE_ORIGIN.replace(/\/$/, "")}${BASE_PATH}${path}`;
}

/** The social preview image every page shares. */
export const OG_IMAGE = { url: `${BASE_PATH}/brand/og.png`, width: 630, height: 630, alt: "nf-claw" };
