# 测试数据文件说明

本目录包含多数据源联合分析的测试数据文件。

---

## 文件清单

### CSV 文件

| 文件名 | 行数 | 说明 |
|--------|------|------|
| `regional_sales.csv` | 6 | 区域销售目标数据（6大区2024年销售目标与实际） |
| `sales_associates_performance.csv` | 10 | 销售人员绩效数据（销售代表姓名、区域、绩效分数、月销售额） |
| `customer_satisfaction.csv` | 8 | 客户满意度调查数据（客户ID、满意度评分、NPS评分、反馈类别） |

### JSON 文件

| 文件名 | 行数 | 说明 |
|--------|------|------|
| `product_categories.json` | 5 | 产品分类数据（分类ID、名称、目标利润率、库存周转天数） |

### Excel 文件

| 工作表 | 行数 | 说明 |
|--------|------|------|
| `Marketing Campaigns` | 5 | 营销活动数据（活动ID、名称、预算、花费、展示量、点击量、转化量） |
| `Product Inventory` | 8 | 产品库存数据（产品ID、名称、分类、成本、售价、库存数量、补货点、供应商ID） |
| `Suppliers` | 5 | 供应商数据（供应商ID、名称、国家、交货天数、质量评分、合同开始日期） |

### Parquet 文件

| 文件名 | 行数 | 说明 |
|--------|------|------|
| `sales_history.parquet` | 1000 | 销售历史交易数据（交易ID、日期、产品ID、地区、销售额、数量、客户ID） |
| `user_behavior.parquet` | 500 | 用户行为数据（用户ID、会话ID、页面浏览量、会话时长、跳出率、设备类型、流量来源、转化标志） |
| `inventory_snapshot.parquet` | 300 | 产品库存快照（SKU、产品名、仓库、库存水平、补货点、最近补货日期、单位成本、类别） |
| `web_logs.parquet` | 2000 | 网站访问日志（日志ID、时间戳、IP地址、端点、状态码、响应时间、用户代理） |

---

## 使用示例

```python
from multi_source_analyzer import MultiSourceAnalyzer

analyzer = MultiSourceAnalyzer()

# 注册 CSV 文件
analyzer.register_file('sales', 'data/regional_sales.csv')

# 注册 Excel 文件的特定工作表
analyzer.register_file('products', 'data/business_data.xlsx', sheet='Product Inventory')
analyzer.register_file('suppliers', 'data/business_data.xlsx', sheet='Suppliers')

# 注册 Parquet 文件
analyzer.register_file('sales_history', 'data/sales_history.parquet')

# 执行跨文件查询
result = analyzer.query("""
    SELECT 
        p.product_name,
        p.unit_price - p.unit_cost as margin,
        s.supplier_name
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.supplier_id
""")
```
