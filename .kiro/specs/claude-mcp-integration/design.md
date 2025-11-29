# Design Document

## Overview

This design document outlines the implementation of a Model Context Protocol (MCP) server that enables Claude (running on AWS Kiro) to interact with NecoKeeper through structured tool calls. The MCP server will act as a bridge between Claude's natural language interface and NecoKeeper's REST API, allowing automated cat registration, QR code generation, and image uploads.

The implementation uses FastMCP, a Python framework for building MCP servers, and integrates with NecoKeeper's existing REST API endpoints. The server will run locally and communicate with both Claude (via MCP protocol) and NecoKeeper (via HTTP REST API).

**Key Design Principles:**
- **Simplicity**: Focus on local demo use case, not production deployment
- **Security**: Use environment-based authentication, no hardcoded credentials
- **Error Transparency**: Provide clear, actionable error messages to Claude
- **Minimal Dependencies**: Leverage existing NecoKeeper APIs without modification

## Architecture

### System Components

```
┌─────────────────┐
│  Claude (Kiro)  │
│                 │
└────────┬────────┘
         │ MCP Protocol
         │ (stdio/HTTP)
         │
┌────────▼────────┐
│  FastMCP Server │
│  (app/mcp/)     │
│                 │
│  - register_cat │
│  - generate_qr  │
│  - upload_image │
└────────┬────────┘
         │ HTTP REST
         │ (with auth)
         │
┌────────▼────────┐
│  NecoKeeper API │
│  (FastAPI)      │
│                 │
│  - POST /animals│
│  - POST /pdf    │
│  - POST /images │
└─────────────────┘
```

### Communication Flow

1. **User → Claude**: User provides cat information in natural language
2. **Claude → MCP Server**: Claude invokes MCP tools with structured parameters
3. **MCP Server → NecoKeeper API**: MCP server makes authenticated HTTP requests
4. **NecoKeeper API → MCP Server**: API returns results or errors
5. **MCP Server → Claude**: MCP server formats response for Claude
6. **Claude → User**: Claude presents results in natural language

### Transport Layer

The MCP server will support **stdio transport** for local development and demo purposes. This is the simplest transport mechanism and works well with Kiro's MCP client.

**Why stdio transport:**
- **Simplicity**: No network configuration required
- **Security**: Communication stays local, no exposed ports
- **Kiro Integration**: Kiro's MCP client natively supports stdio transport
- **Process Management**: Kiro manages the MCP server process lifecycle

**Server Startup:**

```python
# Server startup with stdio transport
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Alternative: HTTP Transport (Future Enhancement)**

For remote access or web-based demos, HTTP transport can be added:

```python
# HTTP transport (not in current scope)
if __name__ == "__main__":
    mcp.run(transport="http", port=8001)
```

This would require additional configuration in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "necokeeper-http": {
      "url": "http://localhost:8001/mcp",
      "transport": "http"
    }
  }
}
```

## Components and Interfaces

### 1. MCP Server (`app/mcp/server.py`)

**Responsibilities:**
- Initialize FastMCP server instance
- Register tool definitions
- Handle tool invocations
- Manage authentication with NecoKeeper API
- Format responses and errors for Claude

**Key Classes:**

```python
class MCPServer:
    """Main MCP server class"""

    def __init__(self):
        self.mcp = FastMCP(name="NecoKeeper MCP Server")
        self.api_client = NecoKeeperAPIClient()
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools"""
        pass

    def run(self):
        """Start the MCP server"""
        self.mcp.run(transport="stdio")
```

### 2. API Client (`app/mcp/api_client.py`)

**Responsibilities:**
- Make HTTP requests to NecoKeeper Automation API using httpx.AsyncClient
- Handle authentication (X-Automation-Key header)
- Parse API responses
- Convert API errors to MCP-friendly format

**Authentication Strategy:**

The MCP server will use NecoKeeper's **Automation API Key** authentication, which is simpler than JWT authentication:

- **Single API Key**: One environment variable (`AUTOMATION_API_KEY`)
- **No Token Expiration**: API keys don't expire like JWT tokens
- **No Login Flow**: No need to manage login/logout
- **Header-Based**: Simple `X-Automation-Key` header

