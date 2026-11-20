# Data Model: Receive Material UI Refactor

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

No tables or schema changes are added. This document describes the data the screen reads, holds, and
writes.

## Persisted entities (existing, read through Kanoa APIs)

### Receiving Order (`mes.workOrder` through `system.kanoa.order.getProductionOrders`)

Shaped by the existing `_orderSummary` (unchanged):

| Field | Source column | Screen use | Rules |
|-------|---------------|------------|-------|
| `workOrderId` | `workOrderId` | key | Required. Without it the screen shows "No eligible order was selected". |
| `orderNumber` | `workOrderName` | Order Number row | Read-only |
| `description` | `workOrderTitle`, fallback `itemDescription` | Title row | Read-only (FR-012) |
| `targetQty` | `reqdQty` | Target Quantity row | Read-only. Shown as `#,##0.###` plus the order unit (FR-013) |
| `unitName` / `itemUnitId` | `itemUnitId` → `itemUnitName` | Default UOM | Must be present, otherwise Confirm is blocked |
| `status` | `workOrderStatusName` | Status row | Read-only. Only `Scheduled` and `In Progress` are eligible |
| scheduled date | schedule row `startDate` (navigation parameter `scheduledStart`) | Scheduled Date row | Read-only. Shows "Not available" when missing (FR-012) |
| `note` | `note` | Notes field | Editable. Written only after a successful receipt (FR-015) |

### Item Unit (`mes.itemUnit` through `system.kanoa.item.getItemUnits`)

| Field | Use |
|-------|-----|
| `itemUnitName` | Dropdown label and value |
| `enabled` | Only enabled units are offered |

The selected unit is display only. It is not sent to `receiveOrder`, which always records in the
configured kg unit.

### Receipt, Lot, Transfer (unchanged)

These are written only by `kanoaScripts.custom.ops.receiving.receiveOrder`, always in kg. See
`specs/001-operator-receiving/data-model.md`.

## View state (`training/receiveMaterial` `view.custom`)

| Property | Type | Change in this feature |
|----------|------|------------------------|
| `order` | object | Unchanged |
| `scheduledStart` | date | Unchanged |
| `orderNotes` | string | Becomes the original loaded notes (used to detect changes) |
| `notesDraft` | string | **New**. Bound to the Notes text area; initialized from `orderNotes` |
| `truckAssetId`, `truckPath`, `tankAssetId`, `tankPath`, `truckOptions`, `tankOptions` | — | Unchanged |
| `receivedQtyKg` | number | Unchanged. Used to compute the outstanding quantity |
| `actualQtyKg` | number | Unchanged. Recorded as entered, in the order unit (kg) |
| `unitName` | string | **New**. Display only. Defaults to `order.unitName` |
| `unitOptions` | list | **New**. Enabled units from `system.kanoa.item.getItemUnits` |
| `submitting`, `loading`, `result`, `errorMessage` | — | Unchanged |
| `truckTreeData`, `tankTreeData` | dataset | **New**. Asset tree data, moved from the old selector bindings so the child views make no Kanoa calls |
| `warningMessage` | string | **New**. Shows a notes save failure after a recorded receipt |

### Derived defaults

- Outstanding quantity in kg = `max(0, targetQty − receivedQtyKg)`, as today.
- Default `actualQtyKg` = outstanding quantity, as today.
- Changing `unitName` does not change `actualQtyKg`.

## State transitions (confirmation)

```text
Idle ──Confirm──▶ ConfirmPopup ──No──▶ Idle
                      │Yes
                      ▼
               Submitting (both actions disabled)
                      │ receiveOrder → VALIDATION/NOT_ELIGIBLE/… ─▶ Idle + error, notes unchanged
                      │ receiveOrder → SUCCESS | TRANSFER_PENDING
                      ▼
               Notes changed? ──No──▶ Done
                      │Yes
                      ▼
               updateProductionOrderField(note) ──ok──▶ Done
                                                 └fail─▶ Done + warning (receipt kept)
Done: Confirm stays disabled (existing priorResult guard); Back enabled.
```
