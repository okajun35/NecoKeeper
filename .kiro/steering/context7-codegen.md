---
inclusion: always
---

# Codegen Rule: Always use Context7 MCP

Apply the following policy to **all code generation and refactoring**:

1. Identify the target language/framework/library, and first obtain the latest documentation using **Context7 MCP**. Follow these steps:
   - Use `resolve-library-id` to resolve the Context7-compatible ID from the library name
   - Call `get-library-docs` with **approximately 5000 tokens** to extract key points of the relevant API/guide
2. For all subsequent design and implementation decisions, use the retrieved documentation as the **primary basis** for explanation and justification.
3. If version differences or deprecated APIs are suspected, **re-fetch Context7 results** to verify.
4. If Context7 cannot be reached, explicitly state this and leave a "temporary alternative basis (official docs link, etc.)" and **TODO: Re-verify with Context7** in the generated output.

> Expected result: PR and commit descriptions should state "Context7 referenced", briefly noting the referenced API name, version, and main basis.
