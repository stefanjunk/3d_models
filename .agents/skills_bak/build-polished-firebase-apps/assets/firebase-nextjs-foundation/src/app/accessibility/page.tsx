import type { Metadata } from "next";

import { LegalShell } from "@/components/legal-shell";

export const metadata: Metadata = { title: "Accessibility", robots: { index: false, follow: false } };

export default function AccessibilityPage() {
  return (
    <LegalShell title="Accessibility review pending">
      <p>This foundation targets semantic, keyboard-operable, reduced-motion-aware output. It has not been certified and does not replace a manual audit of the finished product.</p>
      <h2>Before launch</h2>
      <ul>
        <li>Test every critical journey with keyboard, screen reader, zoom/reflow, contrast, reduced motion, and representative content.</li>
        <li>Publish known limitations, the assessment approach and date, and a working feedback/contact route.</li>
        <li>Track reported barriers to an accountable remediation owner.</li>
      </ul>
    </LegalShell>
  );
}
