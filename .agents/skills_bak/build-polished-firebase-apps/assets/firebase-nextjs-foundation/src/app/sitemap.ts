import type { MetadataRoute } from "next";

import { siteConfig } from "@/lib/site-config";

export default function sitemap(): MetadataRoute.Sitemap {
  if (!siteConfig.url) return [];
  return ["/", "/privacy", "/terms", "/accessibility"].map((path) => ({
    url: new URL(path, siteConfig.url!).toString(),
    lastModified: new Date(),
  }));
}
