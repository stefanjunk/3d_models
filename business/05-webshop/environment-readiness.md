# Webshop environment and launch readiness

Status: `IN_PROGRESS / NOT LAUNCH_READY`

Verification date: 2026-08-28

Named internal owner: Stefan Junk

Repository: `/home/stefan/Projekte/Website/metrimade-store`

This record distinguishes provisioned infrastructure from verified launch behavior. The checks were read-only; no Firebase deployment, branch push, rules deployment, secret change or live checkout activation was performed.

## Environment model

| Logical environment | Firebase project/backend | Branch model | Verified state |
|---|---|---|---|
| Local development | Firebase Emulator Suite with `demo-metrimade` | local working branch | Emulator configuration exists and rule tests run without production fallthrough. |
| Staging/QA | `metrimade-dev` / backend `metrimade-dev` | `main` according to the owner-confirmed branch model; deployed behavior matches current `origin/main` features | App Hosting and Firestore are active in `europe-west4`; `/operator/models` and `/api/catalog` return 200. The API catalog is empty, while the homepage still shows demo fixtures because the backend override uses `NEXT_PUBLIC_CATALOG_MODE=hybrid`. |
| Production | `metrimade-store` / backend `metrimade-store` | `prod` according to the owner-confirmed branch model; deployed behavior matches the older `origin/prod` revision | App Hosting and Firestore are active in `europe-west4`; the homepage returns 200, while the newer operator and catalog API routes return 404. Checkout and legal gates remain closed. |

Both Firestore databases have point-in-time recovery and delete protection enabled. Each project has a dedicated Firebase Web App and Storage bucket. No Firebase Extension is installed in either project, so the planned withdrawal-confirmation email path is not provisioned.

The Firebase CLI does not expose the connected Git branch in its backend response. Confirm `main → metrimade-dev` and `prod → metrimade-store` once in the Firebase App Hosting console and retain screenshots/exports as environment evidence.

## Repository synchronization blocker

The local `main` worktree is not a safe base for new edits:

- local `main` is at `17fab9f`, the same revision as `origin/prod`;
- it tracks `origin/main` but is five commits behind `origin/main` at `1c75c8b`;
- fourteen tracked files are locally modified and `.firebaserc` is untracked;
- upstream changes overlap local edits in `apphosting.yaml`, `firestore.rules`, `storage.rules`, `src/app/layout.tsx` and `src/components/store-header.tsx`.

The local changes must first be preserved in a named branch/commit, then reconciled with `origin/main`. They must not be stashed, reset or overwritten merely to make the branch clean. The existing local E2E edits already address the consent-dialog and account-navigation assumptions that fail on the clean remote snapshot; preserve and retest them during reconciliation.

The untracked `.firebaserc` currently maps `staging` to the production project. For the two-cloud-project MVP model it should map development/staging operations to `metrimade-dev` and production operations to `metrimade-store`, with an explicit project check before every deploy.

## Clean `origin/main` validation

Validation was run in an isolated temporary worktree at commit `1c75c8b` with Node 25. Individual dependencies warn that Node 25 is unsupported; CI should use an explicitly supported even LTS release, currently Node 24.15 or a project-approved Node 22 release.

| Check | Result |
|---|---|
| ESLint | PASS |
| TypeScript | PASS |
| Unit tests | PASS — 25/25 |
| Next.js production build | PASS — 45 routes generated/registered |
| Firestore/Storage emulator rules | PASS — 14/14 positive and negative tests |
| Browser smoke tests | BLOCK — 2/6 pass; four failures come from an undismissed consent dialog and an obsolete automatic-account-redirect expectation. Local uncommitted test edits address these assumptions but are not yet reconciled into `origin/main`. |
| Static global-strict audit | BLOCK — no critical findings; incomplete blueprint keys and intentionally open compliance blockers prevent a launch-ready label. |
| Repository CI | BLOCK — no `.github` workflow is committed on `origin/main`. |

This supports a `deploy-ready candidate` only after the branch is reconciled and E2E/CI pass. It does not support `launch-ready`.

## Remaining actions

1. Preserve the current local website changes in a named branch/commit, reconcile them with `origin/main`, rerun the full suite and push the reviewed result to `main` for the dev/staging backend.
2. Keep `prod` pinned to the last approved production revision. Promote a reviewed immutable commit from `main` to `prod`; never develop directly on `prod`.
3. Commit a CI workflow using a supported Node LTS release. Require lint, typecheck, unit, production build, emulator Rules tests and browser E2E before merge; protect both `main` and `prod`.
4. Correct and commit an environment mapping template; keep the real `.firebaserc` free of secrets. Verify the selected project before every rules/index deployment.
5. Switch staging from `hybrid` to `firestore` catalog mode before release testing and remove/segregate demo product promises. Publish only an exact P5 release.
6. Configure and test App Check using separate site keys/domains; observe before general enforcement and keep debug tokens out of source.
7. Bind Stripe and withdrawal secrets in Secret Manager, configure the Stripe test webhook, install and configure the email extension/SMTP provider, and test retry, duplicate, refund, dispute, expired-session and durable-confirmation paths.
8. Review runtime IAM, including the narrowly scoped signing identity for V4 download URLs and named operator/publisher permissions. Do not rely on client Rules for Admin SDK routes.
9. Deploy and verify Firestore Rules, indexes and Storage Rules first to `metrimade-dev`; compare deployed versions before production promotion.
10. Configure budgets/alerts, error/log redaction, App Hosting/Firestore/Storage monitoring and an incident owner. Perform and record a restore drill; PITR enabled is not restore evidence.
11. Complete the operator/legal profile, provider/data map, retention/deletion flows, accessibility review and German checkout/withdrawal approval before opening server-side gates.
12. Run a real staging E2E for one exact P5 product: publish, purchase, webhook, entitlement, signed download, expiry/unauthorized denial, refund, takedown, reconciliation, rollback and kill switch.

The first ten items can proceed before products two and three exist. Only one exact P5 product is required for the controlled MVP transaction test.
