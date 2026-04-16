# Office API 参考

## Python 库

### python-docx (Word 处理)

**安装：**
```bash
pip install python-docx
```

**常用操作：**

```python
from docx import Document
from docx.shared import Inches, Pt

# 创建文档
doc = Document()
doc.add_heading('标题', 0)
doc.add_paragraph('正文内容')
doc.save('output.docx')

# 读取文档
doc = Document('input.docx')
for para in doc.paragraphs:
    print(para.text)

# 添加表格
table = doc.add_table(rows=3, cols=3)
table.cell(0, 0).text = '单元格内容'

# 设置格式
paragraph = doc.add_paragraph()
run = paragraph.add_run('加粗文本')
run.bold = True
run.font.size = Pt(12)
```

**文档：** https://python-docx.readthedocs.io/

---

### openpyxl (Excel 处理)

**安装：**
```bash
pip install openpyxl
```

**常用操作：**

```python
from openpyxl import Workbook, load_workbook

# 创建工作簿
wb = Workbook()
ws = wb.active
ws['A1'] = '数据'
ws.append([1, 2, 3])
wb.save('output.xlsx')

# 读取工作簿
wb = load_workbook('input.xlsx', data_only=True)
ws = wb['Sheet1']
for row in ws.iter_rows(values_only=True):
    print(row)

# 设置样式
from openpyxl.styles import Font, Alignment
ws['A1'].font = Font(bold=True)
ws['A1'].alignment = Alignment(horizontal='center')
```

**文档：** https://openpyxl.readthedocs.io/

---

### pandas (数据分析)

**安装：**
```bash
pip install pandas
```

**常用操作：**

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# 数据筛选
filtered = df[df['column'] > 100]

# 数据统计
stats = df.describe()

# 数据透视
pivot = df.pivot_table(values='value', index='row', columns='col', aggfunc='sum')

# 导出
df.to_excel('output.xlsx', index=False)
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
```

**文档：** https://pandas.pydata.org/docs/

---

## 模板变量格式

Word 模板使用 `{{变量名}}` 格式：

```
合同编号：{{contract_number}}
甲方：{{party_a}}
乙方：{{party_b}}
日期：{{date}}
```

JSON 数据格式：
```json
[
  {
    "contract_number": "HT2026001",
    "party_a": "甲公司",
    "party_b": "乙公司",
    "date": "2026-02-22",
    "filename": "合同_001.docx"
  }
]
```

---

## 常见问题

### Q: 支持 .doc 格式吗？
A: 不支持。python-docx 只支持 .docx 格式。旧版 .doc 需要先用 Word 另存为 .docx。

### Q: Excel 宏 (.xlsm) 支持吗？
A: openpyxl 可以读取 .xlsm 文件，但不会保留宏代码。

### Q: 如何处理大文件？
A: 使用 pandas 的 `chunksize` 参数分块读取，或直接用 openpyxl 的 `iter_rows()`。

### Q: 中文乱码怎么办？
A: 确保使用 `encoding='utf-8-sig'` 保存 CSV 文件。

---

## 脚本命令速查

### word_processor.py
```bash
# 读取
python word_processor.py read file.docx

# 写入
python word_processor.py write out.docx --content "内容" --title "标题"

# 模板填充
python word_processor.py template doc.docx --output out.docx --data '{"key": "value"}'

# 提取表格
python word_processor.py extract file.docx --table 0 --output-dir ./csv
```

### excel_processor.py
```bash
# 读取
python excel_processor.py read data.xlsx --sheet Sheet1

# 写入
python excel_processor.py write out.xlsx --data '[["a","b"],["1","2"]]' --headers "col1,col2"

# 合并
python excel_processor.py merge ./files/ --output all.xlsx

# 转换
python excel_processor.py convert file.xlsx --to csv

# 分析
python excel_processor.py analyze sales.xlsx --pivot
```

### batch_processor.py
```bash
# 批量填充模板
python batch_processor.py templates --folder ./output --template template.docx --data data.json

# 批量转换
python batch_processor.py convert --folder ./input --from xlsx --to csv --output ./output

# 批量提取表格
python batch_processor.py extract --folder ./docs --output ./tables
```
