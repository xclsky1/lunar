import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import sys
import cnlunar  # 请确保已安装并导入 cnlunar 模块

class RedirectText:
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)

    def flush(self):
        pass  # This is a no-op for the interface

def on_confirm(date_entry, time_var, days_var, options_vars):
    # 清空前一次输出
    sys.stdout.output.delete(1.0, tk.END)

    selected_date = date_entry.get_date()
    selected_time = time_var.get()
    days_to_check = int(days_var.get())

    # 将日期和时间合并成一个 datetime 对象
    datetime_str = f"{selected_date} {selected_time}"
    selected_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

    # 用户选择的复选框选项
    selected_options = [var.get() for var in options_vars]
    selected_labels = ["出行", "宴会", "修造", "嫁娶", "纳采", "剃头", "诸事不宜"]

    no_matching_days = True

    # 显示所选日期未来几天的“宜”和“忌”
    for i in range(days_to_check):
        future_date = selected_datetime + timedelta(days=i)
        lunar_info = cnlunar.Lunar(future_date, godType='8char')

        matching_things = []

        # 如果有选择复选框，进行匹配
        if any(selected_options):
            for option, label in zip(selected_options, selected_labels):
                if option and any(label in good for good in lunar_info.goodThing):  # 确保匹配
                    matching_things.append(label)

            if not matching_things:
                continue  # 跳过当前日期的输出

            print(f"\n日期: {future_date.date()}")
            print('彭祖百忌:', lunar_info.get_pengTaboo())
            print('时辰凶吉:', lunar_info.get_twohourLuckyList())
            print(f"匹配: {', '.join(matching_things)} 适合在 {future_date.date()} 进行")
            no_matching_days = False
        else:
            # 如果没有选择复选框，按原样输出“宜”和“忌”
            print(f"\n日期: {future_date.date()}")
            print('彭祖百忌:', lunar_info.get_pengTaboo())
            print('时辰凶吉:', lunar_info.get_twohourLuckyList())
            print('宜:', lunar_info.goodThing)
            print('忌:', lunar_info.badThing)

    if no_matching_days:
        print(f"所选日期范围内没有适合的活动。")

def create_gui():
    # 创建主窗口
    root = tk.Tk()
    root.title("日期宜忌")
    root.geometry("700x550")  # 调整窗口高度以适应紧凑的第一行

    # 上半部分：日期输入
    frame_top = tk.Frame(root)
    frame_top.pack(fill=tk.X, padx=10, pady=5)

    # 使用 grid 布局管理器
    label_date = tk.Label(frame_top, text="输入日期：", width=10)
    label_date.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    date_entry = DateEntry(frame_top, width=12, year=datetime.now().year, month=datetime.now().month,
                           day=datetime.now().day, date_pattern='y-mm-dd')
    date_entry.grid(row=0, column=1, padx=5, pady=5)

    label_time = tk.Label(frame_top, text="选择时间：", width=10)
    label_time.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

    time_var = tk.StringVar(value=datetime.now().strftime("%H:%M:%S"))
    time_entry = ttk.Entry(frame_top, textvariable=time_var, width=10)
    time_entry.grid(row=0, column=3, padx=5, pady=5)

    label_days = tk.Label(frame_top, text="检查天数：", width=10)
    label_days.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

    days_var = tk.StringVar(value="15")
    days_entry = ttk.Entry(frame_top, textvariable=days_var, width=5)
    days_entry.grid(row=0, column=5, padx=5, pady=5)

    # 添加确认按钮
    confirm_button = ttk.Button(frame_top, text="确认",
                                command=lambda: on_confirm(date_entry, time_var, days_var, options_vars))
    confirm_button.grid(row=0, column=6, padx=5, pady=5)

    # 创建复选框
    options_frame = tk.Frame(root)
    options_frame.pack(fill=tk.X, padx=10, pady=1)

    options_vars = []
    labels = ["出行", "宴会", "修造", "嫁娶", "纳采", "剃头", "诸事不宜"]
    for idx, label in enumerate(labels):
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(options_frame, text=label, variable=var, width=6)
        checkbox.grid(row=0, column=idx, padx=5, pady=1)
        options_vars.append(var)

        # 新增的 "注意事项" Label
    label_notice = tk.Label(
        frame_top,
        text=(
            "注意事项：糸对《钦定协纪辨方书》中描述的农历每日宜忌规则进行了逻辑翻译,"
            "默认显示所选日期未来15天的宜忌、彭祖百忌、时辰凶吉 复选框为所选择的事项在所选天数范围所包含的项."
        ),
        wraplength=580,
        justify=tk.LEFT  # 明确指定左对齐，尽管这通常是默认值
    )
    label_notice.grid(row=1, column=0, columnspan=7, padx=5, pady=1, sticky=tk.W)


    # 下半部分：终端输出
    frame_bottom = tk.Frame(root)
    frame_bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)

    # 添加滚动条
    scrollbar = tk.Scrollbar(frame_bottom)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    terminal_output = tk.Text(frame_bottom, wrap='word', state=tk.NORMAL, yscrollcommand=scrollbar.set)
    terminal_output.pack(fill=tk.BOTH, expand=True)

    # 将滚动条绑定到文本框
    scrollbar.config(command=terminal_output.yview)

    # 重定向stdout和stderr到文本框
    sys.stdout = RedirectText(terminal_output)
    sys.stderr = RedirectText(terminal_output)

    # 示例输出
    print("将显示所选日期未来的宜忌")
    print(f"当前日期：{datetime.now().date()}，当前时间：{datetime.now().time()}")

    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    create_gui()
