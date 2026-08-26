export default function Loading() {
  return (
    <main id="main-content" className="state-page" aria-busy="true" aria-label="Loading __APP_NAME__">
      <div className="loading-mark" aria-hidden="true" />
      <p>Preparing __APP_NAME__…</p>
    </main>
  );
}
