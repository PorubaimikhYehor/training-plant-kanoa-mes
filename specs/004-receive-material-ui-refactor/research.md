# Research: Receive Material UI Refactor

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-11-19

Evidence was gathered from the repository exports and the running local stack
(`training-kanoa-mes-yp_db_1`, `training-kanoa-mes-yp_kanoa_1`). Paths are relative to
`services/ignition/projects/`.

## R1. Left action panel on the Receiving Orders Schedule

**Finding**: The schedule's action panel is not an embedded view. It is an inline structure in
`kanoaMES/.../views/training/receivingOrdersSchedule/view.json`:

- `flxMain` (row flex, `gap: 3px`) → `flxActions` (`kanoa/container`, `minWidth: 35px`,
  `justify: center`, `shrink: 0`) → `flxAction` (column flex, `alignItems: center`, `gap: 5px`,
  `padding: 5px`, `basis: 40px`, `shrink: 0`).
- Each action is an `ia.input.button` with `text: ""`, a `material/*` icon, style class
  `kanoa/button/flatIcon`, `width: 30px`, and `basis: 30px; shrink: 0`. Visibility comes from
  `position.display` bindings.
- Confirm uses `material/check_circle_outline`. `kanoaAPP` uses `material/arrow_back` for back
  navigation in three places.

**Decision**: Reproduce the same `flxMain → flxActions → flxAction` structure, properties, and
classes in `receiveMaterial`, with two buttons: Back (`material/arrow_back`, first) and Confirm
(`material/check_circle_outline`). Add tooltips "Back" and "Confirm receipt" because icon-only
buttons replace the current text buttons.

**Rationale**: Copying the property values of a native container pattern is configuration, not a
new component. It gives an identical position, size, and responsive behavior (SC-001).

**Alternatives considered**: Extracting the panel into a shared embedded view. This would be a new
component under Principle VI and would require changing the schedule screen too, which is out of
scope. Rejected.

## R2. Label-value (4/12 – 8/12) row

**Finding**: No native template provides a horizontal label/value row with 1/3 – 2/3 proportions.
- `kanoa/core/templates/displays/valueWithLabel` is a stacked value-over-label tile with padding.
  It cannot hold an input, so it is not suitable.
- `kanoa/core/templates/displays/valueDisplay` is a right-aligned numeric value with units, and it
  has no label column.
- The current `receiveMaterial` rows (`flxCnt*`) already use the native pattern: a row flex
  containing an `ia.display.label` label and a value component. Only the bases (`65px`/`200px`)
  differ from the required proportions.

**Decision**: Use native row `ia.container.flex` rows with label `basis: 33.333%`, `shrink: 0`,
class `kanoa/font/default` (label style as in the current view), and value `basis: 66.667%`,
`grow: 1`, `shrink: 1`, `minWidth: 0`. Read-only values are `ia.display.label`. Row height is
`30px`, and the Notes row is `68px` (2 × 30px + gap).

**Rationale**: Percentage bases give exactly 4/12 and 8/12 of the container at any width. This is
the same native primitive already used on this screen.

**Alternatives considered**: `valueWithLabel` (wrong orientation, input not supported); a new
label-value embedded view (new component that needs approval, and gives no benefit over the native
flex row). Rejected.

## R3. Responsive layout (desktop, tablet, phone)

**Finding**: Neither `kanoaAPP` nor `kanoaMES` uses `ia.container.breakpt`. The Kanoa screens
achieve responsiveness with flex `wrap` and `basis`/`minWidth`. The schedule screen relies on
`flxActions` with `shrink: 0`, so the panel keeps its 40px width at every size.

**Decision**: Make the order information section a row flex with `wrap: wrap` and two column
containers, each with `basis: 50%`, `grow: 1`, and `minWidth: 320px`. When the available width is
below about 640px, the columns wrap into a vertical stack (tablet wrap and phone stack). The
Operator Inputs section is a column flex below it with `basis: auto` and full width. The main
content area scrolls vertically (`overflow-y: auto`). The left action panel keeps the schedule's
fixed 40px column at all widths.

**Rationale**: This matches the existing Kanoa responsive technique and requires no new component.
The 320px minimum keeps a 1/3 label of at least ~105px, so labels such as "Destination Tank" fit.

**Alternatives considered**: A breakpoint container with separate desktop and mobile children. This
duplicates every field and its bindings, and no Kanoa screen uses it. Rejected.

## R4. Truck and tank selectors

**Finding**: The current view already embeds `kanoa/core/templates/selectors/tree/selector` for
both (`evTreeTruck`, `evTreeTank`). The view uses message handlers `receivingTruckSelected` and
`receivingTankSelected`, and the eligible lists come from
`kanoaScripts.custom.ops.receiving.getReceivingAssets()` (enabled Storage Locations under
`Training Plant\Receiving` and `Training Plant\Bulk Storage`).

**Decision**: Keep both selectors, their parameters, message handlers, and data sources unchanged.
Only move them into the 8/12 value area of their label-value rows.

**Rationale**: These are the existing selectors the spec requires (FR-018, FR-019). Moving them
changes no behavior.

## R5. Unit of measure: source and conversion

**Findings** (local database `kanoa`):
- `mes.itemUnit` has only `itemUnitId`, `itemUnitName`, `enabled`, and audit columns. Enabled units:
  units, oz, Bottles, Cans, Cases, Gallons, lbs, Loaves, Trays, ea, kg.
- `inv.unitOfMeasure` has only `uomId`, `uomCode`, `uomName`, and audit columns.
- There is no conversion table, factor column, or conversion API in KanoaMES 1.15.11:
  `system.kanoa.item.*` exposes `getItemUnits`, `addItemUnit`, `updateItemUnit`, and
  `deleteItemUnit` only, and `mes.itemAttribute` does not exist.
