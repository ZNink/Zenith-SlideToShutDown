import os
import sys
import time
import json
import threading
from pynput import mouse
from ctypes import windll
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from PIL import Image
import winreg

# 获取屏幕尺寸
user32 = windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# 配置文件路径
appdata_path = os.path.join(os.environ['APPDATA'], 'Zenith')
config_path = os.path.join(appdata_path, 'config.json')

# 默认配置
default_config = {
    'SLIDE_THRESHOLD': screen_height * 0.3,
    'SLIDE_DISTANCE': 100,
    'AUTO_START': True  # 开机自启，默认为开启
}

# 初始化变量
start_y = None
is_sliding = False
start_time = None
slide_to_shutdown = r"SlideToShutDown.exe"

# 全局变量
config = default_config.copy()
running = False
listener = None
tray_icon = None

# 动态获取当前脚本的目录
def resource_path(relative_path):
    """获取资源文件的绝对路径，适用于PyInstaller打包后的可执行文件"""
    try:
        # PyInstaller创建的临时目录
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 图标文件路径
icon_path = resource_path("icon.png")

# 保存配置到文件
def save_config():
    os.makedirs(appdata_path, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

# 从文件加载配置
def load_config():
    global config
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                config = {**default_config, **loaded_config}
        except:
            # 如果加载失败，使用默认配置
            config = default_config.copy()
    else:
        # 如果配置文件不存在，创建一个
        save_config()

# 设置开机自启
def set_auto_start(enable):
    # 获取当前脚本的绝对路径
    exe_path = sys.executable
    
    # 打开注册表项
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    
    if enable:
        # 添加开机自启项
        winreg.SetValueEx(key, "Zenith", 0, winreg.REG_SZ, exe_path)
    else:
        # 删除开机自启项
        try:
            winreg.DeleteValue(key, "Zenith")
        except FileNotFoundError:
            pass
    
    winreg.CloseKey(key)

# 鼠标事件处理
def on_move(x, y):
    global start_y, is_sliding, start_time
    
    if start_y is not None and is_sliding:
        # 计算滑动距离
        distance = y - start_y
        print(f"滑动距离: {distance} 像素")
        
        # 检查滑动方向
        if distance <= 0:
            try:
                print("滑动方向错误")
            except Exception as e:
                print(f"调用SlideToShutDown.exe时出错: {e}")
        elif distance >= config['SLIDE_DISTANCE']:
            subprocess.Popen([slide_to_shutdown], shell=True)
            print("SlideToShutDown.exe 已调用")
            distance = 0
            start_y = None
            is_sliding = False
            start_time = None

def on_click(x, y, button, pressed):
    global start_y, is_sliding, start_time
    
    if button == mouse.Button.right:
        if pressed:
            # 检查是否在屏幕顶部区域
            if y <= config['SLIDE_THRESHOLD']:
                start_y = y
                is_sliding = True
                start_time = time.time()
                print(f"开始滑动，起始位置: ({x}, {y})")
        else:
            # 鼠标右键释放
            start_y = None
            is_sliding = False
            start_time = None
            print("滑动已取消")

# 启动鼠标监听器
def start_listener():
    global listener, running
    if not running:
        running = True
        listener = mouse.Listener(on_move=on_move, on_click=on_click)
        listener.start()
        print("鼠标滑动监听已启动")

# 停止鼠标监听器
def stop_listener():
    global listener, running
    if running:
        running = False
        if listener:
            listener.stop()
            listener = None
            print("鼠标滑动监听已停止")

# GUI部分
class ZenithApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zenith - 滑动关机")
        self.root.geometry("400x630")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 加载图标
        if not os.path.exists(icon_path):
            messagebox.showerror("错误", "未找到icon.png文件")
            sys.exit(1)
        
        try:
            self.icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, self.icon)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载icon.png文件: {e}")
            sys.exit(1)
        
        # 创建托盘图标
        self.create_tray_icon()
        
        # 加载配置
        load_config()
        
        # 创建GUI组件
        self.create_widgets()
        
        # 启动监听器
        self.listener_thread = threading.Thread(target=start_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def create_tray_icon(self):
        global tray_icon
        
        # 加载图标
        try:
            image = Image.open(icon_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载icon.png文件: {e}")
            sys.exit(1)
        
        # 创建托盘菜单
        menu = (
            pystray.MenuItem('显示窗口', self.show_window),
            pystray.MenuItem('退出', self.on_close),
        )
        
        # 创建托盘图标
        tray_icon = pystray.Icon("Zenith", image, "Zenith - 滑动关机", menu)
        
        # 启动托盘图标线程
        self.tray_thread = threading.Thread(target=self.run_tray_icon)
        self.tray_thread.daemon = True
        self.tray_thread.start()

    def run_tray_icon(self):
        global tray_icon
        try:
            tray_icon.run()
        except Exception as e:
            messagebox.showerror("错误", f"无法启动托盘图标: {e}")
            sys.exit(1)

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.root, text="Zenith - 滑动关机", font=("Microsoft YaHei UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # 滑动区域设置
        threshold_frame = ttk.LabelFrame(self.root, text="滑动区域 (占屏幕的 %)")
        threshold_frame.pack(fill="x", padx=20, pady=10)
        
        self.threshold_var = tk.DoubleVar(value=(config['SLIDE_THRESHOLD'] / screen_height) * 100)
        threshold_scale = ttk.Scale(
            threshold_frame,
            from_=10,
            to=100,
            orient="horizontal",
            variable=self.threshold_var,
            command=self.update_threshold
        )
        threshold_scale.pack(fill="x", padx=10, pady=5)
        
        # 滑动区域数值显示
        self.threshold_label = ttk.Label(threshold_frame, text=f"当前: {int(self.threshold_var.get())}%")
        self.threshold_label.pack(pady=5)
        
        # 滑动距离设置
        distance_frame = ttk.LabelFrame(self.root, text="滑动距离 (像素)")
        distance_frame.pack(fill="x", padx=20, pady=10)
        
        self.distance_var = tk.IntVar(value=config['SLIDE_DISTANCE'])
        distance_scale = ttk.Scale(
            distance_frame,
            from_=50,
            to=screen_height,
            orient="horizontal",
            variable=self.distance_var,
            command=self.update_distance
        )
        distance_scale.pack(fill="x", padx=10, pady=5)
        
        # 滑动距离数值显示
        self.distance_label = ttk.Label(distance_frame, text=f"当前: {self.distance_var.get()} 像素")
        self.distance_label.pack(pady=5)
        
        # 开机自启选项
        autostart_frame = ttk.LabelFrame(self.root, text="开机自启")
        autostart_frame.pack(fill="x", padx=20, pady=10)
        
        self.autostart_var = tk.BooleanVar(value=config.get('AUTO_START', default_config['AUTO_START']))
        
        # 确保复选框被正确创建并添加到界面中
        autostart_check = ttk.Checkbutton(
            autostart_frame,
            text="开机自启",
            variable=self.autostart_var,
            command=self.update_autostart
        )
        autostart_check.pack(pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        start_button = ttk.Button(button_frame, text="启动", command=self.start_listening)
        start_button.pack(side="left", padx=5)
        
        stop_button = ttk.Button(button_frame, text="停止", command=self.stop_listening)
        stop_button.pack(side="left", padx=5)
        
        # 提示信息
        info_frame = ttk.LabelFrame(self.root, text="使用说明")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        info_text = """
        1. 点击"停止"按钮停止监听
        2. 点击"启动"按钮继续监听
        3. 将鼠标移到屏幕顶部区域（由"滑动区域"设置决定）
        4. 按住鼠标右键并向下拖动
        5. 拖动距离达到"滑动距离"后，将启动滑动关机页面
        6. 点击托盘图标可以显示或退出程序
        
        Zenith by ZNi
        """
        info_label = ttk.Label(info_frame, text=info_text, justify="left")
        info_label.pack(padx=10, pady=10)

    def update_threshold(self, value):
        global config
        value = float(value)
        config['SLIDE_THRESHOLD'] = int((value / 100) * screen_height)
        save_config()
        self.threshold_label.config(text=f"当前: {int(value)}%")

    def update_distance(self, value):
        global config
        value = int(float(value))
        config['SLIDE_DISTANCE'] = value
        save_config()
        self.distance_label.config(text=f"当前: {value} 像素")

    def update_autostart(self):
        global config
        config['AUTO_START'] = self.autostart_var.get()
        save_config()
        set_auto_start(config['AUTO_START'])
        if config['AUTO_START']:
            print("已启用开机自启")
        else:
            print("已禁用开机自启")

    def start_listening(self):
        start_listener()
        print("已启动监听")

    def stop_listening(self):
        stop_listener()
        print("已停止监听")

    def show_window(self):
        self.root.deiconify()

    def hide_window(self):
        self.root.withdraw()

    def on_close(self):
        global running, tray_icon
        
        if messagebox.askyesno("退出", "是否要退出程序？"):
            # 停止监听器
            stop_listener()
            
            # 停止托盘图标
            if tray_icon:
                tray_icon.stop()
            
            # 退出程序
            self.root.destroy()
            sys.exit(0)

# 主程序
if __name__ == "__main__":
    # 创建Tkinter窗口
    root = tk.Tk()
    app = ZenithApp(root)
    
    # 隐藏窗口
    root.withdraw()
    
    # 启动Tkinter主循环
    root.mainloop()