## ADDED Requirements

### Requirement: US Sector Flow Proxy
The system SHALL report daily US sector capital-flow proxy in Section 4.

#### Scenario: US market data available
- **WHEN** sector OHLCV data is available
- **THEN** snapshot includes sector flow proxy top/bottom rankings
- **AND** digest text labels the metric as proxy rather than true net flow

### Requirement: US Stock Flow Proxy
The system SHALL report top US stock flow-proxy movers for a tracked stock universe.

#### Scenario: stock universe configured
- **WHEN** stock OHLCV data is available
- **THEN** snapshot includes top inflow proxy stock list with liquidity context
