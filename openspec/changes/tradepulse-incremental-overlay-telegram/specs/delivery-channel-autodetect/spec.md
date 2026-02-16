## ADDED Requirements

### Requirement: Auto-Detect Channels From Credentials
The system SHALL auto-enable available channels when channel list is not explicitly configured.

#### Scenario: Telegram credentials set and channels unset
- **WHEN** `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are present
- **AND** no explicit channels are configured
- **THEN** telegram sender is enabled for delivery

### Requirement: Explicit Channel Priority
The system SHALL prioritize explicit channel configuration over auto-detection.

#### Scenario: Explicit channels provided
- **WHEN** `TRADEPULSE_CHANNELS` has non-empty value
- **THEN** only listed channels are enabled
