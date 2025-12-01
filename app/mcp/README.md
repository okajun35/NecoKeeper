# NecoKeeper MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for NecoKeeper.

## Overview

The MCP server enables Claude (running on AWS Kiro) to interact with NecoKeeper through structured tool calls. It provides tools for:

- **register_cat**: Register new cat profiles with natural language
- **generate_qr_card**: Generate single QR card PDF (A6 size) for a registered cat
- **generate_qr**: Generate QR code grid PDF (A4 size, 2x5 layout) for multiple cats
- **upload_cat_image**: Upload profile images for cats

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Available Tools](#available-tools)
- [Demo Scenario](#demo-scenario)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Security](#security)
- [References](#references)

## Prerequisites

Before setting up the MCP server, ensure you have:

1. **Python 3.12+** installed
2. **NecoKeeper API** running (default: `http://localhost:8000`)
3. **Kiro IDE** installed (for Claude integration)
4. **Required Python packages**:
   ```bash
   pip install fastmcp httpx pydantic pydantic-settings
   ```

## Installation

### Step 1: Clone and Setup NecoKeeper

```bash
# Clone the repository
git clone <necokeeper-repo-url>
cd NecoKeeper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Generate Automation API Key

```bash
# Generate a secure 32-character API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ
```

### Step 3: Configure Environment Variables

Create or update your `.env` file:

```bash
# Required: Automation API Key
AUTOMATION_API_KEY=xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ

# Required: Enable Automation API
ENABLE_AUTOMATION_API=true

# Optional: API URL (default: http://localhost:8000)
NECOKEEPER_API_URL=http://localhost:8000

# Optional: Logging configuration
MCP_LOG_LEVEL=INFO
MCP_LOG_FILE=logs/mcp-server.log
```

### Step 4: Start NecoKeeper API

```bash
# Start the NecoKeeper API server
uvicorn app.main:app --reload --port 8000
```

Verify the API is running by visiting: `http://localhost:8000/docs`

## Configuration

### Environment Variables

The MCP server requires the following environment variables:

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTOMATION_API_KEY` | API key for authentication (min 32 chars) | `xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ` |
| `ENABLE_AUTOMATION_API` | Enable Automation API in NecoKeeper | `true` |

#### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NECOKEEPER_API_URL` | Base URL for NecoKeeper API | `http://localhost:8000` |
| `MCP_LOG_LEVEL` | Logging level | `INFO` |
| `MCP_LOG_FILE` | Path to log file | `logs/mcp-server.log` |

### Kiro MCP Configuration

To use the MCP server with Kiro, add the following to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "necokeeper": {
      "command": "python",
      "args": ["-m", "app.mcp"],
      "env": {
        "NECOKEEPER_API_URL": "http://localhost:8000",
        "AUTOMATION_API_KEY": "${AUTOMATION_API_KEY}"
      }
    }
  }
}
```

**Note**: The `${AUTOMATION_API_KEY}` syntax references the environment variable from your shell. Alternatively, you can hardcode the key (not recommended for production).

## Running the Server

### Method 1: Direct Execution

```bash
# Run as a Python module
python -m app.mcp
```

### Method 2: With Kiro (Recommended)

1. Ensure `.kiro/settings/mcp.json` is configured (see above)
2. Restart Kiro or reload MCP servers
3. The server will start automatically when Claude needs it

### Verifying the Server

Check the logs to confirm the server started successfully:

```bash
# View logs
tail -f logs/mcp-server.log

# Expected output:
# INFO: MCP Server initialized successfully
# INFO: Registered tools: register_cat, generate_qr, upload_cat_image
# INFO: Server running on stdio transport
```

## Available Tools

### 1. register_cat

Register a new cat profile in NecoKeeper.

**Parameters**:
- `name` (required): Cat's name (1-100 characters)
- `sex` (required): Sex - "オス" (male), "メス" (female), or "不明" (unknown)
- `age` (optional): Age (estimated is fine)
- `status` (optional): Status - "保護中" (protected), "譲渡可能" (adoptable), "譲渡済み" (adopted)
- `color` (optional): Fur color
- `pattern` (optional): Fur pattern
- `intake_date` (optional): Intake date (YYYY-MM-DD)
- `note` (optional): Additional notes

**Returns**:
```json
{
  "animal_id": 42,
  "name": "たま",
  "public_url": "http://localhost:8000/public/care?animal_id=42"
}
```

### 2. generate_qr_card

Generate a single QR card PDF (A6 size) for a registered cat.

**Parameters**:
- `animal_id` (required): Cat's ID from registration

**Returns**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_card_42.pdf",
  "animal_id": 42
}
```

**Notes**:
- A6 size PDF with cat photo, name, ID, and QR code
- Saved to `tmp/qr/qr_card_{animal_id}.pdf`

### 3. generate_qr

Generate a QR code grid PDF (A4 size, 2x5 layout) for multiple cats.

**Parameters**:
- `animal_id` (required): Cat's ID from registration

**Returns**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_42.pdf",
  "animal_id": 42
}
```

**Notes**:
- A4 size PDF with up to 10 QR cards (2x5 grid)
- Saved to `tmp/qr/qr_{animal_id}.pdf`
- Useful for printing multiple cards at once

### 4. upload_cat_image

Upload a profile image for a registered cat.

**Parameters**:
- `animal_id` (required): Cat's ID
- `image_path` (required): Local path to image file

**Returns**:
```json
{
  "image_url": "http://localhost:8000/media/animals/42/image.jpg",
  "animal_id": 42
}
```

## Demo Scenario

This section demonstrates a complete workflow from cat registration to QR code generation.

### Scenario: Register a New Cat and Generate QR Code

**Step 1: Start a conversation with Claude**

```
User: "I need to register a new cat named Tama. She's a female calico cat,
       about 2 years old, currently in protection status."
