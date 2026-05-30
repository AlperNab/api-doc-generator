# Api Doc Generator — Standalone Real GUI Implementation

This folder is now its own runnable project app. It does not depend on the root all-project dashboard at runtime.

## Run

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default URL: `http://127.0.0.1:9102`

## What is inside this project folder

- `app/` — FastAPI backend for this project.
- `static/` — elegant browser GUI.
- `plugins/api-doc-generator.json` — this project’s own feature/customization/input schema.
- `project_config.json` — readable copy of the same project-specific configuration.
- `data/` — local SQLite jobs, uploads, exports.
- `tests/` — verifies this project has a registered real local engine.

## Project-specific scope

- Domain: `Developer / API`
- Target user: `Domain operator, business owner, analyst, or team member who needs this workflow executed reliably.`
- Core job: Code/OpenAPI/schema → publishable developer documentation
- Suite: `Developer Productivity Suite`

## Deep features applied

- OpenAPI import
- endpoint grouping
- auth examples
- SDK snippets
- changelog
- error catalog
- try-it console
- version diff
- Postman/Insomnia export

## Customization controls

- `execution_mode` — Execution mode (select)
- `audience_level` — audience level (select)
- `framework` — framework (select)
- `language_examples` — language examples (select)
- `auth_scheme` — auth scheme (text)
- `version_style` — version style (select)
- `public_private_endpoints` — public/private endpoints (textarea)
- `code_style` — code style (select)
- `output_format` — output format (select)
- `language` — language (select)
- `privacy_mode` — privacy mode (select)
- `confidence_threshold` — Confidence threshold (slider)

## Input fields

- `code` — Code (text) required
- `openapi` — OpenAPI (text) required
- `schema` — schema (select) required
- `work_brief` — Work brief / source text / URL / instructions (textarea) required

## External data policy

The local deterministic core is real and executable. Live external systems are not simulated. If Shopify, ATS, ERP, OCR/STT, maps, SERP, market data, medical databases, tax/customs databases, or other live systems are required, this project reports the missing connector/API requirement instead of inventing data.

---

## Final UX/UI Layer

This project now uses the **Developer Workbench** pattern.

**UX workflow:** Code/schema/log intake → analysis → diff/tests/docs → implementation checklist

**Domain components:**
- Endpoint explorer
- OpenAPI preview
- SDK snippet tabs
- Auth/error catalog
- Docs publish checklist

**Quick actions:**
- Parse endpoints
- Generate OpenAPI outline
- Build SDK examples
- Create changelog notes

**No fake-data policy:** external/live actions require real connectors or API keys. Missing connectors are reported instead of simulated.
