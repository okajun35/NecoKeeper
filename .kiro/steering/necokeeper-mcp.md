# NecoKeeper MCP Tools

This document describes the MCP (Model Context Protocol) tools available in the NecoKeeper project.

## Overview

NecoKeeper implements MCP tools that allow Claude (AI) to manage cats using natural language. These tools integrate with NecoKeeper through the Automation API.

## Available Tools

### 1. register_cat - Register Cat

**Purpose**: Register a new cat in the system

**Required Parameters**:
- `name`: Cat's name (1-100 characters)
- `gender`: Gender (`male`, `female`, `unknown`)
- `pattern`: Pattern/markings
- `tail_length`: Tail length
- `age`: Age/size

**Optional Parameters**:
- `status`: Status (default: "Under Protection")
- `color`: Fur color
- `collar`: Collar information
- `ear_cut`: Ear cut presence (default: false)
- `features`: Features/personality
- `protected_at`: Protection date (YYYY-MM-DD format)

**Return Value**:
```json
{
  "animal_id": 42,
  "name": "Tama",
  "public_url": "http://localhost:8000/public/care?animal_id=42"
}
```

**Usage Example**:
```
User: "Please register a cat named Tama. It's a male tabby with a long tail, adult cat."

Claude: Calls register_cat tool with the following parameters:
- name: "Tama"
- gender: "male"
- pattern: "Tabby"
- tail_length: "Long"
- age: "Adult"
```

### 2. generate_qr_card - Generate Single QR Card PDF

**Purpose**: Generate a single QR card PDF (A6 size) for a registered cat

**Required Parameters**:
- `animal_id`: Cat's ID (integer)

**Return Value**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_card_42.pdf",
  "animal_id": 42
}
```

**Usage Example**:
```
User: "Please generate a QR card for Tama"

Claude: Calls generate_qr_card tool with animal_id=42 to generate PDF
```

**Notes**:
- PDF is saved to `tmp/qr/qr_card_{animal_id}.pdf`
- A6 size single QR card
- Includes cat's photo, name, ID, and QR code
- Directory is created automatically if it doesn't exist
- Existing PDF will be overwritten

### 3. generate_qr - Generate QR Code Grid PDF

**Purpose**: Generate a QR code PDF (A4 size, 2×5 grid) for multiple registered cats

**Required Parameters**:
- `animal_id`: Cat's ID (integer)

**Return Value**:
```json
{
  "pdf_path": "/path/to/NecoKeeper/tmp/qr/qr_42.pdf",
  "animal_id": 42
}
```

**Usage Example**:
```
User: "Please generate a QR code grid for Tama"

Claude: Calls generate_qr tool with animal_id=42 to generate PDF
```

**Notes**:
- PDF is saved to `tmp/qr/qr_{animal_id}.pdf`
- A4 size imposition PDF (2×5 grid, max 10 cards)
- Can print multiple cat QR cards at once
- Directory is created automatically if it doesn't exist
- Existing PDF will be overwritten

### 4. upload_cat_image - Upload Cat Image

**Purpose**: Upload a profile image for a registered cat

**Required Parameters**:
- `animal_id`: Cat's ID (integer)
- `image_path`: Local image file path (absolute or relative path)

**Return Value**:
```json
{
  "image_url": "http://localhost:8000/media/animals/42/gallery/uuid.jpg",
  "animal_id": 42
}
```

**Usage Example**:
```
User: "Please upload an image for Tama. The path is /home/user/tama.jpg"

Claude: Calls upload_cat_image tool to upload the image
```

**Notes**:
- Supported formats: JPEG, PNG, WebP
- Maximum file size: 5MB (default)
- Maximum images per cat: 20 (default)
- Images are saved to `media/animals/{animal_id}/gallery/` with UUID-based filenames
- Images are automatically optimized

## Typical Workflows

### Scenario 1: Complete Registration of a New Cat

```
1. User: "I want to register a new cat. Her name is Mike, a female calico cat"
   → Claude: Register with register_cat

2. User: "Please upload Mike's photo. /path/to/mike.jpg"
   → Claude: Upload image with upload_cat_image

3. User: "Please create a QR card for Mike"
   → Claude: Generate PDF with generate_qr_card (A6 size, single card)
```

### Scenario 2: Batch Registration of Multiple Cats

```
User: "Please register 3 cats:
       1. Tama (male, tabby, adult)
       2. Kuro (female, black cat, kitten)
       3. Shiro (unknown, white cat, adult)"

