## ADDED Requirements

### Requirement: Incremental Event Delivery
The system SHALL only include unseen events in Section A for each hourly run.

#### Scenario: Event already pushed in previous run
- **WHEN** an event cluster exists in push ledger
- **THEN** it is excluded from Section A in the next run
- **AND** `new_events` does not count it again

### Requirement: No-New Message
The system SHALL render explicit no-new text when no incremental events are available.

#### Scenario: No new cluster in current run
- **WHEN** all candidate events are already in ledger
- **THEN** Section A includes a "no new key events" message
- **AND** digest still renders other sections
