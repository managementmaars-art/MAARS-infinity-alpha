# Frontend Generation Logic (Source-Aligned)

This document summarizes frontend generation logic implemented in the online generator project:

- `cisdigital-generator-app/generator/services.py`
- `cisdigital-generator-app/generator/biz_dependencies_forms.py`
- `cisdigital-generator-app/generator/models.py`

## Type Mapping

Frontend project type to template mapping:

- `frontend_app` -> `fe-cisdigital-vite-app-template`
- `frontend_ui` -> `fe-cisdigital-monorepo-template`
- `frontend_sdk` -> `fe-cisdigital-ts-lib-template`

## Command Template

Frontend command is assembled as:

```bash
onebase-cli create -t <template_name> -p <project_name>
```

- CLI name defaults to `onebase-cli` and can be overridden.
- `project_name` format is `fe-<company_slug>-<product_slug>-<service_slug>`.
- Do not append project-type suffixes (`-app`, `-ui`, `-sdk`) to `project_name`.

## Naming Rules

Form-level validation (`ProjectGenerationForm`) requires kebab-case for:

- `company_name`
- `product_name`
- `service_name`

Payload-level normalization uses slugify:

- lower-case input
- replace non `[a-zA-Z0-9._-]` with `-`
- collapse repeated `-`
- trim leading/trailing `-`

## Payload Fields Used by Frontend Flow

Key fields generated for frontend flow:

- `template_name`
- `project_name`
- `frontend_bundle`
- `output_folder`
- `generated_folder`
- `archive_basename`
- `object_name`
- `company_slug`
- `product_slug`
- `service_slug`

## Form Field Note

`frontend_project_type` currently exists and is optional.
It is preserved in payload context but does not affect template selection.