**Key Methods:**

```python
import httpx
import os
from typing import Any

class NecoKeeperAPIClient:
    """Client for NecoKeeper Automation API"""

    def __init__(self):
        self.base_url = os.getenv("NECOKEEPER_API_URL", "http://localhost:8000")
        self.api_key = os.getenv("AUTOMATION_API_KEY")

        if not self.api_key:
            raise ValueError(
                "AUTOMATION_API_KEY environment variable is required. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        # Create httpx client with API Key authentication
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Automation-Key": self.api_key},
            timeout=30.0
        )

    async def create_animal(self, animal_data: dict) -> dict[str, Any]:
        """POST /api/automation/animals"""
        response = await self.client.post("/api/automation/animals", json=animal_data)
        response.raise_for_status()
        return response.json()

    async def generate_qr_pdf(self, animal_ids: list[int]) -> bytes:
        """POST /api/v1/pdf/qr-card-grid (uses JWT auth, not Automation API)"""
        # Note: PDF endpoint requires JWT auth, so we need to handle this differently
        # For POC, we'll use the Automation API to get animal data, then generate PDF locally
        # Or we can add a PDF endpoint to Automation API
        response = await self.client.post(
            "/api/v1/pdf/qr-card-grid",
            json={"animal_ids": animal_ids}
        )
        response.raise_for_status()
        return response.content

    async def upload_image(self, animal_id: int, image_path: str) -> dict[str, Any]:
        """POST /api/automation/animals/{animal_id}/images"""
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = await self.client.post(
                f"/api/automation/animals/{animal_id}/images",
                files=files
            )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
```

**Note on PDF Generation:**

The current PDF endpoint (`/api/v1/pdf/qr-card-grid`) requires JWT authentication. For the POC, we have two options:

1. **Add PDF endpoint to Automation API** (Recommended): Create `/api/automation/pdf/qr-card-grid`
2. **Hybrid Authentication**: Use Automation API Key for most operations, JWT for PDF only

We'll go with Option 1 for consistency and simplicity.

### 3. Tool Definitions (`app/mcp/tools/`)

Each tool will be defined as a separate module for clarity:

- `app/mcp/tools/register_cat.py` - Cat registration tool
- `app/mcp/tools/generate_qr.py` - QR PDF generation tool
- `app/mcp/tools/upload_image.py` - Image upload tool

**Tool Interface Pattern:**

```python
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

def register_tool(mcp: FastMCP, api_client: NecoKeeperAPIClient):
    """Register the tool with the MCP server"""

    @mcp.tool
    async def tool_name(param1: str, param2: int) -> dict:
        """Tool description for Claude"""
        try:
            result = await api_client.some_method(param1, param2)
            return result
        except Exception as e:
            raise ToolError(f"Operation failed: {str(e)}")
```

## Data Models

### Tool Input Schemas

#### 1. register_cat Tool

```python
from typing import Annotated
from pydantic import Field

@mcp.tool
async def register_cat(
    name: Annotated[str, Field(description="猫の名前", min_length=1, max_length=100)],
    sex: Annotated[str, Field(description="性別: オス, メス, 不明")],
    age: Annotated[str | None, Field(description="年齢（推定可）", default=None)],
    status: Annotated[str, Field(description="ステータス: 保護中, 譲渡可能, 譲渡済み", default="保護中")],
    color: Annotated[str | None, Field(description="毛色", default=None)],
    pattern: Annotated[str | None, Field(description="柄", default=None)],
    intake_date: Annotated[str | None, Field(description="保護日 (YYYY-MM-DD)", default=None)],
    note: Annotated[str | None, Field(description="備考", default=None)],
) -> dict:
    """
    猫プロフィールを登録

    Returns:
        dict: {
            "animal_id": int,
            "name": str,
            "public_url": str
        }
    """
```

#### 2. generate_qr Tool

```python
@mcp.tool
async def generate_qr(
    animal_id: Annotated[int, Field(description="猫ID", gt=0)],
) -> dict:
    """
    QR付きPDFを生成

    Returns:
        dict: {
            "pdf_path": str,  # ローカルファイルパス
            "animal_id": int
        }
    """
```

