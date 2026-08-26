const configuredUrl = process.env.NEXT_PUBLIC_SITE_URL?.trim();

export const siteConfig = {
  name: "__APP_NAME__",
  description: "__APP_DESCRIPTION__",
  url: configuredUrl ? new URL(configuredUrl) : null,
  isPublic: Boolean(configuredUrl),
  analyticsEnabled: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === "true",
  adsEnabled: process.env.NEXT_PUBLIC_ENABLE_ADS === "true",
  complianceProfile: process.env.NEXT_PUBLIC_COMPLIANCE_PROFILE ?? "global-strict",
} as const;
