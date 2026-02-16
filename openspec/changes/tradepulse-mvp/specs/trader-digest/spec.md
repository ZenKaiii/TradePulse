## ADDED Requirements

### Requirement: Hourly Top Events Digest
The system SHALL generate an hourly digest ordered by event importance and include at most the configured `top_n` entries.

#### Scenario: Build hourly top list
- **GIVEN** the system has multiple clustered events with importance scores
- **WHEN** a digest cycle runs
- **THEN** the output includes the highest-ranked events up to `digest.top_n`
- **AND** each event includes source attribution links

### Requirement: Non-filtering Topic Overlays
The system SHALL append stock, keyword, and geopolitical overlay matches without removing items from the mainline top-events section.

#### Scenario: Overlay matching
- **GIVEN** user watchlists are configured
- **WHEN** digest events are composed
- **THEN** overlay hits are listed in a dedicated section
- **AND** mainline top events remain unchanged by overlay misses

### Requirement: Market Direction and Ticker Mapping
The system SHALL label each event as bullish, bearish, or neutral and include affected ticker/company mappings when detected.

#### Scenario: Direction and ticker extraction
- **GIVEN** an event headline mentioning a covered company alias
- **WHEN** scoring is computed
- **THEN** the event includes a direction label
- **AND** includes at least one affected ticker with company name

### Requirement: Secret-driven LLM Provider Routing
The system SHALL prefer Bailian when configured and fall back to Gemini on failure when Gemini credentials are available.

#### Scenario: Bailian fallback path
- **GIVEN** both Bailian and Gemini credentials exist
- **AND** Bailian request fails
- **WHEN** a model call is attempted
- **THEN** the system retries through Gemini
- **AND** returns Gemini output instead of failing immediately

### Requirement: Incremental Push Idempotency
The system SHALL avoid duplicate event pushes by persisting previously pushed cluster identifiers.

#### Scenario: Repeat run skips existing cluster
- **GIVEN** a cluster ID has been marked as pushed
- **WHEN** a later run sees the same cluster ID
- **THEN** the cluster is not treated as new
- **AND** is excluded from new-push count
