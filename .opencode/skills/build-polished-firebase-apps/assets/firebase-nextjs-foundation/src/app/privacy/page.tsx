import type { Metadata } from "next";

import { LegalShell } from "@/components/legal-shell";

export const metadata: Metadata = { title: "Privacy", robots: { index: false, follow: false } };

export default function PrivacyPage() {
  return (
    <LegalShell title="Privacy configuration pending">
      <p>Optional analytics and advertising are disabled in this foundation. That technical default is not a complete privacy notice.</p>
      <h2>Before launch</h2>
      <ul>
        <li>Identify the operator, contacts, enabled markets, users, purposes, vendors, regions, transfers, and retention.</li>
        <li>Describe access, correction, export, deletion, objection, opt-out, appeal, and complaint paths that actually work.</li>
        <li>Network-test every consent and privacy-choice state before enabling optional tags or SDKs.</li>
      </ul>
    </LegalShell>
  );
}