#### 3. upload_cat_image Tool

```python
@mcp.tool
async def upload_cat_image(
    animal_id: Annotated[int, Field(description="猫ID", gt=0)],
    image_path: Annotated[str, Field(description="ローカル画像ファイルパス")],
) -> dict:
    """
    猫プロフィール画像をアップロード

    Returns:
        dict: {
            "image_url": str,
            "animal_id": int
        }
    """
```

### API Response Models

The MCP server will use NecoKeeper's existing Pydantic schemas:

- `AnimalResponse` - Cat profile data
- `AnimalCreate` - Cat creation payload
- Error responses follow FastAPI's HTTPException format

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

Before defining the correctness properties, I've reviewed all testable properties from the prework to eliminate redundancy:

**Consolidated Properties:**
- Properties 1.2, 2.2, 3.3, and 6.1 all relate to API calls with authentication - these can be combined into a single comprehensive property
- Properties 1.3, 2.4, and 3.4 all relate to successful responses containing required fields - these follow a similar pattern
- Properties 1.4, 3.5, 7.1, 7.2, 7.3, 7.4, and 7.5 all relate to error handling - these can be organized into a few comprehensive error handling properties
- Properties 8.2, 8.3, and 8.4 all relate to workflow data consistency - these can be combined

**Unique Properties Retained:**
- Tool registration and schema validation (examples)
- Configuration reading from environment
- PDF file creation and naming
- Directory auto-creation (edge case)
- Startup validation
- End-to-end workflow integration

### Correctness Properties

Property 1: API calls include authentication
*For any* MCP tool invocation that requires calling the NecoKeeper API, the HTTP request should include a valid Bearer authentication token in the Authorization header
**Validates: Requirements 1.2, 2.2, 3.3, 6.1**

Property 2: Successful operations return required fields
*For any* successful tool invocation, the response should contain all required fields as specified in the tool's return schema (animal_id and name for register_cat, pdf_path for generate_qr, image_url for upload_cat_image)
**Validates: Requirements 1.3, 2.4, 3.4**

Property 3: PDF files follow naming convention
*For any* successful QR PDF generation, the saved file path should match the pattern `tmp/qr/qr_{animal_id}.pdf` where animal_id is the input parameter
**Validates: Requirements 2.3**

Property 4: Image files are readable before upload
*For any* upload_cat_image invocation with a valid image_path, the MCP server should successfully read the file contents before attempting the API call
**Validates: Requirements 3.2**

Property 5: Configuration from environment variables
*For any* MCP server startup, all configuration values (API_BASE_URL, AUTH_TOKEN) should be read from environment variables and never from hardcoded values
**Validates: Requirements 1.5, 4.2, 6.2**

Property 6: Tool list completeness
*For any* query for available tools, the MCP server should return all three registered tools (register_cat, generate_qr, upload_cat_image) with their complete schemas
**Validates: Requirements 4.4**

Property 7: Error messages are descriptive
*For any* tool invocation that fails, the error message returned to Claude should include the error type (network, validation, authentication, or unexpected) and actionable details
**Validates: Requirements 1.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5**

Property 8: Authentication errors are clear
*For any* API call that fails due to authentication, the error message should explicitly mention authentication failure and not be masked as a generic error
**Validates: Requirements 6.3, 7.3**

Property 9: Startup validation fails fast
*For any* MCP server startup attempt with missing or invalid configuration, the server should fail to start and log a clear error message before attempting any API calls
**Validates: Requirements 4.5, 6.5**

Property 10: Workflow data consistency
*For any* complete workflow (register → upload → generate_qr), the animal_id returned from registration should be valid for subsequent image upload and QR generation operations
**Validates: Requirements 8.2, 8.3, 8.4**

Property 11: Workflow error clarity
*For any* multi-step workflow where a step fails, the error message should clearly indicate which step failed (registration, upload, or QR generation) and the reason
**Validates: Requirements 8.5**

## Error Handling

### Error Categories

The MCP server will handle four categories of errors:

1. **Network Errors**: Connection failures, timeouts, DNS errors
2. **Validation Errors**: Invalid input parameters, schema violations
3. **Authentication Errors**: Missing/invalid tokens, expired credentials
4. **Unexpected Errors**: Server errors, file system errors, unknown exceptions

