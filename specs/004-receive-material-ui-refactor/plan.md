# Implementation Plan: Receive Material UI Refactor

**Branch**: `004-receive-material-ui-refactor` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-receive-material-ui-refactor/spec.md`

## Summary

Restructure `training/receiveMaterial` so it uses the page skeleton and left icon action panel of
`training/receivingOrdersSchedule` (Back and Confirm only). The main area holds two new embedded
views (approval A2):
- **Receiving Order Information**: two columns. The first has five read-only 1/3 – 2/3 label-value
  rows. The second has an editable Notes text area about two rows high.
- **Operator Inputs**: full width. It holds the existing truck and tank tree selectors, plus a
  quantity input with a unit dropdown beside it.

The layout uses native flex wrapping to stay responsive, which is the technique Kanoa screens
already use.

Two behavior changes:
- **Units**: The dropdown lists every enabled Kanoa item unit and defaults to the order unit. It is
  **display only**: the quantity is recorded in the order unit (kg) exactly as entered. Unit
  conversion is a separate future requirement (user decision, 2026-11-19).
- **Notes (Q2 = A)**: After `receiveOrder` succeeds, the existing `confirmReceiveOrder` handler
  saves changed notes with the native `system.kanoa.order.updateProductionOrderField`.

No shared script, `kanoaAPP` resource, schedule view, or schema changes.

## Technical Context

**Language/Version**: Ignition 8.3.10 Perspective view JSON. Jython 2.7 for inline scripts.

**Primary Dependencies**: KanoaMES 1.15.11. Inherited `kanoaAPP` templates are used read-only:
`kanoa/core/templates/selectors/tree/selector`, `kanoa/core/templates/inputs/confirm`, and
`kanoa/core/templates/displays/progressBar`. Style classes: `kanoa/container`,
`kanoa/button/flatIcon`, and `kanoa/font/*`. Native components: `ia.container.flex`,
`ia.display.view`, `ia.display.label`, `ia.input.text-area`, `ia.input.numeric-entry-field`,
`ia.input.dropdown`, and `ia.input.button`. Native APIs: `system.kanoa.item.getItemUnits`,
`system.kanoa.order.getProductionOrders`, `system.kanoa.order.updateProductionOrderField`, and
`system.kanoa.security.getIDPUserId`. The existing receiving module is used unchanged:
`kanoaScripts.custom.ops.receiving` (`getReceivingOrder`, `getReceivingAssets`,
`getReceivedQtyForOrder`, `receiveOrder`, `getLogger`).

**Storage**: No schema change. Receipts are written by the unchanged `receiveOrder` (kg).
`mes.workOrder.note` is written through the native order API.

**Testing**: Manual Gateway acceptance with [quickstart.md](quickstart.md), JSON structural checks,
diff gates, and a rerun of the feature 001 scenarios.

**Target Platform**: Ignition Perspective browser client on the local Training Plant Gateway, at
desktop (≥1024 px), tablet (~768 px), and phone (~390 px) widths.

**Project Type**: Internal MES operator UI (Perspective views).

**Performance Goals**: The screen loads its data once on open (order, assets, receipt history,
units). A standard receipt takes less than 2 minutes (SC-002).

**Constraints**: Do not edit `kanoaAPP`, `KANOA_SCRIPTS`, or the schedule view. Receipts stay in kg.
Only Back and Confirm appear in the panel. No horizontal page scroll at any supported width.

**Scale/Scope**: One view refactored and two child views added. Training Plant data: 2 trucks, 3
tanks, 1 kg order, 11 enabled item units.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Gate

- **I. Version-Controlled Gateway State — PASS**: All changes are exported view JSON under
  `services/ignition/projects/kanoaMES/`. There are no image, module, or schema changes.
- **II. Respect Ignition Project Boundaries — PASS**: The views are in `kanoaMES`. `kanoaAPP` and
  `KANOA_SCRIPTS` are referenced, never edited.
- **III. Jython 2.7 and Ignition API Compatibility — PASS**: Inline scripts use tab indentation and
  Jython-safe syntax with only `system.*` and existing module calls.
- **IV. API-First, Idempotent Data Operations — PASS**: Receipts still go only through
  `receiveOrder`, with its lock and reconciliation. Notes use the native
  `updateProductionOrderField`, which sets a value, so a rerun is idempotent. The write is skipped
  when the notes are unchanged. Failures surface as actionable messages.
- **V. Verifiable, Observable Changes — PASS**: [quickstart.md](quickstart.md) covers every story
  and the regression checks. The notes write logs its start and outcome through the existing
  `receiving` logger.
- **VI. Kanoa-First — PASS (with approval A2)**: The native assets evaluated are listed in
  [research.md](research.md) R1–R8. The action panel, label-value rows, selectors, quantity input,
  unit dropdown, and notes write all use native capability. The only new components are the two
  section views, approved below. The unit conversion methods proposed as A1 were declined, and no
  conversion code is written.

## Project Structure

### Documentation (this feature)

```text
specs/004-receive-material-ui-refactor/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── component-contracts.md
│   └── behavior-preservation.md
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
services/ignition/projects/
├── kanoaMES/com.inductiveautomation.perspective/views/training/
│   ├── receiveMaterial/view.json                       # Refactored page (C1, C5)
│   ├── receiveMaterialSections/orderInformation/view.json      # NEW, approved A2 (C2)
│   ├── receiveMaterialSections/operatorInputs/view.json        # NEW, approved A2 (C3)
│   └── receivingOrdersSchedule/view.json               # Reference only, unchanged
├── kanoaAPP/.../views/kanoa/core/templates/            # Reused, read-only
└── KANOA_SCRIPTS/.../kanoaScripts/custom/ops/receiving/code.py   # Used, unchanged
```

**Structure Decision**: The work stays in the runnable `kanoaMES` project. Page-level logic
(loading, validation, confirmation, notes save) stays in `receiveMaterial/view.json`. The child
views carry layout and bindings only, with no Kanoa calls.

## Complexity Tracking

> Principle VI approval record.

| Request | Requirement | Native assets evaluated and why each is insufficient | Name and location | Maintenance cost | Decision |
|---------|-------------|------------------------------------------------------|-------------------|------------------|----------|
| **A1**: unit conversion methods | Original Q1 = B | KanoaMES has no conversion data or API (R5) | — | — | **Declined** 2026-11-19 by the requester. Conversion is deferred to a separate requirement, and the unit selector is display only. No code is written. |
| **A2**: two embedded section views | FR-008 (reusable, self-contained sections) | No Kanoa template matches a 1/3 – 2/3 label-value form or these sections. `valueWithLabel` is a stacked tile and cannot hold inputs (R2). Only an embedded view is reusable in Perspective. | `training/receiveMaterialSections/orderInformation` and `training/receiveMaterialSections/operatorInputs` in `kanoaMES`. Layout and bindings only. Folder moved from `receiveMaterial/` during implementation, because Ignition cannot nest views inside a view folder. Purpose unchanged. | Low to moderate. Two view resources, with parameter contracts C2/C3 that must stay in sync with the parent. | **Approved** 2026-11-19 by the requester. |

## Known Risk

The unit selector is display only. If an operator selects `lbs` and enters a pound value, it is
recorded as kg. Mitigation: the confirmation prompt and the success message state the recorded unit
("… kg"). The risk is removed by the future conversion requirement.

## Constitution Check (Post-Design)

Re-evaluated after [research.md](research.md), [data-model.md](data-model.md),
[contracts/](contracts/), and [quickstart.md](quickstart.md).

- **I — PASS**: The design touches only `training/receiveMaterial/**`, `training/receiveMaterialSections/**`, and the spec folder. The diff
  gates are in [behavior-preservation.md](contracts/behavior-preservation.md).
- **II — PASS**: No change to `kanoaAPP` or `KANOA_SCRIPTS`. The child views are project-local.
- **III — PASS**: Inline scripts are limited to bindings, navigation, message handling, and calls to
  existing APIs.
- **IV — PASS**: There is one write path per entity: `receiveOrder` for receipts and
  `updateProductionOrderField` for notes. Notes are written only after receipt success, are skipped
  when unchanged, and are protected by the existing handler lock and `priorResult` guard. A failure
  after the receipt is reported, not swallowed. The display-only unit cannot corrupt receipt
  history.
- **V — PASS**: Quickstart V0–V8 define the checks and expected results, including the notes log
  lines.
- **VI — PASS**: The only new components are the two approved section views (A2). No new script
  method exists. A1 was declined and no conversion code exists.

## Verification

| Evidence | Status |
|----------|--------|
| [evidence/baseline.md](evidence/baseline.md): git baseline and schedule panel reference values | Done. Before screenshots pending (manual, no browser tooling in the build session) |
| [evidence/v0.md](evidence/v0.md): JSON parse and diff gates | **Pass** 2026-11-19 |
| Embedded script syntax (32 scripts across 3 views compile when wrapped in a function) | **Pass** 2026-11-19 |
| `evidence/us1.md` … `us5.md`: Gateway acceptance V1–V8 | Pending manual run after loading the views into the Gateway |

- Approval A2 was used: the two section views exist under `training/receiveMaterialSections/`. A1
  was declined, and no conversion code exists. `KANOA_SCRIPTS` and `kanoaAPP` are unchanged
  (evidence/v0.md).
- Resource signatures in the three `resource.json` files were stamped with Ignition 8.3's
  `Resource.calculateContentDigest` algorithm (scope, version, flags, sorted file digests, then
  attributes). This was confirmed to reproduce the signatures of untouched Designer-saved views.
- `checklists/requirements.md` was left unchanged, because the implement step treats checklists as
  read-only.
