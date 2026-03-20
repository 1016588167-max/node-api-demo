import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import openpyxl
import pdfplumber


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_\-.]+)\s*\}\}")


def normalize_key(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def parse_pdf_key_values(pdf_path: Path) -> dict:
    """Parse key-value pairs from PDF text.

    Supported patterns:
    - Key: Value
    - Key：Value (Chinese colon)
    """
    data = {}

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue

                for sep in (":", "："):
                    if sep in line:
                        key, value = line.split(sep, 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            data[normalize_key(key)] = value
                        break

    return data


def replace_placeholders_in_workbook(template_path: Path, output_path: Path, data: dict) -> int:
    wb = openpyxl.load_workbook(template_path)
    replaced_count = 0

    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    matches = PLACEHOLDER_PATTERN.findall(cell.value)
                    if not matches:
                        continue

                    new_value = cell.value
                    for key in matches:
                        normalized = normalize_key(key)
                        replacement = data.get(normalized, "")
                        placeholder = f"{{{{{key}}}}}"
                        new_value = new_value.replace(placeholder, replacement)
                    if new_value != cell.value:
                        replaced_count += 1
                    cell.value = new_value

    wb.save(output_path)
    return replaced_count


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF 自动录入 Excel")
        self.root.geometry("760x520")

        self.pdf_path = tk.StringVar()
        self.template_path = tk.StringVar()
        self.output_path = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="PDF 数据自动录入 Excel 工具", font=("Microsoft YaHei", 14, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        tip = (
            "模板 Excel 中需要使用占位符，例如 {{姓名}}、{{合同编号}}。\n"
            "程序会从 PDF 文本里提取“键:值”并填充。"
        )
        ttk.Label(container, text=tip, foreground="#444").pack(anchor="w", pady=(0, 12))

        self._file_picker_row(container, "PDF 文件", self.pdf_path, self.select_pdf)
        self._file_picker_row(container, "Excel 模板", self.template_path, self.select_template)
        self._file_picker_row(container, "输出 Excel", self.output_path, self.select_output)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=8)

        ttk.Button(btn_frame, text="开始处理", command=self.run).pack(side="left")
        ttk.Button(btn_frame, text="预览提取数据", command=self.preview_data).pack(side="left", padx=8)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(container, text="日志").pack(anchor="w")
        self.log = tk.Text(container, height=14)
        self.log.pack(fill="both", expand=True, pady=(6, 0))

    def _file_picker_row(self, parent, label, var, command):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)

        ttk.Label(row, text=label, width=10).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row, text="选择", command=command).pack(side="left")

    def select_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF 文件", "*.pdf")])
        if path:
            self.pdf_path.set(path)

    def select_template(self):
        path = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx")])
        if path:
            self.template_path.set(path)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel 文件", "*.xlsx")])
        if path:
            self.output_path.set(path)

    def _validate_inputs(self) -> bool:
        if not self.pdf_path.get() or not Path(self.pdf_path.get()).exists():
            messagebox.showerror("错误", "请选择有效的 PDF 文件")
            return False
        if not self.template_path.get() or not Path(self.template_path.get()).exists():
            messagebox.showerror("错误", "请选择有效的 Excel 模板")
            return False
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出文件路径")
            return False
        return True

    def _append_log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def preview_data(self):
        if not self.pdf_path.get() or not Path(self.pdf_path.get()).exists():
            messagebox.showerror("错误", "请先选择 PDF 文件")
            return

        try:
            data = parse_pdf_key_values(Path(self.pdf_path.get()))
            if not data:
                self._append_log("未解析到键值对，请检查 PDF 内容是否为“键:值”格式。")
                return
            pretty = json.dumps(data, ensure_ascii=False, indent=2)
            self._append_log("解析结果:\n" + pretty)
        except Exception as exc:
            messagebox.showerror("错误", f"预览失败: {exc}")

    def run(self):
        if not self._validate_inputs():
            return

        try:
            pdf = Path(self.pdf_path.get())
            template = Path(self.template_path.get())
            output = Path(self.output_path.get())

            self._append_log("开始解析 PDF...")
            data = parse_pdf_key_values(pdf)
            self._append_log(f"提取到 {len(data)} 个字段")

            self._append_log("开始填充 Excel 模板...")
            replaced = replace_placeholders_in_workbook(template, output, data)
            self._append_log(f"完成：已写入 {output}，替换单元格 {replaced} 处")
            messagebox.showinfo("完成", f"处理成功！输出文件：\n{output}")
        except Exception as exc:
            messagebox.showerror("失败", str(exc))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
