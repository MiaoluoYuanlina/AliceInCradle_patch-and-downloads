#引用库
import threading
import time
import requests
import os
import ctypes
import ssl
import glob
from urllib import parse
from colorama import init
import shutil
from tqdm import tqdm
import tkinter as tk
from tkinter import messagebox
import webbrowser
import zipfile
import subprocess
import win32com.client
import sys
# 初始化 colorama
init(autoreset=True)

# -----------------------------------------------------------------------------------------------------------------------

#os.rmdir(r".\f")
debug_mode = True
#debug_mode = False

# -----------------------------------------------------------------------------------------------------------------------
#获取光标位置
def get_cursor_position():
    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", ctypes.c_ushort),
            ("srWindow", ctypes.c_int * 4),
            ("dwMaximumWindowSize", COORD)
        ]

    try:
        # 获取标准输出句柄
        hConsole = ctypes.windll.kernel32.GetStdHandle(-11)  # -11 是 STD_OUTPUT_HANDLE

        if hConsole == ctypes.c_void_p(-1).value:
            return -1

        # 获取控制台屏幕缓冲区信息
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if not ctypes.windll.kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi)):
            return -1

        # 获取光标位置，坐标从 0 开始
        return csbi.dwCursorPosition.X + 1, csbi.dwCursorPosition.Y + 1  # 转换为 1-based 索引

    except Exception as e:
        return -1

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
# 清屏以确保光标在已知位置
clear_screen()

def print_at_position(text, line, column):#自定义位置输出
    # 移动光标到指定位置
    print(f"\033[{line};{column}H{text}                              ")


# -----------------------------------------------------------------------------------------------------------------------
#调试输出
def print2(text):
    if debug_mode == True :
        print(text)

# -----------------------------------------------------------------------------------------------------------------------
#十六进制终端输出
def rgb_to_ansi256(r, g, b):
    """
    将 RGB 值转换为 ANSI 256 色码。
    """
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232

    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)
def colored_text_hex(text, hex_color):
    """
    将文本用指定的十六进制颜色显示。
    """
    # 提取 RGB 值
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    # 将 RGB 转换为 ANSI 256 色码
    ansi_color = rgb_to_ansi256(r, g, b)

    # 构建带颜色的字符串
    colored_text = f"\033[38;5;{ansi_color}m{text}\033[0m"

    return colored_text
# 示例用法
#text = "这是使用#FF5733颜色的文本"
#hex_color = "#FF5733"
#print(colored_text_hex(text, hex_color))
#-----------------------------------------------------------------------------------------------------------------------


#多线程下载 Github@DamageControlStudio https://github.com/DamageControlStudio/D2wnloader/blob/master/D2wnloader.py
# 忽略 https 警告
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()


class DLWorker:
    def __init__(self, name: str, url: str, range_start, range_end, cache_dir, finish_callback, user_agent):
        self.name = name
        self.url = url
        self.cache_filename = os.path.join(cache_dir, name + ".d2l")
        self.range_start = range_start  # 固定不动
        self.range_end = range_end  # 固定不动
        self.range_curser = range_start  # curser 所指尚未开始
        self.finish_callback = finish_callback  # 通知调用 DLWorker 的地方
        self.terminate_flag = False  # 该标志用于终结自己
        self.FINISH_TYPE = ""  # DONE 完成工作, HELP 需要帮忙, RETIRE 不干了
        self.user_agent = user_agent

    def __run(self):
        chunk_size = 1 * 1024  # 1 kb
        headers = {
            'User-Agent': self.user_agent, 
            'Range': f'Bytes={self.range_curser}-{self.range_end}', 
            'Accept-Encoding': '*'
        }
        req = requests.get(self.url, stream=True, verify=False, headers=headers)
        ####################################
        # Informational responses (100–199)
        # Successful responses (200–299)
        # Redirection messages (300–399)
        # Client error responses (400–499)
        # Server error responses (500–599)
        ####################################
        if 200 <= req.status_code <= 299:
            with open(self.cache_filename, "wb") as cache:
                for chunk in req.iter_content(chunk_size=chunk_size):
                    if self.terminate_flag:
                        break
                    cache.write(chunk)
                    self.range_curser += len(chunk)
        if not self.terminate_flag:  # 只有正常退出才能标记 DONE，但是三条途径都经过此处
            self.FINISH_TYPE = "DONE"
        req.close()
        self.finish_callback(self)  # 执行回调函数，根据 FINISH_TYPE 结局不同

    def get_cursor_position(): #获取终端位置
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", ctypes.c_int * 4),
                ("dwMaximumWindowSize", COORD)
            ]

        try:
            # 获取标准输出句柄
            hConsole = ctypes.windll.kernel32.GetStdHandle(-11)  # -11 是 STD_OUTPUT_HANDLE

            if hConsole == ctypes.c_void_p(-1).value:
                return -1

            # 获取控制台屏幕缓冲区信息
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            if not ctypes.windll.kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi)):
                return -1

            # 获取光标位置，坐标从 0 开始
            return csbi.dwCursorPosition.X + 1, csbi.dwCursorPosition.Y + 1  # 转换为 1-based 索引

        except Exception as e:
            return -1
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    clear_screen()



    def start(self):
        threading.Thread(target=self.__run).start()
    def help(self):
        self.FINISH_TYPE = "HELP"
        self.terminate_flag = True

    def retire(self):
        self.FINISH_TYPE = "RETIRE"
        self.terminate_flag = True

    def __lt__(self, another):
        """用于排序"""
        return self.range_start < another.range_start

    def get_progress(self):
        """获得进度"""
        _progress = {
            "curser": self.range_curser,
            "start": self.range_start,
            "end": self.range_end
        }
        return _progress


