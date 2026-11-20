# Quickstart: Validate the Receive Material UI Refactor

**Feature**: `specs/004-receive-material-ui-refactor/`
**Scope**: Local Training Plant Gateway only. Do not reset or reseed the database for this
validation.

Layout and binding details are in [contracts/component-contracts.md](contracts/component-contracts.md).
The rules that must not change are in
[contracts/behavior-preservation.md](contracts/behavior-preservation.md). The view state and
conversion factors are in [data-model.md](data-model.md).

## Prerequisites

- The Compose stack is running (`podman ps` or `docker compose ps`), and `kanoaMES` is deployed with
  the edited views.
- At least one `Scheduled` or `In Progress` order in kg, with an item, a target quantity, and a
  schedule entry. Order `0001` qualifies in the local data.
- Enabled Storage Locations under `Training Plant\Receiving` and `Training Plant\Bulk Storage`.
- Enabled item units in `mes.itemUnit` (the local data has 11, including `kg`).
- An operator account that can open **Receiving → Receive Material**.

## V0. Structural and diff checks (repository root)

```bash
V=services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training
for f in $(find "$V/receiveMaterial" "$V/receiveMaterialSections" -name view.json); do python3 -m json.tool "$f" >/dev/null && echo "OK $f"; done
git diff --name-only -- services/ignition/projects/kanoaAPP services/ignition/projects/KANOA_SCRIPTS services/ignition/projects/kanoaMES/com.inductiveautomation.perspective/views/training/receivingOrdersSchedule
```

**Expected**: All three views parse (page, `orderInformation`, `operatorInputs`). The second
command prints nothing.

## V1. Navigation and action panel (US1, SC-001)

1. Open Receiving Orders Schedule, select an eligible order, and press Confirm.
2. Compare Receive Material with the schedule.

**Expected**: The left panel is in the same place and has the same width. It uses flat 30px Material
icons in the same style, and it shows only Back (arrow) followed by Confirm (check circle).
Tooltips appear on hover. Back returns to the schedule, and the order's receipts, lots, and notes
are unchanged.

## V2. Order information (US2, SC-003)

**Expected**: Column 1 shows Order Number, Title, Target Quantity (with unit), Scheduled Date, and
Status, matching the order in Kanoa. The values are not editable. Every label takes 1/3 of its row
(check with the browser inspector: label width ≈ row width ÷ 3). Clear the order title in Kanoa
to see the item description fallback. Open the screen without a schedule date to see "Not
available".

## V3. Operator inputs and defaults (US3)

**Expected**: The section is below the order information and spans the full width. Truck and tank
use the tree selectors and offer only eligible locations. The quantity defaults to the outstanding
quantity, and the unit defaults to `kg`, with `lbs` and `oz` also offered.

## V4. Display-only unit selector (US3 scenarios 5–6, SC-009)

1. Open the unit dropdown. **Expected**: All enabled units are listed, and the order unit (kg) is
   selected.
2. Select `lbs`, enter `500`, select a truck and a tank, and confirm.
   **Expected**: The prompt says "500 kg". The lot event in Kanoa is `500` kg. Receipt history
   still loads without `UNIT_ERROR` on the next open of the order.

## V5. Validation (SC-005)

Try each case: no truck, no tank, an empty quantity, `0`, a negative quantity, and more than the
remaining quantity.
**Expected**: Each one is blocked with an actionable message, and the lot count for the order is
unchanged.

## V6. Notes saved only with a successful receipt (US4, SC-007)

1. Edit the notes and press Back. **Expected**: The order notes in Kanoa are unchanged.
2. Edit the notes and confirm with an invalid quantity. **Expected**: The notes are unchanged, and
   the edited text is still in the field.
3. Edit the notes and confirm a valid receipt. **Expected**: The notes equal the entered text. The
   Gateway log shows a notes save start and outcome. Pressing Confirm again does nothing.
4. Confirm without editing the notes. **Expected**: No notes update is logged.

## V7. Regression (SC-006)

Rerun the feature 001 acceptance scenarios: partial receipt default, double-click Confirm (one
lot), ineligible order, and a forced transfer failure leading to Pending Transfers guidance.
**Expected**: All pass unchanged.

## V8. Responsive and themes (US5, SC-004)

Use the browser device toolbar at 1440, 1024, 768, and 390 px widths, in light and dark Kanoa
themes.
**Expected**: At 1440 px the two columns are side by side. At 768 px or below the columns stack.
At 390 px the order is column 1, Notes, then Operator Inputs. The quantity input and unit dropdown
stay on one line. The page never scrolls horizontally, and the action panel keeps the same width
as on the schedule.

Record the outcomes, screenshots, and log lines under `specs/004-receive-material-ui-refactor/evidence/`.
