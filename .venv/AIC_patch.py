#引用库
#多线程
import threading, time
from urllib import parse
import requests
import os
import sys
import glob
import hashlib
import ssl
import ctypes
import psutil
from colorama import init, Fore, Back, Style
import shutil
#程序所需
import time
#import os
import sys
import tkinter as tk
from tkinter import messagebox
import signal
import subprocess
import pefile
import webbrowser


import time, datetime, re, subprocess, sys, os, win32net, win32api, win32con, win32netcon, win32security, pymysql, time, \
    wmi, requests, ctypes, json
import schedule, shutil, datetime, time
import winreg, math
#from glob import glob
import subprocess as sp
import traceback, re

# 初始化 colorama
init(autoreset=True)



# -----------------------------------------------------------------------------------------------------------------------


debug_mode = False

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
#启动参数
startup_parameters_game = "0"


def main_startup_parameters():
    global startup_parameters_game

    # 获取启动参数
    args = sys.argv[1:]

    # 确保 index 变量已定义和初始化
    index = 1

    # 使用 while 循环遍历所有参数
    while index <= len(args):
        if args[index - 1] == "--game":
            index += 1
            if index <= len(args):  # 确保索引在范围内
                startup_parameters_game = args[index - 1]
                print(f"启动参数_游戏目录: {startup_parameters_game}")
        index += 1


if __name__ == "__main__":
    main_startup_parameters()

#-----------------------------------------------------------------------------------------------------------------------
#获取exe dll版本
def getFileVersion(file_name):
    try:
        info = win32api.GetFileVersionInfo(file_name, os.sep)
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = '%d.%d.%d.%d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
        return version
    except Exception as e:
        return "None"

if getattr(sys, 'frozen', False):
    # 如果是通过PyInstaller打包的
    executable_name = os.path.basename(sys.executable)
else:
    # 如果是在解释器中运行
    executable_name = os.path.basename(__file__)
    debug_mode = True
print("Executable name:", executable_name+"\n")

response = requests.get("https://api.xiaomiao-ica.top/AIC/new_edition.php")#git获取最新版
Vercontent = response.text.strip()  # 获取响应内容并去掉首尾空白
number = float(Vercontent)
current_version = getFileVersion(rf"{os.getcwd()}\{executable_name}")
print(colored_text_hex("\n免责声明：本程序仅供参考，技术分享。请勿用于非法用途商业用途！软件的使用没有任何担保责任\n", "#FF0000"))
print(colored_text_hex(f"目前版本:{current_version}", "#CFFCCF"))
print(colored_text_hex(f"最新版本:{Vercontent}", "#CFFCCF"))
print(colored_text_hex(rf"运行目录:{os.getcwd()}\{executable_name}", "#CFFCCF"))
print(colored_text_hex("\n\n作者信息:", "#b935ff"))
print(colored_text_hex("""https://space.bilibili.com/1775750067
https://www.xiaomiao-ica.top
https://twitter.com/XiaoMiao_ICa
mailto:xiaomiaoica@outlook.com
""", "#35eaff"))

#检测更新
if current_version < Vercontent :
    print(colored_text_hex("发现更新！", "#ff3560"))
    print(colored_text_hex("\033[40m推荐使用 windows powershell 脚本，自动获取最新版！", "#ff3560"))
    print(colored_text_hex("\033[40mirm", "#fffc43F")+colored_text_hex("\033[40m https://api.xiaomiao-ica.top/AICP.ps1 | ", "#FFFFFF")+colored_text_hex("\033[40miex", "#fffc43F"))
    print("\n")
    if messagebox.askyesno("欧尼酱~这里有一个问题哦~", f"有新的更新可用啦~\n你的版本{current_version}\n最新版本{Vercontent}\n是否前往更新？", icon='question'):
        webbrowser.open("https://www.xiaomiao-ica.top/index.php/alice-in-cradle/")
        sys.exit()  # 结束程序


