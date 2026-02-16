## ADDED Requirements

### Requirement: Optional Tavily Search Enhancement
The system SHALL support optional Tavily enrichment for top events.

#### Scenario: Tavily enabled and API key present
- **WHEN** top events are composed
- **THEN** first N detailed events include concise external search context

#### Scenario: Tavily unavailable
- **WHEN** Tavily call fails or key missing
- **THEN** digest generation continues without failure
