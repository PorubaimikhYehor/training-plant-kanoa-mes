---

description: "Task list for the Receive Material UI Refactor"
---

# Tasks: Receive Material UI Refactor

**Input**: Design documents from `specs/004-receive-material-ui-refactor/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: The spec does not request automated tests. Verification is by the Gateway checks in
[quickstart.md](quickstart.md), as required by constitution Principle V. Each story ends with a
validation task.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated
on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on unfinished tasks)
- **[Story]**: The user story the task belongs to (US1–US5)

## Path Conventions

- `VIEWS` = `services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training`
- Page view: `VIEWS/receiveMaterial/view.json`
- New child views (approval A2): `VIEWS/receiveMaterialSections/orderInformation/view.json` and
  `VIEWS/receiveMaterialSections/operatorInputs/view.json`
- Reference only, never edit: `VIEWS/receivingOrdersSchedule/view.json`, everything under
  `services/ignition/projects/kanoaAPP/`, and
  `services/ignition/projects/KANOA_SCRIPTS/ignition/script-python/kanoaScripts/custom/ops/receiving/code.py`

## Ground rules for every task

- Edit view JSON as Designer exports it: tab-indented Jython in `script` strings, `meta.name` on
  every component, and positions in `position` (`basis`, `grow`, `shrink`).
- Keep the existing component names `evProgressBar`, `evTreeTruck`, and `evTreeTank`, the message
  handlers `receivingTruckSelected`, `receivingTankSelected`, and `confirmReceiveOrder`, and the
  `custom.errorMessage` / `custom.result` `onChange` scripts unless a task says otherwise.
- Do not change `receiveOrder` or any other `kanoaScripts.custom.ops.receiving` function, and do not
  add script functions (Principle VI; only A2 is approved).
- The unit selection is **display only**. Never pass it to `receiveOrder` and never convert the
  quantity.

---

## Phase 1: Setup

**Purpose**: Capture the baseline and prepare the evidence location.

- [ ] T001 Record the baseline: run `git status --porcelain` and `git diff --stat` from the
  repository root, and save the output plus a screenshot of the current Receive Material and
  Receiving Orders Schedule screens (desktop width, order `0001`) to
  `specs/004-receive-material-ui-refactor/evidence/baseline.md`.
- [X] T002 [P] Measure and record in `specs/004-receive-material-ui-refactor/evidence/baseline.md`
  the schedule's action panel values from `VIEWS/receivingOrdersSchedule/view.json`: `flxMain`
  props, `flxActions` props and position, `flxAction` props and position, and the props, position,
  and style of `btnConfirm` (icon `material/check_circle_outline`, class `kanoa/button/flatIcon`,
  `width: 30px`, `basis: 30px`, `shrink: 0`). Later tasks copy these values exactly.

---

## Phase 2: Foundational (blocking)

**Purpose**: The page skeleton, the two empty child views, and the shared view state. Every story
depends on this phase.

- [X] T003 [P] Create `VIEWS/receiveMaterialSections/orderInformation/resource.json` by copying
  `VIEWS/receiveMaterial/resource.json` with `"files": ["view.json"]` (no thumbnail) and
  `lastModification.timestamp` set to the current UTC time. Then create
  `VIEWS/receiveMaterialSections/orderInformation/view.json` with:
  - `params`: `order` (default `{}`), `scheduledStart` (default `null`), `notes` (default `""`),
    and `enabled` (default `true`).
  - `propConfig`: `params.order`, `params.scheduledStart`, and `params.enabled` with
    `paramDirection: "input"`, and `params.notes` with `paramDirection: "inout"`.
  - `props.defaultSize`: `{"width": 800, "height": 200}`.
  - `root`: an `ia.container.flex` with `direction: "row"`, `wrap: "wrap"`, and
    `style.gap: "6px"`, and no children yet.
  The file must contain no Kanoa calls and no scripts.
- [X] T004 [P] Create `VIEWS/receiveMaterialSections/operatorInputs/resource.json` (same pattern as T003)
  and `VIEWS/receiveMaterialSections/operatorInputs/view.json` with:
  - `params`: `truckOptions` (`[]`), `tankOptions` (`[]`), `truckTreeData` (`null`),
    `tankTreeData` (`null`), `truckPath` (`null`), `tankPath` (`null`), `actualQty` (`null`),
    `unitName` (`null`), `unitOptions` (`[]`), and `enabled` (`true`).
  - `propConfig`: `truckOptions`, `tankOptions`, `truckTreeData`, `tankTreeData`, `truckPath`,
    `tankPath`, `unitOptions`, and `enabled` with `paramDirection: "input"`, and `actualQty` and `unitName` with `paramDirection: "inout"`.
  - `props.defaultSize`: `{"width": 800, "height": 120}`.
  - `root`: an `ia.container.flex` with `direction: "column"` and `style.gap: "4px"`, and no
    children yet.
  The file must contain no Kanoa calls and no scripts.
- [X] T005 Restructure the component tree in `VIEWS/receiveMaterial/view.json` to match contract
  C1 in [contracts/component-contracts.md](contracts/component-contracts.md):
  - `root`: column flex with `style: {"gap": "2px", "padding": "3px"}`, as on the schedule.
  - Children, in order: the existing `evProgressBar` (keep its props and bindings; move it out of
    `flxCntProgress`), then a new `flxMain` (row flex, `style.gap: "3px"`, `position.grow: 1`).
  - Inside `flxMain`: an empty `flxActions` with the T002 values, then `flxContent` (column flex,
    `grow: 1`, `style: {"gap": "6px", "overflowY": "auto", "minWidth": 0}`).
  - Move `lblNoOrder` into `flxContent` as its first child and keep its existing display binding.
  - Delete `lblTitle`, `flxCntProgress`, and all `flxCnt*` rows, `flxCntActions`, `btnSubmit`, and
    `btnBack`. Their replacements come in US1–US3. **Keep** the `evTreeTruck` and `evTreeTank`
    JSON (`props.params` and `propConfig`) in a scratch note, because T006 and T016 reuse it.
- [X] T006 Extend the view state in `VIEWS/receiveMaterial/view.json` as in
  [data-model.md](data-model.md):
  - Add `custom.notesDraft` (`null`), `custom.unitName` (`null`), `custom.unitOptions` (`[]`), and
    `custom.warningMessage` (`""`).
  - Add `custom.truckTreeData` and `custom.tankTreeData`, each with the **exact** binding taken from
    the old `props.params.values.data` of `evTreeTruck` / `evTreeTank`: expression `1` with a script
    transform `return system.kanoa.asset.getAssets({'assetPath': 'Training Plant\\Receiving\\%',
    'assetTypeName': 'Storage Location', 'enabled': True})`, using `Bulk Storage` for tanks. This
    keeps every Kanoa call in the page view.
  - Keep `custom.actualQtyKg`, which is recorded as entered in the order unit (kg).
  - Add a `custom.warningMessage` `onChange` script that, when the value is non-empty, calls
    `system.kanoa.toast.show({'type': 'warning', 'message': self.custom.warningMessage})`.
- [X] T007 Extend the existing `onStartup` script in `VIEWS/receiveMaterial/view.json`, without
  changing its existing logic:
  - Reset `self.custom.warningMessage = ''` at the top.
  - After the notes load, set `self.custom.notesDraft = self.custom.orderNotes or ''`.
  - Set `self.custom.unitName = (self.custom.order or {}).get('unitName')`.
  - Load units in their own `try` block:
    `rows = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.item.getItemUnits({'enabled': True}))`,
    then `self.custom.unitOptions = [{'label': r['itemUnitName'], 'value': r['itemUnitName']} for r in rows]`.
    Make sure the order unit is present: if it is missing, insert it first.
  - On an exception, log through `kanoaScripts.custom.ops.receiving.getLogger().warn(...)` and set
    `unitOptions` to only the order unit. Do **not** set `errorMessage`, because the unit is
    display only and must not block receiving (research R8).
  - When `order.unitName` is empty, set
    `errorMessage = 'This order has no unit of measure. Ask a supervisor to correct the order.'`
    (spec Edge Cases).

**Checkpoint**: The page opens with the progress bar, an empty action panel column, and an empty
content area. The JSON files parse (`python3 -m json.tool`).

---

## Phase 3: User Story 1 — Same structure and navigation as the schedule (P1) 🎯 MVP

**Goal**: The left icon panel with Back and Confirm only, behaving exactly as in the schedule and
keeping the existing receiving outcome.

**Independent Test**: Quickstart V1. Compare the panel with the schedule, check that Back returns
with no writes, and check that Confirm records a receipt with the existing feedback.

- [X] T008 [US1] Add `btnBack` as the first child of `flxAction` in
  `VIEWS/receiveMaterial/view.json`:
  - `ia.input.button` with `text: ""`, `image.icon.path: "material/arrow_back"`,
    `style: {"classes": "kanoa/button/flatIcon", "width": "30px"}`, `position: {"basis": "30px",
    "shrink": 0}`, and `meta.tooltip: {"enabled": true, "text": "Back"}`.
  - Bind `props.enabled` with the expression `!{view.custom.submitting}`.
  - `onActionPerformed` (scope `G`):
    `system.perspective.navigate(view='training/receivingOrdersSchedule')`.
- [X] T009 [US1] Add `btnConfirm` after `btnBack` in `flxAction` in
  `VIEWS/receiveMaterial/view.json`:
  - The same props as T008, with `image.icon.path: "material/check_circle_outline"` and the tooltip
    text `"Confirm receipt"`.
  - Bind `props.enabled` with an expression that is true only when `{view.custom.order}` is
    non-empty, `!{view.custom.submitting}`, and the status of `{view.custom.result}` is not
    `SUCCESS` or `TRANSFER_PENDING`. Use an expression structure with a script transform, as in the
    schedule's `btnConfirm`.
  - `onActionPerformed`: reuse the old `btnSubmit` script unchanged, except that the confirmation
    text reads `'Confirm receipt of %s %s for order %s?' % (qty, unitOfOrder, orderNumber)`, where
    `unitOfOrder = (self.view.custom.order or {}).get('unitName') or 'kg'` and `qty` is
    `self.view.custom.actualQtyKg` formatted with `'{:,.3f}'.format(...)` and trailing zeros
    stripped. This states the **recorded** unit (FR-022a).
- [X] T010 [US1] In the `custom.result` `onChange` script in `VIEWS/receiveMaterial/view.json`,
  replace the hard-coded `kg` in the success and transfer-pending toasts with the order unit
  (`(self.custom.order or {}).get('unitName') or 'kg'`). Make no other change to that script.
- [ ] T011 [US1] Validate quickstart V1 and V7 (regression: partial-receipt default,
  double-click Confirm creates one lot, ineligible order, transfer failure → Pending Transfers
  guidance). Record the results and side-by-side screenshots in
  `specs/004-receive-material-ui-refactor/evidence/us1.md`.

**Checkpoint**: The screen can record receipts with the new panel. Order and input sections are
still pending.

---

## Phase 4: User Story 2 — Order information in a two-column label-value layout (P1)

**Goal**: The Receiving Order Information section with five read-only rows in column 1.

**Independent Test**: Quickstart V2. The values match Kanoa, every label is one third of its row,
the title falls back to the item description, and a missing date shows "Not available".

- [X] T012 [US2] Build column 1 in `VIEWS/receiveMaterialSections/orderInformation/view.json`:
  - `flxColInfo`: column flex, `position: {"basis": "50%", "grow": 1, "shrink": 1}`,
    `style: {"minWidth": "320px", "gap": "4px"}`.
  - Five rows named `flxOrderNumber`, `flxTitle`, `flxTarget`, `flxSchedule`, and `flxStatus`. Each
    is a row flex with `position.basis: "30px"`, `shrink: 0`, and `alignItems: "center"`.
  - Each row holds a label `lbl<Name>Label` (`basis: "33.333%"`, `shrink: 0`, class
    `kanoa/font/default`, texts "Order #", "Title", "Target Qty", "Schedule Date", "Status") and a
    value `lbl<Name>Value` (`ia.display.label`, `basis: "66.667%"`, `grow: 1`, `shrink: 1`,
    `style: {"minWidth": 0, "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace":
    "nowrap"}`, `meta.tooltip.text` bound to the same value).
- [X] T013 [US2] Add the value bindings in `VIEWS/receiveMaterialSections/orderInformation/view.json`:
  - Order Number → `{view.params.order.orderNumber}`.
  - Title → `{view.params.order.description}` (already falls back to the item description, FR-012).
  - Target Qty → a script transform that returns `'{:,.3f}'.format(float(targetQty))` with trailing
    zeros and dot stripped, plus `' ' + unitName`, or `'Not available'` when `targetQty` is None
    (FR-013).
  - Schedule Date → `{view.params.scheduledStart}` with a transform that returns `'Not available'`
    when it is None. Otherwise use `system.date.format(value, 'yyyy-MM-dd HH:mm')`, the same format
    as the previous view.
  - Status → `{view.params.order.status}`.
  Use `null` / empty-safe transforms so the view never shows a binding error.
- [X] T014 [US2] Embed the section in `VIEWS/receiveMaterial/view.json`: add `evOrderInformation`
  (`ia.display.view`, `props.path: "training/receiveMaterialSections/orderInformation"`,
  `position.shrink: 0`, `props.useDefaultHeight: false`, `style.minHeight: "160px"`) to
  `flxContent` after `lblNoOrder`. Bind `params.order` → `{view.custom.order}` and
  `params.scheduledStart` → `{view.custom.scheduledStart}`. Hide it with a `position.display`
  binding when `{view.custom.order}` is empty.
- [ ] T015 [US2] Validate quickstart V2 and record the results in
  `specs/004-receive-material-ui-refactor/evidence/us2.md`.

**Checkpoint**: The order information column renders. Notes (US4) are not yet present.

---

## Phase 5: User Story 3 — Operator inputs with quantity and unit (P1)

**Goal**: A full-width Operator Inputs section with the existing truck and tank selectors and the
quantity plus display-only unit dropdown.

**Independent Test**: Quickstart V3, V4, V5. The section is below the order information, the
selectors offer only eligible assets, the quantity defaults to the outstanding quantity, and the
unit defaults to the order unit. Selecting another unit does not change what is recorded.

- [X] T016 [US3] Build the truck and tank rows in
  `VIEWS/receiveMaterialSections/operatorInputs/view.json`:
  - Rows `flxTruck` and `flxTank`: row flex, `basis: "30px"`, `shrink: 0`, and
    `alignItems: "center"`.
  - Each has a label (`basis: "33.333%"`, `shrink: 0`, class `kanoa/font/default`, texts
    "Receiving Truck" and "Destination Tank") and the selector `evTreeTruck` / `evTreeTank`
    (`ia.display.view`, `path: "kanoa/core/templates/selectors/tree/selector"`, `basis: "66.667%"`,
    `grow: 1`, `style: {"minWidth": 0, "height": 30}`) with **exactly** the `props.params` saved
    in T005. Keep the `msgHandler` values `receivingTruckSelected` / `receivingTankSelected` so
    the parent's page-scoped handlers keep working.
  - Replace the old selector bindings: `props.params.values.data` ← `{view.params.truckTreeData}` /
    `{view.params.tankTreeData}`, and `props.params.values.path` ← `{view.params.truckPath}` /
    `{view.params.tankPath}` (property bindings with `overlayOptOut: true`). The child view makes no
    Kanoa call.
  - After each row, add an empty-state row (`flxTruckEmpty` / `flxTankEmpty`): a 33.333% spacer
    label plus a message label with the previous texts "No eligible receiving trucks were found.
    Ask an administrator…" / "No eligible destination tanks were found. Ask an administrator…".
    Show it with a `position.display` binding when `len({view.params.truckOptions}) = 0` (and the
    same for tanks). Hide the selector row in that case (FR-023).
- [X] T017 [US3] Build the Actual Quantity row in
  `VIEWS/receiveMaterialSections/operatorInputs/view.json`:
  - `flxQty`: row flex, `basis: "30px"`, `shrink: 0`, `alignItems: "center"`. Label "Actual Qty"
    (`basis: "33.333%"`, `shrink: 0`).
  - The value container `flxQtyValue`: row flex, `basis: "66.667%"`, `grow: 1`,
    `style: {"gap": "6px", "minWidth": 0}`.
  - Inside it, `numActualQty` (`ia.input.numeric-entry-field`, `format: "#,##0.###"`,
    `spinner.enabled: false`, class `kanoa/font/default`, `grow: 1`, `shrink: 1`,
    `style.minWidth: "80px"`, `props.value` bound **bidirectionally** to
    `{view.params.actualQty}`), then `ddUnit` (`ia.input.dropdown`, `basis: "110px"`, `shrink: 0`,
    `props.options` ← `{view.params.unitOptions}`, `props.value` bound **bidirectionally** to
    `{view.params.unitName}`, `props.multiSelect: false`, `props.showClearIcon: false`).
  - Bind `props.enabled` of `numActualQty`, `ddUnit`, and both selector views to
    `{view.params.enabled}`.
- [X] T018 [US3] Embed the section in `VIEWS/receiveMaterial/view.json`: add `evOperatorInputs`
  (`ia.display.view`, `path: "training/receiveMaterialSections/operatorInputs"`, `position.shrink: 0`,
  `props.useDefaultHeight: false`, `style.minHeight: "110px"`) to `flxContent` after
  `evOrderInformation`. Add these bindings:
  - `params.truckOptions` ← `{view.custom.truckOptions}`.
  - `params.tankOptions` ← `{view.custom.tankOptions}`.
  - `params.truckTreeData` ← `{view.custom.truckTreeData}` and `params.tankTreeData` ←
    `{view.custom.tankTreeData}`.
  - `params.truckPath` ← `{view.custom.truckPath}` and `params.tankPath` ← `{view.custom.tankPath}`.
  - `params.actualQty` ↔ `{view.custom.actualQtyKg}` (bidirectional).
  - `params.unitName` ↔ `{view.custom.unitName}` (bidirectional).
  - `params.unitOptions` ← `{view.custom.unitOptions}`.
  - `params.enabled` ← an expression that is true when `!{view.custom.submitting}` and the result
    status is not `SUCCESS` or `TRANSFER_PENDING`.
  Hide the section when `{view.custom.order}` is empty.
- [ ] T019 [US3] Confirm in a Perspective session that selecting a truck or tank inside the child
  view still updates `view.custom.truckAssetId` / `tankAssetId` in the parent through the existing
  handlers. If page-scoped messages do not reach the parent, set `sessionScope` to false and
  `pageScope` to true on both handlers in `VIEWS/receiveMaterial/view.json`. Do not move the
  handlers into the child view.
- [ ] T020 [US3] Validate quickstart V3, V4 (pick `lbs`, enter 500: the prompt says "500 kg", the lot
  event is 500 kg, and the next open of the order has no `UNIT_ERROR`), and V5. Record the results
  in `specs/004-receive-material-ui-refactor/evidence/us3.md`.

**Checkpoint**: The full receive flow works with the new layout: US1 + US2 + US3 = MVP.

---

## Phase 6: User Story 4 — Edit order notes during receiving (P2)

**Goal**: An editable Notes area in column 2, saved only after a successful confirmation.

**Independent Test**: Quickstart V6. Back and failed confirmations leave the notes unchanged. A
successful confirmation saves the notes once, and confirming without edits writes nothing.

- [X] T021 [P] [US4] Add column 2 to `VIEWS/receiveMaterialSections/orderInformation/view.json`:
  - `flxColNotes`: the same sizing as `flxColInfo` (T012).
  - One row `flxNotes`: row flex, `basis: "68px"`, `shrink: 0`, `alignItems: "flex-start"`.
  - Label "Notes": `basis: "33.333%"`, `shrink: 0`, class `kanoa/font/default`,
    `style.paddingTop: "6px"`.
  - `taNotes`: `ia.input.text-area`, `basis: "66.667%"`, `grow: 1`,
    `style: {"minWidth": 0, "resize": "none", "overflowY": "auto"}`, `props.text` bound
    **bidirectionally** to `{view.params.notes}`, `props.enabled` ← `{view.params.enabled}`.
- [X] T022 [US4] In `VIEWS/receiveMaterial/view.json`, bind `evOrderInformation.props.params.notes`
  ↔ `{view.custom.notesDraft}` (bidirectional) and `params.enabled` with the same expression as in
  T018.
- [X] T023 [US4] Extend the `confirmReceiveOrder` message handler in
  `VIEWS/receiveMaterial/view.json` (contract C5). Inside the existing `try`, after
  `self.view.custom.result = result`:
  - When `result.get('status') in ('SUCCESS', 'TRANSFER_PENDING')` and
    `(self.view.custom.notesDraft or '') != (self.view.custom.orderNotes or '')`:
    - Log `'Receive notes save start workOrderId=%s'`.
    - Get `userId = system.kanoa.security.getIDPUserId(self.session.props.auth.user)`.
    - Call `system.kanoa.order.updateProductionOrderField(workOrderId, 'note', self.view.custom.notesDraft, userId)`.
    - On success, log the outcome and set `self.view.custom.orderNotes = self.view.custom.notesDraft`.
  - On an exception in that block only: log an error with the `workOrderId` and the cause, and set
    `self.view.custom.warningMessage = 'Receipt recorded, but the notes were not saved. Re-enter them in the work order editor.'`.
    Keep the receipt result.
  - Do not save notes for any other status (FR-015).
- [ ] T024 [US4] Validate quickstart V6 (Back, invalid confirmation, valid confirmation, and no-edit
  confirmation). Check the Gateway log for the start and outcome lines and record the results in
  `specs/004-receive-material-ui-refactor/evidence/us4.md`.

**Checkpoint**: Notes behave as in clarification Q2 = A.

---

## Phase 7: User Story 5 — Desktop, tablet, and mobile (P2)

**Goal**: The layout adapts without horizontal page scroll.

**Independent Test**: Quickstart V8 at 1440, 1024, 768, and 390 px in light and dark themes.

- [X] T025 [P] [US5] In `VIEWS/receiveMaterialSections/orderInformation/view.json`, confirm that `root` has
  `wrap: "wrap"`. Set `alignContent: "flex-start"`. Both columns must keep `basis: "50%"`,
  `grow: 1`, and `minWidth: "320px"`, so they stack below about 646 px (FR-024). Make sure that
  `props.defaultSize` does not force a minimum width.
- [X] T026 [P] [US5] In `VIEWS/receiveMaterialSections/operatorInputs/view.json`, make sure every label has
  `minWidth: "100px"` and every value has `minWidth: 0`, so that at 390 px the
  `numActualQty` + `ddUnit` pair stays on one line (80 px + 6 px + 110 px fits the 2/3 width of
  about 300 px).
- [X] T027 [US5] In `VIEWS/receiveMaterial/view.json`, make the embedded section heights follow
  their content when wrapped: give `evOrderInformation` a `style.minHeight` of `"160px"` at
  desktop and set `position.basis: "auto"`. If stacking clips the Notes row, raise `minHeight` to
  `"240px"` through a binding on `{page.props.dimensions.viewport.width} < 646`. Make sure
  `flxContent` scrolls vertically and `flxActions` keeps `shrink: 0` (same width as the schedule
  at every size).
- [ ] T028 [US5] Validate quickstart V8 and record screenshots at each width and theme in
  `specs/004-receive-material-ui-refactor/evidence/us5.md`.

---

## Phase 8: Polish & Cross-Cutting

- [X] T029 Run quickstart V0: run `python3 -m json.tool` on all three `view.json` files, and confirm
  that `git diff --name-only -- services/ignition/projects/kanoaAPP services/ignition/projects/KANOA_SCRIPTS VIEWS/receivingOrdersSchedule`
  prints nothing. Record the output in `specs/004-receive-material-ui-refactor/evidence/v0.md`.
- [ ] T030 Export the three views from the Designer (or trigger a project scan) so
  `resource.json` signatures and `thumbnail.png` match Gateway state. Commit only
  `VIEWS/receiveMaterial/**`, `VIEWS/receiveMaterialSections/**`, and `specs/004-receive-material-ui-refactor/**`; leave out unrelated
  re-exports (constitution workflow step 4).
- [X] T031 [P] Update `specs/004-receive-material-ui-refactor/checklists/requirements.md` notes and
  add a short "Verification" section to `specs/004-receive-material-ui-refactor/plan.md` that
  links each evidence file and states that the A2 approval was used and that no conversion code
  exists.
- [X] T032 Draft the PR Testing section from the evidence files, including the known risk of the
  display-only unit and the follow-up "unit conversion" requirement, in
  `specs/004-receive-material-ui-refactor/evidence/pr-testing.md`.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (T001–T002)**: No dependencies.
- **Foundational (T003–T007)**: Depends on Setup. T003 and T004 run in parallel. T005 → T006 → T007
  edit the same file in sequence. **Blocks all stories.**
- **US1 (T008–T011)**: Depends on Foundational.
- **US2 (T012–T015)**: Depends on Foundational (T003). It can be built in parallel with US1 because
  T012/T013 touch only the child view. T014 edits the page view, so run it after T009.
- **US3 (T016–T020)**: Depends on Foundational (T004 and T005's saved selector JSON). T016/T017
  can be built in parallel with US1/US2. T018 edits the page view, after T014.
- **US4 (T021–T024)**: Depends on US2 (it extends the same child view and section embed) and US1
  (it extends the confirm handler).
- **US5 (T025–T028)**: Depends on US2, US3, and US4 (it tunes their layout).
- **Polish (T029–T032)**: Depends on all stories.

### Story completion order

```text
Setup → Foundational → US1 ─┐
                     → US2 ─┼─→ US4 ─→ US5 ─→ Polish
                     → US3 ─┘
```

### Within each story

Child view tasks come first, then the page-view embed and bindings, then validation. Tasks that
edit `VIEWS/receiveMaterial/view.json` are never parallel with each other.

## Parallel Opportunities

- T002 alongside T001.
- T003 alongside T004 (two new child views).
- After Foundational: T012 + T013 (US2 child view), T016 + T017 (US3 child view), and T008–T010
  (page view) can be done by three people at once.
- T021 (US4 child view) alongside T023 (page view handler), with T022 after both.
- T025 alongside T026 (different child views).

### Parallel example: after Foundational

```text
Task: "T012 [US2] Build column 1 in VIEWS/receiveMaterialSections/orderInformation/view.json"
Task: "T016 [US3] Build truck and tank rows in VIEWS/receiveMaterialSections/operatorInputs/view.json"
Task: "T008 [US1] Add btnBack to flxAction in VIEWS/receiveMaterial/view.json"
```

## Implementation Strategy

### MVP

US1 alone gives a working screen with no order or input fields, which is not useful to operators.
The **MVP is therefore US1 + US2 + US3** (all P1): Setup → Foundational → US1 → US2 → US3, then
validate with quickstart V1–V5 and V7.

### Incremental delivery

1. MVP (P1 stories): new navigation, order information, and operator inputs. This is
   functionally equivalent to today, plus the display-only unit.
2. US4: editable notes saved with the receipt.
3. US5: responsive tuning and the theme check.
4. Polish: export, diff gates, evidence, and PR notes.

## Notes

- Total: 32 tasks. Setup 2, Foundational 5, US1 4, US2 4, US3 5, US4 4, US5 4, Polish 4.
- Stop at each checkpoint and validate the story in the running Gateway before continuing.
- If any task seems to need a new script function or a `kanoaAPP` change, stop and request
  approval under Principle VI. Do not improvise.