class D2wnloader:


    def __init__(self, url: str, download_dir: str = f".{os.sep}d2l{os.sep}", blocks_num: int = 8):
        assert 0 <= blocks_num <= 32
        self.url = url
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0'
        filename = self.url.split("/")[-1]
        filename = parse.unquote(filename)
        self.filename = filename
        self.download_dir = download_dir
        self.blocks_num = blocks_num
        self.__bad_url_flag = False
        self.file_size = self.__get_size()
        if not self.__bad_url_flag:
            # 建立下载目录
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
            # 建立缓存目录
            self.cache_dir = f".{os.sep}d2l{os.sep}.cache{os.sep}"
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
            # 分块下载
            self.startdlsince = time.time()
            self.workers = []  # 装载 DLWorker
            self.AAEK = self.__get_AAEK_from_cache()  # 需要确定 self.file_size 和 self.block_num
            # 测速
            self.__done = threading.Event()
            self.__download_record = []
            threading.Thread(target=self.__supervise).start()
            # 主进程信号，直到下载结束后解除
            self.__main_thread_done = threading.Event()
            # 显示基本信息
            readable_size = self.__get_readable_size(self.file_size)
            pathfilename = os.path.join(self.download_dir, self.filename)

    def __get_size(self):
        try:
            # req = request.urlopen(self.url)
            # content_length = req.headers["Content-Length"]
            # req.close()
            # return int(content_length)
            headers = {'User-Agent': self.user_agent}
            req = requests.get(self.url, headers=headers, stream=True)
            content_length = req.headers["Content-Length"]
            req.close()
            return int(content_length)
        except Exception as err:
            self.__bad_url_flag = True
            self.__whistleblower(f"[Error] {err}")
            return 0

    def __get_readable_size(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        K = 1024.0
        while size >= K:
            size = size / K
            unit_index += 1
        return "%.1f %s" % (size, units[unit_index])

    def __get_cache_filenames(self):
        return glob.glob(f"{self.cache_dir}{self.filename}.*.d2l")

    def __get_ranges_from_cache(self):
        # 形如 ./cache/filename.1120.d2l
        ranges = []
        for filename in self.__get_cache_filenames():
            size = os.path.getsize(filename)
            if size > 0:
                cache_start = int(filename.split(".")[-2])
                cache_end = cache_start + size - 1
                ranges.append((cache_start, cache_end))
        ranges.sort(key=lambda x: x[0])  # 排序
        return ranges

    def __get_AAEK_from_cache(self):
        ranges = self.__get_ranges_from_cache()  # 缓存文件里的数据
        AAEK = []  # 根据 ranges 和 self.file_size 生成 AAEK
        if len(ranges) == 0:
            AAEK.append((0, self.file_size - 1))
        else:
            for i, (start, end) in enumerate(ranges):
                if i == 0:
                    if start > 0:
                        AAEK.append((0, start - 1))
                next_start = self.file_size if i == len(ranges) - 1 else ranges[i + 1][0]
                if end < next_start - 1:
                    AAEK.append((end + 1, next_start - 1))
        return AAEK

    def __increase_ranges_slice(self, ranges: list, minimum_size=1024 * 1024):
        """增加分块数目，小于 minimum_size 就不再分割了"""
        assert len(ranges) > 0
        block_size = [end - start + 1 for start, end in ranges]
        index_of_max = block_size.index(max(block_size))
        start, end = ranges[index_of_max]
        halfsize = block_size[index_of_max] // 2
        if halfsize >= minimum_size:
            new_ranges = [x for i, x in enumerate(ranges) if i != index_of_max]
            new_ranges.append((start, start + halfsize))
            new_ranges.append((start + halfsize + 1, end))
        else:
            new_ranges = ranges
        return new_ranges

    def __ask_for_work(self, worker_num: int):
        """申请工作，返回 [work_range]，从 self.AAEK 中扣除。没工作的话返回 []。"""
        assert worker_num > 0
        task = []
        aaek_num = len(self.AAEK)
        if aaek_num == 0:  # 没任务了
            self.__share_the_burdern()
            return []
        if aaek_num >= worker_num:  # 数量充足，直接拿就行了
            for _ in range(worker_num):
                task.append(self.AAEK.pop(0))
        else:  # 数量不足，需要切割
            slice_num = worker_num - aaek_num  # 需要分割几次
            task = self.AAEK  # 这个时候 task 就不可能是 [] 了
            self.AAEK = []
            for _ in range(slice_num):
                task = self.__increase_ranges_slice(task)
        task.sort(key=lambda x: x[0])
        return task

    def __share_the_burdern(self, minimum_size=1024 * 1024):
        """找出工作最繁重的 worker，调用他的 help。回调函数中会将他的任务一分为二。"""
        max_size = 0
        max_size_name = ""
        for w in self.workers:
            p = w.get_progress()
            size = p["end"] - p["curser"] + 1
            if size > max_size:
                max_size = size
                max_size_name = w.name
        if max_size >= minimum_size:
            for w in self.workers:
                if w.name == max_size_name:
                    w.help()
                    break

    def __give_back_work(self, worker: DLWorker):
        """接纳没干完的工作。需要按 size 从小到大排序。"""
        progress = worker.get_progress()
        curser = progress["curser"]
        end = progress["end"]
        if curser <= end:  # 校验一下是否是合理值
            self.AAEK.append((curser, end))
            self.AAEK.sort(key=lambda x: x[0])

    def __give_me_a_worker(self, start, end):
        worker = DLWorker(name=f"{self.filename}.{start}",
                          url=self.url, range_start=start, range_end=end, cache_dir=self.cache_dir,
                          finish_callback=self.__on_dlworker_finish,
                          user_agent=self.user_agent)
        return worker

    def __whip(self, worker: DLWorker):
        """鞭笞新来的 worker，让他去工作"""
        self.workers.append(worker)
        self.workers.sort()
        worker.start()

    def __on_dlworker_finish(self, worker: DLWorker):
        assert worker.FINISH_TYPE != ""
        self.workers.remove(worker)
        if worker.FINISH_TYPE == "HELP":  # 外包
            self.__give_back_work(worker)
            self.workaholic(2)
        elif worker.FINISH_TYPE == "DONE":  # 完工
            # 再打一份工，也可能打不到
            self.workaholic(1)
        elif worker.FINISH_TYPE == "RETIRE":  # 撂挑子
            # 把工作添加回 AAEK，离职不管了。
            self.__give_back_work(worker)
        # 下载齐全，开始组装
        if self.workers == [] and self.__get_AAEK_from_cache() == []:
            green_text0 = f"\033[35m[下载进度]\033[0m"
            green_text1 = colored_text_hex(f"文件名:{self.filename}", "#cFFCCFF")
            green_text2 = f"\033[93m百分比:100.0%\033[0m"
            green_text3 = f"\033[94m下载速度:0.0/s\033[0m"
            green_text4 = f"\033[32m目前线程0\033[0m"
            text = f"{self.__get_readable_size(self.file_size)}/{self.__get_readable_size(self.file_size)}"
            hex_color = "#FF69B4"
            green_text5 = colored_text_hex(text, hex_color)
            green_text6 = f"\033[31m耗时:{(time.time() - self.startdlsince):.0f}秒\033[0m"
            text = "正在合并碎片文件"
            hex_color = "#FF5733"
            green_text7 = f" | " + colored_text_hex(text, hex_color)
            status_msg = f"\r{green_text0} \033[36m⇒\033[0m {green_text1} | {green_text2} | {green_text3} | {green_text4} | {green_text5} | {green_text6} {green_text7} \033[0m "
            self.__whistleblower(status_msg)
            #print(status_msg+"\n", end='', flush=True)
            self.__sew()
            green_text0 = f"\033[35m[下载进度]\033[0m"
            green_text1 = colored_text_hex(f"文件名:{self.filename}", "#cFFCCFF")
            green_text2 = f"\033[93m百分比:100.0%\033[0m"
            green_text3 = f"\033[94m下载速度:0.0/s\033[0m"
            green_text4 = f"\033[32m目前线程0\033[0m"
            text = f"{self.__get_readable_size(self.file_size)}/{self.__get_readable_size(self.file_size)}"
            hex_color = "#FF69B4"
            green_text5 = colored_text_hex(text, hex_color)
            green_text6 = f"\033[31m耗时:{(time.time() - self.startdlsince):.0f}秒\033[0m"
            text = "下载完成！"
            hex_color = "#FF5733"
            green_text7 = f" | " + colored_text_hex(text, hex_color)
            status_msg = f"\r{green_text0} \033[36m⇒\033[0m {green_text1} | {green_text2} | {green_text3} | {green_text4} | {green_text5} | {green_text6} {green_text7} \033[0m "
            self.__whistleblower(status_msg)
            #print(status_msg, end='', flush=True)
            #print("\n")

    def start(self):
        position = get_cursor_position()#光标位置
        X = -1
        Y = -1
        if isinstance(position, (tuple, list)) and len(position) == 2:
            X, Y = position
        else:
            # 处理错误或异常情况
            print("errors : 光标位置获取出错。")
        global terminalX
        global terminalY
        terminalX = int(X)
        terminalY = int(Y)
        if position == -1:
            print2("Error: 当前无法获取终端位置")
        else:
            print2(f"当前坐标: x={X}, y={Y}")


        green_text0 = f"\033[35m[下载进度]\033[0m"
        green_text1 = colored_text_hex(f"（*＾-＾*）", "#cFFCCFF")
        green_text2 = f"\033[93m(/≧▽≦)/)\033[0m"
        green_text3 = f"\033[94mᕕ(◠ڼ◠)ᕗ\033[0m"
        green_text4 = f"\033[32mヽ(✿ﾟ▽ﾟ)ノ\033[0m"
        text = f"_(‾▿◝_　)ﾉｼ"
        hex_color = "#FF69B4"
        green_text5 = colored_text_hex(text, hex_color)
        green_text6 = f"\033[31mCiallo～(∠・ω< )⌒☆\033[0m"
        text = "发出请求......"
        hex_color = "#FF5733"
        green_text7 = f" | " + colored_text_hex(text, hex_color)
        status_msg = f"\r{green_text0} \033[36m⇒\033[0m {green_text1} | {green_text2} | {green_text3} | {green_text4} | {green_text5} | {green_text6} {green_text7} \033[0m"
        self.__whistleblower(status_msg)

        # TODO 尝试整理缓存文件夹内的相关文件
        if not self.__bad_url_flag:
            # 召集 worker
            for start, end in self.__ask_for_work(self.blocks_num):
                worker = self.__give_me_a_worker(start, end)
                self.__whip(worker)
            # 卡住主进程
            self.__main_thread_done.wait()

    def stop(self):
        for w in self.workers:
            w.retire()
        while len(self.workers) != 0:
            time.sleep(0.5)
        self.AAEK = self.__get_AAEK_from_cache()

    def workaholic(self, n=1):
        """九九六工作狂。如果能申请到，就地解析；申请不到，__give_me_a_worker 会尝试将一个 worker 的工作一分为二；"""
        for s, e in self.__ask_for_work(n):
            worker = self.__give_me_a_worker(s, e)
            self.__whip(worker)

    def restart(self):
        self.stop()
        # 再次召集 worker。不调用 start 的原因是希望他继续卡住主线程。
        for start, end in self.__ask_for_work(self.blocks_num):
            worker = self.__give_me_a_worker(start, end)
            self.__whip(worker)

    def __supervise(self):
        """万恶的督导：监视下载速度、进程数；提出整改意见；"""
        REFRESH_INTERVAL = 1  # 每多久输出一次监视状态
        LAG_COUNT = 10  # 计算过去多少次测量的平均速度
        WAIT_TIMES_BEFORE_RESTART = 30  # 乘以时间就是等待多久执行一次 restart
        SPEED_DEGRADATION_PERCENTAGE = 0.5  # 速度下降百分比
        self.__download_record = []
        maxspeed = 0
        wait_times = WAIT_TIMES_BEFORE_RESTART
        while not self.__done.is_set():
            dwn_size = sum([os.path.getsize(cachefile) for cachefile in self.__get_cache_filenames()])
            self.__download_record.append({"timestamp": time.time(), "size": dwn_size})
            if len(self.__download_record) > LAG_COUNT:
                self.__download_record.pop(0)
            s = self.__download_record[-1]["size"] - self.__download_record[0]["size"]
            t = self.__download_record[-1]["timestamp"] - self.__download_record[0]["timestamp"]
            if not t == 0:
                speed = s / t
                readable_speed = self.__get_readable_size(speed)  # 变成方便阅读的样式
                percentage = self.__download_record[-1]["size"] / self.file_size * 100

                if speed > 0:
                    remaining_size = self.file_size - dwn_size
                    remaining_time = remaining_size / speed
                else:
                    remaining_time = float('inf')  # 如果速度为零，则预计时间为无限大

                # 将剩余时间转换为易读的格式
                remaining_time_str = self._format_remaining_time(remaining_time)

                # 将已下载大小和文件总大小显示出来
                readable_downloaded_size = self.__get_readable_size(dwn_size)
                readable_total_size = self.__get_readable_size(self.file_size)

                #显示进度
                #green_text0 = Fore.MAGENTA + f"\033[35m[下载进度]\033[0m"
                green_text0 = f"\033[35m[下载进度]\033[0m"
                green_text1 = colored_text_hex(f"文件名:{self.filename}", "#cFFCCFF")
                green_text2 = f"\033[93m百分比:{percentage:.1f}%\033[0m"
                green_text3 = f"\033[94m下载速度:{readable_speed}/s\033[0m"
                green_text4 = f"\033[32m目前线程{len(self.workers)}+{threading.active_count() - len(self.workers)}\033[0m"
                text = f"{readable_downloaded_size}/{readable_total_size}"
                hex_color = "#FF69B4"
                green_text5 = colored_text_hex(text, hex_color)
                green_text6 = f"\033[31m耗时:{(time.time() - self.startdlsince):.0f}秒\033[0m"
                green_text7 = f"\033[31m预计剩余时间:{remaining_time_str}\033[0m"
                green_text8 = f"" + colored_text_hex("接送数据", "#FF5733")
                status_msg = f"\r{green_text0} \033[36m⇒\033[0m {green_text1} | {green_text2} | {green_text3} | {green_text4} | {green_text5} | {green_text6} {green_text7} | {green_text8}\033[0m "

                #print(status_msg + "\n", end='', flush=True)
                self.__whistleblower(status_msg)
                # 监测下载速度下降
                maxspeed = max(maxspeed, speed)
                EPSILON = 1e-5  # 表示很小的值，避免除以零
                # 构建几个表达式用于简化逻辑，首先是前提条件
                time_over = wait_times < 0  # 容忍时间到了
                not_finished = not self.__done.is_set()  # 尚未完成下载
                # 情况 1. 速度在 1MB/s 以下，并且下降明显（如果速度在 1MB/s 以上可以先不管）
                speed_drops_significantly = (maxspeed - speed + EPSILON) / (maxspeed + EPSILON) > SPEED_DEGRADATION_PERCENTAGE
                speed_under_threshold = speed < 1024 * 1024  # 1MB
                scene_1 = speed_drops_significantly and speed_under_threshold
                # 情况 2. 速度很慢
                scene_2 = speed < 16 * 1024  # 16KB
                if time_over and not_finished and (scene_1 or scene_2):  # 若满足重启条件
                    self.__whistleblower("\r[下载进度] speed degradation, restarting...")
                    self.restart()
                    maxspeed = 0
                    wait_times = WAIT_TIMES_BEFORE_RESTART
                else:
                    wait_times -= 1
            time.sleep(REFRESH_INTERVAL)

    def __sew(self):
        self.__done.set()
        chunk_size = 10 * 1024 * 1024
        with open(f"{os.path.join(self.download_dir, self.filename)}", "wb") as f:
            for start, _ in self.__get_ranges_from_cache():
                cache_filename = f"{self.cache_dir}{self.filename}.{start}.d2l"
                with open(cache_filename, "rb") as cache_file:
                    data = cache_file.read(chunk_size)
                    while data:
                        f.write(data)
                        f.flush()
                        data = cache_file.read(chunk_size)
        self.clear()
        self.__main_thread_done.set()


    def __whistleblower(self, saying: str):
        if terminalY == -1:
            print(saying)
        else:
            print_at_position(saying, terminalY, 1)



        """
        if len(saying.replace("\r", "")) > wordsCountOfEachLine:
            sys.stdout.write(saying[:wordsCountOfEachLine])
        else:
            sys.stdout.write(saying + " " * (wordsCountOfEachLine - len(saying.replace("\r", ""))))
            """






    def md5(self):
        chunk_size = 1024 * 1024
        filename = f"{os.path.join(self.download_dir, self.filename)}"
        md5 = hashlib.md5()
        with open(filename, "rb") as f:
            data = f.read(chunk_size)
            while data:
                md5.update(data)
                data = f.read(chunk_size)
        return md5.hexdigest()

    def clear(self):
        for filename in self.__get_cache_filenames():
            os.remove(filename)

    def _format_remaining_time(self, seconds):
        #将剩余时间格式化为易读的格式
        if seconds == float('inf'):
            return "无法计算"
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}时{int(minutes)}分{int(seconds)}秒"

