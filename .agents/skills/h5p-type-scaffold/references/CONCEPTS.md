# H5P Concepts

## Content Types (Runnable Libraries)
Content types are the interactive libraries end users see (e.g., quizzes, presentations). They are runnable libraries (`"runnable": 1`) and are exposed under the `H5P.*` namespace. A content type is defined by:

- `library.json` metadata and asset entry points
- `semantics.json` editor form schema
- runtime JS/CSS that renders the interaction

## Editor Widgets (Editor Libraries)
Editor widgets are custom UI controls inside the H5P editor. They are not runnable (`"runnable": 0`) and are exposed under `H5PEditor.*`. They implement editor lifecycle methods such as `appendTo`, `validate`, and `remove`.

## Dependency Libraries
Dependency libraries are non-runnable shared code used by content types (often under `H5P.*` or `H5PApi.*`). They provide reusable functionality, UI elements, or APIs that other libraries depend on.

## Semantics
`semantics.json` drives the editor form fields and validation. It defines the data structure, labels, defaults, and constraints for your content type.

## References
- H5P library development: https://h5p.org/library-development
- H5P semantics: https://h5p.org/semantics
- Creating editor widgets: https://h5p.org/creating-editor-widgets
- Technical overview: https://h5p.org/technical-overview
- See also: references/CONTENT-TYPE-AUTHORING.md
- See also: references/DEV-HARNESS.md
- See also: references/XAPI.md
