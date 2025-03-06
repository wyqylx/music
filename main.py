import sys
import os
# 禁用 libpng warnings
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.svg.warning=false'

import re
import random
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal, QRect, QElapsedTimer, 
                         QPointF, QRectF, QTime, QSize, QPoint)
from PyQt5.QtGui import (QFont, QPainter, QColor, QLinearGradient, QIcon, 
                      QPalette, QBrush, QRadialGradient, QPixmap, QPen,
                      QTransform, QFontMetrics, QPainterPath)
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                          QPushButton, QMainWindow, QApplication, QDesktopWidget,
                          QFrame, QStackedWidget, QLineEdit, QListWidget,
                          QListWidgetItem, QScrollArea, QSizePolicy, QComboBox,
                          QSpacerItem, QGridLayout, QMessageBox, QProgressBar)
import math

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 歌单常量
# 随机的歌单
PLAYLIST_COLLECTION = {
    "Part 1": ["简单爱", "至少还有你", "这世界那么多人", "十年", "江南", "last dance", "一千年以后", "知足", "爱爱爱"],
    "Part 2": ["找自己", "童年", "再见", "告白气球", "稻香", "恋爱 ing", "今天你要嫁给我", "失恋阵线联盟", "离开地球表面"],
    "Part 3": ["平凡之路", "鼓楼", "那些花儿", "成都", "好久不见", "你不是真正的快乐", "乌兰巴托的夜", "活着", "后来"],
    "Part 4": ["倔强", "我怀念的", "七里香", "那些年", "晴天", "当", "老男孩", "光辉岁月", "海阔天空"],
    "Part Test": ["终结孤单","test"],
}

# 搜索的歌
SEARCH_PLAYLIST_COLLECTION = {
    "list":["简单爱", "至少还有你", "这世界那么多人", "十年", "江南", "last dance", "一千年以后", "知足", "爱爱爱", "找自己", "童年", "再见", "告白气球", "稻香", "恋爱 ing", "今天你要嫁给我", "失恋阵线联盟", "离开地球表面", "平凡之路", "鼓楼", "那些花儿", "成都", "好久不见", "你不是真正的快乐", "乌兰巴托的夜", "活着", "后来", "倔强", "我怀念的", "七里香", "那些年", "晴天", "当", "老男孩", "光辉岁月", "海阔天空"],
}

LYRICS_FOLDER = 'lyrics'  # 歌词文件夹路径

def resource_path(relative_path):
    """获取资源文件路径，优先使用外部文件夹，找不到再使用打包内的文件"""
    # 首先尝试从当前目录读取
    external_path = os.path.join(os.path.abspath("."), relative_path)
    if os.path.exists(external_path):
        # print(f"Using external file: {external_path}")  # 注释掉这行
        return external_path
        
    # 如果外部文件不存在，且是打包环境，则使用打包内的文件
    if hasattr(sys, '_MEIPASS'):
        packed_path = os.path.join(sys._MEIPASS, relative_path)
        # print(f"Using packed file: {packed_path}")  # 注释掉这行
        return packed_path
        
    # 如果都找不到，返回外部路径（会导致文件未找到错误）
    return external_path

