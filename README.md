# PDF 自动录入 Excel（可打包 EXE）

这是一个桌面小工具：
- 从 PDF 中提取 `键:值` 数据（支持英文冒号 `:` 和中文冒号 `：`）。
- 将数据自动填充到 Excel 模板中的占位符。

## 1. 模板规则

在模板 `.xlsx` 里写占位符，例如：

- `{{姓名}}`
- `{{合同编号}}`
- `客户：{{客户名称}}`

程序会按占位符名字查找 PDF 中的键值对并替换。

## 2. PDF 数据格式建议

PDF 文本建议包含如下格式行：

- `姓名: 张三`
- `合同编号：HT2026-001`
- `客户名称: 北京某某科技有限公司`

> 注意：如果 PDF 是纯图片扫描件，没有可复制文本，需要先 OCR。

## 3. 本地运行

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 请用 .venv\Scripts\activate
pip install -r requirements.txt
python pdf_to_excel_app.py
```

## 4. 打包成 Windows EXE

> 建议在 Windows 上执行以下命令进行打包。

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name PDFExcelAutoFill pdf_to_excel_app.py
```

打包后 EXE 位于：

- `dist/PDFExcelAutoFill.exe`

## 5. 使用流程

1. 打开程序。
2. 选择 PDF 文件。
3. 选择 Excel 模板。
4. 选择输出 Excel 路径。
5. 点击「开始处理」。

## 6. 适配你的模板

如果你有固定的 PDF 版式或更复杂规则（例如多行表格、多 PDF 合并、按行写入明细表），可以在当前脚本上继续扩展解析逻辑。

## 7. 导出程序工程包

在项目根目录执行：

```bash
zip -r pdf-excel-autofill-project.zip README.md pdf_to_excel_app.py requirements.txt
```

会生成工程包：`pdf-excel-autofill-project.zip`。
