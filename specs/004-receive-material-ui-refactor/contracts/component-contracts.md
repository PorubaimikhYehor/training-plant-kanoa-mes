# Component Contracts: Receive Material UI Refactor

**Feature**: [../spec.md](../spec.md) | **Research**: [../research.md](../research.md)

Paths are relative to `services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/`.

## C1. `training/receiveMaterial` page layout

```text
root (column flex, gap 2px, padding 3px)                       ← same as schedule root
├── evProgressBar  kanoa/core/templates/displays/progressBar   ← unchanged
└── flxMain (row flex, gap 3px, grow 1)                        ← same as schedule flxMain
    ├── flxActions (kanoa/container, minWidth 35px, justify center, shrink 0)
    │   └── flxAction (column, alignItems center, gap 5px, padding 5px, basis 40px, shrink 0)
    │       ├── btnBack     material/arrow_back            kanoa/button/flatIcon 30px  tooltip "Back"
    │       └── btnConfirm  material/check_circle_outline  kanoa/button/flatIcon 30px  tooltip "Confirm receipt"
    └── flxContent (column flex, grow 1, gap 6px, overflow-y auto, minWidth 0)
        ├── lblMessage            error / warning / no-order message (existing classes)
        ├── evOrderInformation    → C2
        └── evOperatorInputs      → C3
```

| Action | Enabled when | Visible | Behavior |
|--------|--------------|---------|----------|
| Back | `!view.custom.submitting` | always | `system.perspective.navigate(view='training/receivingOrdersSchedule')`. No writes |
| Confirm | `order` loaded and `!submitting` and result not `SUCCESS`/`TRANSFER_PENDING` | always | Validates locally, then opens the existing `kanoa/core/templates/inputs/confirm` popup with handler `confirmReceiveOrder`. The message states the recorded order unit, e.g. "Confirm receipt of 1,000 kg for order 0001?" |

## C2. Receiving Order Information section

Embedded view `training/receiveMaterialSections/orderInformation` (approval A2 granted 2026-11-19).

**Params**

| Param | Direction | Type | Notes |
|-------|-----------|------|-------|
| `order` | input | object | `orderNumber`, `description`, `targetQty`, `unitName`, `status` |
| `scheduledStart` | input | date | May be null |
| `notes` | input/output | string | Bidirectionally bound to the parent's `view.custom.notesDraft` |
| `enabled` | input | bool | false while submitting or after success; locks Notes |

**Layout**: row flex `wrap: wrap`, gap 6px.
- Column 1 (`basis 50%`, `grow 1`, `minWidth 320px`, column flex): five rows of 30px each. Each row
  has a label (`basis 33.333%`) and an `ia.display.label` value (`basis 66.667%`, `minWidth 0`,
  text ellipsis with the full value in the tooltip).
  Order: Order Number · Title · Target Quantity (`#,##0.### {unitName}`) · Scheduled Date
  (`MM/dd/yyyy HH:mm`, or "Unavailable") · Status.
- Column 2 (same sizing): one 68px row. The label "Notes" is aligned to the top, and the value is an
  `ia.input.text-area` (vertical scroll, no resize) bound to `notes`.

## C3. Operator Inputs section

Embedded view `training/receiveMaterialSections/operatorInputs` (approval A2 granted 2026-11-19). Column flex, full width, rows of 30px with the same 1/3 – 2/3 proportions.

**Params**

| Param | Direction | Type | Notes |
|-------|-----------|------|-------|
| `truckOptions`, `tankOptions` | input | list | From `getReceivingAssets()`. Empty → the explanatory message row is shown |
| `truckTreeData`, `tankTreeData` | input | dataset | Asset tree data loaded by the parent (moved from the old selector bindings) |
| `truckPath`, `tankPath` | input | string | Selected paths held in the parent's `view.custom` |
| `truckAssetId`, `tankAssetId` | output | int | Set through the existing `receivingTruckSelected` and `receivingTankSelected` message handlers |
| `actualQty` | input/output | number | Bound to the parent's `view.custom.actualQtyKg` |
| `unitName` | input/output | string | Bound to the parent's `view.custom.unitName`. Display only |
| `unitOptions` | input | list | `[{label, value}]` of enabled units from `system.kanoa.item.getItemUnits` |
| `enabled` | input | bool | Locks the unit dropdown while submitting or after success |
| `qtyEnabled` | input | bool | Locks the quantity input. It uses the existing rule (no receipt history, no target, or fully received → locked), plus submitting or success |

**Rows**
1. Receiving Truck → `kanoa/core/templates/selectors/tree/selector`, with the same parameters and
   handler as today.
2. Destination Tank → the same selector and handler as today.
3. Actual Quantity → value area row flex, gap 6px:
   `ia.input.numeric-entry-field` (`grow 1`, `minWidth 80px`, format `#,##0.###`, no spinner) +
   `ia.input.dropdown` (`basis 110px`, `shrink 0`, options `unitOptions`, default order unit).
   The selection is display only and does not change the recorded quantity.

## C5. Message handler `confirmReceiveOrder` (existing, extended)

Order of operations inside the existing lock and guards:
1. `receiveOrder(workOrderId, actualQtyKg, truckAssetId, tankAssetId, authUser)`. This call is
   **unchanged**.
2. If the status is `SUCCESS` or `TRANSFER_PENDING` and `notesDraft != orderNotes`, call
   `system.kanoa.order.updateProductionOrderField(workOrderId, 'note', notesDraft, userId)`, logging
   the start and outcome. On success, set `orderNotes = notesDraft`. On failure, set
   `warningMessage`.

## Implementation notes (2026-11-19)

- **Location**: Ignition cannot nest a view inside another view's resource folder (no precedent
  among the project's 700+ views), so the approved A2 views live in the sibling folder
  `training/receiveMaterialSections/`. Their purpose and contents are unchanged.
- **Empty values**: Empty values show `—`, and a missing target quantity or date shows
  `Unavailable`. Both reuse the existing transforms of feature 003.
- **Kanoa calls in the section views**: The only one is `system.kanoa.utilities.formatNumber` in the
  Target Qty display transform, a formatting utility carried over from feature 003. There are no
  data reads or writes.
- **Embedded selectors**: `ia.display.view` has no `enabled` property, so the tree selectors stay
  clickable after success. Confirm is disabled at that point, so a new selection cannot be
  submitted.