class RotatingVinylLabel(QLabel):
    """旋转的黑胶唱片标签"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.is_rotating = True
        
        # 加载黑胶唱片图片
        self.vinyl = QPixmap(resource_path("vinyl.png"))
        if not self.vinyl.isNull():
            self.setFixedSize(300, 300)  # 设置固定大小
            
        # 创建旋转动画定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # 每50毫秒旋转一次
        
    def rotate(self):
        """更新旋转角度"""
        if self.is_rotating:
            self.angle = (self.angle + 2) % 360
            self.update()
    
    def paintEvent(self, event):
        """绘制旋转的唱片"""
        if not self.vinyl.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 计算中心点
            center = self.rect().center()
            
            # 保存当前画家状态
            painter.save()
            
            # 移动到中心点，旋转，然后绘制图片
            painter.translate(center)
            painter.rotate(self.angle)
            painter.translate(-center)
            
            # 绘制缩放后的图片
            scaled_vinyl = self.vinyl.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(self.rect(), scaled_vinyl)
            
            # 恢复画家状态
            painter.restore()

    def toggle_rotation(self, playing):
        """切换旋转状态"""
        self.is_rotating = playing
        if playing:
            self.timer.start()
        else:
            self.timer.stop()

class LaunchPage(QWidget):
    """启动页面"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("启动页面")

        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        self.screen_height = screen.height()
        self.screen_width = screen.width()

        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        layout.setSpacing(0)  # 移除间距

        # 上半部分 - Logo区域，设置为屏幕高度的 1/3
        self.logo_container = QWidget()
        self.logo_container.setFixedHeight(int(self.screen_height * 0.33))
        self.logo_container.setStyleSheet("background: transparent;")
        layout.addWidget(self.logo_container, 1)

        # 中间部分 - 按钮区域
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 200, 0, 100)  # 将上边距从100增加到200
        button_layout.setSpacing(60)  # 增加按钮之间的间距

        # 创建一个水平布局用于居中按钮
        button_container = QHBoxLayout()
        button_container.setSpacing(5)  # 设置按钮之间的间距为5像素
        
        # 固定歌单按钮
        self.fixed_playlist_button = QPushButton(self)
        fixed_icon = QPixmap(resource_path("fixed.png"))
        if not fixed_icon.isNull():
            scaled_icon = fixed_icon.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.fixed_playlist_button.setFixedSize(400, 400)
        
        # 创建一个垂直布局容器
        fixed_button_layout = QVBoxLayout()
        fixed_button_layout.setSpacing(20)  # 设置图标和文字之间的间距
        fixed_button_layout.setAlignment(Qt.AlignCenter)
        
        # 创建图标标签
        fixed_icon_label = QLabel()
        fixed_icon_label.setPixmap(scaled_icon)
        fixed_icon_label.setAlignment(Qt.AlignCenter)
        
        # 创建文字标签
        fixed_text_label = QLabel("固定歌单")
        fixed_text_label.setAlignment(Qt.AlignCenter)
        fixed_text_label.setStyleSheet("font-size: 32px; color: black;")
        
        # 将图标和文字添加到垂直布局中
        fixed_button_layout.addWidget(fixed_icon_label)
        fixed_button_layout.addWidget(fixed_text_label)
        
        # 将布局设置到按钮
        self.fixed_playlist_button.setLayout(fixed_button_layout)
        
        self.fixed_playlist_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50%;  // 确保是圆形
                min-width: 100px;  // 设置相等的宽度和高度
                min-height: 100px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.9);
            }
        """)
        button_container.addWidget(self.fixed_playlist_button)

        # 随机歌曲按钮
        self.random_button = QPushButton(self)
        random_icon = QPixmap(resource_path("random.png"))
        if not random_icon.isNull():
            scaled_icon = random_icon.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.random_button.setFixedSize(400, 400)
        
        # 创建随机按钮的垂直布局
        random_button_layout = QVBoxLayout()
        random_button_layout.setSpacing(20)
        random_button_layout.setAlignment(Qt.AlignCenter)
        
        # 创建随机按钮的图标标签
        random_icon_label = QLabel()
        random_icon_label.setPixmap(scaled_icon)
        random_icon_label.setAlignment(Qt.AlignCenter)
        
        # 创建随机按钮的文字标签
        random_text_label = QLabel("随机歌曲")
        random_text_label.setAlignment(Qt.AlignCenter)
        random_text_label.setStyleSheet("font-size: 32px; color: black;")
        
        # 添加到布局
        random_button_layout.addWidget(random_icon_label)
        random_button_layout.addWidget(random_text_label)
        
        # 设置布局
        self.random_button.setLayout(random_button_layout)
        
        self.random_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50%;  // 确保是圆形
                min-width: 100px;  // 设置相等的宽度和高度
                min-height: 100px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.9);
            }
        """)
        button_container.addWidget(self.random_button)

        # 搜索歌曲按钮
        self.search_button = QPushButton(self)
        search_icon = QPixmap(resource_path("search.png"))
        if not search_icon.isNull():
            scaled_icon = search_icon.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.search_button.setFixedSize(400, 400)
        
        # 创建搜索按钮的垂直布局
        search_button_layout = QVBoxLayout()
        search_button_layout.setSpacing(20)
        search_button_layout.setAlignment(Qt.AlignCenter)
        
        # 创建搜索按钮的图标标签
        search_icon_label = QLabel()
        search_icon_label.setPixmap(scaled_icon)
        search_icon_label.setAlignment(Qt.AlignCenter)
        
        # 创建搜索按钮的文字标签
        search_text_label = QLabel("搜索歌曲")
        search_text_label.setAlignment(Qt.AlignCenter)
        search_text_label.setStyleSheet("font-size: 32px; color: black;")
        
        # 添加到布局
        search_button_layout.addWidget(search_icon_label)
        search_button_layout.addWidget(search_text_label)
        
        # 设置布局
        self.search_button.setLayout(search_button_layout)
        
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50%;  // 确保是圆形
                min-width: 100px;  // 设置相等的宽度和高度
                min-height: 100px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.9);
            }
        """)
        button_container.addWidget(self.search_button)

        # 调整按钮容器的布局
        button_container.setContentsMargins(0, 0, 0, 0)  # 移除边距
        button_container.setSpacing(42)  # 恢复按钮之间的间距为60像素

        # 添加弹性空间使按钮居中
        button_container.addStretch()
        button_container.insertStretch(0)

        # 将水平布局添加到按钮布局中
        button_layout.addLayout(button_container)
        layout.addWidget(button_widget, 2)  # 增加按钮区域的比例

        # 添加标语标签，使用绝对定位
        slogan_label = QLabel("FUN Happens when Love meets Music", self)
        slogan_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 1);
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-size: 46px;
                font-weight: 450;
                letter-spacing: 3px;
                text-transform: uppercase;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3),
                             -2px -2px 4px rgba(255, 255, 255, 0.1);
                background: transparent;
                padding: 20px;
            }
        """)
        slogan_label.setAlignment(Qt.AlignCenter)
        
        # 计算标语位置
        slogan_width = int(self.screen_width * 0.8)  # 标语宽度为屏幕宽度的80%
        slogan_height = 100  # 固定高度
        slogan_x = (self.screen_width - slogan_width) // 2
        slogan_y = int(self.screen_height * 0.8) + 40  # 位于屏幕底部20%处再往下40px
        
        # 设置标语大小和位置
        slogan_label.setFixedSize(slogan_width, slogan_height)
        slogan_label.move(slogan_x, slogan_y)

        self.setLayout(layout)

        # 连接固定歌单按钮的点击事件到切换页面的方法
        self.fixed_playlist_button.clicked.connect(self.switch_to_fixed_playlist_page)

    def paintEvent(self, event):
        """绘制背景和Logo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)  # 启用平滑缩放
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿

        # 绘制背景
        bg_pixmap = QPixmap(resource_path("BG.png"))
        if not bg_pixmap.isNull():
            window_size = self.size()
            pixmap_size = bg_pixmap.size()
            
            scale = max(window_size.width() / pixmap_size.width(), 
                       window_size.height() / pixmap_size.height())
            
            new_width = int(pixmap_size.width() * scale)
            new_height = int(pixmap_size.height() * scale)
            
            x = int((window_size.width() - new_width) / 2)
            y = int((window_size.height() - new_height) / 2)
            
            target_rect = QRect(x, y, new_width, new_height)
            painter.drawPixmap(target_rect, bg_pixmap)

        # 绘制Logo
        logo_pixmap = QPixmap(resource_path("logo4.png"))
        if not logo_pixmap.isNull():
            # 计算Logo显示区域（上半部分）
            logo_area = QRect(0, 0, self.width(), int(self.screen_height * 0.5))
            
            # 计算保持宽高比的缩放尺寸，使用90%的区域大小
            logo_size = logo_pixmap.size()
            scale = min(logo_area.width() * 1.0 / logo_size.width(),
                       logo_area.height() * 1.0 / logo_size.height())
            
            new_width = int(logo_size.width() * scale)
            new_height = int(logo_size.height() * scale)
            
            # 计算居中位置
            x = int((logo_area.width() - new_width) / 2)
            y = int((logo_area.height() - new_height) / 2)
            
            # 创建临时pixmap进行高质量缩放并绘制
            scaled_logo = logo_pixmap.scaled(new_width, new_height, 
                                           Qt.KeepAspectRatio, 
                                           Qt.SmoothTransformation)
            
            # 直接绘制Logo
            painter.drawPixmap(x, y, scaled_logo)

    def switch_to_playback_control_page(self, playlist_name):
        """切换到播放控制页面"""
        self.playback_control_page = PlaybackControlPage(
            playlist_name, self.switch_to_lyrics_page, self.switch_to_launch_page
        )
        self.setCentralWidget(self.playback_control_page)

    def switch_to_fixed_playlist_page(self):
        """切换到固定歌单页面"""
        main_window = self.parent().parent()  # 获取主窗口实例
        main_window.switch_to_fixed_playlist_page()

class PlaybackControlPage(QWidget):
    """播放控制页面"""

    def __init__(self, playlist_name, switch_to_lyrics_page, switch_to_launch_page):
        super().__init__()
        
        # 获取页面宽高
        self.update_screen_size()
        
        self.playlist_name = playlist_name
        self.songs = PLAYLIST_COLLECTION.get(playlist_name, [])
        self.current_index = 0

        # 获取Part编号
        self.part_number = ''.join(filter(str.isdigit, playlist_name))
        if not self.part_number:
            raise ValueError("Playlist name must contain a part number.")

        # 初始化进度条参数
        self.progress = 0.0  # 初始化进度为0

        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧布局
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # 创建pad和BG容器
        pad_container = QWidget()
        pad_layout = QVBoxLayout(pad_container)
        pad_layout.setContentsMargins(0, 0, 0, 0)
        pad_layout.setSpacing(0)

        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(20)  # 设置按钮间距
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 创建四个按钮
        self.prev_button = QPushButton(self)
        self.play_button = QPushButton(self)
        self.pause_button = QPushButton(self)
        self.next_button = QPushButton(self)
        # 设置左右窗口大小
        left_container_width = int(self.page_width * 0.7)  # 左侧容器占70%
        right_container_width = int(self.page_width * 0.3)  # 右侧容器占30%
        container_height = int(self.page_height * 0.9)  # 容器高度占90%

        # 设置pad大小
        pad_width = int(left_container_width * 0.9)  # pad宽度为左侧容器的90%
        pad_height = int(container_height * 0.9)  # pad高度为容器高度的90%

        # 设置按钮大小和样式
        # 按钮大小随pad大小变化
        button_radius = min(int(pad_width * 0.05), int(pad_height * 0.05))  # 按钮半径为pad宽高中较小值的8%
        button_size = button_radius * 2  # 按钮大小为半径的2倍
        button_style = f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: {button_radius}px;  
                width: {button_size}px;
                height: {button_size}px;
                font-size: {int(button_radius * 0.8)}px;
            }}
            QPushButton:hover {{
                background-color: rgba(220, 220, 220, 0.9);
            }}
            QPushButton:pressed {{
                background-color: rgba(200, 200, 200, 0.9);
            }}
        """

        # 设置按钮和对应的功能
        buttons = [
            (self.prev_button, "last.png", self.prev_song),
            (self.play_button, "play.png", lambda: self.play_song(switch_to_lyrics_page)),
            (self.pause_button, "pause.png", self.return_to_fixed_playlist),
            (self.next_button, "next.png", self.next_song)
        ]

        # 设置按钮容器布局的间距为按钮半径
        button_layout.setSpacing(button_radius)

        for button, icon_name, callback in buttons:
            icon = QPixmap(resource_path(icon_name))
            if not icon.isNull():
                button.setIcon(QIcon(icon))
                button.setIconSize(QSize(int(button_size * 0.6), int(button_size * 0.6)))  # 图标大小为按钮的60%
            button.setFixedSize(button_size, button_size)
            button.setStyleSheet(button_style)
            button.clicked.connect(callback)
            button_layout.addWidget(button)

        # 添加按钮容器到pad布局
        pad_layout.addStretch(5)  # 上方占4份空间
        pad_layout.addWidget(button_container, alignment=Qt.AlignCenter)  # 按钮位于下1/5处

        # 添加进度条
        self.progress_bar = QProgressBar(self)
        # 设置进度条宽度为按钮半径的1/5
        progress_bar_height = int(button_radius * 0.2)
        # 设置进度条长度等于四个按钮加间距的总长度
        progress_bar_width = button_size * 4 + button_radius * 3
        self.progress_bar.setFixedSize(progress_bar_width, progress_bar_height)
        pad_layout.addSpacing(button_radius)  # 间距等于按钮半径
        pad_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        pad_layout.addStretch(1)  # 下方弹性空间

        # 添加pad容器到左侧布局
        left_layout.addWidget(pad_container)
        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        # 创建旋转的黑胶唱片标签
        self.vinyl_label = RotatingVinylLabel(self)
        
        # 设置黑胶唱片大小为窗口宽度的25%
        self.vinyl_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置最小尺寸以防止太小
        min_vinyl_size = 200
        self.vinyl_label.setMinimumSize(min_vinyl_size, min_vinyl_size)
        
        # 显示当前播放歌曲
        self.song_label = QLabel("PLAYING: " + self.songs[self.current_index], self)
        self.song_label.setAlignment(Qt.AlignCenter)
        self.song_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 设置标签字体
        font = QFont("Microsoft YaHei UI")  # 使用微软雅黑字体
        font.setBold(True)  # 设置为粗体
        self.song_label.setFont(font)
        self.song_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px; /* 基础字体大小 */
            }
        """)

        # 添加黑胶唱片和标签到右侧布局，确保垂直居中
        right_layout.addStretch(1)  # 上方弹性空间
        right_layout.addWidget(self.vinyl_label, alignment=Qt.AlignCenter)
        right_layout.addSpacing(20)  # 黑胶唱片和标签之间的间距
        right_layout.addWidget(self.song_label, alignment=Qt.AlignCenter)
        right_layout.addStretch(1)  # 下方弹性空间

        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, 2)  # 左侧占2/3
        main_layout.addLayout(right_layout, 1)  # 右侧占1/3

        self.setLayout(main_layout)
        

    def paintEvent(self, event):
        """绘制背景和pad"""
        # 更新页面宽高
        self.update_screen_size()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建动态渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        # 使用当前时间创建动态效果
        time = QTime.currentTime()
        msecs = time.msecsSinceStartOfDay() / 1000.0  # 转换为秒
        
        # 计算动态颜色值
        intensity = (math.sin(msecs * 0.5) + 1) * 0.5  # 产生0到1之间的值
        
        # 设置渐变点
        gradient.setColorAt(0, QColor(40, 40, 40))  # 深灰色
        gradient.setColorAt(0.4, QColor(int(20 + intensity * 20), 
                                      int(20 + intensity * 20), 
                                      int(20 + intensity * 20)))  # 动态灰色
        gradient.setColorAt(0.6, QColor(int(30 + intensity * 20), 
                                      int(20 + intensity * 20), 
                                      int(20 + intensity * 20)))  # 带一点红色调的灰色
        gradient.setColorAt(1, QColor(35, 35, 35))  # 中灰色
        
        # 填充背景
        painter.fillRect(0, 0, self.width(), self.height(), gradient)
        
        # 触发重绘以实现动画效果
        self.update()
        
        window_size = self.size()
        # 计算并绘制pad
        pad_pixmap = QPixmap(resource_path("pad.png"))
        if not pad_pixmap.isNull():
            # 计算pad的尺寸 - 使用窗口高度的85%作为最大高度
            max_height = int(window_size.height() * 0.9)
            pad_ratio = pad_pixmap.width() / pad_pixmap.height()
            
            # 先尝试用最大高度计算宽度
            pad_height = max_height
            pad_width = int(pad_height * pad_ratio)
            
            # 如果宽度超过了左侧2/3区域的宽度,则以宽度为基准重新计算
            max_width = int(window_size.width() * 2/3 * 0.9) # 左侧2/3区域的90%
            if pad_width > max_width:
                pad_width = max_width
                pad_height = int(pad_width / pad_ratio)
            
            # 缩放pad图片
            scaled_pad = pad_pixmap.scaled(pad_width, pad_height, 
                                         Qt.KeepAspectRatio, 
                                         Qt.SmoothTransformation)
            
            # pad的位置 - 左侧2/3区域内居中
            left_section_width = window_size.width() * 2 // 3
            pad_x = (left_section_width - pad_width) // 2
            pad_y = (window_size.height() - pad_height) // 2  # 严格垂直居中

            # 绘制pad
            painter.drawPixmap(pad_x, pad_y, scaled_pad)
            
            # 计算并绘制BG1
            bg_path = f"BG{self.part_number}.png"
            bg_pixmap = QPixmap(resource_path(bg_path))
            if not bg_pixmap.isNull():
                # 计算BG1的尺寸
                bg_width = int(pad_width * 0.945)
                bg_height = int(pad_height * 0.945)
                
                # 缩放BG1
                scaled_bg = bg_pixmap.scaled(bg_width, bg_height,
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
                # BG1的位置 - 在pad内居中
                bg_x = pad_x + (pad_width - bg_width) // 2
                bg_y = pad_y + (pad_height - bg_height) // 2
                
                # 绘制BG1
                painter.drawPixmap(bg_x, bg_y, scaled_bg)
        else:
            print("无法加载pad背景图片")
            
    def update_screen_size(self):
        """更新页面宽高"""
        screen = QDesktopWidget().screenGeometry()
        self.page_width = screen.width()
        self.page_height = screen.height()

    def return_to_fixed_playlist(self):
        """返回到选趴页面"""
        self.vinyl_label.toggle_rotation(False)  # 停止旋转
        main_window = self.window()
        if hasattr(main_window, 'fixed_playlist_page'):
            main_window.stack.setCurrentWidget(main_window.fixed_playlist_page)

    def update_song_label(self):
        """更新当前播放歌曲标签"""
        self.song_label.setText("PLAYING: " + self.songs[self.current_index])

    def prev_song(self):
        """切换到上一首歌曲"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_song_label()

    def next_song(self):
        """切换到下一首歌曲"""
        if self.current_index < len(self.songs) - 1:
            self.current_index += 1
            self.update_song_label()

    def switch_back(self):
        """返回到播放控制页面"""
        self.parent().setCurrentWidget(self)
        self.update_song_label()  # 确保返回时更新歌曲标签

    def play_song(self, switch_to_lyrics_page):
        """播放歌曲并切换到歌词页面"""
        self.vinyl_label.toggle_rotation(True)  # 开始旋转
        switch_to_lyrics_page(self.songs[self.current_index])

    def update_start_button(self):
        """根据播放状态更新按钮的外观和图标"""
        if self.playing:
            self.start_button.setIcon(QIcon(resource_path("pause.png")))
            self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                border: 2px solid white;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #3C3C3C;
            }
            """)
        else:
            self.start_button.setIcon(QIcon(resource_path("play.png")))
            self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                border: 2px solid white;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #3C3C3C;
            }
            """)

    #def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # 更新页面宽度和高度
        self.page_width = self.width()
        self.page_height = self.height()
        
        # 更新左右容器大小
        left_container_width = int(self.page_width * 0.7)  # 左侧容器占70%
        right_container_width = int(self.page_width * 0.3)  # 右侧容器占30%
        
        # 更新容器高度
        container_height = int(self.page_height * 0.9)  # 容器高度占90%
        
        # 更新按钮大小
        button_radius = int(self.page_height * 0.05)  # 按钮半径为窗口高度的1/20
        button_size = button_radius * 2  # 按钮大小为半径的2倍
        
        # 更新按钮样式和大小
        button_style = f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: {button_radius}px;  
                width: {button_size}px;
                height: {button_size}px;
                font-size: 32px;
            }}
            QPushButton:hover {{
                background-color: rgba(220, 220, 220, 0.9);
            }}
            QPushButton:pressed {{
                background-color: rgba(200, 200, 200, 0.9);
            }}
        """
        
        for button in [self.prev_button, self.play_button, self.pause_button, self.next_button]:
            button.setFixedSize(button_size, button_size)
            button.setStyleSheet(button_style)
            if button.icon():
                button.setIconSize(QSize(int(button_size * 0.6), int(button_size * 0.6)))
        
        # 更新进度条大小和样式
        progress_bar_height = int(button_radius * 0.2)
        progress_bar_width = button_size * 4 + button_radius * 3
        self.progress_bar.setFixedSize(progress_bar_width, progress_bar_height)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: rgba(200, 200, 200, 0.3);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 2px;
            }
        """)
        
        # 更新黑胶唱片大小
        vinyl_size = int(self.page_width * 0.25)  # 保持为窗口宽度的25%
        self.vinyl_label.setFixedSize(max(vinyl_size, 200), max(vinyl_size, 200))  # 确保不小于200px
        
        # 更新歌曲标签字体大小
        font = self.song_label.font()
        font.setPixelSize(int(vinyl_size * 0.1))  # 字体大小为黑胶唱片大小的10%
        self.song_label.setFont(font)


