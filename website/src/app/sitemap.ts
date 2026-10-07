import type { MetadataRoute } from "next";
import { getDocs, getPipelines } from "@/lib/data";
import { siteUrl } from "@/lib/site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: siteUrl("/"), priority: 1 },
    { url: siteUrl("/pipelines/"), priority: 0.9 },
    { url: siteUrl("/docs/"), priority: 0.7 },
    ...getPipelines().map((p) => ({
      url: siteUrl(`/pipelines/${p.name}/`),
      lastModified: p.releaseDate ?? undefined,
      priority: 0.8,
    })),
    ...getDocs().map((d) => ({ url: siteUrl(`/docs/${d.slug}/`), priority: 0.5 })),
  ];
}