#-----------------------------------------------------------------------------------------------------------------------
import psutil

#获取盘符
def get_drives():
    partitions = psutil.disk_partitions()
    drives = [partition.device.upper() for partition in partitions]
    return drives

# 获取每个核心的 CPU 使用率
def get_cpu_usage_per_core():
    usage_per_core = psutil.cpu_percent(percpu=True, interval=1)
    return usage_per_core

# 获取总的 CPU 使用率
def get_total_cpu_usage():
    total_usage = psutil.cpu_percent(interval=1)
    return total_usage

#返回文件名
def extract_name(path):
    # 如果路径是文件
    if os.path.isfile(path):
        return os.path.basename(path)
    # 如果路径是文件夹
    elif os.path.isdir(path):
        return os.path.basename(os.path.normpath(path))
    else:
        return None  # 路径无效或类型不支持

#创建快捷方式
def create_shortcut(target_path, shortcut_path, working_directory=None, icon_path=None, description=None):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    if working_directory:
        shortcut.WorkingDirectory = working_directory
    if icon_path:
        shortcut.IconLocation = icon_path
    if description:
        shortcut.Description = description
    shortcut.save()



def get_valid_drive():
    drives = get_drives()
    return os.getcwd()


"""
    print(colored_text_hex("\n输入你要安装的盘符：", "#3498db"))
    for drive in drives:
        print(colored_text_hex(drive.rstrip(':/\\'),"#45b39d"))

    while True:
        user_input = input(colored_text_hex("\n输入一个字母：", "#3498d0")).strip().upper()

        matched_drive = None
        for drive in drives:
            if user_input in drive:
                matched_drive = drive
                break

        if matched_drive:
            Game_trails = matched_drive

            print(colored_text_hex("安装盘符: ", "#9b59b6")+colored_text_hex(f"{matched_drive}", "#8e44ad"))
            return drive
        else:
            print(colored_text_hex("输入的盘符无效，请重新输入。", "#ff9043"))
"""