- Orders store `mes.workOrder.itemUnitId`. The only training order (`0001`) is in kg.
- `receiveOrder`, `getReceivedQtyForOrder`, and the receipt history are kg-only, and they block any
  non-kg order with `UNIT_ERROR`.

**Decision (2026-11-19, replaces proposal A1)**: Do not convert units. The unit dropdown offers all
enabled `mes.itemUnit` rows from the native `system.kanoa.item.getItemUnits({'enabled': True})`. It
defaults to the order unit and is display only: the quantity is passed to the unchanged
`receiveOrder` as entered, so it is validated and recorded in the order's unit (kg). The
confirmation prompt and success message state the recorded unit ("… kg") to reduce the chance of
misreading. No `KANOA_SCRIPTS` change is made.

**Rationale**: The user decided that conversion will be a separate future requirement. A display-only
selector keeps the layout ready for that requirement without changing the proven write path or
corrupting receipt history. Recording in another unit would make `getReceivedQtyForOrder` return
`UNIT_ERROR` for every later receipt on the order.

**Alternatives considered**:
- (a) Proposal A1, exact mass conversion methods in `KANOA_SCRIPTS`: declined by the user and
  deferred to the conversion requirement.
- (b) Block Confirm when the selected unit differs from the order unit: offered and not chosen.
- (c) Record the receipt in the selected unit: needs a `receiveOrder` change and breaks the
  receipt-history check. Rejected.

**Known risk**: An operator who selects lbs and types a pound value has it recorded as kg. This is
accepted until the conversion requirement is delivered and is mitigated by stating the recorded
unit in the confirmation prompt.

## R6. Saving notes with the receipt

**Finding**: `kanoaAPP/.../mes/workOrders/woEditor` saves order fields with the native
`system.kanoa.order.updateProductionOrderField(workOrderId, field, value, userId)`. The order
column is `mes.workOrder.note`. The current Receive Material screen reads notes from the schedule
row (`orderNotes` parameter) and falls back to `system.kanoa.order.getProductionOrders`.

**Decision**: In the existing `confirmReceiveOrder` message handler, after `receiveOrder` returns
`SUCCESS` or `TRANSFER_PENDING`, and only if the edited notes differ from the loaded notes, call
`system.kanoa.order.updateProductionOrderField(workOrderId, 'note', notes, userId)` with
`userId = system.kanoa.security.getIDPUserId(self.session.props.auth.user)`. Log the start and
outcome through `kanoaScripts.custom.ops.receiving.getLogger()`. If the notes save fails after the
receipt is recorded, keep the receipt result, show a warning ("Receipt recorded, but notes were not
saved"), and leave the edited text in the field.

**Rationale**: This is a single native API call made after the write that defines success, so it is
configuration and not reusable business logic (Principle VI). The existing handler lock, the
`priorResult` guard, and the `submitting` flag prevent a second save (FR-015). Comparing with the
loaded notes avoids unnecessary writes. The call sets a value, so a rerun is idempotent.

**Alternatives considered**: Saving notes inside `receiveOrder` (true atomicity, but it changes the
shared write path and requires renewed approval of an existing method). Rejected. A failed notes
save after a successful receipt is reported to the operator instead, which the spec allows because
the receipt is the primary outcome.

## R7. Embedding the two sections as reusable views

**Finding**: FR-008 requires each section to be self-contained and reusable. In Perspective, the
only unit that is reusable across views is an embedded view, which is a new component under
Principle VI.

**Decision (approval A2 granted 2026-11-19)**: Create two project-local embedded
views in `kanoaMES`:
- `training/receiveMaterialSections/orderInformation`: input parameter `order` (read-only fields and
  scheduled date), plus a bidirectional `notes` parameter.
- `training/receiveMaterialSections/operatorInputs`: input parameters for the asset lists and the
  default quantity and unit, plus bidirectional outputs `truckAssetId`, `tankAssetId`,
  `actualQty`, and `unitName`.

Both views hold layout and bindings only. They make no Kanoa calls and contain no business logic.
The parent `receiveMaterial` view keeps all loading, validation, and confirmation scripts.

**Alternative considered**: Two named flex containers inside `receiveMaterial/view.json`. They are
visually identical but cannot be reused by other views, so they do not meet FR-008. Rejected after
A2 was approved.

## R8. UOM selector component

**Finding**: There is no Kanoa item-unit selector template. `qds/templates/selectors/engUnitSelector`
targets quality engineering units (`system.kanoa.quality.config.getUnits`), which is a different
entity, and it includes add and delete actions. `ia.input.dropdown` is the native selector used in
261 places in `kanoaAPP`.

**Decision**: Use a native `ia.input.dropdown`. Its `options` come from
`system.kanoa.item.getItemUnits({'enabled': True})`, loaded once in the parent view's `onStartup`
and shaped as `[{label, value}]` by `itemUnitName`. The default value is the order unit. The
dropdown has `basis: 110px` and `shrink: 0`. The quantity `ia.input.numeric-entry-field` has
`grow: 1` and `minWidth: 80px`. Both sit in one row flex inside the 8/12 value area. If loading
units fails, the options contain only the order unit and a warning is logged; receiving is not
blocked, because the unit is display only.

## R9. Back behavior while a confirmation is in progress

**Finding**: The current Back button is always enabled. FR-006 requires both actions to be
unavailable during confirmation.

**Decision**: Bind `props.enabled` of both icon buttons to `!{view.custom.submitting}`. Confirm is
also disabled when no order is loaded or when the result is already `SUCCESS` or
`TRANSFER_PENDING`.