class FixedPlaylistPage(QWidget):
    """选趴页面"""

    def __init__(self, switch_to_playback_control_page):
        super().__init__()
        self.setWindowTitle("固定歌单页面")
        
        # 获取屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        # 保存参数
        self.switch_to_playback_control_page = switch_to_playback_control_page

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        main_layout.setSpacing(0)  # 移除间距

        # 上部分容器 (占90%)
        upper_container = QWidget()
        upper_container.setFixedHeight(int(self.screen_height * 0.9))
        
        # 创建2x2网格布局
        grid_layout = QGridLayout(upper_container)
        grid_layout.setSpacing(15)  # 设置统一的间距为15像素
        grid_layout.setContentsMargins(15, 15, 15, 15)  # 设置所有边距为15像素
        grid_layout.setHorizontalSpacing(15)  # 设置水平间距为15像素
        grid_layout.setVerticalSpacing(15)   # 设置垂直间距为15像素

        # 调整网格布局的对齐方式
        grid_layout.setAlignment(Qt.AlignCenter)  # 设置网格布局居中对齐

        # Part 1 到 Part 4 按钮
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(255, 255, 255, 0.8),
                                          stop:1 rgba(220, 220, 220, 0.8));
                border: 3px solid rgba(128, 128, 128, 0.75);
                border-radius: 50px;
                font-family: "Impact", "Haettenschweiler", "Franklin Gothic Bold", sans-serif;
                font-size: 120px;
                font-weight: bold;
                color: rgba(0, 0, 0, 0.8);
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(220, 220, 220, 0.9),
                                          stop:1 rgba(200, 200, 200, 0.9));
                border: 3px solid rgba(100, 100, 100, 0.85);
                color: rgba(0, 0, 0, 0.9);
                text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(200, 200, 200, 0.9),
                                          stop:1 rgba(180, 180, 180, 0.9));
                border: 3px solid rgba(80, 80, 80, 0.9);
                padding: 2px;
            }
        """

        # 创建四个按钮并添加到网格布局
        self.part1_button = QPushButton("PART 1", self)
        self.part1_button.clicked.connect(lambda: self.switch_to_playback_control_page("Part 1"))
        self.part1_button.setStyleSheet(button_style)
        self.part1_button.setFixedSize(700, 400)
        grid_layout.addWidget(self.part1_button, 0, 0)

        self.part2_button = QPushButton("PART 2", self)
        self.part2_button.clicked.connect(lambda: self.switch_to_playback_control_page("Part 2"))
        self.part2_button.setStyleSheet(button_style)
        self.part2_button.setFixedSize(700, 400)
        grid_layout.addWidget(self.part2_button, 0, 1)

        self.part3_button = QPushButton("PART 3", self)
        self.part3_button.clicked.connect(lambda: self.switch_to_playback_control_page("Part 3"))
        self.part3_button.setStyleSheet(button_style)
        self.part3_button.setFixedSize(700, 400)
        grid_layout.addWidget(self.part3_button, 1, 0)

        self.part4_button = QPushButton("PART 4", self)
        self.part4_button.clicked.connect(lambda: self.switch_to_playback_control_page("Part 4"))
        self.part4_button.setStyleSheet(button_style)
        self.part4_button.setFixedSize(700, 400)
        grid_layout.addWidget(self.part4_button, 1, 1)

        main_layout.addWidget(upper_container, stretch=4)

        # 下部分容器 (占20%)
        lower_container = QWidget()
        lower_container.setFixedHeight(int(self.screen_height * 0.2))
        lower_layout = QVBoxLayout(lower_container)  # 改为垂直布局

        # 添加标语标签
        slogan_label = QLabel("FUN Happens when Love meets Music", self)
        slogan_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 1);
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-size: 46px;
                font-weight: 450;
                letter-spacing: 3px;
                text-transform: uppercase;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3),
                             -2px -2px 4px rgba(255, 255, 255, 0.1);
                background: transparent;
                padding: 20px;
            }
        """)
        slogan_label.setAlignment(Qt.AlignCenter)
        lower_layout.addWidget(slogan_label)

        # 返回按钮
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        self.back_button = QPushButton("", self)
        return_icon = QPixmap(resource_path("return.png"))
        if not return_icon.isNull():
            scaled_icon = return_icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.back_button.setIcon(QIcon(scaled_icon))
            self.back_button.setIconSize(scaled_icon.size())
        
        self.back_button.setFixedSize(100, 100)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.9);
            }
        """)
        self.back_button.clicked.connect(self.switch_to_playback_control_page)
        
        button_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
        lower_layout.addWidget(button_container)
        
        main_layout.addWidget(lower_container, stretch=1)

        self.setLayout(main_layout)

    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        pixmap = QPixmap(resource_path("BG.png"))
        if not pixmap.isNull():
            window_size = self.size()
            pixmap_size = pixmap.size()
            
            # 计算保持宽高比的缩放比例
            scale = max(window_size.width() / pixmap_size.width(), 
                       window_size.height() / pixmap_size.height())
            
            # 计算缩放后的尺寸
            new_width = int(pixmap_size.width() * scale)
            new_height = int(pixmap_size.height() * scale)
            
            # 计算居中位置
            x = int((window_size.width() - new_width) / 2)
            y = int((window_size.height() - new_height) / 2)
            
            # 绘制图片
            target_rect = QRect(x, y, new_width, new_height)
            painter.drawPixmap(target_rect, pixmap)
        else:
            print("无法加载背景图片")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 更新按钮大小
        window_size = min(self.width(), self.height())
        button_size = int(window_size * 0.3)  # 按钮大小为窗口大小的30%
        
        # 更新Part按钮的大小
        for button in self.findChildren(QPushButton):
            if hasattr(self, 'back_button') and button != self.back_button:  # 不处理返回按钮
                button.setFixedSize(button_size, button_size)
                # 更新按钮字体大小
                font = button.font()
                font.setPixelSize(int(button_size * 0.25))  # 字体大小为按钮大小的25%
                button.setFont(font)
        
        # 只有在标语标签存在时才更新它的样式
        if hasattr(self, 'slogan_label'):
            slogan_font_size = int(window_size * 0.04)  # 标语字体大小为窗口大小的4%
            slogan_style = f"""
                QLabel {{
                    color: rgba(255, 255, 255, 1);
                    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                    font-size: {slogan_font_size}px;
                    font-weight: 450;
                    letter-spacing: 3px;
                }}
            """
            self.slogan_label.setStyleSheet(slogan_style)

class RandomSongPage(QWidget):
    selected_song = pyqtSignal(str)  # 信号，用于通知主窗口选中的歌曲名

    def __init__(self):
        super().__init__()
        self.setWindowTitle("随机歌曲")
        self.resize(1500, 400)
        self.center()

        # 初始化歌曲列表
        self.remaining_songs_dict = {}  # 用于持久保存每个歌单的剩余歌曲列表
        for playlist in PLAYLIST_COLLECTION:
            self.remaining_songs_dict[playlist] = list(PLAYLIST_COLLECTION[playlist])

        # 当前选定歌单和歌曲
        self.current_playlist_name = "Part 1"  # 默认加载第一个歌单
        self.init_playlist(self.current_playlist_name)  # 初始化默认歌单
        self.remaining_songs = self.remaining_songs_dict[self.current_playlist_name]

        # 滚动状态控制
        self.current_index = 0
        self.is_scrolling = True
        self.selected_song_name = None

        # 主布局
        layout = QVBoxLayout()

        # 歌曲显示标签
        self.label = QLabel("请选择歌单并点击按钮开始滚动...", self)
        self.label.setStyleSheet("font-size: 24px; color: #333; background: rgba(255, 255, 255, 0.8); padding: 15px;")
        self.label.setFixedSize(300, 100)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # 下拉框：选择歌单
        self.playlist_selector = QComboBox(self)
        self.playlist_selector.addItems(PLAYLIST_COLLECTION.keys())
        self.playlist_selector.currentTextChanged.connect(self.update_playlist)
        self.playlist_selector.setFixedSize(800, 50)
        layout.addWidget(self.playlist_selector, alignment=Qt.AlignCenter)

        # 按钮区域的水平布局
        button_layout = QHBoxLayout()

        # 随机选择按钮
        self.random_button = QPushButton("随机选择", self)
        self.random_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.random_button.setFixedSize(400, 70)
        self.random_button.clicked.connect(self.stop_scrolling)
        button_layout.addWidget(self.random_button)

        # 跳转按钮
        self.jump_button = QPushButton("跳转到歌词页面", self)
        self.jump_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.jump_button.setFixedSize(400, 70)
        self.jump_button.clicked.connect(self.emit_selected_song)
        self.jump_button.setVisible(False)
        button_layout.addWidget(self.jump_button)

        # 返回按钮
        self.back_button = QPushButton("返回启动页面", self)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.back_button.setFixedSize(400, 70)
        button_layout.addWidget(self.back_button)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 滚动定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.scroll_songs)
        self.timer.start(200)

    def init_playlist(self, playlist_name):
        """初始化歌单：如果歌单未被初始化，则创建新的剩余歌曲列表"""
        if playlist_name not in self.remaining_songs_dict:
            self.remaining_songs_dict[playlist_name] = list(PLAYLIST_COLLECTION[playlist_name])
        random.shuffle(self.remaining_songs_dict[playlist_name])

    def emit_selected_song(self):
        """发射信号以通知主窗口选中的歌曲，并跳转"""
        if self.selected_song_name:
            self.selected_song.emit(self.selected_song_name)
            self.jump_button.setVisible(False)
        else:
            self.label.setText("请首先随机选择一首歌！")

    def center(self):
        """将窗口移动到屏幕中央"""
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def update_playlist(self, playlist_name):
        """切换到新歌单"""
        self.current_playlist_name = playlist_name
        self.init_playlist(playlist_name)
        self.remaining_songs = self.remaining_songs_dict[playlist_name]

        self.current_index = 0
        self.is_scrolling = True
        self.timer.start(200)
        self.label.setText(f"{playlist_name} - 准备开始滚动...")
        self.jump_button.setVisible(False)

    def scroll_songs(self):
        """滚动播放歌单中的歌曲名称"""
        if self.is_scrolling and self.remaining_songs:
            self.label.setText(self.remaining_songs[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.remaining_songs)

    def stop_scrolling(self):
        """停止滚动，随机选歌"""
        if self.is_scrolling:
            # 如果正在滚动，则停止并选歌
            self.is_scrolling = False
            self.timer.stop()

            if not self.remaining_songs:
                # 如果歌曲列表为空，提示用户
                self.label.setText("当前歌单歌曲已经全部选完！请切换到其他歌单！")
                self.jump_button.setVisible(False)
                return

            # 从剩余歌曲中随机选择一首
            self.selected_song_name = random.choice(self.remaining_songs)
            self.remaining_songs.remove(self.selected_song_name)  # 从当前列表中移除
            self.label.setText(f"你选中的歌曲是: {self.selected_song_name}")
            self.jump_button.setVisible(True)  # 确保按钮在选中歌曲后可见
            
            # 修改按钮文字
            self.random_button.setText("继续随机")
        else:
            # 如果已经停止，则重新开始滚动
            if self.remaining_songs:  # 确保还有歌曲可以滚动
                self.is_scrolling = True
                self.current_index = 0
                self.timer.start(200)
                self.jump_button.setVisible(False)
                self.random_button.setText("随机选择")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        window_size = min(self.width(), self.height())
        
        # 更新标签大小
        label_width = int(window_size * 0.4)
        label_height = int(window_size * 0.15)
        self.label.setFixedSize(label_width, label_height)
        
        # 更新下拉框大小
        combo_width = int(window_size * 0.5)
        combo_height = int(window_size * 0.06)
        self.playlist_selector.setFixedSize(combo_width, combo_height)
        
        # 更新按钮大小
        button_width = int(window_size * 0.3)
        button_height = int(window_size * 0.08)
        for button in [self.random_button, self.jump_button, self.back_button]:
            button.setFixedSize(button_width, button_height)

class MusicPlayer(QWidget):
    selected_song = pyqtSignal(str, str)  # Signal to notify the main window of the selected song
    back_to_launch = pyqtSignal()  # Signal to notify the main window to switch to the launch page

    def __init__(self):
        super().__init__()
        self.setWindowTitle("微型演唱会")
        self.resize(1500, 400)
        self.center()

        # 全局歌曲列表管理
        self.remaining_songs_dict = {}  # 用于持久保存每个歌单的剩余歌曲列表
        for playlist in PLAYLIST_COLLECTION:
            self.remaining_songs_dict[playlist] = list(PLAYLIST_COLLECTION[playlist])
        random.shuffle(self.remaining_songs_dict[playlist_name])  # 打乱歌曲顺序

        # 当前选定歌单
        self.current_playlist_name = "Part 1"
        self.init_playlist(self.current_playlist_name)
        self.remaining_songs = self.remaining_songs_dict[self.current_playlist_name]

        # 滚动状态控制
        self.current_index = 0
        self.is_scrolling = True
        self.selected_song_name = None

        # 主布局
        layout = QVBoxLayout()

        # 歌曲显示标签
        self.label = QLabel("请选择歌单并点击按钮开始滚动...", self)
        self.label.setStyleSheet("font-size: 24px; color: #333; background: rgba(255, 255, 255, 0.8); padding: 15px;")
        self.label.setFixedSize(300, 100)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # 下拉框：选择歌单
        self.playlist_selector = QComboBox(self)
        self.playlist_selector.addItems(PLAYLIST_COLLECTION.keys())
        self.playlist_selector.currentTextChanged.connect(self.update_playlist)
        self.playlist_selector.setFixedSize(800, 50)
        layout.addWidget(self.playlist_selector, alignment=Qt.AlignCenter)

        # 随机选择按钮
        self.button = QPushButton("随机选择", self)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.button.setFixedSize(400, 70)
        self.button.clicked.connect(self.stop_scrolling)
        layout.addWidget(self.button, alignment=Qt.AlignCenter)

        # 跳转按钮
        self.jump_button = QPushButton("跳转到歌词页面", self)
        self.jump_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.jump_button.setFixedSize(400, 70)
        self.jump_button.clicked.connect(self.emit_selected_song)
        self.jump_button.setVisible(False)
        layout.addWidget(self.jump_button, alignment=Qt.AlignCenter)

        # 返回按钮
        self.back_button = QPushButton("返回", self)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: none;
                border-radius: 30px;
                min-width: 300px;
                min-height: 225px;
                font-size: 32px;
            }
            QPushButton:hover {
                background-color: rgba(220, 220, 220, 0.7);
            }
        """)
        self.back_button.setFixedSize(400, 70)
        button_layout.addWidget(self.back_button)

        self.setLayout(layout)

        # 滚动定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.scroll_songs)
        self.timer.start(200)

    def init_playlist(self, playlist_name):
        """初始化歌单：如果歌单未被初始化，则创建新的剩余歌曲列表"""
        if playlist_name not in self.remaining_songs_dict:
            self.remaining_songs_dict[playlist_name] = list(PLAYLIST_COLLECTION[playlist_name])
        random.shuffle(self.remaining_songs_dict[playlist_name])  # 打乱歌曲顺序

    def reset_state(self):
        """重置界面状态"""
        self.is_scrolling = True
        self.timer.start(200)
        self.label.setText("请选择歌单并点击按钮开始滚动...")
        self.jump_button.setVisible(False)  # 确保按钮在重置时不可见
        self.selected_song_name = None

    def emit_selected_song(self):
        """Emit signal to notify the main window of the selected song and switch to lyrics page"""
        if self.selected_song_name:
            print(f"Emitting signal for song: {self.selected_song_name}")
            self.selected_song.emit(self.selected_song_name, self.current_playlist_name)  # Emit signal with playlist name
            self.jump_button.setVisible(False)  # Hide the jump button
        else:
            self.label.setText("请首先随机选择一首歌！")

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(resource_path("album.png"))  # 修改为album.png
        if not pixmap.isNull():
            window_size = self.size()
            pixmap_size = pixmap.size()
            scale = min(window_size.width() / pixmap_size.width(), window_size.height() / pixmap_size.height())
            
            new_width = int(pixmap_size.width() * scale)
            new_height = int(pixmap_size.height() * scale)
            x = int((window_size.width() - new_width) / 2)
            y = int((window_size.height() - new_height) / 2)
            
            target_rect = QRect(x, y, new_width, new_height)
            painter.drawPixmap(target_rect, pixmap)
        else:
            print("无法加载背景图片")

    def center(self):
        """将窗口移动到屏幕中央"""
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def update_playlist(self, playlist_name):
        """切换到新歌单"""
        self.current_playlist_name = playlist_name
        self.init_playlist(playlist_name)
        self.remaining_songs = self.remaining_songs_dict[playlist_name]

        self.current_index = 0
        self.is_scrolling = True
        self.timer.start(200)
        self.label.setText(f"{playlist_name} - 准备开始滚动...")
        self.jump_button.setVisible(False)  # 切换歌单时隐藏跳转按钮

    def scroll_songs(self):
        """滚动播放歌单中的歌曲名称"""
        if self.is_scrolling and self.remaining_songs:
            self.current_index = (self.current_index + 1) % len(self.remaining_songs)
            self.label.setText(self.remaining_songs[self.current_index])  # 显示当前歌曲

    def stop_scrolling(self):
        """停止滚动，随机选歌"""
        if self.is_scrolling:
            # 如果正在滚动，则停止并选歌
            self.is_scrolling = False
            self.timer.stop()

            if not self.remaining_songs:
                # 如果歌曲列表为空，提示用户
                self.label.setText("当前歌单歌曲已经全部选完！请切换到其他歌单！")
                self.jump_button.setVisible(False)
                return

            # 从剩余歌曲中随机选择一首
            self.selected_song_name = random.choice(self.remaining_songs)
            self.remaining_songs.remove(self.selected_song_name)  # 从当前列表中移除
            self.label.setText(f"你选中的歌曲是: {self.selected_song_name}")
            self.jump_button.setVisible(True)  # 确保按钮在选中歌曲后可见
            
            # 修改按钮文字
            self.random_button.setText("继续随机")
        else:
            # 如果已经停止，则重新开始滚动
            if self.remaining_songs:  # 确保还有歌曲可以滚动
                self.is_scrolling = True
                self.current_index = 0
                self.timer.start(200)
                self.jump_button.setVisible(False)
                self.random_button.setText("随机选择")