### Error Handling Strategy

```python
from fastmcp.exceptions import ToolError

async def handle_api_call(operation: Callable) -> dict:
    """Centralized error handling for API calls"""
    try:
        return await operation()
    except httpx.ConnectError as e:
        raise ToolError(f"Network error: Could not connect to NecoKeeper API. {str(e)}")
    except httpx.TimeoutException as e:
        raise ToolError(f"Network error: Request timed out. {str(e)}")
    except HTTPException as e:
        if e.status_code == 401:
            raise ToolError("Authentication error: Invalid or expired token. Please check NECOKEEPER_AUTH_TOKEN.")
        elif e.status_code == 400:
            raise ToolError(f"Validation error: {e.detail}")
        elif e.status_code == 404:
            raise ToolError(f"Not found: {e.detail}")
        else:
            raise ToolError(f"API error ({e.status_code}): {e.detail}")
    except FileNotFoundError as e:
        raise ToolError(f"File error: Image file not found at {str(e)}")
    except Exception as e:
        # Log full error for debugging
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        # Return generic message to user
        raise ToolError(f"Unexpected error occurred. Please check server logs.")
```

### Error Response Format

All errors will be returned to Claude using FastMCP's `ToolError` exception, which ensures consistent error formatting:

```json
{
  "error": {
    "type": "tool_error",
    "message": "Network error: Could not connect to NecoKeeper API. Connection refused."
  }
}
```

## Testing Strategy

### Unit Testing

**Test Coverage Goals:**
- API Client: 80%+ coverage
- Tool implementations: 80%+ coverage
- Error handling: 90%+ coverage

**Key Unit Tests:**

1. **API Client Tests** (`tests/mcp/test_api_client.py`):
   - Test authentication token retrieval
   - Test API request formatting
   - Test response parsing
   - Test error handling for each error category

2. **Tool Tests** (`tests/mcp/test_tools.py`):
   - Test each tool with valid inputs
   - Test each tool with invalid inputs
   - Test error propagation
   - Test response formatting

3. **Configuration Tests** (`tests/mcp/test_config.py`):
   - Test environment variable reading
   - Test missing configuration handling
   - Test invalid configuration handling

### Property-Based Testing

We will use **Hypothesis** for property-based testing in Python. Hypothesis will be configured to run a minimum of 100 iterations per property test.

**Property Test Framework:**

```python
from hypothesis import given, strategies as st
import pytest

# Example property test structure
@given(
    name=st.text(min_size=1, max_size=100),
    sex=st.sampled_from(["オス", "メス", "不明"]),
    status=st.sampled_from(["保護中", "譲渡可能", "譲渡済み"])
)
@pytest.mark.property_test
async def test_register_cat_property(name, sex, status):
    """
    Feature: claude-mcp-integration, Property 2: Successful operations return required fields

    For any valid cat registration, the response should contain animal_id and name.
    """
    # Test implementation
    pass
```

**Property Test Requirements:**
- Each property test MUST be tagged with `@pytest.mark.property_test`
- Each property test MUST include a docstring with the format: `Feature: {feature_name}, Property {number}: {property_text}`
- Each property test MUST run at least 100 iterations (Hypothesis default)
- Property tests MUST use Hypothesis strategies to generate test data

**Property Test Implementation Plan:**

1. **Property 1: API calls include authentication**
   - Generate random valid cat data
   - Verify Authorization header is present in all API calls
   - Verify header format is "Bearer {token}"

2. **Property 2: Successful operations return required fields**
   - Generate random valid inputs for each tool
   - Verify response contains all required fields
   - Verify field types match schema

3. **Property 3: PDF files follow naming convention**
   - Generate random animal IDs
   - Verify file path matches pattern
   - Verify file exists after generation

4. **Property 4: Image files are readable before upload**
   - Generate random valid image files
   - Verify file is read before API call
   - Verify file contents are not empty

5. **Property 7: Error messages are descriptive**
   - Generate random invalid inputs
   - Verify error messages contain error type
   - Verify error messages contain actionable details

