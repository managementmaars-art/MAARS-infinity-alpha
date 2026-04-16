# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-22

### Added
- Initial release of Office Automation Skill
- Word document processing (`word_processor.py`)
  - Read document content and structure
  - Create new documents with title and content
  - Template filling with JSON data
  - Extract tables to CSV format
- Excel spreadsheet processing (`excel_processor.py`)
  - Read single or multiple sheets
  - Write data with custom headers
  - Merge multiple Excel files
  - Convert between Excel and CSV formats
  - Basic data analysis (statistics, missing values)
- Batch processing utilities (`batch_processor.py`)
  - Batch template filling for mass document generation
  - Batch format conversion (Excel ↔ CSV)
  - Batch table extraction from Word documents
- Documentation
  - Complete usage guide (使用指南.md)
  - Example collection (示例集合.md)
  - API reference (office_api.md)
  - Bilingual README (Chinese/English)
- Example files
  - Sample JSON data for testing
  - Template examples
- GitHub ready files
  - MIT License
  - .gitignore for Python projects
  - Changelog

### Dependencies
- python-docx >= 0.8.11
- openpyxl >= 3.0.0
- pandas >= 1.3.0

### Compatibility
- Python 3.8+
- OpenClaw 2026.2+
- Windows, macOS, Linux
