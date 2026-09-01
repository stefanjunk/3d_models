# Quality and release gates

## Contents

1. [Use the proof pyramid](#use-the-proof-pyramid)
2. [Run the repository gate](#run-the-repository-gate)
3. [Run the functional gate](#run-the-functional-gate)
4. [Run the visual and responsive gate](#run-the-visual-and-responsive-gate)
5. [Run the accessibility gate](#run-the-accessibility-gate)
6. [Run the performance gate](#run-the-performance-gate)
7. [Run the Firebase and security gate](#run-the-firebase-and-security-gate)
8. [Run the content, asset, and legal gate](#run-the-content-asset-and-legal-gate)
9. [Test deployment and operations](#test-deployment-and-operations)
10. [Write the readiness report](#write-the-readiness-report)

## Use the proof pyramid

Use the cheapest reliable proof first, but never stop before the layer that can reveal the relevant failure:

1. Static inspection and schemas.
2. Format, lint, typecheck, secret/dependency scan.
3. Unit and component tests.
4. Firebase Rules and emulator integration tests.
5. Production build.
6. Browser end-to-end and visual inspection.
7. Staging deployment checks.
8. Human accessibility, content, security, and legal review.
9. Production monitoring and field performance.

Record commands actually run, exit status, environment, and material limitations. Do not convert “not run” into “passed.”

## Run the repository gate

- Confirm the app starts from the documented command in a clean checkout.
- Commit a lockfile and use supported Node/framework versions.
- Validate environment variables at startup/build with clear errors.
- Keep `.env.example` free of live credentials and exhaustive for required keys.
- Keep generated/compiled artifacts out of source where appropriate.
- Remove unused dependencies, routes, components, media, and dead feature flags.
- Search for TODO/FIXME, lorem ipsum, placeholder domains, sample secrets, fake claims, disabled tests, and console debugging.
- Keep Firebase config, rules, indexes, emulator settings, and App Hosting/Hosting files under source control.
- Ensure setup/build scripts do not overwrite existing work or create paid/live resources silently.

Suggested base commands, adapted to the repository:

```bash
npm ci
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build
```

Run `python3 <skill-dir>/scripts/audit_webapp.py . --profile global-strict` as a backstop. Review false positives instead of deleting checks merely to make the report green.

## Run the functional gate

Test the actual primary job end to end:

- first visit and returning visit;
- signed out, signed in, expired session, wrong role/tenant;
- create, read/list, edit, delete/undo as applicable;
- search, filter, sort, pagination, deep links, browser back/forward;
- form invalid/partial/duplicate input;
- slow, timed-out, failed, and malformed API/data responses;
- offline/reconnect and retry where supported;
- concurrent/double submission and idempotency;
- upload cancel/retry/invalid type/oversize;
- notification/email/webhook success and failure if present;
- export, deletion, cancellation, consent withdrawal, report/appeal where present.

Every visible control must perform its described action. Remove mock buttons and fake navigation. If an integration lacks credentials, provide a truthful disabled/demo boundary and list it as not operational.

Test recovery as carefully as success:

- preserve user input;
- prevent duplicate side effects;
- show an actionable error near the cause;
- offer retry, alternate path, or support;
- restore focus and announce status;
- keep unaffected page regions usable.

## Run the visual and responsive gate

Inspect rendered screens at representative viewports near:

- 320×568;
- 375×812;
- 768×1024;
- 1024×768;
- 1440×900.

Also test intrinsic breakpoints where content actually fails. Capture the homepage and at least the primary interior journey, empty state, error state, and a dense/content-heavy screen.

Review:

- hierarchy and one dominant purpose/action;
- route-to-route consistency without repetitive template composition;
- text wrapping, truncation, overflow, sticky/fixed obstruction;
- navigation, dialogs, menus, tooltips, toasts, virtual keyboard, safe areas;
- image crop, aspect ratio, loading shift, dark/light treatment;
- dense table/chart behavior and alternate representation;
- long content, long names, translations, large numbers, no data;
- browser zoom at 200%, text spacing override, and narrow effective viewport;
- hoverless/touch behavior and target spacing;
- print/download layout if it is a product requirement.

Compare the result to the visual thesis and distinctiveness score. Fix the weakest interior screen before adding polish to the hero.

## Run the accessibility gate

Target WCAG 2.2 AA, but test the actual journey rather than relying on a score.

### Automated

- Run an accessibility engine such as axe on representative routes/states.
- Run semantic/lint rules for JSX/HTML.
- Check contrast across themes and states.
- Treat automated success as partial evidence only.

### Manual keyboard

- Reach and operate every control without pointer.
- Verify logical focus order and visible, unobscured focus.
- Verify skip link and landmarks.
- Verify menus, tabs, disclosure, dialogs, comboboxes, grids, drag alternatives.
- Verify focus enters/traps/returns correctly for dialogs and route transitions.
- Verify no keyboard trap or inaccessible hover-only content.

### Screen reader/semantics

- Check page title, language, landmarks, headings, links, labels, descriptions.
- Check form errors and summary, required state, status/progress/live updates.
- Check names/roles/states for custom components.
- Check alt text, decorative images, charts/tables, media captions/transcripts.
- Check loading, success, toast, network error, and validation announcements.

### Visual/motor/cognitive

- Verify reflow/zoom, contrast, color independence, target size, spacing.
- Verify reduced motion and that time limits can be extended/stopped.
- Provide non-drag and non-gesture alternatives.
- Keep help consistent and authentication compatible with password managers/copy-paste.
- Use plain instructions, stable navigation, and recoverable errors.

Document assistive technology/browser/version used. Block launch for a critical-path failure.

## Run the performance gate

Measure the production build and deployed/staging behavior, not only the dev server.

Field targets at the 75th percentile:

| Metric | Good target |
| --- | --- |
| Largest Contentful Paint | <= 2.5 s |
| Interaction to Next Paint | <= 200 ms |
| Cumulative Layout Shift | <= 0.1 |

Set project-specific budgets for:

- initial JS and route chunks;
- CSS;
- image/video/font bytes;
- request count and third-party scripts;
- server p95 and error rate;
- Firestore reads/writes per primary action;
- Cloud Run/Functions duration/concurrency;
- cache-hit ratio for public routes.

Inspect:

- LCP resource discovery/priority and no lazy loading;
- explicit media dimensions;
- font subset/fallback/preload behavior;
- hydration and client-component boundaries;
- long tasks and interaction delay;
- layout shifts after consent, ads, fonts, images, personalization;
- CDN cache headers and personalized-output safety;
- third-party tags loaded only after applicable permission;
- slow-device and throttled-network experience.

Do not promise a field metric from a local lab run. Add real-user monitoring only under the configured privacy/consent profile.

## Run the Firebase and security gate

- Use separate dev/staging/prod projects and explicit environment mapping.
- Verify App Hosting/Hosting build from a clean lockfile.
- Verify every resource region and dependency co-location.
- Confirm client/server Firebase imports and secret boundaries.
- Run positive and negative Firestore/Storage Rules tests.
- Test cross-user and cross-tenant reads/writes, list queries, extra fields, privilege escalation, invalid transitions.
- Confirm Admin/server paths perform explicit authn/authz/validation and do not rely on Rules.
- Observe App Check before enforcement; verify debug tokens never ship.
- Scan source/history/build output for secrets and dangerous public env variables.
- Validate upload type/size/ownership and higher-risk scanning.
- Test rate limits/abuse controls/idempotency on expensive and side-effecting operations.
- Review dependency advisories/licenses and pin critical runtime dependencies.
- Review security headers: CSP, framing, content type, referrer, permissions policy as applicable.
- Verify cookies use appropriate Secure, HttpOnly, SameSite, domain/path, and lifetime.
- Verify no sensitive content in URLs, analytics, logs, errors, cache, screenshots, or client source.
- Verify backup/PITR and restoration steps; code rollback is not data recovery.
- Verify budgets/alerts and maximum instances/quotas; alerts do not cap charges.

Perform a compact threat model around assets, actors, entry points, trust boundaries, abuse cases, and mitigations. Escalate payments, identity, children, health, finance, UGC, marketplace, admin, and high-value data for expert review.

## Run the content, asset, and legal gate

- Verify operator, contact, support, pricing, plan, delivery, refund/cancellation, and policy facts.
- Verify every claim against the claims ledger.
- Confirm no fake customers, testimonials, ratings, badges, scarcity, countdown, or AI-generated reviews.
- Confirm affiliate/sponsored/ad disclosure placement and accessibility.
- Confirm asset ledger completeness, license, attribution, trademark/release, and local optimized copies.
- Confirm metadata, canonical/indexing, share images, status codes, sitemap/robots.
- Confirm language, date/number/currency, text expansion, and RTL if targeted.
- Complete `product/legal-profile.yaml` and `product/compliance.md`.
- Network-test consent choices, GPC/opt-out behavior, preferences withdrawal, and privacy requests.
- Test account export/deletion and subscription cancellation/withdrawal/refund if present.
- Test UGC report/moderation/reason/appeal, marketplace trader/dispute, AI disclosure/human review where present.
- Confirm regulated-sector features have named approval.

Never publish placeholder legal text. Mark unverified legal/business facts as launch blockers.

## Test deployment and operations

On staging:

- verify domain/HTTPS, redirects, canonical host, 404/500/offline;
- verify Auth authorized domains and redirect flows;
- verify cache headers/hit behavior and no public personalized caching;
- verify robots/noindex for staging and private routes;
- verify environment, Secret Manager bindings, IAM, Rules, indexes, migrations;
- verify logging/error reporting without sensitive payloads;
- verify alert delivery, support/contact, incident owner;
- smoke-test primary and recovery flows after deploy;
- review Cloud Run/Functions/Firestore/App Check/Auth metrics.

For production:

- use an approved immutable artifact or source revision;
- record deploy/migration version and owner;
- monitor immediately after rollout;
- define rollback and forward-fix criteria;
- keep database/file migration backup and restore plan;
- perform a post-deploy smoke test without destructive test data.

## Write the readiness report

Create a short report with evidence:

```markdown
# Readiness

Status: prototype-ready | deploy-ready | launch-ready | blocked
Build revision:
Environment tested:

## Operational
- ...

## Mocked or disabled
- ...

## Validation run
| Check | Command/method | Result | Evidence/limits |

## Assumptions
- ...

## Launch blockers
| Blocker | Risk | Owner/input needed | Resolution evidence |

## Firebase actions requiring account access
- ...

## Recommended next iteration
- ...
```

Use readiness labels precisely:

- **Prototype-ready:** primary journey works with explicit demo/integration boundaries.
- **Deploy-ready:** clean production build and required automated tests pass; infrastructure config exists.
- **Launch-ready:** deploy-ready plus production resources/credentials, verified content/legal profile, monitoring, consent/security/accessibility review, and accountable approval.
- **Blocked:** a critical functionality, security, data, legal, accessibility, credential, or infrastructure dependency remains.
