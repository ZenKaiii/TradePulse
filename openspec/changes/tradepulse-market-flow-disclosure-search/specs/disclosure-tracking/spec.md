## ADDED Requirements

### Requirement: Institution 13F Tracking
The system SHALL surface recent 13F filings for configured institutions.

#### Scenario: SEC submissions endpoint reachable
- **WHEN** institution CIKs are configured
- **THEN** snapshot includes recent 13F filing rows per institution

### Requirement: Insider Form4 Tracking
The system SHALL surface recent Form4 filings for tracked symbols.

#### Scenario: tracked symbols have SEC mapping
- **WHEN** watchlist symbols map to issuer CIK
- **THEN** snapshot includes recent Form4 filing rows with links
