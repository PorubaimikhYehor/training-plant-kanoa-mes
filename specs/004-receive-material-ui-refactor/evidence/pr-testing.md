# PR Testing — Spec 004 Receive Material UI Refactor (draft)

## Automated / structural (done)

- `python3 -m json.tool` passes on `training/receiveMaterial/view.json`,
  `training/receiveMaterialSections/orderInformation/view.json`, and
  `training/receiveMaterialSections/operatorInputs/view.json`.
- All 32 embedded Perspective scripts and transforms compile (syntax check).
- `git diff --name-only -- services/ignition/projects/kanoaAPP services/ignition/projects/KANOA_SCRIPTS .../training/receivingOrdersSchedule`
  prints nothing.
- The section views contain no data reads or writes. The only Kanoa reference is the `formatNumber`
  display utility.

## Gateway acceptance (to fill in from evidence/us1–us5.md)

| Check | Quickstart | Result |
|-------|------------|--------|
| Panel matches schedule; Back writes nothing | V1 | ☐ |
| Order fields, label proportion, fallbacks | V2 | ☐ |
| Inputs, defaults, selector scope | V3 | ☐ |
| Display-only unit: lbs + 500 → prompt "500 kg", lot event 500 kg, no UNIT_ERROR later | V4 | ☐ |
| Validation blocks with no lot created | V5 | ☐ |
| Notes saved only with a successful receipt; log lines present | V6 | ☐ |
| Feature 001 regression (partial default, double-click, ineligible, transfer pending) | V7 | ☐ |
| Widths 1440/1024/768/390, light and dark | V8 | ☐ |

## Known risk and follow-up

- The unit selector is display only. A quantity typed in another unit is recorded in the order unit
  (kg). The confirmation prompt states the recorded unit. Follow-up: a separate unit conversion
  requirement.
- The A2 section views were moved to `training/receiveMaterialSections/`, because Ignition cannot
  nest views inside a view folder.
