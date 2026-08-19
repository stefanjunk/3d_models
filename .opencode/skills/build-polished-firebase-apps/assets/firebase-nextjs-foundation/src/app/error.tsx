"use client";

import { useEffect } from "react";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // Connect a privacy-reviewed error reporter in production; do not include sensitive input.
    void error.digest;
  }, [error]);

  return (
    <main id="main-content" className="state-page">
      <p className="eyebrow">Recoverable error</p>
      <h1>That part of __APP_NAME__ did not load.</h1>
      <p>Your input should be preserved where the final product supports it. Try the action again.</p>
      <button className="button primary" type="button" onClick={reset}>
        Try again
      </button>
    </main>
  );
}
