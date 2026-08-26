import Link from "next/link";

export default function NotFound() {
  return (
    <main id="main-content" className="state-page">
      <p className="eyebrow">404</p>
      <h1>This route is not part of __APP_NAME__.</h1>
      <p>Check the address or return to the product entry point.</p>
      <Link className="button primary" href="/">
        Return home
      </Link>
    </main>
  );
}
