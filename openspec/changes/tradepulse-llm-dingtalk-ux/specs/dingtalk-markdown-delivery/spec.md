## ADDED Requirements

### Requirement: DingTalk Markdown Rendering
The system SHALL send DingTalk robot messages using markdown payload format.

#### Scenario: Push digest to DingTalk
- **WHEN** DingTalk channel is enabled
- **THEN** request payload uses `msgtype=markdown`
- **AND** digest content is sent in `markdown.text`

### Requirement: Readable Novice-friendly Formatting
The system SHALL include clear Chinese section labels and visual markers for novice readability.

#### Scenario: Compose digest body
- **WHEN** digest text is assembled
- **THEN** sections include explanatory labels and concise emoji markers
- **AND** section C includes metric explanations and representative stocks hints