#解压
def unzip_file(zip_path, extract_to):
    try:
        # 确保目标目录存在
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            for i, file_info in enumerate(zip_ref.infolist()):
                print(fr"{colored_text_hex("[解压]", "#9b59b6")} {colored_text_hex("⇒", "#2e86c1")} {colored_text_hex(fr"压缩包名:{extract_name(zip_path)}", "#f4d03f")} | {colored_text_hex(fr"文件数量:{i + 1}/{total_files}", "#27ae60")} | {colored_text_hex(fr"当前解压文件:{file_info.filename}", "#479be6")} | {colored_text_hex(fr"正在解压", "#ec7063")}")

                zip_ref.extract(file_info, extract_to)
            print(fr"{colored_text_hex("[解压]", "#9b59b6")} {colored_text_hex("⇒", "#2e86c1")} {colored_text_hex(fr"压缩包名:{extract_name(zip_path)}", "#f4d03f")} | {colored_text_hex(fr"文件数量:{i + 1}/{total_files}", "#27ae60")} | {colored_text_hex(fr"当前解压文件:{file_info.filename}", "#479be6")} | {colored_text_hex(fr"解压完成", "#ec7063")}")

    except PermissionError as e:
        print(fr"{colored_text_hex("[解压]", "#9b59b6")} {colored_text_hex("⇒", "#2e86c1")} {colored_text_hex(fr"压缩包名:{extract_name(zip_path)}", "#f4d03f")} | {colored_text_hex(fr"文件数量:{total_files}/{total_files}", "#27ae60")} | {colored_text_hex(fr"当前解压文件:{file_info.filename}", "#479be6")} | {colored_text_hex(fr"Error:目标没有访问权限", "#ec7063")}")
    except Exception as e:
        print(fr"{colored_text_hex("[解压]", "#9b59b6")} {colored_text_hex("⇒", "#2e86c1")} {colored_text_hex(fr"压缩包名:{extract_name(zip_path)}", "#f4d03f")} | {colored_text_hex(fr"文件数量:{total_files}/{total_files}", "#27ae60")} | {colored_text_hex(fr"当前解压文件:{file_info.filename}", "#479be6")} | {colored_text_hex(fr"Error:解压过程中下出错", "#ec7063")}")


#创建目录
from pathlib import Path
def create_directories(directory_path):
    path = Path(directory_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        print(f"目录 '{directory_path}' 已创建")
    except Exception as e:
        print(f"创建目录时发生错误: {e}")


if __name__ == "__main__":

    Game_trails = get_valid_drive()

    url = fr"https://dl.aliceincradle.dev/Win%20ver025f.zip"  # 下载地址
    download_dir = "./downloads/"  # 下载目录
    blocks_num = 16  # 自定义线程数量
    downloader = D2wnloader(url=url, download_dir=download_dir, blocks_num=blocks_num)
    downloader.start()  # 调用函数

    print(colored_text_hex("下载完成，正在解压文件。", "#9b59b6"))
    create_directories(fr"{Game_trails}\AliceInCradle")#创建文件夹

    unzip_file(fr'./downloads/Win ver025f.zip', fr"{Game_trails}\AliceInCradle")#解压



    print(colored_text_hex("正在创建快捷栏方式", "#9b59b6"))
    desktop_path = Path.home() # 获取桌面路径
    target = fr"{Game_trails}\AliceInCradle\Win ver025\AliceInCradle_ver025\AliceInCradle.exe"  # 快捷方式指向的目标文件
    shortcut = fr"{desktop_path}\Desktop\Alice In Cradle.lnk"  # 快捷方式的保存路径 #桌面
    working_dir = fr"{Game_trails}AliceInCradle\Win ver025\AliceInCradle_ver025"   # 可选的工作目录
    icon = "" #r"C:\Path\To\Your\Icon.ico"  # 可选的图标路径
    description = "Alice In Cradle"  # 可选的描述
    create_shortcut(target, shortcut, working_dir, icon, description) #调用函数 #桌面
    shortcut = fr"{desktop_path}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Alice In Cradle.lnk"  # 快捷方式的保存路径 #开始菜单
    create_shortcut(target, shortcut, working_dir, icon, description) #调用函数 #开始菜单
    print(colored_text_hex("安装完成啦~", "#9b59b6"))

    """
    if messagebox.askyesno("欧尼酱~有个问题要问您~", "是否安装 马赛克打咩~ 补丁？"):
        #subprocess.Popen(fr"{Game_trails}\AliceInCradle\Win ver025\AliceInCradle_ver025\AliceInCradle.exe")#启动游戏
        sys.exit(fr"{Game_trails}AliceInCradle\Win ver025\AliceInCradle_ver025\AliceInCradle.exe")
    else:
        sys.exit(0)
    """


"""
.\your_script.exe
$exitCode = $LASTEXITCODE
Write-Output "Exit Code: $exitCode"
"""








