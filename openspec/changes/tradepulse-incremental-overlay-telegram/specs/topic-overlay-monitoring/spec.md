## ADDED Requirements

### Requirement: Boundary-aware Stock Matching
The system SHALL match stock tickers using token boundaries instead of naive substrings.

#### Scenario: Short ticker false positive
- **WHEN** watchlist contains ticker `MU`
- **THEN** text like `community` does not count as stock hit
- **AND** `$MU` or `MU` token does count

### Requirement: Event-level Overlay Evidence
The system SHALL include matched event snippets in overlay output.

#### Scenario: Keyword overlay hit
- **WHEN** event title matches configured keyword
- **THEN** overlay output includes hit topic and related event titles/sources
