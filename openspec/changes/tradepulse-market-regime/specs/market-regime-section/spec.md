## ADDED Requirements

### Requirement: US Sector Relative Strength Ranking
The system SHALL compute and rank US sector leadership using the 11 SPDR sector ETFs against SPY and QQQ on 4-week and 12-week horizons.

#### Scenario: Build US top and bottom ranking
- **WHEN** a digest cycle runs with market regime enabled
- **THEN** the system computes 4-week and 12-week relative strength scores for each configured US sector ETF
- **AND** returns ordered top and bottom sector lists based on configurable row counts

### Requirement: A-share Sector Fund Flow Ranking
The system SHALL fetch A-share sector fund flow data and provide inflow/outflow rankings for the digest.

#### Scenario: Build A-share inflow and outflow tables
- **WHEN** a digest cycle runs with A-share flow enabled
- **THEN** the system fetches sector flow data from the configured provider endpoint
- **AND** returns ordered top inflow and top outflow sector entries with net flow metrics

### Requirement: Section 4 Digest Rendering
The system SHALL append a dedicated Section 4 block containing US rotation and A-share flow output without changing existing Top events and overlay behavior.

#### Scenario: Append section after existing digest blocks
- **WHEN** market regime payload is available
- **THEN** digest output includes a new section with US and A-share subsections
- **AND** existing section ordering and semantics remain unchanged

### Requirement: Resilient Partial Output
The system SHALL degrade gracefully when one market-data provider fails.

#### Scenario: One sub-provider fails
- **WHEN** US or A-share provider request fails or times out
- **THEN** digest generation still succeeds with available subsection data
- **AND** the failed subsection is replaced by an explicit fallback message
