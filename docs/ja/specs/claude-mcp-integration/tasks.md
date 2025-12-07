# Implementation Plan

This document outlines the implementation tasks for the Claude MCP Integration feature. Each task builds incrementally on previous tasks, with property-based tests integrated close to implementation to catch errors early.

- [x] 1. Set up MCP server structure and configuration
  - Create `app/mcp/` directory structure
  - Implement `MCPConfig` class for environment variable validation
  - Create `__init__.py` and `__main__.py` for module execution
  - _Requirements: 4.1, 4.2, 4.5, 6.2, 6.5_

- [x] 2. Implement API client with Automation API Key authentication
  - Create `app/mcp/api_client.py` with `NecoKeeperAPIClient` class
  - Implement httpx.AsyncClient with X-Automation-Key header
  - Add configuration validation for AUTOMATION_API_KEY
  - Implement error handling for network and authentication errors
  - _Requirements: 1.2, 1.5, 6.1, 6.2, 6.3_

- [ ]* 2.1 Write property test for API authentication
  - **Property 1: API calls include authentication**
  - **Validates: Requirements 1.2, 2.2, 3.3, 6.1**

- [x] 3. Add PDF endpoint to Automation API
  - Create `/api/automation/pdf/qr-card-grid` endpoint in NecoKeeper
  - Use existing `pdf_service.generate_qr_card_grid_pdf` function
  - Add Automation API Key authentication
  - _Requirements: 2.2_

- [x] 4. Implement register_cat tool
  - Create `app/mcp/tools/register_cat.py`
  - Define tool with Pydantic Field annotations for parameters
  - Implement cat registration via `/api/automation/animals`
  - Return animal_id, name, and public_url
  - Handle validation and API errors with ToolError
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 4.1 Write property test for register_cat
  - **Property 2: Successful operations return required fields**
  - **Validates: Requirements 1.3**

- [ ]* 4.2 Write property test for error handling
  - **Property 7: Error messages are descriptive**
  - **Validates: Requirements 1.4, 7.1, 7.2, 7.3, 7.4**

- [x] 5. Implement generate_qr tool
  - Create `app/mcp/tools/generate_qr.py`
  - Define tool with animal_id parameter
  - Call `/api/automation/pdf/qr-card-grid` endpoint
  - Save PDF to `tmp/qr/qr_{animal_id}.pdf`
  - Create directory if it doesn't exist
  - Return local file path
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 5.1 Write property test for PDF naming convention
  - **Property 3: PDF files follow naming convention**
  - **Validates: Requirements 2.3**

- [x] 5.2 Add image upload endpoint to Automation API
  - Create `POST /api/automation/animals/{animal_id}/images` endpoint in `app/api/automation/animals.py`
  - Accept multipart/form-data with image file (UploadFile)
  - Use existing `image_service.upload_image()` function
  - Images saved to `media/animals/{animal_id}/gallery/` with UUID-based filenames
  - Add Automation API Key authentication (already applied via router dependency)
  - Return image_url (e.g., `/media/animals/42/gallery/uuid.jpg`) and image_id
  - Handle errors: 404 (animal not found), 400 (invalid file/size limit), 500 (upload failed)
  - _Requirements: 3.3, 3.4_

- [x] 6. Implement upload_cat_image tool
  - Create `app/mcp/tools/upload_image.py`
  - Define tool with animal_id and image_path parameters
  - Read image file from local filesystem
  - Upload via `/api/automation/animals/{animal_id}/images`
  - Return image_url or image_id
  - Handle file not found and invalid file errors
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 6.1 Write property test for image file reading
  - **Property 4: Image files are readable before upload**
  - **Validates: Requirements 3.2**

- [x] 7. Create main MCP server
  - Create `app/mcp/server.py` with `MCPServer` class
  - Initialize FastMCP instance
  - Register all three tools (register_cat, generate_qr, upload_cat_image)
  - Configure stdio transport
  - Add startup configuration validation
  - _Requirements: 4.1, 4.3, 4.4_

- [ ]* 7.1 Write property test for tool list completeness
  - **Property 6: Tool list completeness**
  - **Validates: Requirements 4.4**

- [ ]* 7.2 Write property test for startup validation
  - **Property 9: Startup validation fails fast**
  - **Validates: Requirements 4.5, 6.5**

- [x] 8. Add error handling and logging
  - Implement centralized error handling function
  - Add logging configuration
  - Map HTTP errors to user-friendly messages
  - Ensure authentication errors are clear
  - _Requirements: 6.3, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 8.1 Write property test for authentication error clarity
  - **Property 8: Authentication errors are clear**
  - **Validates: Requirements 6.3, 7.3**

- [x] 9. Create documentation
  - Write README.md with setup instructions
  - Document environment variables
  - Add demo scenario with example prompts
  - Include troubleshooting section
  - Document Kiro MCP configuration
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 10. Checkpoint - Integration testing
  - Ensure all tests pass, ask the user if questions arise
  - Test complete workflow: register → upload → generate_qr
  - Verify error handling for each tool
  - Test with missing/invalid configuration
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 10.1 Write property test for workflow data consistency
  - **Property 10: Workflow data consistency**
  - **Validates: Requirements 8.2, 8.3, 8.4**

- [ ]* 10.2 Write property test for workflow error clarity
  - **Property 11: Workflow error clarity**
  - **Validates: Requirements 8.5**

- [ ] 11. Final Checkpoint - Make sure all tests are passing
  - Ensure all tests pass, ask the user if questions arise
