import type { MetadataRoute } from "next";

import { siteConfig } from "@/lib/site-config";

export default function robots(): MetadataRoute.Robots {
  if (!siteConfig.url) {
    return { rules: { userAgent: "*", disallow: "/" } };
  }
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/app/", "/account/", "/checkout/", "/result/"] },
    ],
    sitemap: new URL("/sitemap.xml", siteConfig.url).toString(),
  };
}
