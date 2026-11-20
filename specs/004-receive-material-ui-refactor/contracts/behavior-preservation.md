# Behavior Preservation Contract

**Feature**: [../spec.md](../spec.md)

This refactor changes the layout and adds a display-only unit selector and saving notes. Everything else from
features 001–003 MUST behave as before.

## Must stay identical

| Behavior | Owner | Check |
|----------|-------|-------|
| Order eligibility (`Scheduled`, `In Progress`) and reload before write | `receiveOrder`, `getReceivingOrder` | Quickstart V7 |
| Truck and tank eligibility (enabled Storage Locations under Receiving and Bulk Storage) | `getReceivingAssets`, `_getEligibleAsset` | Quickstart V3, V5 |
| Remaining-quantity rule in kg, over-receipt rejection | `receiveOrder` | Quickstart V5 |
| One receipt and one transfer per confirmation; per-order lock; reconciliation on an uncertain outcome | `receiveOrder`, the `confirmReceiveOrder` lock | Quickstart V6 |
| Transfer failure → `TRANSFER_PENDING` and guidance to Pending Transfers | `receiveOrder` + view messages | Quickstart V7 |
| Navigation parameters from the schedule (`workOrderId`, `order`, `scheduledStart`, `orderNotes`) | schedule `btnConfirm` | Quickstart V1 |
| Default quantity = outstanding quantity | view `onStartup` | Quickstart V3 |

## Diff gates

- `git diff --stat` touches only:
  - `kanoaMES/.../views/training/receiveMaterial/**`
  - `kanoaMES/.../views/training/receiveMaterialSections/**` (the new `orderInformation` and
    `operatorInputs` views)
  - `specs/004-receive-material-ui-refactor/**`
- No file under `KANOA_SCRIPTS/` changes.
- No file under `kanoaAPP/` changes.
- `training/receivingOrdersSchedule/view.json` does not change.