class LyricsPage(QWidget):
    """歌词页面"""
    back_to_random = pyqtSignal()  # 添加返回随机页面的信号
    back_to_search = pyqtSignal()  # 添加返回搜索页面的信号

    def __init__(self, switch_to_playback_control_callback):
        super().__init__()
        self.switch_to_playback_control_callback = switch_to_playback_control_callback
        
        # 初始化来源页面标记
        self.from_random_page = False
        self.from_search_page = False
        
        # 初始化其他属性
        self.current_line = 0
        self.lyrics = []
        self.playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.scroll_lyrics)
        self.elapsed_timer = QElapsedTimer()
        
        # 主布局
        layout = QVBoxLayout()

        # 初始化歌词显示区域
        self.lyrics_label = QLabel("正在加载歌词...", self)
        self.lyrics_label.setStyleSheet("font-size: 16px; background: transparent;")
        self.lyrics_label.setWordWrap(True)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.lyrics_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.scroll_area)

        # 添加按钮
        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        
        # 创建并设置开始播放按钮
        self.start_button = QPushButton(self)
        self.start_button.setFixedSize(100, 100)
        self.start_button.setIcon(QIcon(resource_path("play.png")))
        self.start_button.setIconSize(QSize(50, 50))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)
        
        # 创建并设置返回按钮
        self.back_button = QPushButton(self)
        self.back_button.setFixedSize(100, 100)
        self.back_button.setIcon(QIcon(resource_path("return.png")))
        self.back_button.setIconSize(QSize(50, 50))
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)
        
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(40)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(button_container)
        self.start_button.clicked.connect(self.toggle_playback)
        self.back_button.clicked.connect(self.handle_back_button)

        self.setLayout(layout)

        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)

        # 定时器用于更新渐变颜色
        self.gradient_timer = QTimer(self)
        self.gradient_timer.timeout.connect(self.update_gradient)
        self.gradient_timer.start(500)

        # 初始颜色位置
        self.gradient_position = 0.0

    def set_from_random_page(self, value):
        """设置是否来自随机歌曲页面"""
        self.reset_source_flags()
        self.from_random_page = value
        if value:
            self.from_search_page = False  # 确保其他标记为False

    def set_from_search_page(self, value):
        """设置是否从搜索页面进入"""
        self.reset_source_flags()
        self.from_search_page = value
        if value:
            self.from_random_page = False  # 确保其他标记为False

    def reset_source_flags(self):
        """重置所有来源标记"""
        self.from_random_page = False
        self.from_search_page = False

    def update_gradient(self):
        """更新渐变颜色"""
        self.gradient_position += 0.02  # 加快变化速度，从0.005改为0.02
        if self.gradient_position > 1.0:
            self.gradient_position = 0.0
        self.update()  # 触发重绘

    def load_lyrics(self, song_name):
        """加载歌词文件"""
        lyrics_path = resource_path(os.path.join("lyrics", f"{song_name}.lrc"))

        self.lyrics = []
        if not os.path.exists(lyrics_path):
            self.lyrics = [(0, f"未找到歌词文件：{lyrics_path}"), (0, "请返回选歌页面重试")]
            self.update_lyrics_label()
            return

        with open(lyrics_path, "r", encoding="utf-8") as file:
            for line in file:
                match = re.match(r"\[\s*(\d+):(\d+).(\d+)\s*\](.+)", line)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    milliseconds = int(match.group(3))
                    timestamp = minutes * 60 + seconds + milliseconds / 1000.0
                    content = match.group(4).strip()
                    self.lyrics.append((timestamp, content))
        self.lyrics.sort(key=lambda x: x[0])
        self.current_line = 0
        self.update_lyrics_label()

    def update_lyrics_label(self):
        """更新歌词显示"""
        if not self.lyrics:
            return

        # 设置字体样式
        font = QFont("Microsoft YaHei", 60, QFont.Bold)
        self.lyrics_label.setFont(font)
        self.lyrics_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
                font-weight: bold;
                letter-spacing: 3px;
                line-height: 1.2;
            }
        """)

        # 创建一个固定高度的容器div
        lyrics_text = ['<div style="height: 1000px; display: flex; flex-direction: column; justify-content: center;">']
        
        # 计算要显示的总行数
        total_lines = 9  # 显示9行歌词
        half_lines = 1  # 上面显示1行，其余都分配给下面
        
        # 计算起始行，确保当前行总是在中间位置
        start_line = max(0, self.current_line - half_lines)
        end_line = min(len(self.lyrics), start_line + total_lines)
        
        # 如果到达末尾，调整起始位置以保持总行数
        if end_line - start_line < total_lines and start_line > 0:
            start_line = max(0, end_line - total_lines)
        
        # 添加所有行
        for i in range(start_line, end_line):
            if i == self.current_line:
                # 当前行（大号高亮）
                lyrics_text.append(f'<div style="color: white; font-size: 200px; font-weight: 900; text-shadow: 0 0 20px white; margin: -4px 0; text-align: center;">{self.lyrics[i][1]}</div>')
            elif i < self.current_line:
                # 之前的行（暗色）
                opacity = 0.6 - (self.current_line - i) * 0.1
                lyrics_text.append(f'<div style="color: rgba(255,255,255,{max(0.5, opacity)}); font-size: 120px; margin: -8px 0; text-align: center;">{self.lyrics[i][1]}</div>')
            else:
                # 之后的行（渐变暗色）
                opacity = 0.7 - (i - self.current_line) * 0.5
                lyrics_text.append(f'<div style="color: rgba(255,255,255,{max(0.5, opacity)}); font-size: 100px; margin: -8px 0; text-align: center;">{self.lyrics[i][1]}</div>')
        
        lyrics_text.append('</div>')
        
        # 使用HTML格式设置歌词显示
        self.lyrics_label.setText("".join(lyrics_text))

    def toggle_playback(self):
        """切换开始/停止播放状态"""
        if self.playing:
            self.stop_scroll()
        else:
            self.start_scroll()

    def scroll_lyrics(self):
        """滚动到下一行歌词，根据歌词时间进行高亮和滚动"""
        if self.current_line < len(self.lyrics) - 1:
            self.current_line += 1  # 移动到下一行
            self.update_lyrics_label()
            
            # 检查实际经过的时间
            elapsed_time = self.elapsed_timer.elapsed()

            self.start_scroll()  # 继续滚动到下一行
        else:
            self.stop_scroll()  # 确保在最后一行时停止滚动和高亮

    def start_scroll(self):
        if self.lyrics:
            if not self.playing:
                self.playing = True
                self.update_start_button()
            
            if self.current_line < len(self.lyrics) - 1:
                # 计算下一行的时间戳差，并设置定时器
                current_timestamp = self.lyrics[self.current_line][0]
                next_timestamp = self.lyrics[self.current_line + 1][0]
                interval = int((next_timestamp - current_timestamp) * 1000)
                
                # 使用 QElapsedTimer 来测量时间
                self.elapsed_timer.start()
                self.timer.start(interval)

    def stop_scroll(self):
        """停止滚动"""
        self.timer.stop()
        self.playing = False
        self.update_start_button()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.current_line > 0:
                self.current_line -= 1
        elif event.key() == Qt.Key_Down:
            if self.current_line < len(self.lyrics) - 1:
                self.current_line += 1
        elif event.key() == Qt.Key_Space:
            self.toggle_playback()
        self.update_lyrics_label()  # 更新歌词显示

    def update_start_button(self):
        """根据播放状态更新按钮图标"""
        if self.playing:
            self.start_button.setIcon(QIcon(resource_path("pause.png")))
        else:
            self.start_button.setIcon(QIcon(resource_path("play.png")))
        
        # 保持按钮样式不变
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)

    def focusInEvent(self, event):
        """确保获得焦点时歌词页面可以捕获键盘事件"""
        self.setFocus(Qt.OtherFocusReason)
        super().focusInEvent(event)

    def paintEvent(self, event):
        """绘制背景渐变"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        pos = self.gradient_position
        
        # 使用柔和的自然色彩渐变
        gradient.setColorAt(pos, QColor("#E0F7FA"))                  # 浅蓝
        gradient.setColorAt((pos + 0.2) % 1, QColor("#87CEEB"))     # 天蓝
        gradient.setColorAt((pos + 0.4) % 1, QColor("#D8BFD8"))     # 淡紫
        gradient.setColorAt((pos + 0.6) % 1, QColor("#FFB6C1"))     # 浅粉
        gradient.setColorAt((pos + 0.8) % 1, QColor("#FFE4B5"))     # 浅橙

        painter.fillRect(self.rect(), gradient)

    def handle_back_button(self):
        """处理返回按钮点击事件"""
        # 停止歌词滚动
        self.stop_scroll()
        
        # 根据来源页面决定返回行为
        if self.from_search_page:
            # 如果是从搜索页面来的
            self.back_to_search.emit()
        elif self.from_random_page:
            # 如果是从随机歌曲页面来的
            self.back_to_random.emit()
        else:
            # 从播放控制页面来的，返回播放控制页面
            if hasattr(self, 'switch_to_playback_control_callback'):
                self.switch_to_playback_control_callback()

