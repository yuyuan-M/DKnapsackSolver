# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import sys

# 导入其他模块
from data_parser import parse_knapsack_file
from solver import solve_dp_with_selection
from plotter import plot_scatter

class DKnapsackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D{0-1}KP 求解器")
        self.root.geometry("850x650")

        # 当前数据
        self.current_data = None
        self.current_filename = None
        self.instances = []               # 解析出的所有实例
        self.current_instance_index = 0

        # 存储最近求解结果
        self.last_result = None           # (best_val, elapsed, mode)
        self.last_selection = None
        self.last_sorted_flag = False
        self.last_solved_data = None

        self.create_widgets()

    def create_widgets(self):
        # 菜单栏
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开数据文件", command=self.load_file)
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件信息区域
        info_frame = ttk.LabelFrame(main_frame, text="文件信息", padding="5")
        info_frame.pack(fill=tk.X, pady=5)

        self.file_label = ttk.Label(info_frame, text="未加载文件")
        self.file_label.pack(anchor=tk.W)

        # 实例选择区域
        instance_frame = ttk.LabelFrame(main_frame, text="实例选择", padding="5")
        instance_frame.pack(fill=tk.X, pady=5)

        self.instance_combo = ttk.Combobox(instance_frame, state="readonly")
        self.instance_combo.pack(fill=tk.X, pady=5)
        self.instance_combo.bind("<<ComboboxSelected>>", self.on_instance_selected)

        # 数据显示区域
        data_frame = ttk.LabelFrame(main_frame, text="实例数据", padding="5")
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.data_text = tk.Text(data_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=scrollbar.set)
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.plot_btn = ttk.Button(button_frame, text="绘制散点图", command=self.plot_data, state=tk.DISABLED)
        self.plot_btn.pack(side=tk.LEFT, padx=5)

        self.sort_btn = ttk.Button(button_frame, text="按第三项价值/重量比排序", command=self.sort_data, state=tk.DISABLED)
        self.sort_btn.pack(side=tk.LEFT, padx=5)

        self.solve_btn = ttk.Button(button_frame, text="求解（未排序）", command=lambda: self.solve(False), state=tk.DISABLED)
        self.solve_btn.pack(side=tk.LEFT, padx=5)

        self.solve_sorted_btn = ttk.Button(button_frame, text="求解（排序后）", command=lambda: self.solve(True), state=tk.DISABLED)
        self.solve_sorted_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(button_frame, text="导出结果", command=self.export_result, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="求解结果", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
        scrollbar_res = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar_res.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_res.pack(side=tk.RIGHT, fill=tk.Y)

        # 状态栏
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("就绪")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        self.status_var.set("正在解析文件...")
        try:
            self.instances = parse_knapsack_file(file_path)
            if not self.instances:
                messagebox.showerror("错误", "文件中未找到有效实例")
                return
            self.current_filename = os.path.basename(file_path)
            self.file_label.config(text=f"文件: {self.current_filename}，共 {len(self.instances)} 个实例")
            # 更新实例下拉框
            instance_names = [inst.name for inst in self.instances]
            self.instance_combo['values'] = instance_names
            self.instance_combo.current(0)
            self.current_instance_index = 0
            self.current_data = self.instances[0]
            self.display_instance_data()
            self.enable_buttons(True)
            self.status_var.set("文件加载成功")
        except Exception as e:
            messagebox.showerror("错误", f"解析文件失败:\n{str(e)}")
            self.status_var.set("加载失败")

    def on_instance_selected(self, event):
        idx = self.instance_combo.current()
        if idx >= 0:
            self.current_instance_index = idx
            self.current_data = self.instances[idx]
            self.display_instance_data()
            # 清空结果区域
            self.result_text.delete(1.0, tk.END)
            self.last_result = None
            self.last_selection = None

    def display_instance_data(self):
        """显示当前实例的基本数据"""
        data = self.current_data
        info = (f"实例名称: {data.name}\n"
                f"项集数量: {data.n_sets}\n"
                f"背包容量: {data.capacity}\n"
                f"物品总数: {data.n_sets * 3}\n")
        # 可加价值/重量范围
        all_vals = [v for s in data.item_sets for v in (s.items[0].value, s.items[1].value, s.items[2].value)]
        all_weights = [w for s in data.item_sets for w in (s.items[0].weight, s.items[1].weight, s.items[2].weight)]
        info += f"价值范围: {min(all_vals)} - {max(all_vals)}\n"
        info += f"重量范围: {min(all_weights)} - {max(all_weights)}\n"
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, info)

    def enable_buttons(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.plot_btn.config(state=state)
        self.sort_btn.config(state=state)
        self.solve_btn.config(state=state)
        self.solve_sorted_btn.config(state=state)
        self.export_btn.config(state=state)

    def plot_data(self):
        if self.current_data:
            threading.Thread(target=plot_scatter, args=(self.current_data, self.current_data.name), daemon=True).start()

    def sort_data(self):
        if self.current_data:
            self.current_data.sort_by_ratio()
            self.display_instance_data()
            self.status_var.set("已按第三项价值/重量比排序")

    def solve(self, sorted_flag):
        if not self.current_data:
            return
        self.status_var.set("正在求解...")
        # 禁用按钮避免重复操作
        self.solve_btn.config(state=tk.DISABLED)
        self.solve_sorted_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)

        def solve_task():
            try:
                best_val, selection, elapsed = solve_dp_with_selection(self.current_data, sorted_flag)
                self.root.after(0, self.display_solution, best_val, elapsed, sorted_flag, selection)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("求解错误", str(e)))
            finally:
                self.root.after(0, lambda: self.solve_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.solve_sorted_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_var.set("求解完成"))

        threading.Thread(target=solve_task, daemon=True).start()

    def display_solution(self, best_val, elapsed, sorted_flag, selection):
        self.last_selection = selection
        self.last_sorted_flag = sorted_flag
        self.last_solved_data = self.current_data
        mode = "排序后" if sorted_flag else "未排序"
        text = f"求解模式: {mode}\n最优值: {best_val}\n耗时: {elapsed:.2f} ms\n"
        text += f"已选择物品数量: {sum(1 for s in selection if s != 0)}\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.last_result = (best_val, elapsed, mode)

    def export_result(self):
        if not hasattr(self, 'last_result') or self.last_selection is None:
            messagebox.showinfo("提示", "请先求解")
            return

        best_val, elapsed, mode = self.last_result
        selection = self.last_selection
        data = self.last_solved_data

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if not file_path:
            return

        try:
            if file_path.endswith('.xlsx'):
                # 导出为 Excel 文件
                try:
                    from openpyxl import Workbook
                except ImportError:
                    messagebox.showerror("错误", "未安装 openpyxl，请执行：pip install openpyxl")
                    return
                wb = Workbook()
                ws = wb.active
                ws.title = "求解结果"
                ws.append(["实例名称", data.name])
                ws.append(["求解模式", mode])
                ws.append(["最优值", best_val])
                ws.append(["求解时间(ms)", f"{elapsed:.2f}"])
                ws.append([])
                ws.append(["项集编号", "所选物品编号", "重量", "价值"])
                for i, choice in enumerate(selection):
                    if choice == 0:
                        ws.append([i+1, "不选", "-", "-"])
                    else:
                        item = data.item_sets[i].items[choice-1]
                        ws.append([i+1, choice, item.weight, item.value])
                wb.save(file_path)
            else:
                # 导出为 TXT 文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"实例名称: {data.name}\n")
                    f.write(f"求解模式: {mode}\n")
                    f.write(f"最优值: {best_val}\n")
                    f.write(f"求解时间: {elapsed:.2f} ms\n\n")
                    f.write("详细解结果（每个项集的选择）:\n")
                    f.write("项集编号\t所选物品编号\t重量\t价值\n")
                    for i, choice in enumerate(selection):
                        if choice == 0:
                            f.write(f"{i+1}\t不选\t-\t-\n")
                        else:
                            item = data.item_sets[i].items[choice-1]
                            f.write(f"{i+1}\t{choice}\t{item.weight}\t{item.value}\n")
            self.status_var.set(f"结果已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))