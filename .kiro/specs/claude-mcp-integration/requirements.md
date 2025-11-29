# Requirements Document

## Introduction

This feature implements a Model Context Protocol (MCP) server that enables Claude (running on AWS Kiro) to interact with NecoKeeper through a local MCP server. The integration allows Claude to automatically register cat profiles, generate QR code PDFs, and optionally upload profile images through structured tool calls.

## Glossary

- **MCP (Model Context Protocol)**: A protocol that enables AI assistants like Claude to interact with external systems through structured tool definitions
- **FastMCP**: A Python framework for building MCP servers
- **NecoKeeper**: The cat shelter management system
- **Claude**: The AI assistant running on AWS Kiro
- **QR Card**: A PDF document containing QR codes for public access to cat profiles
- **Service Account**: An authentication mechanism for automated system-to-system communication
- **Animal Profile**: A cat's registration record in NecoKeeper containing basic information like name, sex, age, status, etc.

## Requirements

### Requirement 1

**User Story:** As a shelter administrator using Claude, I want to register cat profiles through natural language conversation, so that I can quickly add new cats to the system without manually filling forms.

#### Acceptance Criteria

1. WHEN Claude receives cat profile information from the user THEN the MCP Server SHALL expose a `register_cat` tool that accepts cat profile parameters
2. WHEN the `register_cat` tool is invoked with valid cat data THEN the MCP Server SHALL call the NecoKeeper REST API `POST /api/v1/animals` with authentication
3. WHEN the cat registration succeeds THEN the MCP Server SHALL return the animal_id, name, and public_url to Claude
4. WHEN the cat registration fails THEN the MCP Server SHALL return a descriptive error message to Claude
5. WHERE authentication is required THEN the MCP Server SHALL read API credentials from environment variables

### Requirement 2

**User Story:** As a shelter administrator using Claude, I want to generate QR code PDFs for registered cats, so that I can quickly create printable QR cards for public access.

#### Acceptance Criteria

1. WHEN Claude needs to generate a QR PDF for a cat THEN the MCP Server SHALL expose a `generate_qr` tool that accepts animal_id
2. WHEN the `generate_qr` tool is invoked with a valid animal_id THEN the MCP Server SHALL call the NecoKeeper PDF generation API `POST /api/v1/pdf/qr-card-grid`
3. WHEN the PDF generation succeeds THEN the MCP Server SHALL save the PDF to `tmp/qr/qr_{animal_id}.pdf`
4. WHEN the PDF is saved THEN the MCP Server SHALL return the local file path to Claude
5. WHERE the `tmp/qr/` directory does not exist THEN the MCP Server SHALL create it automatically

### Requirement 3

**User Story:** As a shelter administrator using Claude, I want to upload a profile image for a registered cat, so that the cat's profile includes a visual representation.

#### Acceptance Criteria

1. WHEN Claude needs to upload an image for a cat THEN the MCP Server SHALL expose an `upload_cat_image` tool that accepts animal_id and image_path
2. WHEN the `upload_cat_image` tool is invoked with valid parameters THEN the MCP Server SHALL read the image file from the local filesystem
3. WHEN the image file is read THEN the MCP Server SHALL call the NecoKeeper image upload API with authentication
4. WHEN the image upload succeeds THEN the MCP Server SHALL return the image_url or image_id to Claude
5. WHERE the image file does not exist or is invalid THEN the MCP Server SHALL return a descriptive error message

### Requirement 4

**User Story:** As a developer, I want the MCP server to be easily configurable and startable, so that I can quickly set up the integration for demos and development.

#### Acceptance Criteria

1. WHEN the MCP server needs to start THEN the System SHALL provide a command `python -m app.mcp.server` to launch the server
2. WHEN the MCP server starts THEN the System SHALL read configuration from environment variables including API_BASE_URL and AUTH_TOKEN
3. WHEN the MCP server is running THEN the System SHALL register itself with Kiro/Claude as an available MCP server
4. WHEN Claude queries available tools THEN the MCP Server SHALL return a list of all registered tools with their schemas
5. WHERE configuration is missing or invalid THEN the MCP Server SHALL log clear error messages and fail to start

### Requirement 5

**User Story:** As a developer, I want comprehensive documentation for the MCP integration, so that I can understand how to use and demonstrate the feature.

#### Acceptance Criteria

1. WHEN a developer needs to set up the MCP integration THEN the Documentation SHALL include prerequisites and environment setup instructions
2. WHEN a developer needs to start the MCP server THEN the Documentation SHALL include the startup command and configuration steps
3. WHEN a developer needs to demonstrate the feature THEN the Documentation SHALL include a complete demo scenario with example prompts
4. WHEN a developer needs to troubleshoot THEN the Documentation SHALL include common issues and solutions
5. WHERE the MCP server configuration is needed THEN the Documentation SHALL include `.kiro/settings` registration instructions

### Requirement 6

**User Story:** As a system, I want to authenticate MCP requests securely using Automation API Key, so that only authorized Claude instances can interact with NecoKeeper.

#### Acceptance Criteria

1. WHEN the MCP server makes API calls to NecoKeeper THEN the System SHALL include X-Automation-Key header with each request
2. WHEN authentication credentials are needed THEN the System SHALL read AUTOMATION_API_KEY from environment variables (not hardcoded)
3. WHEN authentication fails THEN the System SHALL return a clear error message to Claude
4. WHERE the Automation API Key is at least 32 characters THEN the System SHALL accept it as valid
5. WHERE no Automation API Key is configured THEN the MCP Server SHALL fail to start with a clear error message

### Requirement 7

**User Story:** As a developer, I want the MCP server to handle errors gracefully, so that Claude receives meaningful feedback when operations fail.

#### Acceptance Criteria

1. WHEN a tool invocation fails due to network errors THEN the MCP Server SHALL return a user-friendly error message
2. WHEN a tool invocation fails due to validation errors THEN the MCP Server SHALL return specific validation error details
3. WHEN a tool invocation fails due to authentication errors THEN the MCP Server SHALL return an authentication error message
4. WHEN an unexpected error occurs THEN the MCP Server SHALL log the full error details and return a generic error message to Claude
5. WHERE multiple errors occur THEN the MCP Server SHALL return the most relevant error to the user

### Requirement 8

**User Story:** As a developer testing the MCP integration, I want to verify the complete workflow from cat registration to QR generation, so that I can ensure the integration works end-to-end.

#### Acceptance Criteria

1. WHEN testing the complete workflow THEN the System SHALL support registering a cat, uploading an image, and generating a QR PDF in sequence
2. WHEN the cat registration completes THEN the System SHALL return an animal_id that can be used in subsequent operations
3. WHEN the image upload completes THEN the System SHALL associate the image with the correct animal_id
4. WHEN the QR generation completes THEN the System SHALL create a PDF that includes the registered cat's information
5. WHERE any step fails THEN the System SHALL provide clear error messages indicating which step failed and why
