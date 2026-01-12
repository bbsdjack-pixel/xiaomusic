import os
import sys
import threading
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

# 确保当前目录在 path 中
sys.path.append(os.getcwd())

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AndroidMain")

class LogHandler(logging.Handler):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def emit(self, record):
        msg = self.format(record)
        Clock.schedule_once(lambda dt: self.update_label(msg))

    def update_label(self, msg):
        if len(self.label.text) > 10000: # 限制日志长度
            self.label.text = self.label.text[-5000:]
        self.label.text += msg + '\n'

class XiaoMusicApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.status_label = Label(text="Initializing...", size_hint_y=None, height=100, font_size='20sp')
        self.layout.add_widget(self.status_label)
        
        # Log view
        self.log_label = Label(text="", size_hint_y=None, markup=True, font_size='12sp')
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.log_label)
        self.layout.add_widget(scroll)
        
        # Setup logging to UI
        handler = LogHandler(self.log_label)
        logging.getLogger().addHandler(handler)
        
        # Start server
        threading.Thread(target=self.prepare_and_start, daemon=True).start()
        
        return self.layout

    def prepare_and_start(self):
        self.update_status("Setting up environment...")
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import app_storage_path, primary_external_storage_path
            
            # 请求必要权限
            request_permissions([
                Permission.INTERNET, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE,
                Permission.FOREGROUND_SERVICE
            ])
            
            # 尝试使用外部存储，以便用户可以访问 music 目录
            # /storage/emulated/0/XiaoMusic
            external_root = primary_external_storage_path()
            if external_root:
                work_dir = os.path.join(external_root, "XiaoMusic")
            else:
                work_dir = os.path.join(app_storage_path(), "XiaoMusic")
                
            if not os.path.exists(work_dir):
                os.makedirs(work_dir, exist_ok=True)
                
            music_path = os.path.join(work_dir, "music")
            conf_path = os.path.join(work_dir, "conf")
            
            if not os.path.exists(music_path):
                os.makedirs(music_path, exist_ok=True)
            if not os.path.exists(conf_path):
                os.makedirs(conf_path, exist_ok=True)
                
            os.environ["XIAOMUSIC_MUSIC_PATH"] = music_path
            os.environ["XIAOMUSIC_CONF_PATH"] = conf_path
            
        else:
            # 桌面测试环境
            work_dir = os.getcwd()
            os.environ["XIAOMUSIC_MUSIC_PATH"] = os.path.join(work_dir, "music")
            os.environ["XIAOMUSIC_CONF_PATH"] = os.path.join(work_dir, "conf")

        os.environ["XIAOMUSIC_PORT"] = "8090"
        os.environ["XIAOMUSIC_HOSTNAME"] = "0.0.0.0" # 监听所有接口
        
        self.update_status(f"Dir: {os.environ['XIAOMUSIC_MUSIC_PATH']}\nStarting Server on :8090...")
        logger.info(f"Working Directory: {work_dir}")
        
        try:
            # 导入并启动 XiaoMusic
            # 注意: 这里需要在新线程中运行，否则会阻塞 UI
            from xiaomusic.cli import main
            
            # 模拟命令行参数
            sys.argv = ["xiaomusic", "--port", "8090"]
            
            # 启动
            main()
        except Exception as e:
            logger.exception("Failed to start server")
            self.update_status(f"Error: {e}")

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

if __name__ == '__main__':
    XiaoMusicApp().run()
