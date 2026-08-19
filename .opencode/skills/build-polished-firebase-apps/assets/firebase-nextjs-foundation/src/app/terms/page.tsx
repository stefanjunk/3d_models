import type { Metadata } from "next";

import { LegalShell } from "@/components/legal-shell";

export const metadata: Metadata = { title: "Terms", robots: { index: false, follow: false } };

export default function TermsPage() {
  return (
    <LegalShell title="Service terms pending">
      <p>Do not publish generic generated terms. Terms must match the verified operator, product behavior, payment model, markets, support, cancellation, refunds, rights, and limitations.</p>
      <h2>Before launch</h2>
      <ul>
        <li>Verify every commercial and operator fact with the accountable owner.</li>
        <li>Place material price, renewal, delivery, cancellation, and limitation information in the transaction journey as well as the terms.</li>
        <li>Obtain qualified review for enabled markets and regulated features.</li>
      </ul>
    </LegalShell>
  );
}
