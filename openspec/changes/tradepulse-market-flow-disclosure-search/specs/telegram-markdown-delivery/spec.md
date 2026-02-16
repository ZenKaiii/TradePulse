## ADDED Requirements

### Requirement: Telegram Markdown Rendering
The system SHALL send Telegram messages with markdown parse mode when possible.

#### Scenario: Telegram channel enabled
- **WHEN** digest is sent to Telegram
- **THEN** payload includes parse mode for markdown formatting
- **AND** long messages are split safely

### Requirement: Fallback on Markdown Parse Error
The system SHALL retry with plain text when markdown parsing fails.

#### Scenario: Telegram API rejects markdown
- **WHEN** first send attempt returns parse error
- **THEN** sender retries without parse mode
