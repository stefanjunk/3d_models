# Firebase and Google Cloud architecture

## Contents

1. [Choose the deployment profile](#choose-the-deployment-profile)
2. [Use Firebase App Hosting correctly](#use-firebase-app-hosting-correctly)
3. [Use Firebase Hosting correctly](#use-firebase-hosting-correctly)
4. [Set Next.js client and server boundaries](#set-nextjs-client-and-server-boundaries)
5. [Choose Firestore or Firebase SQL Connect](#choose-firestore-or-firebase-sql-connect)
6. [Design authentication and authorization](#design-authentication-and-authorization)
7. [Write and test Security Rules](#write-and-test-security-rules)
8. [Add App Check safely](#add-app-check-safely)
9. [Handle uploads and Storage](#handle-uploads-and-storage)
10. [Choose Functions or Cloud Run](#choose-functions-or-cloud-run)
11. [Select locations and residency](#select-locations-and-residency)
12. [Design caching and performance](#design-caching-and-performance)
13. [Separate environments and previews](#separate-environments-and-previews)
14. [Protect secrets and IAM](#protect-secrets-and-iam)
15. [Gate analytics, ads, and Remote Config](#gate-analytics-ads-and-remote-config)
16. [Use emulators and release gates](#use-emulators-and-release-gates)
17. [Operate costs, logs, and recovery](#operate-costs-logs-and-recovery)

## Choose the deployment profile

| App shape | Default deployment |
| --- | --- |
| Static marketing/docs site, Vite/React SPA, static export | Firebase Hosting |
| Next.js/Angular SSR, server actions, route handlers, ISR | Firebase App Hosting |
| Small callable, scheduled, database/storage/auth event work | Cloud Functions for Firebase 2nd gen |
| Custom runtime/container, independent service, advanced networking | Cloud Run |
| Realtime/document/offline-first data | Firestore |
| Relational integrity, joins, PostgreSQL | Firebase SQL Connect (formerly Data Connect) |
| User-uploaded media/files | Cloud Storage for Firebase |

Do not start a new dynamic Next.js app on framework-aware Firebase Hosting. Firebase closed that experiment to new participants and directs new dynamic framework apps to App Hosting. A fully static Next.js export can still use Firebase Hosting.

Preserve an existing working architecture when it meets the product. Migrate only with a concrete benefit and a tested transition plan.

## Use Firebase App Hosting correctly

Treat App Hosting as an orchestration layer over Cloud Build, Artifact Registry, Cloud Run, Cloud CDN, Secret Manager, and rollout controls. It builds a new revision, checks health, then shifts traffic.

Current built-in support includes Next.js 13.5+, Angular 18.2+, and Node.js 20+. Do not blindly choose the newest release. Verify the current App Hosting active/LTS support table, pin a supported patch range, and commit the lockfile.

Required practices:

- Keep the conventional framework build script. Overriding the build command in `apphosting.yaml` can opt out of framework adapter optimizations.
- Choose one App Hosting origin region close to data and primary dynamic traffic.
- Put public static output behind CDN caching; treat uncached SSR as regional compute.
- Configure runtime resources and instance bounds from measured needs.
- Use Secret Manager bindings for server secrets.
- Verify Next.js image optimization. It is not a safe assumption that Vercel-style optimization exists automatically.
- Check compatibility of middleware, streaming, route handlers, and framework updates in a staging backend.

Minimal `apphosting.yaml` starting point:

```yaml
runConfig:
  minInstances: 0
  maxInstances: 10
  concurrency: 80
  cpu: 1
  memoryMiB: 512
```

Tune values after observing latency, memory, concurrency, and cost. Minimum instances spend money continuously; maximum instances protect downstream systems and budget but can throttle traffic.

Do not claim App Hosting gives active-active regional SSR. The load balancer and CDN are global, but uncached requests reach the chosen regional Cloud Run origin. Use an explicitly designed multi-region Cloud Run/load-balancer/data strategy for higher requirements.

## Use Firebase Hosting correctly

Use Hosting for static assets, SPAs, and static exports. Configure:

- immutable caching for fingerprinted assets;
- short/controlled caching for HTML;
- security headers;
- clean URLs/trailing-slash policy;
- custom 404/error routes;
- SPA rewrite only for a true client router;
- Functions/Cloud Run rewrites only when the route needs them.

Hosting rule order matters and first matches win. Reserved `/__/*` behavior, redirects, exact files, rewrites, custom 404, and default 404 have distinct precedence. Verify deployed behavior rather than reasoning from config alone.

Do not rerun `firebase init` over an established configuration without inspecting the diff; it can replace existing settings.

Hosting preview URLs are public to anyone with the URL and normally reach whatever backend the preview build is configured to use. Point preview builds at a separate staging Firebase project, never production by accident.

## Set Next.js client and server boundaries

### Browser

- Use the modular Firebase JavaScript SDK.
- Treat Firebase web config/API key as public project configuration, not authorization.
- Use Auth + Security Rules for direct Firestore/Storage access.
- Initialize optional Analytics/App Check only through explicit wrappers.

### Server

- Keep Firebase Admin SDK imports in server-only modules.
- Use Admin SDK for trusted privileged operations and authenticate/authorize every request in application logic/IAM.
- Remember Admin/server SDK access bypasses Firestore Security Rules.
- Use `FirebaseServerApp` when SSR should continue the signed-in user's identity/App Check context instead of unrestricted Admin behavior.
- Never serialize service account credentials or server tokens into client props, logs, errors, source maps, or `NEXT_PUBLIC_*` variables.

Classify routes:

| Route | Data boundary | Cache default |
| --- | --- | --- |
| Public static/editorial | Server/static | Public, controlled freshness |
| Public changing catalog | Server/cacheable | `s-maxage` + bounded revalidation |
| Signed-in user/tenant | Client or authenticated server | `private` or `no-store` |
| Privileged mutation | Server only | `no-store` |

Avoid reading cookies or `next/headers` on routes that should remain publicly cacheable.

## Choose Firestore or Firebase SQL Connect

### Choose Firestore for

- realtime listeners;
- direct client access with rules;
- document-oriented, denormalized read models;
- offline-capable clients;
- elastic records without relational joins.

Production Firestore defaults:

- Choose location before creation; it is a major architectural decision.
- Prefer multi-region for availability/durability or regional for lower write latency/cost and tight compute co-location.
- Use random/auto IDs; avoid sequential IDs and hot documents.
- Minimize index fanout and exempt unused large/sequential fields.
- Use cursors, not offsets, for pagination.
- Design queries together with rules; rules are not post-filters.
- Define TTL/retention and backups/PITR according to explicit RPO/RTO.
- Treat persistent web offline cache as a privacy decision on shared devices; it is not enabled by default.

### Choose Firebase SQL Connect for

- foreign keys and relational constraints;
- joins and normalized models;
- PostgreSQL compatibility;
- typed, predefined client operations;
- multi-table transactional workflows.

SQL Connect requirements:

- Place the service and Cloud SQL database in the same region.
- Add explicit `@auth` policy to client operations; absence defaults to no access.
- Generate typed SDKs in CI and fail when generated code is stale.
- Use compatible production migrations.
- Do not use strict/forced destructive migrations without backup, review, and migration approval.
- Do not treat a trial Cloud SQL instance as production; provision HA/backups as required.

For a hybrid, declare one system of record per entity and an explicit asynchronous projection. Avoid uncoordinated dual writes.

## Design authentication and authorization

- Enable only needed identity providers.
- Configure authorized production and preview domains intentionally.
- Use a consistent session model across client and server rendering.
- Authorize at API/data boundaries; hiding a control is not authorization.
- Model owner, tenant, role, and admin actions explicitly.
- Add reauthentication for password/email/provider changes, export, deletion, payment, and other sensitive actions.
- Add MFA/passkeys for privileged users when supported by the threat model.
- Test redirect sign-in under current browser storage restrictions and custom-domain topology.
- Avoid user enumeration in sign-in, password reset, invite, and account recovery responses.

Residency warning: Firebase documents Authentication processing in US data centers. A hard non-US identity residency requirement may disqualify Firebase Authentication even when application compute and databases are in another region. Verify current Firebase privacy documentation and legal requirements before choosing it.

## Write and test Security Rules

Start locked:

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

Then grant the minimum operation, path, and fields:

- separate `get` and `list` when listing needs tighter constraints;
- distinguish create, update, and delete;
- validate required/allowed keys, types, immutable ownership, size/range, timestamps, and status transitions;
- require owner/tenant membership or verified role/custom claim;
- ensure list queries include constraints that guarantee every possible result satisfies the rule;
- keep privileged transitions server-side when Rules become ambiguous;
- account for rule document-read limits and billable reads.

Test every rule with positive and negative cases using Emulator Suite and `@firebase/rules-unit-testing`:

- signed out;
- correct owner/member;
- another owner/tenant;
- malformed/missing/extra fields;
- privilege escalation attempt;
- invalid state transition;
- over-broad list query;
- create/update/delete boundaries.

Do not ship test mode, `if true`, or “any signed-in user can read/write everything.”

## Add App Check safely

Use App Check as abuse attestation, not authentication or authorization.

Recommended rollout:

1. Register every web app.
2. Prefer reCAPTCHA Enterprise for new web integrations.
3. Configure production domains; do not add localhost to the production key.
4. Initialize early and explicitly enable token refresh.
5. Observe metrics without enforcement.
6. Tune threshold/TTL and investigate legitimate failures.
7. Enforce service by service.
8. Use protected debug tokens for local/CI only.
9. Verify custom-backend tokens in a header such as `X-Firebase-AppCheck`, never a URL.

Never commit a debug token. Enforcement changes can take time to propagate; include an operational rollback path.

## Handle uploads and Storage

- Default to authenticated access unless an object is intentionally public.
- Include tenant/owner in path or validated metadata and enforce it in Rules.
- Generate safe object names; do not trust raw user filenames as paths.
- Validate maximum size and allowed media/content type in Rules and application logic.
- Treat client-supplied MIME metadata as untrusted; scan/process higher-risk uploads server-side.
- Use resumable upload, visible progress, cancellation, retry, and orphan cleanup.
- Strip dangerous metadata when appropriate and generate safe derivatives.
- Define retention, lifecycle, deletion, quarantine, moderation, and backup expectations.
- Remember Storage Rules can consult only the default Firestore database within tight/billable access limits.

Never serve arbitrary active HTML/SVG/script uploads from a trusted application origin without a deliberate isolation policy.

## Choose Functions or Cloud Run

Use Functions 2nd gen for Firebase event glue, callables, scheduled jobs, and small HTTP APIs. Use Cloud Run for custom containers/runtimes, substantial services, independent release cadence, or advanced networking.

Functions defaults:

- set region explicitly and co-locate with triggering data;
- write event handlers idempotently because delivery can repeat;
- keep module-level code concurrency-safe;
- set maximum instances and downstream connection limits;
- use minimum instances only for measured latency needs;
- bind each secret only to functions that need it;
- configure artifact cleanup;
- split large deployments into safe groups.

Do not force all backend logic into Next.js route handlers. Keep app-coupled server actions there; move independently scalable or reusable business services to Functions/Cloud Run.

## Select locations and residency

Firebase has no single project-wide location. Complete a location worksheet before creating resources:

| Resource | Candidate region | User latency | Data dependency | Residency/transfer | Immutable? | Decision owner |
| --- | --- | --- | --- | --- | --- | --- |

Cover App Hosting, Firestore, SQL Connect/Cloud SQL, Storage, Functions, Cloud Run, logs, Analytics, extensions, backups, and subprocessors.

Use these patterns:

- Typical global app: one origin close to data/primary users + CDN for public output.
- High availability in one geography: multi-region database where suitable + redundant compute plan.
- Active-active compute: multi-region Cloud Run + global load balancer + health/outlier detection + explicit consistency/failover.
- Hard residency: often separate project/stack per geography plus routing and audited service-by-service processing.

Do not infer storage/processing location from CDN reach or Analytics reporting location. Do not promise “data never leaves the region” without verifying auth, logs, support, backups, telemetry, subprocessors, and transfers.

## Design caching and performance

Cloud CDN fronts App Hosting, but cache only responses that are safe and eligible.

- Fingerprinted assets: long public `max-age`, immutable.
- Public pages/data: explicit `s-maxage` and bounded `stale-while-revalidate`.
- User/tenant output: `private` or `no-store`; never shared-public caching.
- Sensitive content that must not remain in a browser cache: `no-store`.

Cookies, authorization, `Set-Cookie`, middleware, unsupported `Vary`, large responses, and dynamic header APIs can reduce cache hits. Inspect deployed cache headers and hit ratio.

Performance gates:

- explicit image dimensions and Firebase-compatible image strategy;
- discoverable/prioritized LCP resource;
- no blocking analytics, CMP, chat widget, experiment, or ad script;
- route p95 latency, error rate, and cache hit monitoring;
- field Core Web Vitals on deployed traffic/staging where feasible.

## Separate environments and previews

Use separate Firebase/GCP projects for development, staging, and production. Apps in one Firebase project share important service boundaries; multiple web app registrations do not provide full environment isolation.

- Use `demo-*` project IDs or explicit emulator config locally to prevent fallback into real resources.
- Use a dedicated staging App Hosting backend/project on a staging branch.
- Use Hosting preview channels for static sites, but remember URLs are public and backend resources must still be isolated.
- Do not assume App Hosting has Vercel-style ephemeral per-PR previews; design a staging workflow.
- Keep environment mapping in reviewed config, not developer memory.
- Never copy production user data into lower environments without a documented minimized/anonymized process.

## Protect secrets and IAM

- Store credentials in Secret Manager/App Hosting secret bindings.
- Prefer Application Default Credentials/workload identity to service-account key files.
- Grant the App Hosting compute account only required roles.
- Restrict Firebase API keys to expected APIs/apps even though the client key is not authorization.
- Keep secrets out of `NEXT_PUBLIC_*`, Remote Config, source, build logs, error messages, client bundles, and analytics.
- Decide whether secret versions should be pinned for reproducibility or resolve `latest` at build; document rotation behavior.
- Scan committed history and build artifacts, not only the current `.env`.

## Gate analytics, ads, and Remote Config

Design consent before SDK initialization. Firebase Analytics APIs can default consent types to granted; in prior-opt-in contexts, set denied defaults before measurement or defer initialization until the consent manager resolves.

Control separately:

- `analytics_storage`;
- `ad_storage`;
- `ad_user_data`;
- `ad_personalization`;
- optional diagnostic/performance/session-replay tools.

Persist the decision, permit withdrawal, update SDK state immediately, and verify behavior with network inspection and Tag Assistant/appropriate vendor tools. Consent Mode communicates a state; it does not obtain legally valid consent by itself.

Remote Config rules:

- ship local defaults;
- never store secrets or decide authorization/entitlements;
- avoid structural mid-session changes;
- activate known config and fetch the next version in the background when possible;
- keep a local fallback and bounded failure state;
- remember web A/B testing depends on Analytics and identity/storage behavior.

## Use emulators and release gates

Provide one command for applicable local services:

- App Hosting/Hosting;
- Authentication;
- Firestore;
- Storage;
- Functions;
- SQL Connect/PGlite when selected.

Use `firebase emulators:exec` in CI so services start and stop reliably. Seed deterministic records and users. Block network fallthrough to production.

Release sequence:

1. Format, lint, typecheck, unit/component tests.
2. Positive and negative Security Rules tests.
3. SQL schema/connector compatibility and generated SDK freshness.
4. Emulator integration and end-to-end primary/recovery flows.
5. Locked production build.
6. Accessibility, performance, headers, cache, auth redirect, and consent tests on staging.
7. Manual approval for data-destructive changes.
8. Staging deploy and smoke test.
9. Production deploy and post-deploy smoke/monitoring.

Rollback of code does not restore deleted data. Pair releases with backups and migration rollback/forward plans.

## Operate costs, logs, and recovery

Baseline production controls:

- Cloud Logging and Error Reporting with PII/secrets filtering;
- route request count, p95, 4xx/5xx, cache-hit ratio;
- Cloud Run/Functions CPU, memory, concurrency, instances, cold starts;
- Auth and App Check failures;
- Firestore usage, latency, denied requests, indexes/hotspots;
- billing budgets/alerts and service-specific maximum instances/quotas;
- deployment and admin audit logs;
- backup/PITR configuration and a documented restore drill;
- IAM groups, environment labels, production deletion protection where available;
- on-call/incident owner and user notification path.

Budget alerts do not stop spending. App Hosting requires the Blaze plan and may incur Cloud Run, Build, Artifact Registry, Logging, CDN, and egress charges. Estimate, cap where possible, monitor, and state remaining cost assumptions before live deployment.