if __name__ == "__main__":
    # PID 进程路径
    def get_process_pid_and_path(process_name):
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['pid'], proc.info['exe']
        return None, None

    # 上一级目录
    def get_parent_path(path):
        # 获取文件名或文件夹名
        base_name = os.path.basename(path)

        if os.path.isfile(path):
            return os.path.dirname(path)
        else:
            return os.path.dirname(path)

    # 检测文件夹大小
    def get_folder_size(folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

    # 关闭进程
    def kill_process(pid):
        try:
            os.kill(pid, signal.SIGTERM)  # 发送终止信号
            print(f"PID {pid} 已关闭。")
            return True
        except ProcessLookupError:
            print(f"未找到 PID 为 {pid} 的进程！")
            return False
        except PermissionError:
            print(f"结束PID {pid} 失败，因为权限不足！")
            return False




    # path = get_parent_path(Game_path)

    Game_pid = 0
    Game_path = ""

    if (startup_parameters_game == "0"):
        Game_pid, Game_path = get_process_pid_and_path("AliceInCradle.exe")
    else:
        Game_pid = 0
        Game_path = startup_parameters_game


    if Game_pid == None or Game_path == None : #检测失败结束游戏
        messagebox.showwarning("欧尼酱~出错啦~", "未能成功检测到游戏路径。\n请先打开游戏！", icon='warning')
        sys.exit()  # 结束程序

    print(colored_text_hex("游戏PID: ", "#32CD32") + colored_text_hex(f"{Game_pid}", "#00FF7F") + colored_text_hex(
        "\n游戏路径: ", "#32CD32") + colored_text_hex(f"{Game_path}", "#00FF7F"))

    # 获取文件夹大小（字节）
    file_size =  get_folder_size(get_parent_path(Game_path) + r"\AliceInCradle_Data\Managed")
    # 将文件大小转换为MB
    file_size_mb = file_size / (1024 * 1024)
    # 取小数点后两位
    file_size_mb_rounded = round(file_size_mb, 2)
    print2(f"游戏数据文件夹大小：{file_size_mb}MB")
    print2(f"游戏数据文件夹大小(大约)：{file_size_mb_rounded}MB")
    if abs(file_size_mb_rounded) == 23.62:#0.24g
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.24g", "#00FF7F"))
        Game_releases = "0.24g"
    elif abs(file_size_mb_rounded) == 25.76:#0.25a
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.25a", "#00FF7F"))
        Game_releases = "0.25a"
    elif abs(file_size_mb_rounded) == 25.77:#0.25b
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.25b", "#00FF7F"))
        Game_releases = "0.25b"
    elif abs(file_size_mb_rounded) == 25.79:#0.25c
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.25c", "#00FF7F"))
        Game_releases = "0.25c"
    elif abs(file_size_mb_rounded) == 25.81 :#0.25e
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.25e", "#00FF7F"))
        Game_releases = "0.25e"
    elif abs(file_size_mb_rounded) == 25.83 :#0.25f
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("0.25f", "#00FF7F"))
        Game_releases = "0.25f"
    elif abs(file_size_mb_rounded) == 0:#预留
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("未知", "#00FF7F"))
        Game_releases = "未知"
        sys.exit()  # 结束程序
    else:
        print(colored_text_hex("版本自动检测: ", "#32CD32") + colored_text_hex("未知", "#00FF7F"))
        Game_releases = "未知"

    #手动选择版本
    if Game_releases == "未知" :
        Verresponse = False
        if messagebox.askyesno("欧尼酱~出错啦~", "无法自动识别版本，可以尝试手动选择版本。\n是否手动选择版本？", icon='error'):
            Verresponse = False
        else:
            sys.exit()  # 结束程序
    else:
        if (startup_parameters_game == ""):
            if messagebox.askyesno("欧尼酱~这里有一个问题哦~",
                                   f"版本自动检测为{Game_releases}\n如果版本号不正确，是否手动选择版本？",
                                   icon='question'):
                Verresponse = True
            else:
                Verresponse2 = messagebox.askyesno("欧尼酱~出错啦~", "未能正常识别版本。\n是否手动选择版本？",
                                                   icon='error')
                Verresponse = True
                if Verresponse2:
                    Verresponse = False
                else:
                    sys.exit()  # 结束程序
        else:
            Verresponse = True


    if Verresponse:
        print("版本信息获取完成")
    else:
        print(fr"""
{colored_text_hex(f"编号1", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.24", "#1bf7fd")}{colored_text_hex(f"g", "#49acfd")}
{colored_text_hex(f"编号2", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.25", "#1bf7fd")}{colored_text_hex(f"a", "#49acfd")}
{colored_text_hex(f"编号3", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.25", "#1bf7fd")}{colored_text_hex(f"b", "#49acfd")}
{colored_text_hex(f"编号4", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.25", "#1bf7fd")}{colored_text_hex(f"c", "#49acfd")}
{colored_text_hex(f"编号5", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.25", "#1bf7fd")}{colored_text_hex(f"e", "#49acfd")}
{colored_text_hex(f"编号6", "#fe8de3")}{colored_text_hex(f" : ", "#fd7afe")}{colored_text_hex(f"0.25", "#1bf7fd")}{colored_text_hex(f"f", "#49acfd")}
""")
        while True:
            user_input = input("请输入游戏版本号对应的编号(1~6): ")
            try:
                number = int(user_input)
                if 1 <= number <= 10:
                    print(f"你输入的数字是: {number}")
                    break
                else:
                    print("输入不在范围之间，请重新输入。")
            except ValueError:
                print("输入无效，请输入一个数字。")

        if int(user_input) == 1:
            Game_releases = "0.24g"
        elif int(user_input) == 2:
            Game_releases = "0.25a"
        elif int(user_input) == 3:
            Game_releases = "0.25b"
        elif int(user_input) == 4:
            Game_releases = "0.25c"
        elif int(user_input) == 5:
            Game_releases = "0.25e"
        elif int(user_input) == 6:
            Game_releases = "0.25f"
        else:
            messagebox.askyesno("欧尼酱~出错啦~", "if判断结果未知错误。", icon="warning")
            sys.exit()  # 结束程序


    success = kill_process(Game_pid)#关闭游戏
    if success:
        print("")
    else:
        print(colored_text_hex("为能成功关闭游戏！安装不一定会成功！", "#FF0000"))

    #下载文件
    url = fr"https://api.xiaomiao-ica.top/AIC/{Game_releases}.dll" # 下载地址
    download_dir = "./downloads/"# 下载目录
    blocks_num = 8  # 自定义线程数量
    downloader = D2wnloader(url=url, download_dir=download_dir, blocks_num=blocks_num)
    downloader.start()# 调用函数

    # 替换文件
    if not os.path.isfile(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll"):
        raise FileNotFoundError(fr"源文件 {get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll 不存在。")
    # 如果目标文件已存在，删除它
    if os.path.isfile(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll"):
        # 把dll读入内存
        with open(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll", 'rb') as file:
            Game_fileDLL = file.read()




        print(fr"删除 {get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll")
        removeDLL = os.remove(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll")
    # 复制文件
    if shutil.copy2(fr"./downloads/{Game_releases}.dll", fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll"):
        print(
            rf"文件已从 ./downloads/{Game_releases}.dll 复制到 {get_parent_path(Game_path)}\AliceInCradle_Data\Managed\Assembly-CSharp.dll。")
    else:
        sys.exit()  # 结束程序
        if removeDLL :
            with open(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\Managed", 'wb') as file:#把DLL从内存读出
                if file.write(Game_fileDLL) :
                    print(colored_text_hex("替换文件失败！且将原DLL写出失败，Assembly-CSharp.dll删除成功，游戏数据已经损坏！但放心，存档是不会出现问题的，前往官网 https://nanamehacha.dev 重新下载即可。", "#FF0000"))
                    messagebox.askyesno("替换文件失败！且将原DLL写出失败，Assembly-CSharp.dll删除成功，游戏数据已经损坏！\n但放心，存档是不会出现问题的，前往官网 https://nanamehacha.dev 重新下载即可。", icon="warning")
                    sys.exit()  # 结束程序

    #声明
    txt_herald = """
// ========================================================
// 补丁追加
// https://www.xiaomiao-ica.wiki/index.php/2024/04/28/aliceincradle_patch/
// https://space.bilibili.com/1775750067
// ========================================================
/* ___ SaveDataDesc_auto  ___ */
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color="#E70B0B"  size="15px">补丁程序包括游戏都免费为爱发电~
如果你是购买而来的，证明你被骗啦~</font>
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color=#0800F7>游</font><font color=#1000EF>戏</font><font color=#1800E7>官</font><font color=#2000DF>网</font><font color=#2800D7>:</font><font color=#3000CF>h</font><font color=#3800C7>t</font><font color=#4000BF>t</font><font color=#4800B7>p</font><font color=#5000AF>s</font><font color=#5800A7>:</font><font color=#60009F>/</font><font color=#680097>/</font><font color=#70008F>a</font><font color=#780087>l</font><font color=#80007F>i</font><font color=#880077>c</font><font color=#90006F>e</font><font color=#980067>i</font><font color=#A0005F>n</font><font color=#A80057>c</font><font color=#B0004F>r</font><font color=#B80047>a</font><font color=#C0003F>d</font><font color=#C80037>l</font><font color=#D0002F>e</font><font color=#D80027>.</font><font color=#E0001F>d</font><font color=#E80017>e</font><font color=#F0000F>v</font><font color=#F80007>/</font>
<font color=#FD04F9>补</font><font color=#FB08F3>丁</font><font color=#F90CED>制</font><font color=#F710E7>作</font><font color=#F514E1>:</font><font color=#F318DB>h</font><font color=#F11CD5>t</font><font color=#EF20CF>t</font><font color=#ED24C9>p</font><font color=#EB28C3>s</font><font color=#E92CBD>:</font><font color=#E730B7>/</font><font color=#E534B1>/</font><font color=#E338AB>s</font><font color=#E13CA5>p</font><font color=#DF409F>a</font><font color=#DD4499>c</font><font color=#DB4893>e</font><font color=#D94C8D>.</font><font color=#D75087>b</font><font color=#D55481>i</font><font color=#D3587B>l</font><font color=#D15C75>i</font><font color=#CF606F>b</font><font color=#CD6469>i</font><font color=#CB6863>l</font><font color=#C96C5D>i</font><font color=#C77057>.</font><font color=#C57451>c</font><font color=#C3784B>o</font><font color=#C17C45>m</font><font color=#BF803F>/</font><font color=#BD8439>1</font><font color=#BB8833>7</font><font color=#B98C2D>7</font><font color=#B79027>5</font><font color=#B59421>7</font><font color=#B3981B>5</font><font color=#B19C15>0</font><font color=#AFA00F>0</font><font color=#ADA409>6</font><font color=#ABA803>7</font>
感谢您的游玩！

/* ___ SaveDataDesc  ___ */
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color="#E70B0B"  size="15px">补丁程序包括游戏都免费为爱发电~
如果你是购买而来的，证明你被骗啦~</font>
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color=#0800F7>游</font><font color=#1000EF>戏</font><font color=#1800E7>官</font><font color=#2000DF>网</font><font color=#2800D7>:</font><font color=#3000CF>h</font><font color=#3800C7>t</font><font color=#4000BF>t</font><font color=#4800B7>p</font><font color=#5000AF>s</font><font color=#5800A7>:</font><font color=#60009F>/</font><font color=#680097>/</font><font color=#70008F>a</font><font color=#780087>l</font><font color=#80007F>i</font><font color=#880077>c</font><font color=#90006F>e</font><font color=#980067>i</font><font color=#A0005F>n</font><font color=#A80057>c</font><font color=#B0004F>r</font><font color=#B80047>a</font><font color=#C0003F>d</font><font color=#C80037>l</font><font color=#D0002F>e</font><font color=#D80027>.</font><font color=#E0001F>d</font><font color=#E80017>e</font><font color=#F0000F>v</font><font color=#F80007>/</font>
<font color=#FD04F9>补</font><font color=#FB08F3>丁</font><font color=#F90CED>制</font><font color=#F710E7>作</font><font color=#F514E1>:</font><font color=#F318DB>h</font><font color=#F11CD5>t</font><font color=#EF20CF>t</font><font color=#ED24C9>p</font><font color=#EB28C3>s</font><font color=#E92CBD>:</font><font color=#E730B7>/</font><font color=#E534B1>/</font><font color=#E338AB>s</font><font color=#E13CA5>p</font><font color=#DF409F>a</font><font color=#DD4499>c</font><font color=#DB4893>e</font><font color=#D94C8D>.</font><font color=#D75087>b</font><font color=#D55481>i</font><font color=#D3587B>l</font><font color=#D15C75>i</font><font color=#CF606F>b</font><font color=#CD6469>i</font><font color=#CB6863>l</font><font color=#C96C5D>i</font><font color=#C77057>.</font><font color=#C57451>c</font><font color=#C3784B>o</font><font color=#C17C45>m</font><font color=#BF803F>/</font><font color=#BD8439>1</font><font color=#BB8833>7</font><font color=#B98C2D>7</font><font color=#B79027>5</font><font color=#B59421>7</font><font color=#B3981B>5</font><font color=#B19C15>0</font><font color=#AFA00F>0</font><font color=#ADA409>6</font><font color=#ABA803>7</font>
感谢您的游玩！

/* ___ SaveDataDesc_Empty_auto ___ */
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color="#E70B0B"  size="15px">补丁程序包括游戏都免费为爱发电~
如果你是购买而来的，证明你被骗啦~</font>
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color=#0800F7>游</font><font color=#1000EF>戏</font><font color=#1800E7>官</font><font color=#2000DF>网</font><font color=#2800D7>:</font><font color=#3000CF>h</font><font color=#3800C7>t</font><font color=#4000BF>t</font><font color=#4800B7>p</font><font color=#5000AF>s</font><font color=#5800A7>:</font><font color=#60009F>/</font><font color=#680097>/</font><font color=#70008F>a</font><font color=#780087>l</font><font color=#80007F>i</font><font color=#880077>c</font><font color=#90006F>e</font><font color=#980067>i</font><font color=#A0005F>n</font><font color=#A80057>c</font><font color=#B0004F>r</font><font color=#B80047>a</font><font color=#C0003F>d</font><font color=#C80037>l</font><font color=#D0002F>e</font><font color=#D80027>.</font><font color=#E0001F>d</font><font color=#E80017>e</font><font color=#F0000F>v</font><font color=#F80007>/</font>
<font color=#FD04F9>补</font><font color=#FB08F3>丁</font><font color=#F90CED>制</font><font color=#F710E7>作</font><font color=#F514E1>:</font><font color=#F318DB>h</font><font color=#F11CD5>t</font><font color=#EF20CF>t</font><font color=#ED24C9>p</font><font color=#EB28C3>s</font><font color=#E92CBD>:</font><font color=#E730B7>/</font><font color=#E534B1>/</font><font color=#E338AB>s</font><font color=#E13CA5>p</font><font color=#DF409F>a</font><font color=#DD4499>c</font><font color=#DB4893>e</font><font color=#D94C8D>.</font><font color=#D75087>b</font><font color=#D55481>i</font><font color=#D3587B>l</font><font color=#D15C75>i</font><font color=#CF606F>b</font><font color=#CD6469>i</font><font color=#CB6863>l</font><font color=#C96C5D>i</font><font color=#C77057>.</font><font color=#C57451>c</font><font color=#C3784B>o</font><font color=#C17C45>m</font><font color=#BF803F>/</font><font color=#BD8439>1</font><font color=#BB8833>7</font><font color=#B98C2D>7</font><font color=#B79027>5</font><font color=#B59421>7</font><font color=#B3981B>5</font><font color=#B19C15>0</font><font color=#AFA00F>0</font><font color=#ADA409>6</font><font color=#ABA803>7</font>
感谢您的游玩！

/* ___ SaveDataDesc_Empty ___ */
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color="#E70B0B"  size="15px">补丁程序包括游戏都免费为爱发电~
如果你是购买而来的，证明你被骗啦~</font>
<font color=#963AFC>—</font><font color=#9341F9>—</font><font color=#9048F6>—</font><font color=#8D4FF3>—</font><font color=#8A56F0>—</font><font color=#875DED>—</font><font color=#8464EA>—</font><font color=#816BE7>—</font><font color=#7E72E4>—</font><font color=#7B79E1>—</font><font color=#7880DE>—</font><font color=#7587DB>—</font><font color=#728ED8>—</font><font color=#6F95D5>—</font><font color=#6C9CD2>—</font><font color=#69A3CF>—</font><font color=#66AACC>—</font><font color=#63B1C9>—</font><font color=#60B8C6>—</font><font color=#5DBFC3>—</font><font color=#5AC6C0>—</font><font color=#57CDBD>—</font><font color=#54D4BA>—</font><font color=#51DBB7>—</font><font color=#4EE2B4>—</font><font color=#4BE9B1>—</font><font color=#48F0AE>—</font><font color=#45F7AB>—</font><font color=#42FEA8>—</font>
<font color=#0800F7>游</font><font color=#1000EF>戏</font><font color=#1800E7>官</font><font color=#2000DF>网</font><font color=#2800D7>:</font><font color=#3000CF>h</font><font color=#3800C7>t</font><font color=#4000BF>t</font><font color=#4800B7>p</font><font color=#5000AF>s</font><font color=#5800A7>:</font><font color=#60009F>/</font><font color=#680097>/</font><font color=#70008F>a</font><font color=#780087>l</font><font color=#80007F>i</font><font color=#880077>c</font><font color=#90006F>e</font><font color=#980067>i</font><font color=#A0005F>n</font><font color=#A80057>c</font><font color=#B0004F>r</font><font color=#B80047>a</font><font color=#C0003F>d</font><font color=#C80037>l</font><font color=#D0002F>e</font><font color=#D80027>.</font><font color=#E0001F>d</font><font color=#E80017>e</font><font color=#F0000F>v</font><font color=#F80007>/</font>
<font color=#FD04F9>补</font><font color=#FB08F3>丁</font><font color=#F90CED>制</font><font color=#F710E7>作</font><font color=#F514E1>:</font><font color=#F318DB>h</font><font color=#F11CD5>t</font><font color=#EF20CF>t</font><font color=#ED24C9>p</font><font color=#EB28C3>s</font><font color=#E92CBD>:</font><font color=#E730B7>/</font><font color=#E534B1>/</font><font color=#E338AB>s</font><font color=#E13CA5>p</font><font color=#DF409F>a</font><font color=#DD4499>c</font><font color=#DB4893>e</font><font color=#D94C8D>.</font><font color=#D75087>b</font><font color=#D55481>i</font><font color=#D3587B>l</font><font color=#D15C75>i</font><font color=#CF606F>b</font><font color=#CD6469>i</font><font color=#CB6863>l</font><font color=#C96C5D>i</font><font color=#C77057>.</font><font color=#C57451>c</font><font color=#C3784B>o</font><font color=#C17C45>m</font><font color=#BF803F>/</font><font color=#BD8439>1</font><font color=#BB8833>7</font><font color=#B98C2D>7</font><font color=#B79027>5</font><font color=#B59421>7</font><font color=#B3981B>5</font><font color=#B19C15>0</font><font color=#AFA00F>0</font><font color=#ADA409>6</font><font color=#ABA803>7</font>
感谢您的游玩！
"""
    with open(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\StreamingAssets\localization\zh-cn\zh-cn_tx.txt", 'r', encoding='utf-8') as file:
        Game_rawtext = file.read()
    if Game_rawtext.find(txt_herald) != -1:
        print("")
    else:
        Game_rawtext = Game_rawtext.replace('（空）', '')
        Game_rawtext = Game_rawtext.replace('存档 &1', '')
        Game_rawtext = Game_rawtext.replace('暂无自动存档。', '')
        Game_rawtext = Game_rawtext + "\n" + txt_herald

        with open(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\StreamingAssets\localization\zh-cn\zh-cn_tx.txt", 'w', encoding='utf-8') as file:
            file.write(Game_rawtext)

            # 判断是否替换成功
            with open(fr"{get_parent_path(Game_path)}\AliceInCradle_Data\StreamingAssets\localization\zh-cn\zh-cn_tx.txt", 'r', encoding='utf-8') as file:
                updated_text = file.read()
            if Game_rawtext == Game_rawtext :
                print("")
            else:
                messagebox.askyesno("部分替换文件失败！游戏可能会出现错误！\n但放心，存档是不会出现问题的，前往官网 https://nanamehacha.dev 重新下载即可。", icon="warning")
    #重新游戏游戏。
    subprocess.Popen(Game_path)