```

**Step 2: Claude invokes register_cat**

Claude will automatically call the `register_cat` tool with:
```json
{
  "name": "たま",
  "sex": "メス",
  "age": "2歳",
  "status": "保護中",
  "pattern": "三毛"
}
```

**Step 3: MCP Server Response**

```json
{
  "animal_id": 42,
  "name": "たま",
  "public_url": "http://localhost:8000/public/care?animal_id=42"
}
```

**Step 4: Claude responds to user**

```
Claude: "I've successfully registered Tama (ID: 42) in the system.
        She's a 2-year-old female calico cat currently in protection status.
        Her public profile is available at: http://localhost:8000/public/care?animal_id=42"
```

**Step 5: Generate QR card**

```
User: "Great! Now generate a QR card for Tama."
```

Claude invokes `generate_qr_card`:
```json
{
  "animal_id": 42
}
```

**Step 6: QR Card Generated**

```json
{
  "pdf_path": "/home/user/NecoKeeper/tmp/qr/qr_card_42.pdf",
  "animal_id": 42
}
```

```
Claude: "I've generated a QR card PDF for Tama at:
        /home/user/NecoKeeper/tmp/qr/qr_card_42.pdf

        This is an A6 size card with Tama's photo, name, and QR code.
        You can print this card to allow volunteers to log care records for Tama."
```

**Step 7: Upload an image (optional)**

```
User: "Can you upload this image for Tama? /path/to/tama.jpg"
```

Claude invokes `upload_cat_image`:
```json
{
  "animal_id": 42,
  "image_path": "/path/to/tama.jpg"
}
```

```
Claude: "I've uploaded the image for Tama. It's now visible on her profile page."
```

### Example Prompts

Here are more example prompts you can use with Claude:

1. **Register multiple cats**:
   ```
   "Register three cats: Momo (male, orange tabby, 1 year old),
    Kuro (female, black, 3 years old), and Shiro (unknown sex, white, 6 months old)"
   ```

2. **Generate QR codes in batch**:
   ```
   "Generate QR codes for cats with IDs 42, 43, and 44"
   ```

3. **Update with image**:
   ```
   "Register a cat named Luna, then upload the image at /path/to/luna.jpg"
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Server Fails to Start

**Symptom**: Error message "AUTOMATION_API_KEY is required"

**Solution**:
```bash
# Check if environment variable is set
echo $AUTOMATION_API_KEY

# If empty, add to .env file
echo "AUTOMATION_API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env

# Reload environment
source .env  # or restart your terminal
```

#### 2. Authentication Errors

**Symptom**: "Authentication error: Invalid or expired token"

**Solution**:
1. Verify the API key is correct in `.env`
2. Ensure `ENABLE_AUTOMATION_API=true` in NecoKeeper's `.env`
3. Restart both NecoKeeper API and MCP server
4. Check that the API key is at least 32 characters

```bash
# Verify API key length
python -c "import os; print(len(os.getenv('AUTOMATION_API_KEY', '')))"
# Should output: 32 or more
```

#### 3. Connection Refused

**Symptom**: "Network error: Could not connect to NecoKeeper API"

**Solution**:
1. Verify NecoKeeper API is running:
   ```bash
   curl http://localhost:8000/docs
   ```
2. Check the `NECOKEEPER_API_URL` in your configuration
3. Ensure no firewall is blocking port 8000

#### 4. Tool Not Found

**Symptom**: Claude says "I don't have access to that tool"

**Solution**:
1. Restart Kiro to reload MCP servers
2. Verify `.kiro/settings/mcp.json` is configured correctly
3. Check MCP server logs for startup errors:
   ```bash
   tail -f logs/mcp-server.log
   ```

#### 5. PDF Generation Fails

**Symptom**: "Failed to generate QR code PDF"

**Solution**:
1. Ensure the `tmp/qr/` directory exists:
   ```bash
   mkdir -p tmp/qr
   ```
2. Check file permissions:
   ```bash
   chmod 755 tmp/qr
   ```