class SearchPage(QWidget):
    selected_song = pyqtSignal(str)  # 信号，用于通知主窗口选中的歌曲名

    def __init__(self):
        super().__init__()
        self.setWindowTitle("搜索歌曲")
        self.resize(1500, 400)
        self.center()

        # 主布局
        layout = QVBoxLayout()

        # 搜索结果显示标签
        self.label = QLabel("请输入要搜索的歌曲名...", self)
        self.label.setStyleSheet("font-size: 24px; color: #333; background: rgba(255, 255, 255, 0.8); padding: 15px;")
        self.label.setFixedSize(300, 100)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # 搜索框
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("输入歌曲名称...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                padding: 10px;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.9);
            }
            QLineEdit:focus {
                border-color: #45a049;
            }
        """)
        self.search_input.setFixedSize(800, 50)
        layout.addWidget(self.search_input, alignment=Qt.AlignCenter)

        # 按钮区域的水平布局
        button_layout = QHBoxLayout()

        # 选中按钮
        self.select_button = QPushButton("跳转歌词页面", self)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 24px;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.select_button.setFixedSize(400, 70)
        self.select_button.clicked.connect(self.select_song)
        self.select_button.setVisible(False)  # 初始时隐藏
        button_layout.addWidget(self.select_button)

        # 返回按钮
        self.back_button = QPushButton("返回启动页面", self)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                font-size: 24px;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        self.back_button.setFixedSize(400, 70)
        button_layout.addWidget(self.back_button)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 连接搜索框的文本变化信号
        self.search_input.textChanged.connect(self.on_search)

        # 连接回车键信号
        self.search_input.returnPressed.connect(self.select_song)

    def center(self):
        """将窗口移动到屏幕中央"""
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def on_search(self, text):
        """当搜索框文本改变时调用"""
        if not text:
            self.label.setText("请输入要搜索的歌曲名...")
            self.select_button.setVisible(False)
            return

        # 在歌曲列表中搜索
        found_songs = [song for song in SEARCH_PLAYLIST_COLLECTION["list"] 
                      if text.lower() in song.lower()]
        
        if found_songs:
            if len(found_songs) == 1:
                self.label.setText(f"找到歌曲: {found_songs[0]}")
                self.select_button.setVisible(True)
            else:
                self.label.setText(f"找到 {len(found_songs)} 首相关歌曲，请输入更精确的名称")
                self.select_button.setVisible(False)
        else:
            self.label.setText("未找到相关歌曲")
            self.select_button.setVisible(False)

    def select_song(self):
        """选中当前搜索到的歌曲"""
        text = self.search_input.text()
        if not text:
            return

        # 精确匹配搜索
        found_songs = [song for song in SEARCH_PLAYLIST_COLLECTION["list"] 
                      if text.lower() in song.lower()]
        
        if len(found_songs) == 1:
            self.selected_song.emit(found_songs[0])
            self.search_input.clear()
            self.label.setText("请输入要搜索的歌曲名...")
            self.select_button.setVisible(False)

    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)  # 启用平滑缩放
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        
        pixmap = QPixmap(resource_path("album.png"))
        if not pixmap.isNull():
            window_size = self.size()
            pixmap_size = pixmap.size()
            
            # 计算保持宽高比的缩放比例
            scale_w = window_size.width() / pixmap_size.width()
            scale_h = window_size.height() / pixmap_size.height()
            scale = max(scale_w, scale_h)  # 使用max确保图片填充整个窗口
            
            # 计算缩放后的尺寸
            new_width = int(pixmap_size.width() * scale)
            new_height = int(pixmap_size.height() * scale)
            
            # 计算居中位置
            x = int((window_size.width() - new_width) / 2)
            y = int((window_size.height() - new_height) / 2)
            
            # 创建一个临时pixmap进行高质量缩放
            scaled_pixmap = pixmap.scaled(new_width, new_height, 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            
            # 绘制图片，确保使用整数坐标
            target_rect = QRect(int(x), int(y), int(new_width), int(new_height))
            painter.drawPixmap(target_rect, scaled_pixmap)
        else:
            print("无法加载背景图片")

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("微型演唱会")
        
        # 添加已播放歌曲记录
        self.played_songs = set()

        # 创建页面实例
        self.launch_page = LaunchPage()
        self.random_song_page = RandomSongPage()
        self.search_page = SearchPage()
        self.lyrics_page = LyricsPage(self.switch_to_playback_control_page)
        self.fixed_playlist_page = FixedPlaylistPage(self.switch_to_playback_control_page)

        # 设置堆栈布局
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.launch_page)
        self.stack.addWidget(self.random_song_page)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.lyrics_page)
        self.stack.addWidget(self.fixed_playlist_page)
        self.setCentralWidget(self.stack)

        # 设置初始页面为启动页面
        self.stack.setCurrentWidget(self.launch_page)

        # 连接信号和槽
        self.launch_page.random_button.clicked.connect(self.switch_to_random_song_page)
        self.launch_page.search_button.clicked.connect(self.switch_to_search_page)
        self.launch_page.fixed_playlist_button.clicked.connect(self.switch_to_fixed_playlist_page)
        self.random_song_page.back_button.clicked.connect(self.switch_to_launch_page)
        self.search_page.back_button.clicked.connect(self.switch_to_launch_page)
        self.fixed_playlist_page.back_button.clicked.connect(self.switch_to_launch_page)
        
        # 连接随机歌曲页面的信号
        self.random_song_page.selected_song.connect(self.switch_to_lyrics_page)
        # 连接搜索页面的信号
        self.search_page.selected_song.connect(self.switch_to_lyrics_page)
        # 连接歌词页面返回随机页面的信号
        self.lyrics_page.back_to_random.connect(self.switch_to_random_song_page)
        # 连接歌词页面返回搜索页面的信号
        self.lyrics_page.back_to_search.connect(self.switch_to_search_page)

        # 自动最大化窗口
        self.showMaximized()

    def switch_to_random_song_page(self):
        """切换到随机歌曲页面"""
        self.stack.setCurrentWidget(self.random_song_page)

    def switch_to_search_page(self):
        """切换到搜索页面"""
        self.stack.setCurrentWidget(self.search_page)

    def switch_to_lyrics_page(self, song_name):
        """切换到歌词页面"""
        self.lyrics_page.load_lyrics(song_name)
        
        # 根据当前页面设置来源标记
        if isinstance(self.centralWidget().currentWidget(), SearchPage):
            self.lyrics_page.set_from_search_page(True)
        elif isinstance(self.centralWidget().currentWidget(), RandomSongPage):
            self.lyrics_page.set_from_random_page(True)
        else:
            # 默认情况下重置所有标记（从播放控制页面进入）
            self.lyrics_page.reset_source_flags()
            
        self.stack.setCurrentWidget(self.lyrics_page)

    def switch_to_fixed_playlist_page(self):
        """切换到固定歌单页面"""
        self.stack.setCurrentWidget(self.fixed_playlist_page)

    def switch_to_playback_control_page(self, playlist_name=None):
        """切换到播放控制页面"""
        if playlist_name and playlist_name in PLAYLIST_COLLECTION:
            self.playback_control_page = PlaybackControlPage(
                playlist_name, self.switch_to_lyrics_page, self.switch_to_launch_page
            )
            self.stack.addWidget(self.playback_control_page)
            self.stack.setCurrentWidget(self.playback_control_page)
        else:
            if hasattr(self, 'playback_control_page'):
                self.stack.setCurrentWidget(self.playback_control_page)

    def switch_to_launch_page(self):
        """切换回启动页面"""
        self.stack.setCurrentWidget(self.launch_page)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序发生错误: {e}")
        sys.exit(1)  # 确保程序完全退出
    finally:
        # 确保清理所有资源
        if 'app' in locals():
            app.quit()
        sys.exit(0)  # 正常退出程序