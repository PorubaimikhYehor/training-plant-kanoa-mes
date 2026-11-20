# Feature Specification: Receive Material UI Refactor

**Feature Branch**: `004-receive-material-ui-refactor`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Training Plant - Receive Material UI Refactoring. Redesign training/receiveMaterial to align with the layout, navigation pattern, and reusable components already used in training/receivingOrdersSchedule: reuse the left-side action panel (Back, Confirm); split the main content into a Receiving Order Information section (two 6/12 columns of 4/12–8/12 label-value rows: Order Number, Title, Target Quantity, Scheduled Date, Status in column 1; an editable multiline Notes field of about two rows' height in column 2) and an Operator Inputs section underneath at full width (Receiving Truck, Destination Tank, and Actual Quantity with a UOM selector beside the quantity input, defaulting to the order UOM); keep the page responsive for desktop, tablet, and mobile; reuse existing label-value, selector, and action-panel components and only create new components when no reusable one exists."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive material on a screen that looks and navigates like the schedule (Priority: P1)

As a receiving operator, I want the Receive Material screen to use the same page structure and left-side action panel as the Receiving Orders Schedule, so that moving from the schedule to the receipt feels like one continuous workflow and I always find Back and Confirm in the same place.

**Why this priority**: Consistent navigation is the core reason for the refactor. Operators who must look for actions in a different place on each screen hesitate and make mistakes during the main receiving task.

**Independent Test**: Open the Receiving Orders Schedule, select an order, open Receive Material, and compare the two screens. Verify that the left action panel is in the same position with the same icon style and size, that it exposes only Back and Confirm, and that Back returns to the schedule.

**Acceptance Scenarios**:

1. **Given** an eligible order has been selected on the schedule, **When** the Receive Material screen opens, **Then** the page shows the same overall structure as the schedule: a left-side action panel and a main content area.
2. **Given** the Receive Material screen is open, **When** the operator looks at the left action panel, **Then** it shows exactly two actions, Back and Confirm, with the same icon style, position, size, and spacing as the schedule's action panel.
3. **Given** the operator activates Back, **When** the schedule is shown, **Then** no receipt, transfer, or note change has been recorded and unsaved input is discarded.
4. **Given** valid operator inputs, **When** the operator activates Confirm, **Then** the receipt is recorded with the same outcome, validation, and feedback as the existing receiving workflow.
5. **Given** a confirmation is in progress, **When** the operator looks at the action panel, **Then** Confirm and Back are unavailable until the outcome is known, and repeated activation cannot create a duplicate receipt.

---

### User Story 2 - Review order information in a two-column label-value layout (Priority: P1)

As a receiving operator, I want the order's key information shown in a compact two-column section with consistently aligned labels and values, so that I can quickly verify that I am receiving against the correct order.

**Why this priority**: The operator must confirm the correct order and target quantity before recording anything. A scannable and consistent layout reduces verification time and wrong-order receipts.

**Independent Test**: Open the screen for an order with known values and verify that Order Number, Title, Target Quantity, Scheduled Date, and Status appear in the first column, that Notes appears in the second column, and that every row uses the same label-to-value proportion.

**Acceptance Scenarios**:

1. **Given** an order is selected, **When** the Receiving Order Information section is displayed, **Then** the first column shows Order Number, Title, Target Quantity, Scheduled Date, and Status, in that order, as read-only values.
2. **Given** the section is displayed on a desktop-width screen, **When** the operator views it, **Then** the two columns appear side by side with equal width.
3. **Given** any information row, **When** the label and value are compared with the other rows, **Then** the label occupies one third of the row width and the value occupies two thirds, and labels are aligned consistently.
4. **Given** the order has no title, **When** the Title row is displayed, **Then** the item description is shown as the fallback value.
5. **Given** the scheduled date is unavailable, **When** the Scheduled Date row is displayed, **Then** it shows an explicit unavailable value instead of a blank.

---

### User Story 3 - Enter operator inputs including quantity and unit (Priority: P1)

As a receiving operator, I want to select the receiving truck and destination tank and enter the actual quantity with its unit of measure in one full-width input section, so that I can complete all receipt inputs in one place without switching context.

**Why this priority**: These inputs determine where the material is recorded and how much is received. They are the data that create inventory.

**Independent Test**: Open the screen, use the existing selectors to choose a truck and a tank, check that the quantity and unit are prefilled, change the quantity, and confirm. Verify that the receipt reflects the selected truck, tank, and quantity, recorded in the order's unit.

**Acceptance Scenarios**:

1. **Given** the screen is open, **When** the Operator Inputs section is displayed, **Then** it appears below the Receiving Order Information section, spans the full content width, and shows Receiving Truck, Destination Tank, and Actual Quantity rows in the same label-value proportion.
2. **Given** the operator opens the Receiving Truck or Destination Tank selector, **When** the options are shown, **Then** the selection experience and eligible choices are the same as in the existing receiving workflow.
3. **Given** the screen opens, **When** the Actual Quantity row is displayed, **Then** the quantity input and the unit of measure selector are shown side by side in the value area, and the unit defaults to the receiving order's unit of measure.
4. **Given** the screen opens, **When** the Actual Quantity row is displayed, **Then** the quantity defaults to the order's outstanding quantity, as in the existing receiving workflow.
5. **Given** the operator opens the unit of measure selector, **When** the options are shown, **Then** all enabled units of measure are offered.
6. **Given** the operator selects a unit other than the order's unit, **When** the operator confirms, **Then** the quantity is recorded in the order's unit exactly as entered; the selected unit is not used for conversion or recording in this feature.
7. **Given** a missing or invalid truck, tank, or quantity, **When** the operator confirms, **Then** the receipt is blocked with an actionable message and no record is created.

---

### User Story 4 - Edit order notes during receiving (Priority: P2)

As a receiving operator, I want to add or update the order's notes in a multiline field next to the order information, so that I can record delivery observations, such as seal condition or driver remarks, against the order.

**Why this priority**: Notes capture valuable context, but receiving can still be completed without them, so this follows the core receive flow in priority.

**Independent Test**: Open the screen for an order with existing notes, verify that they are shown in an editable multiline area about twice the height of a standard row, change the notes, and confirm the receipt, and verify that the order notes reflect the change; repeat with Back and with a failed confirmation and verify that the notes are unchanged.

**Acceptance Scenarios**:

1. **Given** the order has notes, **When** the Notes field is displayed in the second column, **Then** it shows the full existing notes in an editable multiline area that uses the same label-value structure and is about twice the height of a standard row.
2. **Given** the order has no notes, **When** the Notes field is displayed, **Then** it is empty and ready for input.
3. **Given** the operator edits the notes, **When** the change is saved, **Then** the order notes reflect the new text. Notes are saved only when Confirm succeeds, together with the receipt.
4. **Given** the notes are longer than the visible area, **When** the operator reviews them, **Then** the full text remains readable by scrolling within the field without breaking the page layout.
5. **Given** the operator edits the notes and then activates Back, **When** the schedule is shown, **Then** the note changes are discarded and the order notes are unchanged.
6. **Given** the operator edits the notes and the confirmation is rejected or fails before the receipt is recorded, **When** the error is shown, **Then** the order notes are unchanged and the edited text remains in the field so the operator can retry.

---

### User Story 5 - Use the screen on desktop, tablet, and mobile (Priority: P2)

As a receiving operator working at a desk, on a tablet at the dock, or on a phone, I want the Receive Material screen to adapt to my screen size, so that I can read every field and reach every action without horizontal scrolling.

**Why this priority**: Receiving happens at the truck as well as at the desk. The screen must remain usable on smaller devices, but the desktop layout is the primary reference.

**Independent Test**: Open the screen at desktop, tablet, and phone widths and verify the layout at each width.

**Acceptance Scenarios**:

1. **Given** a desktop-width screen, **When** the page is displayed, **Then** order information is shown as two side-by-side columns and Operator Inputs are shown at full width underneath.
2. **Given** a tablet-width screen, **When** the space for two columns becomes insufficient, **Then** the order information columns wrap so that no field is clipped.
3. **Given** a phone-width screen, **When** the page is displayed, **Then** all sections are stacked vertically: column 1, then Notes, then Operator Inputs.
4. **Given** any supported width, **When** the left action panel is displayed, **Then** it behaves the same way as the schedule's action panel at that width.
5. **Given** a narrow screen, **When** the Actual Quantity row is displayed, **Then** the quantity input and unit selector remain visible and usable without horizontal scrolling of the page.

### Edge Cases

- The screen is opened with no selected order: a clear message is shown, the order and input sections are not usable, Confirm is unavailable, and Back remains available.
- Long values such as titles, notes, or asset paths do not overlap adjacent fields and do not force the page to scroll horizontally.
- No eligible receiving trucks or destination tanks exist: the corresponding row explains why instead of showing an empty selector.
- The order's unit of measure is missing: the operator is told and Confirm is blocked rather than defaulting to an arbitrary unit.
- The order becomes ineligible, or its remaining quantity changes, before confirmation: the submission is blocked with an explanation, as in the existing workflow.
- The receipt succeeds but the tank transfer fails: the operator is directed to the separate Pending Transfers screen, as in the existing workflow.
- The screen is viewed in each supported Kanoa theme: labels, values, inputs, and actions remain legible.

## Requirements *(mandatory)*

### Functional Requirements

**Page structure and navigation**

- **FR-001**: The Receive Material screen MUST follow the same overall page structure as the Receiving Orders Schedule: a left-side action panel beside the main content area.
- **FR-002**: The left action panel MUST be the same panel pattern used on the Receiving Orders Schedule, with the same icon style, position, sizing, spacing, and responsive behavior.
- **FR-003**: The left action panel MUST expose only two actions: Back and Confirm.
- **FR-004**: Back MUST return to the Receiving Orders Schedule without creating or changing any receipt, transfer, or order notes, and MUST discard unsaved input.
- **FR-005**: Confirm MUST preserve the existing receiving outcome, validation, idempotency, success feedback, failure feedback, and pending-transfer guidance.
- **FR-006**: While confirmation is in progress, Confirm and Back MUST be unavailable, and duplicate submissions MUST be prevented.
- **FR-007**: The main content area MUST contain two distinct sections: Receiving Order Information first, then Operator Inputs below it.
- **FR-008**: Each section MUST be a self-contained unit that can be reused independently of the other.

**Receiving Order Information**

- **FR-009**: The section MUST use two columns of equal width on desktop-width screens.
- **FR-010**: Every information and input row on the screen MUST use the existing label-value pattern, with the label occupying one third of the row and the value occupying two thirds.
- **FR-011**: Column 1 MUST show, in order, Order Number, Title, Target Quantity, Scheduled Date, and Status as read-only values.
- **FR-012**: When the order title is empty, the Title row MUST display the item description as a fallback; when the scheduled date is unavailable, the Scheduled Date row MUST show an explicit unavailable value.
- **FR-013**: Target Quantity MUST be shown together with the order's unit of measure.
- **FR-014**: Column 2 MUST show Notes as an editable, multiline text field that uses the label-value structure and is about twice the height of a standard row.
- **FR-015**: The Notes field MUST show the order's current notes when the screen opens and MUST save edits to the same order notes only when Confirm successfully records the receipt. Notes MUST NOT be saved on Back or when confirmation is rejected or fails before the receipt is recorded, and MUST NOT be saved more than once for repeated confirmation attempts.
- **FR-016**: Notes longer than the visible area MUST remain fully readable through scrolling within the field.

**Operator Inputs**

- **FR-017**: The Operator Inputs section MUST span the full width of the main content area and use the existing form styling of the Training Plant screens.
- **FR-018**: The Receiving Truck row MUST use the existing truck selector and MUST offer the same eligible choices as the existing receiving workflow.
- **FR-019**: The Destination Tank row MUST use the existing tank selector and MUST offer the same eligible choices as the existing receiving workflow.
- **FR-020**: The Actual Quantity row MUST place a numeric quantity input and a unit of measure selector side by side within the value area.
- **FR-021**: Actual quantity MUST default to the order's outstanding quantity, and the unit of measure MUST default to the receiving order's unit of measure.
- **FR-022**: The unit of measure selector MUST offer all enabled units of measure. The selection MUST be display only in this feature: the quantity MUST be validated against the remaining quantity and recorded in the order's unit exactly as entered, with no conversion.
- **FR-022a**: The confirmation prompt and success result MUST state the quantity in the order's unit, which is the unit that is recorded.
- **FR-023**: When no eligible trucks or tanks exist, the corresponding row MUST show an explanatory message.

**Responsiveness and reuse**

- **FR-024**: On desktop-width screens, order information MUST be displayed as two columns with Operator Inputs at full width underneath; on tablet-width screens, the columns MUST wrap when space is insufficient; on phone-width screens, all sections MUST stack vertically.
- **FR-025**: At every supported width, all fields and actions MUST remain readable and reachable without horizontal scrolling of the page.
- **FR-026**: The feature MUST reuse existing Training Plant and Kanoa components for the action panel, label-value rows, and the truck, tank, and unit selectors. A new component MAY be created only when no reusable one exists, and only after explicit approval is recorded, as required by the project constitution.
- **FR-027**: The feature MUST follow existing KanoaMES styling standards and MUST NOT alter vendor-managed Kanoa resources.

### Key Entities *(include if feature involves data)*

- **Receiving Order**: The scheduled order being received; provides the order number, title, target quantity, unit of measure, scheduled date, status, and notes.
- **Order Notes**: Free-text notes attached to the receiving order; displayed and editable on this screen.
- **Receiving Truck**: An eligible receiving location where the receipt is first recorded.
- **Destination Tank**: An eligible bulk storage location where the received material is transferred.
- **Unit of Measure**: An enabled unit shown in the selector; defaults to the order's unit. In this feature the selection is display only and does not affect the recorded quantity.
- **Receipt**: The operator-confirmed actual quantity recorded against one order, truck, and tank.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a side-by-side review with the Receiving Orders Schedule, the left action panel shows zero differences in position, icon style, sizing, and responsive behavior.
- **SC-002**: An operator can complete a standard receipt, from opening the screen through confirmation, in under 2 minutes when the order and assets are available.
- **SC-003**: In acceptance review, 100% of the five read-only order fields match the order's stored values, and 100% of rows use the one-third label and two-thirds value proportion.
- **SC-004**: At desktop, tablet, and phone widths, 100% of fields and both actions remain visible and usable with no horizontal page scrolling.
- **SC-005**: 100% of tested invalid inputs, including truck, tank, and quantity, are blocked with no receipt created.
- **SC-006**: All existing receiving acceptance scenarios continue to pass after the refactor, with zero functional regressions.
- **SC-007**: In 100% of tested cases, notes are saved exactly as entered only after a successful confirmation and remain unchanged after Back or a failed confirmation.
- **SC-009**: In 100% of tested receipts, the recorded quantity and unit equal the entered quantity in the order's unit, regardless of the unit selected.
- **SC-008**: The change introduces zero new components without a recorded prior approval, and every reused component is identified in the plan.

## Assumptions

- This is primarily a layout and interaction refactor. Receiving rules, eligibility, validation, idempotency, and transfer recovery from the earlier receiving features remain unchanged except for the explicit changes in this spec: editable notes and unit selection.
- Unit conversion is out of scope and will be handled as a separate requirement (decision 2026-11-19). Until then, the unit selector is display only: any enabled unit can be selected, and the quantity is always validated and recorded in the order's unit. Known risk: an operator who selects another unit and enters a quantity in that unit will have it recorded as the order's unit. The confirmation prompt states the recorded unit to mitigate this.
- Note edits are part of the confirmation. They are saved together with a successful receipt and are never saved independently.
- This spec supersedes the earlier Receive Material refactor (`specs/003-receive-material-woeditor-ui`) where they conflict. In particular, Notes becomes editable instead of read-only, and the work order editor-style layout is replaced by the Receiving Orders Schedule page structure.
- The schedule's left action panel is the visual and behavioral reference; only Back and Confirm are carried over, not the schedule's other actions.
- The existing tree selectors already used for truck and tank selection are the "existing selectors" referred to in the request; their eligibility rules remain the Receiving area for trucks and the Bulk Storage area for tanks.
- The phrase "independent reusable containers/components" means each section is self-contained. If that requires a new embeddable view, the constitution's approval gate applies before implementation.
- Supported widths follow the existing KanoaMES responsive breakpoints used by the Receiving Orders Schedule.
- Operators are authenticated users working under the site's existing access controls. Editing notes requires no additional permission beyond what receiving already requires.

## Dependencies

- Operator Receiving feature (`specs/001-operator-receiving`) for receipt, transfer, and recovery behavior.
- Kanoa UI alignment feature (`specs/002-operator-receiving-kanoa-ui`) for the application shell, themes, and feedback patterns.
- The Receiving Orders Schedule screen as the reference for page structure and the left action panel.
- Existing label-value, truck, tank, and unit selectors, and the order's stored unit of measure and notes.
