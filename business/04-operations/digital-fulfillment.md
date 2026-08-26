# Digital product fulfillment

## MVP promise

The customer receives the exact licensed 3MF revision shown on the order, with durable order/download access and clear instructions. For V1, do not promise STL, PDF, ZIP, slicer profiles, textures, components, or manufacturer extensions because the current publisher accepts one safe-core 3MF.

## Required flow

1. Customer sees revision, format, units, printer envelope, material/profile basis, included parts, tested scope, exclusions and license before paying.
2. Checkout records country, tax treatment, consent/withdrawal information and the exact release identifier.
3. A verified payment event creates one idempotent entitlement.
4. Account/order page exposes the exact immutable revision through a short-lived signed URL.
5. Expired and unauthorized links fail; entitlement can be blocked for refund, fraud, legal takedown or safety incident while preserving audit history.
6. Customer receives confirmation, invoice/receipt as applicable, license and support route on a durable medium.

## Operational controls

- Separate ingestion, approval/publishing, payment, and download-signing identities.
- Store hashes and release IDs on order line items; never resolve “latest” for an old order.
- Retry webhooks idempotently and reconcile payment, order and entitlement state.
- Monitor failed delivery, unusual download volume, signature errors, and orphaned storage objects.
- Test backup/restore for catalog, entitlements and storage metadata.
- Define whether buyers receive future minor/major revisions; do not make silent lifetime-update promises.

## Customer package for V1

Because only one file is currently publishable, essential print/use information must appear on the product page, order confirmation/account, and embedded 3MF metadata where feasible. Extend the manifest/publisher before selling a multi-file documentation bundle.

## Launch acceptance

- successful guest/account purchase path as designed;
- exact-revision entitlement and download;
- retry and duplicate webhook handling;
- expired/unauthorized negative tests;
- refund and entitlement behavior;
- takedown/kill switch;
- support can reproduce the purchased hash from the order.