Claude:
1. Call register_cat 3 times
2. Record each cat's ID
3. Generate QR codes as needed
```

## Technical Details

### Authentication

MCP tools internally use the Automation API:

- **Authentication Method**: Automation API Key (`X-Automation-Key` header)
- **Environment Variable**: `AUTOMATION_API_KEY` (minimum 32 characters)
- **Configuration**: Requires `ENABLE_AUTOMATION_API=true` in `.env` file

### Endpoints

MCP tools use the following Automation API endpoints:

| Tool | Endpoint | Method |
|------|----------|--------|
| register_cat | `/api/automation/animals` | POST |
| generate_qr_card | `/api/automation/pdf/qr-card` | POST |
| generate_qr | `/api/automation/pdf/qr-card-grid` | POST |
| upload_cat_image | `/api/automation/animals/{id}/images` | POST |

### Error Handling

MCP tools properly handle the following errors:

1. **Network Error**: API connection failure
2. **Authentication Error**: Invalid or expired API Key
3. **Validation Error**: Invalid parameters
4. **File Error**: Image file not found or invalid format
5. **Resource Error**: Cat does not exist (404)

When errors occur, user-friendly messages are returned.

## Usage Guidelines

### DO (Recommended)

- ✅ Accurately convert user-provided information to parameters
- ✅ Record animal_id after registration and use it in subsequent operations
- ✅ Explain the specific cause to users when errors occur
- ✅ Specify image paths as absolute paths (relative paths possible but not recommended)
- ✅ Verify the result of each step when performing multiple operations

### DON'T (Not Recommended)

- ❌ Don't omit required parameters
- ❌ Don't send invalid values (empty strings, null, etc.)
- ❌ Don't use wrong animal_id (use the return value from registration)
- ❌ Don't specify non-existent image paths
- ❌ Don't ignore errors and proceed to the next operation

## Troubleshooting

### Issue: "Authentication error: Invalid or expired token"

**Cause**: API Key is not configured or invalid

**Solution**:
1. Verify `AUTOMATION_API_KEY` is set in `.env` file
2. Confirm API Key is at least 32 characters
3. Verify `ENABLE_AUTOMATION_API=true` is set
4. Restart NecoKeeper API

### Issue: "Network error: Could not connect to NecoKeeper API"

**Cause**: NecoKeeper API is not running

**Solution**:
1. Verify NecoKeeper API is running: `curl http://localhost:8000/docs`
2. Verify `NECOKEEPER_API_URL` is correct (default: `http://localhost:8000`)
3. Check if firewall is blocking port 8000

### Issue: "File error: Image file not found"

**Cause**: Image file path is invalid

**Solution**:
1. Verify file path is correct (absolute path recommended)
2. Verify file exists: `ls -la /path/to/image.jpg`
3. Verify file has read permissions

### Issue: Cat not found (404 error)

**Cause**: Specified animal_id does not exist

**Solution**:
1. Accurately obtain animal_id from register_cat return value
2. Verify cat is registered in database
3. Check if confused with another cat's ID

## Developer Information

### File Structure

```
app/mcp/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point
├── config.py            # Configuration management
├── api_client.py        # Automation API client
├── server.py            # MCP server (FastMCP)
├── error_handler.py     # Error handling
├── tools/               # Tool implementations
│   ├── register_cat.py     # Cat registration tool
│   ├── generate_qr_card.py # Single QR card generation tool
│   ├── generate_qr.py      # QR grid generation tool
│   └── upload_image.py     # Image upload tool
└── README.md            # Detailed documentation
```

### Testing

```bash
# Run MCP tool tests
pytest tests/mcp/ -v

# Run integration tests
pytest tests/mcp/test_integration.py -v

# Run with coverage
pytest tests/mcp/ --cov=app/mcp --cov-report=html
```

### Debugging

Enable debug logging:

```bash
# Add to .env file
MCP_LOG_LEVEL=DEBUG
MCP_LOG_FILE=logs/mcp-server.log

# View logs
tail -f logs/mcp-server.log
```

## Related Documentation

- **MCP Server README**: `app/mcp/README.md` - Detailed technical documentation
- **Automation API README**: `app/api/automation/README.md` - API specifications
- **Design Document**: `.kiro/specs/claude-mcp-integration/design.md` - Design document
- **Requirements**: `.kiro/specs/claude-mcp-integration/requirements.md` - Requirements definition

## Summary

Using NecoKeeper MCP tools, Claude can manage cats using natural language. By properly interpreting user instructions and calling tools with correct parameters, efficient cat registration and management becomes possible.

When errors occur, explain them clearly to users and suggest appropriate solutions.

---

**Last Updated**: 2024-12-02
**Version**: 1.1.0

## Changelog

### v1.1.0 (2024-12-02)
- ✨ Added `generate_qr_card` tool (single QR card, A6 size)
- 🐛 Fixed image path handling (`media/` prefix issue resolved)
- 📝 Separated `generate_qr` into `generate_qr` (grid) and `generate_qr_card` (single)

### v1.0.0 (2024-11-29)
- 🎉 Initial release
- ✨ Implemented `register_cat`, `generate_qr`, `upload_cat_image` tools
