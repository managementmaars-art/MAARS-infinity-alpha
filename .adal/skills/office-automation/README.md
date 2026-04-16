# 📊 Office Automation Skill for OpenClaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange)](https://clawhub.ai)

> 自动化处理 Word 和 Excel 文件的 OpenClaw 技能  
> Automate Word and Excel document processing with OpenClaw

[English](#english) | [中文](#中文)

---

## 🌟 功能特点 / Features

- 📄 **Word 处理** - 读取、写入、模板填充、表格提取
- 📊 **Excel 处理** - 读取、写入、合并、转换、数据分析
- 🔄 **批量处理** - 批量生成文档、格式转换、数据提取
- 🤖 **AI 集成** - 与 OpenClaw 无缝集成，支持自然语言命令

---

## 🚀 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
pip install python-docx openpyxl pandas
```

### 测试脚本 / Test Scripts

```bash
# Word 测试 / Word Test
python scripts/word_processor.py write test.docx --content "Hello World" --title "Test"

# Excel 测试 / Excel Test
python scripts/excel_processor.py write test.xlsx --data '[["Name","Age"],["Alice",25]]' --headers "Name,Age"
```

---

## 📖 文档 / Documentation

| 文档 | 说明 |
|------|------|
| [使用指南](docs/使用指南.md) | 完整的使用教程和命令参考 |
| [示例集合](docs/示例集合.md) | 实战案例和代码示例 |
| [API 参考](references/office_api.md) | Python API 详细文档 |

---

## 💡 使用示例 / Usage Examples

### Word 模板填充

```bash
python scripts/word_processor.py template contract.docx \
  --output contract_filled.docx \
  --data '{"name":"张三","date":"2026-02-22"}'
```

### Excel 数据合并

```bash
python scripts/excel_processor.py merge ./reports/ --output all.xlsx
```

### 批量生成文档

```bash
python scripts/batch_processor.py templates \
  --folder ./output \
  --template invitation.docx \
  --data attendees.json
```

---

## 📁 项目结构 / Project Structure

```
office-automation/
├── SKILL.md                    # OpenClaw 技能定义
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
├── .gitignore                  # Git 忽略文件
├── scripts/
│   ├── word_processor.py       # Word 处理脚本
│   ├── excel_processor.py      # Excel 处理脚本
│   └── batch_processor.py      # 批量处理脚本
├── references/
│   └── office_api.md           # API 参考文档
├── docs/
│   ├── 使用指南.md             # 使用教程
│   └── 示例集合.md             # 示例代码
└── examples/
    └── sample_data.json        # 示例数据
```

---

## 🔧 脚本命令 / Script Commands

### word_processor.py

| 命令 | 说明 |
|------|------|
| `read <file>` | 读取文档内容 |
| `write <output> --content "文本"` | 创建新文档 |
| `template <文件> --output <输出> --data 'JSON'` | 填充模板 |
| `extract <文件> --table 0` | 提取表格到 CSV |

### excel_processor.py

| 命令 | 说明 |
|------|------|
| `read <file> --sheet Sheet1` | 读取 Excel |
| `write <output> --data 'JSON'` | 写入数据 |
| `merge <文件夹> --output <输出>` | 合并文件 |
| `convert <文件> --to csv/xlsx` | 格式转换 |
| `analyze <文件>` | 数据分析 |

### batch_processor.py

| 命令 | 说明 |
|------|------|
| `templates --folder --template --data` | 批量填充模板 |
| `convert --folder --from --to --output` | 批量转换格式 |
| `extract --folder --output` | 批量提取表格 |

---

## 🎯 实战案例 / Use Cases

### 1. 批量生成合同 / Batch Generate Contracts

```bash
python scripts/batch_processor.py templates \
  --folder ./contracts \
  --template contract_template.docx \
  --data clients.json
```

### 2. 月度报告合并 / Merge Monthly Reports

```bash
python scripts/excel_processor.py merge ./monthly_reports/ \
  --output yearly_report.xlsx
```

### 3. 数据提取与分析 / Extract and Analyze Data

```bash
# 提取 Word 表格
python scripts/word_processor.py extract report.docx

# 分析 Excel 数据
python scripts/excel_processor.py analyze sales.xlsx
```

---

## ⚠️ 注意事项 / Notes

1. **Word 格式** - 仅支持 .docx（不支持旧版 .doc）
2. **Excel 格式** - 支持 .xlsx 和 .xlsm
3. **编码** - CSV 文件使用 UTF-8-BOM 编码
4. **大文件** - 超过 100MB 建议分批次处理

---

## 🤝 与 OpenClaw 集成 / OpenClaw Integration

在 OpenClaw 聊天中直接使用：

```
请帮我读取 document.docx 的内容
从 data.xlsx 提取销售数据
批量生成 100 份合同，数据在 data.json 中
```

---

## 📄 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢 / Acknowledgments

- [OpenClaw](https://clawhub.ai) - AI 代理网关框架
- [python-docx](https://python-docx.readthedocs.io/) - Word 处理库
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel 处理库
- [pandas](https://pandas.pydata.org/) - 数据分析库

---

## 📮 联系方式 / Contact

- 🐛 问题反馈：GitHub Issues
- 💬 社区讨论：OpenClaw Discord
- 📚 更多技能：[ClawHub](https://clawhub.ai)

---

<div align="center">

**Made with ❤️ for OpenClaw Community**

[⬆ 返回顶部](#-office-automation-skill-for-openclaw)

</div>
