import Link from "next/link";
import type { ReactNode } from "react";

export function LegalShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main id="main-content" className="legal-shell">
      <Link href="/" className="text-link">
        ← Back to __APP_NAME__
      </Link>
      <p className="eyebrow">Draft launch surface</p>
      <h1>{title}</h1>
      <div className="legal-callout" role="note">
        This foundation does not contain legally approved operator-specific text. Complete the legal profile and replace this draft before public launch.
      </div>
      <div className="prose">{children}</div>
    </main>
  );
}