6. **Property 10: Workflow data consistency**
   - Generate random cat profiles
   - Execute full workflow
   - Verify animal_id consistency across operations

### Integration Testing

**Integration Test Scenarios:**

1. **End-to-End Workflow Test**:
   - Start MCP server
   - Register a cat via register_cat tool
   - Upload an image via upload_cat_image tool
   - Generate QR PDF via generate_qr tool
   - Verify all operations succeed
   - Verify data consistency

2. **Authentication Flow Test**:
   - Test with valid token
   - Test with invalid token
   - Test with expired token
   - Test with missing token

3. **Error Recovery Test**:
   - Test network failure recovery
   - Test API error handling
   - Test file system error handling

### Testing Tools

- **pytest**: Test runner and framework
- **pytest-asyncio**: Async test support
- **Hypothesis**: Property-based testing
- **httpx**: HTTP client for API testing
- **pytest-mock**: Mocking support
- **pytest-cov**: Coverage reporting

### Test Execution

```bash
# Run all tests
pytest tests/mcp/

# Run only property tests
pytest tests/mcp/ -m property_test

# Run with coverage
pytest tests/mcp/ --cov=app/mcp --cov-report=html

# Run specific property test
pytest tests/mcp/test_properties.py::test_api_authentication_property -v
```

## Security Considerations

### Authentication

1. **Token Storage**: Authentication tokens MUST be stored in environment variables, never in code
2. **Token Transmission**: Tokens MUST be transmitted via HTTPS in production (local demo uses HTTP)
3. **Token Validation**: The MCP server MUST validate token presence before making API calls

### Input Validation

1. **File Path Validation**: Image paths MUST be validated to prevent directory traversal attacks
2. **Parameter Validation**: All tool parameters MUST be validated using Pydantic schemas
3. **File Type Validation**: Uploaded images MUST be validated for allowed file types

### Error Information Disclosure

1. **Sensitive Data**: Error messages MUST NOT include sensitive data (tokens, passwords, internal paths)
2. **Stack Traces**: Full stack traces MUST only be logged, not returned to Claude
3. **Generic Errors**: Unexpected errors MUST return generic messages to Claude

## Configuration

### Environment Variables

The MCP server requires the following environment variables:

**Required:**

```bash
# NecoKeeper API URL
NECOKEEPER_API_URL=http://localhost:8000

# Automation API Key (generate with command below)
AUTOMATION_API_KEY=<your-api-key>

# Enable Automation API on NecoKeeper server
ENABLE_AUTOMATION_API=true
```

**Optional:**

```bash
MCP_LOG_LEVEL=INFO
MCP_LOG_FILE=logs/mcp-server.log
```

**How to generate an Automation API Key:**

```bash
# Generate a secure 32-character API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ

# Add to .env:
echo "AUTOMATION_API_KEY=xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ" >> .env
echo "ENABLE_AUTOMATION_API=true" >> .env
```

**Why Automation API Key is simpler:**

- ✅ No login flow required
- ✅ No token expiration to manage
- ✅ Single environment variable
- ✅ Already implemented in NecoKeeper
- ✅ Perfect for automation and MCP use cases

### Configuration Validation

The server will validate configuration on startup:

```python
import os

class MCPConfig:
    """MCP Server configuration"""

    def __init__(self):
        self.api_url = os.getenv("NECOKEEPER_API_URL", "http://localhost:8000")
        self.api_key = os.getenv("AUTOMATION_API_KEY")
        self.log_level = os.getenv("MCP_LOG_LEVEL", "INFO")
        self.log_file = os.getenv("MCP_LOG_FILE", "logs/mcp-server.log")

        self._validate()

    def _validate(self):
        """Validate required configuration"""
        if not self.api_url:
            raise ValueError("NECOKEEPER_API_URL is required")

        if not self.api_key:
            raise ValueError(
                "AUTOMATION_API_KEY is required. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        # Validate API key length (should be at least 32 characters for security)
        if len(self.api_key) < 32:
            raise ValueError(
                "AUTOMATION_API_KEY must be at least 32 characters. "
                "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
```

## Deployment

### Local Development Setup