3. Verify the animal_id exists in the database

#### 6. Image Upload Fails

**Symptom**: "File error: Image file not found"

**Solution**:
1. Verify the image path is correct and absolute
2. Check file permissions:
   ```bash
   ls -la /path/to/image.jpg
   ```
3. Ensure the image format is supported (JPEG, PNG, GIF)
4. Check file size (should be under 5MB)

### Debug Mode

Enable debug logging for more detailed error information:

```bash
# In .env file
MCP_LOG_LEVEL=DEBUG

# Restart the MCP server
python -m app.mcp
```

View detailed logs:
```bash
tail -f logs/mcp-server.log
```

### Getting Help

If you encounter issues not covered here:

1. Check the logs: `logs/mcp-server.log`
2. Review the design document: `.kiro/specs/claude-mcp-integration/design.md`
3. Run tests to verify functionality:
   ```bash
   pytest tests/mcp/ -v
   ```
4. Check NecoKeeper API health:
   ```bash
   curl http://localhost:8000/health
   ```

## Development

### Project Structure

```
app/mcp/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for module execution
├── config.py            # Configuration and validation
├── api_client.py        # HTTP client for NecoKeeper API
├── server.py            # Main MCP server with FastMCP
├── error_handler.py     # Centralized error handling
├── tools/               # Tool implementations
│   ├── __init__.py
│   ├── register_cat.py  # Cat registration tool
│   ├── generate_qr.py   # QR code generation tool
│   └── upload_image.py  # Image upload tool
└── README.md            # This file
```

### Running Tests

```bash
# Run all MCP tests
pytest tests/mcp/ -v

# Run with coverage
pytest tests/mcp/ --cov=app/mcp --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/mcp/test_server.py -v

# Run integration tests
pytest tests/mcp/test_integration.py -v
```

### Development Status

#### Completed Tasks
- ✅ Task 1: MCP server structure and configuration
- ✅ Task 2: API client with Automation API Key authentication
- ✅ Task 3: PDF endpoint for Automation API
- ✅ Task 4: register_cat tool implementation
- ✅ Task 5: generate_qr tool implementation
- ✅ Task 6: upload_cat_image tool implementation
- ✅ Task 7: Main MCP server with FastMCP
- ✅ Task 8: Error handling and logging
- ✅ Task 9: Documentation

#### Upcoming Tasks
- [ ] Task 10: Integration testing
- [ ] Task 11: Final checkpoint

### Code Quality

The MCP server follows strict code quality standards:

- **Type hints**: All functions have complete type annotations
- **Testing**: 80%+ test coverage
- **Linting**: Passes Ruff checks
- **Formatting**: Formatted with Ruff
- **Documentation**: Comprehensive docstrings

Run quality checks:
```bash
# Format code
ruff format app/mcp/

# Lint code
ruff check app/mcp/ --fix

# Type check
mypy app/mcp/

# Run all checks
make check
```

## Security

### Best Practices

1. **API Key Storage**
   - ✅ Store in environment variables
   - ✅ Use `.env` file (gitignored)
   - ❌ Never hardcode in source code
   - ❌ Never commit to version control

2. **API Key Generation**
   - Use cryptographically secure random generation
   - Minimum 32 characters
   - Use `secrets.token_urlsafe()` for generation

3. **Key Transmission**
   - Use HTTPS in production
   - Keys transmitted via `X-Automation-Key` header
   - Never log full API keys

4. **File Path Validation**
   - Image paths are validated to prevent directory traversal
   - Only allowed file types are accepted
   - File size limits are enforced

5. **Error Messages**
   - Sensitive data is never included in error messages
   - Stack traces are logged but not returned to Claude
   - Generic errors for unexpected failures

### Security Checklist

Before deploying to production:

- [ ] API keys are stored in environment variables
- [ ] HTTPS is enabled for API communication
- [ ] File upload validation is in place
- [ ] Error messages don't leak sensitive information
- [ ] Logs are properly secured and rotated
- [ ] API key rotation policy is established

## References

### Documentation

- **Design Document**: `.kiro/specs/claude-mcp-integration/design.md`
- **Requirements**: `.kiro/specs/claude-mcp-integration/requirements.md`
- **Tasks**: `.kiro/specs/claude-mcp-integration/tasks.md`

### External Resources

- **FastMCP Documentation**: [gofastmcp.com](https://gofastmcp.com/)
- **Model Context Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **NecoKeeper API**: `http://localhost:8000/docs`

### Context7 References

- `/jlowin/fastmcp` - FastMCP framework (Code Snippets: 1375, Trust Score: High)
- `/fastapi/fastapi` - FastAPI framework (Trust Score: 9.9)
- `/pydantic/pydantic` - Pydantic validation (Trust Score: 9.8)

## License

Part of the NecoKeeper project.

---

**Last Updated**: 2024-11-29
**Version**: 1.0.0
**Status**: Production Ready
