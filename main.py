import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys  # 必须导入sys来获取exe的真实路径
import time
import winsound
import random
from PIL import Image

# 设置外观模式
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --- 关键修复：路径管理函数 ---
def get_app_path():
    """获取程序运行的真实目录（解决打包后配置文件丢失的问题）"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe，使用 exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行，使用脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

def get_asset_path():
    """获取素材目录（素材打包在临时文件夹中，逻辑不同）"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "assets")

# 定义常量
APP_DIR = get_app_path()
ASSETS_PATH = get_asset_path()
CONFIG_FILE_PATH = os.path.join(APP_DIR, "app_config.json") # 配置文件一定要存在exe旁边

class TaskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FocusFlow Pro - 专注流")
        self.geometry("1000x700")
        self.after(10, lambda: self.state('zoomed'))

        # --- 1. 存储位置逻辑 (修复版) ---
        self.data_file_path = self.init_storage_location()
        
        # --- 加载素材 ---
        self.load_assets()

        # 数据初始化
        self.tasks = []
        self.active_task_index = None
        self.right_clicked_index = None 
        self.timer_running = False
        self.timer_seconds = 25 * 60
        self.is_break = False
        
        self.load_data()

        # 彩虹颜色盘
        self.rainbow_colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A8", 
            "#FFD700", "#00CED1", "#FF4500", "#8A2BE2",
            "#32CD32", "#4169E1", "#FF1493", "#00BFFF"
        ]

        # --- 布局配置 ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === 左侧面板 ===
        self.left_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(2, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(self.left_frame, text="My Tasks Mission", font=ctk.CTkFont(family="Impact", size=24))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # 添加任务区
        self.add_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.add_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        
        self.entry_task = ctk.CTkEntry(self.add_frame, placeholder_text="新任务名称...", height=35)
        self.entry_task.pack(fill="x", pady=(0, 8))
        
        self.entry_est = ctk.CTkEntry(self.add_frame, placeholder_text="预计分钟数", width=100)
        self.entry_est.pack(anchor="w", pady=(0, 8))
        
        self.btn_add = ctk.CTkButton(self.add_frame, text=" 创建任务", command=self.add_task, 
                                     image=self.icon_add, compound="left", height=40, font=("Arial", 14, "bold"))
        self.btn_add.pack(fill="x")

        # 任务列表区
        self.scroll_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="待办清单 (右键可修改)")
        self.scroll_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")

        # 左下角历史记录按钮
        self.history_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.history_frame.grid(row=3, column=0, padx=15, pady=20, sticky="ew")
        
        self.btn_history = ctk.CTkButton(self.history_frame, text=" 查看历史归档 (50条)", 
                                         fg_color="transparent", border_width=2, text_color=("gray10", "gray90"),
                                         command=self.open_history_window,
                                         image=self.icon_check, compound="left")
        self.btn_history.pack(fill="x")

        # === 右侧面板 ===
        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#242424"))
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # 顶部横幅
        self.banner_label = ctk.CTkLabel(self.right_frame, text="", image=self.banner_img)
        self.banner_label.pack(pady=(0, 20))

        # 计时器容器
        self.timer_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.timer_container.pack(expand=True, fill="both")

        # 动态彩虹文字区域
        self.welcome_text_frame = ctk.CTkFrame(self.timer_container, fg_color="transparent")
        self.welcome_text_frame.pack(pady=(80, 20), anchor="center")

        welcome_msg = "✨ 左侧添加你的任务，开始每天的进步吧 🚀"
        self.welcome_char_labels = []
        welcome_font = ctk.CTkFont(family="Microsoft YaHei UI", size=26, weight="bold")

        for char in welcome_msg:
            lbl = ctk.CTkLabel(self.welcome_text_frame, text=char, font=welcome_font)
            lbl.pack(side="left", padx=2) 
            self.welcome_char_labels.append(lbl)
        
        self.animate_welcome_text()

        # 计时器组件
        self.timer_label = ctk.CTkLabel(self.timer_container, text="25:00", font=ctk.CTkFont(family="Helvetica", size=90, weight="bold"), text_color="#3b82f6")
        
        self.status_label = ctk.CTkLabel(self.timer_container, text="准备好开始新的挑战了吗？", font=ctk.CTkFont(size=20))
        self.status_label.pack(pady=(10, 40))

        # 控制按钮
        self.btn_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent", height=100)
        self.btn_frame.pack(side="bottom", pady=40)

        self.btn_start = ctk.CTkButton(self.btn_frame, text=" 开始专注", width=160, height=55, 
                                       command=self.toggle_timer, state="disabled", 
                                       image=self.icon_play, compound="left", font=("Arial", 18, "bold"))
        self.btn_start.pack(side="left", padx=15)

        self.btn_finish = ctk.CTkButton(self.btn_frame, text=" 完成归档", width=160, height=55, 
                                        fg_color="#10b981", hover_color="#059669", 
                                        command=self.open_finish_dialog, state="disabled",
                                        image=self.icon_check, compound="left", font=("Arial", 18, "bold"))
        self.btn_finish.pack(side="left", padx=15)

        # --- 初始化右键菜单 ---
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="✏️ 修改/编辑任务", command=self.edit_selected_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 删除任务", command=self.delete_selected_task)

        # 启动
        self.refresh_task_list()
        self.timer_loop()

    # --- 修复后的存储位置初始化逻辑 ---
    def init_storage_location(self):
        # 1. 检查是否存在配置文件 (在exe旁边)
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_path = config.get("data_path")
                    # 如果配置里的文件夹存在，直接返回完整的文件路径
                    if saved_path and os.path.isdir(saved_path):
                        return os.path.join(saved_path, "tasks_data.json")
            except:
                pass # 如果配置文件坏了，重新询问

        # 2. 如果没有配置，询问用户
        messagebox.showinfo("欢迎使用 FocusFlow", "初次运行，请选择您的数据保存位置。\n\n如果不选择，将默认保存在【我的文档】中。")
        selected_dir = filedialog.askdirectory(title="选择数据保存文件夹")
        
        # 3. 如果用户点了取消，使用默认位置
        if not selected_dir:
            selected_dir = os.path.join(os.path.expanduser("~"), "Documents")
            # 如果连我的文档都找不到，就保存在 exe 旁边
            if not os.path.exists(selected_dir):
                selected_dir = APP_DIR
        
        # 4. 立即保存配置 (记住这个位置)
        try:
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({"data_path": selected_dir}, f)
        except Exception as e:
            messagebox.showerror("配置保存失败", f"无法保存配置文件: {e}")
            
        return os.path.join(selected_dir, "tasks_data.json")

    def load_assets(self):
        try:
            self.icon_add = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "icon_add.png")), size=(20, 20))
            self.icon_play = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "icon_play.png")), size=(24, 24))
            self.icon_check = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "icon_check.png")), size=(24, 24))
            self.banner_img = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "banner.jpg")), size=(800, 200)) 
        except Exception:
            self.icon_add = self.icon_play = self.icon_check = self.banner_img = None

    def animate_welcome_text(self):
        if self.welcome_text_frame.winfo_ismapped():
            for lbl in self.welcome_char_labels:
                rand_color = random.choice(self.rainbow_colors)
                lbl.configure(text_color=rand_color)
        self.after(250, self.animate_welcome_text)

    # --- 右键菜单 ---
    def show_context_menu(self, event, index):
        self.right_clicked_index = index
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def edit_selected_task(self):
        if self.right_clicked_index is None: return
        task = self.tasks[self.right_clicked_index]
        
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("修改任务")
        edit_win.geometry("400x250")
        edit_win.attributes("-topmost", True)
        edit_win.grab_set()

        ctk.CTkLabel(edit_win, text="任务名称:").pack(pady=(20, 5))
        entry_name = ctk.CTkEntry(edit_win, width=300)
        entry_name.pack(pady=5)
        entry_name.insert(0, task['title'])

        ctk.CTkLabel(edit_win, text="预计时间 (分钟):").pack(pady=(10, 5))
        entry_time = ctk.CTkEntry(edit_win, width=300)
        entry_time.pack(pady=5)
        entry_time.insert(0, str(task['est_time']))

        def save_edits():
            new_title = entry_name.get()
            new_est = entry_time.get()
            if new_title:
                self.tasks[self.right_clicked_index]['title'] = new_title
                try:
                    self.tasks[self.right_clicked_index]['est_time'] = int(new_est)
                except: pass
                self.save_data()
                self.refresh_task_list()
                
                if self.active_task_index == self.right_clicked_index:
                    t = self.tasks[self.active_task_index]
                    self.status_label.configure(text=f"正在攻克: {t['title']}\n已累计投入: {t['actual_time']} 分钟")
                
                edit_win.destroy()

        ctk.CTkButton(edit_win, text="保存修改", command=save_edits).pack(pady=20)

    def delete_selected_task(self):
        if self.right_clicked_index is None: return
        if messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
            if self.active_task_index == self.right_clicked_index and self.timer_running:
                self.timer_running = False
                self.btn_start.configure(text=" 开始专注")
                self.timer_label.pack_forget()
                self.welcome_text_frame.pack(pady=(80, 20), anchor="center")
            
            if self.active_task_index == self.right_clicked_index:
                self.active_task_index = None
                self.btn_start.configure(state="disabled")
                self.btn_finish.configure(state="disabled")
            elif self.active_task_index is not None and self.active_task_index > self.right_clicked_index:
                self.active_task_index -= 1

            del self.tasks[self.right_clicked_index]
            self.save_data()
            self.refresh_task_list()

    # --- 核心逻辑 ---

    def add_task(self):
        title = self.entry_task.get()
        est = self.entry_est.get()
        if not title: return
        try: est_time = int(est)
        except ValueError: est_time = 30
        
        new_task = {
            "title": title, "est_time": est_time, "actual_time": 0, 
            "status": "todo", "completion_rate": 0, "remarks": "",
            "timestamp": int(time.time())
        }
        self.tasks.append(new_task)
        self.save_data()
        self.entry_task.delete(0, "end")
        self.entry_est.delete(0, "end")
        self.refresh_task_list()

    def select_task(self, index):
        if self.timer_running:
            messagebox.showwarning("提示", "请先暂停当前计时器")
            return

        self.active_task_index = index
        task = self.tasks[index]
        
        self.welcome_text_frame.pack_forget()
        self.timer_label.pack(pady=(20, 10))

        self.status_label.configure(text=f"正在攻克: {task['title']}\n已累计投入: {task['actual_time']} 分钟")
        self.btn_start.configure(state="normal")
        self.btn_finish.configure(state="normal")
        
        self.timer_seconds = 25 * 60
        self.is_break = False
        self.update_timer_display()
        self.refresh_task_list()

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.btn_start.configure(text=" 继续专注")
        else:
            self.timer_running = True
            self.btn_start.configure(text=" 暂停计时")

    def timer_loop(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            if not self.is_break and self.active_task_index is not None and self.timer_seconds % 60 == 0:
                self.tasks[self.active_task_index]['actual_time'] += 1
                self.save_data() 
                t = self.tasks[self.active_task_index]
                self.status_label.configure(text=f"正在攻克: {t['title']}\n已累计投入: {t['actual_time']} 分钟")
        elif self.timer_running and self.timer_seconds == 0:
            self.timer_running = False
            self.timer_finished()
        self.after(1000, self.timer_loop)

    def update_timer_display(self):
        mins, secs = divmod(self.timer_seconds, 60)
        self.timer_label.configure(text=f"{mins:02}:{secs:02}")

    def timer_finished(self):
        winsound.Beep(1000, 500)
        if not self.is_break:
            ans = messagebox.askyesno("Nice Work!", "番茄钟完成！休息5分钟？")
            if ans:
                self.is_break = True
                self.timer_seconds = 5 * 60
                self.status_label.configure(text="☕ 休息时间")
                self.btn_start.configure(text=" 开始休息")
            else:
                self.btn_start.configure(text=" 开始专注")
        else:
            messagebox.showinfo("Ready?", "休息结束，准备开始工作！")
            self.is_break = False
            self.timer_seconds = 25 * 60
            self.btn_start.configure(text=" 开始专注")
        self.update_timer_display()

    def open_finish_dialog(self):
        if self.active_task_index is None: 
            messagebox.showwarning("错误", "当前没有选中的任务！")
            return
        
        self.timer_running = False
        self.dialog = ctk.CTkToplevel(self)
        self.dialog.title("Mission Complete!")
        self.dialog.geometry("450x480")
        self.dialog.attributes("-topmost", True) 

        try:
             header_img = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "banner.jpg")), size=(450, 80))
             ctk.CTkLabel(self.dialog, text="", image=header_img).pack()
        except: pass

        ctk.CTkLabel(self.dialog, text="本次任务完成度评估", font=("Arial", 16, "bold")).pack(pady=(20,10))
        slider_val = ctk.IntVar(value=100)
        lbl_val = ctk.CTkLabel(self.dialog, text="100%", font=("Arial", 20, "bold"), text_color="#10b981")
        lbl_val.pack()
        
        def update_val(val): lbl_val.configure(text=f"{int(val)}%")
        slider = ctk.CTkSlider(self.dialog, from_=0, to=100, variable=slider_val, command=update_val, width=300, progress_color="#10b981")
        slider.pack(pady=5)

        ctk.CTkLabel(self.dialog, text="复盘备注 (可选)", font=("Arial", 14)).pack(pady=(20, 5))
        textbox = ctk.CTkTextbox(self.dialog, height=80, border_width=2)
        textbox.pack(padx=30, fill="x")

        def save_complete():
            try:
                if self.active_task_index is None or self.active_task_index >= len(self.tasks):
                    messagebox.showerror("错误", "任务数据异常")
                    self.dialog.destroy()
                    return

                task = self.tasks[self.active_task_index]
                task['status'] = 'completed'
                task['completion_rate'] = int(slider.get())
                task['remarks'] = textbox.get("1.0", "end-1c")
                
                self.active_task_index = None
                self.save_data()
                self.refresh_task_list()
                
                self.timer_label.pack_forget()
                self.welcome_text_frame.pack(pady=(80, 20), anchor="center")
                self.status_label.configure(text="准备好开始新的挑战了吗？")
                self.btn_start.configure(state="disabled", text=" 开始专注")
                self.btn_finish.configure(state="disabled")
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("保存失败", f"错误: {str(e)}")

        ctk.CTkButton(self.dialog, text="确认归档任务", command=save_complete, 
                      height=45, fg_color="#10b981", hover_color="#059669", font=("Arial", 16, "bold")).pack(pady=30)
        
        self.dialog.grab_set() 
        self.dialog.focus_force()

    def open_history_window(self):
        history_win = ctk.CTkToplevel(self)
        history_win.title("历史归档记录")
        history_win.geometry("600x600")
        history_win.attributes("-topmost", True)
        
        ctk.CTkLabel(history_win, text="已完成任务 (最近50条)", font=("Arial", 20, "bold")).pack(pady=15)
        scroll = ctk.CTkScrollableFrame(history_win)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        completed_tasks = [t for t in self.tasks if t.get('status') == 'completed']
        completed_tasks.reverse() 
        if not completed_tasks:
            ctk.CTkLabel(scroll, text="暂无已完成任务", text_color="gray").pack(pady=50)
            return

        for task in completed_tasks[:50]:
            card = ctk.CTkFrame(scroll, fg_color=("white", "#333333"), corner_radius=10)
            card.pack(fill="x", pady=5)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 5))
            
            # 长文本自动换行
            ctk.CTkLabel(top_row, text=task['title'], font=("Arial", 16, "bold"), wraplength=350, justify="left").pack(side="left")
            
            rate = task.get('completion_rate', 0)
            color = "#10b981" if rate >= 80 else "#f59e0b" if rate >= 50 else "#ef4444"
            ctk.CTkLabel(top_row, text=f"{rate}% 完成", text_color=color, font=("Arial", 14, "bold")).pack(side="right")
            
            mid_row = ctk.CTkLabel(card, text=f"预计: {task.get('est_time',0)}m  |  实际投入: {task.get('actual_time',0)}m", 
                                   font=("Arial", 12), text_color="gray")
            mid_row.pack(anchor="w", padx=10)
            
            if task.get('remarks') and len(task['remarks'].strip()) > 0:
                remark_lbl = ctk.CTkLabel(card, text=f"📝: {task['remarks'].strip()}", 
                                          font=("Arial", 12, "italic"), text_color=("gray30", "gray70"), wraplength=500, justify="left")
                remark_lbl.pack(anchor="w", padx=10, pady=(5, 10))
            else:
                 ctk.CTkFrame(card, height=5, fg_color="transparent").pack()

    def refresh_task_list(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        
        for i, task in enumerate(self.tasks):
            if task.get('status') == 'completed': continue
            
            color = "transparent"
            if i == self.active_task_index: color = ("#e5e7eb", "#374151")
            
            frame = ctk.CTkFrame(self.scroll_frame, fg_color=color, corner_radius=8)
            frame.pack(fill="x", pady=3, padx=2)
            
            # 长文本自动换行
            title_lbl = ctk.CTkLabel(frame, text=f"{task['title']}", font=("Arial", 15, "bold"), 
                                     wraplength=240, justify="left")
            title_lbl.pack(anchor="w", padx=10, pady=(8,0))
            
            info_lbl = ctk.CTkLabel(frame, text=f"🕒 预计 {task['est_time']}m | 🔥 已用 {task['actual_time']}m", font=("Arial", 12), text_color="gray")
            info_lbl.pack(anchor="w", padx=10, pady=(0,8))
            
            title_lbl.bind("<Button-1>", lambda e, idx=i: self.select_task(idx))
            info_lbl.bind("<Button-1>", lambda e, idx=i: self.select_task(idx))
            frame.bind("<Button-1>", lambda e, idx=i: self.select_task(idx))

            # 右键菜单
            title_lbl.bind("<Button-3>", lambda e, idx=i: self.show_context_menu(e, idx))
            info_lbl.bind("<Button-3>", lambda e, idx=i: self.show_context_menu(e, idx))
            frame.bind("<Button-3>", lambda e, idx=i: self.show_context_menu(e, idx))

    def save_data(self):
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e: 
            messagebox.showerror("保存失败", f"无法保存数据: {e}")

    def load_data(self):
        if os.path.exists(self.data_file_path):
            try:
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except: self.tasks = []
        else:
            self.tasks = []

if __name__ == "__main__":
    app = TaskApp()
    app.mainloop()