1. **Install Dependencies**:
   ```bash
   pip install fastmcp httpx pydantic
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start NecoKeeper API**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Start MCP Server**:
   ```bash
   python -m app.mcp.server
   ```

5. **Generate Automation API Key**:
   ```bash
   # Generate a secure API key
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Add to .env:
   echo "AUTOMATION_API_KEY=<generated-key>" >> .env
   echo "ENABLE_AUTOMATION_API=true" >> .env
   ```

6. **Register with Kiro**:
   - Add to `.kiro/settings/mcp.json`:
   ```json
   {
     "mcpServers": {
       "necokeeper": {
         "command": "python",
         "args": ["-m", "app.mcp.server"],
         "env": {
           "NECOKEEPER_API_URL": "http://localhost:8000",
           "AUTOMATION_API_KEY": "${AUTOMATION_API_KEY}"
         }
       }
     }
   }
   ```

### Demo Scenario

**Scenario: Register a new cat and generate QR code**

1. **User to Claude**: "I need to register a new cat named Tama. She's a female calico cat, about 2 years old, currently in protection status."

2. **Claude invokes register_cat**:
   ```json
   {
     "name": "Tama",
     "sex": "メス",
     "age": "2歳",
     "status": "保護中",
     "pattern": "三毛"
   }
   ```

3. **MCP Server response**:
   ```json
   {
     "animal_id": 42,
     "name": "Tama",
     "public_url": "http://localhost:8000/public/care?animal_id=42"
   }
   ```

4. **User to Claude**: "Great! Now generate a QR code for Tama."

5. **Claude invokes generate_qr**:
   ```json
   {
     "animal_id": 42
   }
   ```

6. **MCP Server response**:
   ```json
   {
     "pdf_path": "/home/user/NecoKeeper/tmp/qr/qr_42.pdf",
     "animal_id": 42
   }
   ```

7. **Claude to User**: "I've successfully registered Tama (ID: 42) and generated a QR code PDF at /home/user/NecoKeeper/tmp/qr/qr_42.pdf. You can print this QR code to allow volunteers to log care records for Tama."

## Performance Considerations

### Response Times

- **register_cat**: < 2 seconds (includes API call and database write)
- **generate_qr**: < 5 seconds (includes PDF generation)
- **upload_cat_image**: < 3 seconds (includes file upload and processing)

### Resource Usage

- **Memory**: < 100MB for MCP server process
- **Disk**: QR PDFs stored in `tmp/qr/` (cleanup recommended)
- **Network**: Minimal (local API calls only)

### Optimization Strategies

1. **Connection Pooling**: Reuse HTTP connections to NecoKeeper API
2. **Async Operations**: Use async/await for all I/O operations
3. **File Cleanup**: Implement periodic cleanup of old QR PDFs
4. **Caching**: Cache authentication tokens (if using login flow)

## Future Enhancements

### Phase 2 Features (Not in Current Scope)

1. **Batch Operations**: Register multiple cats in one operation
2. **Image Generation**: Generate cat images using AI (DALL-E, Stable Diffusion)
3. **OCR Integration**: Extract cat information from photos
4. **Search Tools**: Search for existing cats before registration
5. **Update Tools**: Update existing cat profiles
6. **Webhook Support**: Notify external systems of new registrations

### Production Considerations (Not in Current Scope)

1. **HTTP Transport**: Support HTTP transport for remote MCP servers
2. **Rate Limiting**: Implement rate limiting for API calls
3. **Monitoring**: Add metrics and health checks
4. **Multi-tenancy**: Support multiple NecoKeeper instances
5. **Audit Logging**: Log all MCP operations for compliance

## References

### Context7 Documentation

- **FastMCP**: `/jlowin/fastmcp` (Code Snippets: 1375, Source Reputation: High, Benchmark Score: 82.4)
  - Server creation and tool registration
  - Authentication patterns
  - Error handling with ToolError
  - Transport configuration

### NecoKeeper API Documentation

- `POST /api/v1/animals` - Cat registration endpoint
- `POST /api/v1/pdf/qr-card-grid` - QR PDF generation endpoint
- `POST /api/v1/animals/{animal_id}/profile-image` - Image upload endpoint

### External Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
