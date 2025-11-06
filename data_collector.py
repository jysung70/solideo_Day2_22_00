"""
시스템 리소스 데이터 수집 모듈
"""

import psutil
import time
from datetime import datetime
from collections import deque
from threading import Thread, Event
import platform


class SystemDataCollector:
    """시스템 리소스 데이터를 수집하는 클래스"""

    def __init__(self, max_samples=300):
        """
        Args:
            max_samples: 최대 저장할 샘플 수 (기본 300개 = 5분)
        """
        self.max_samples = max_samples

        # 데이터 저장용 deque (자동으로 오래된 데이터 제거)
        self.timestamps = deque(maxlen=max_samples)
        self.cpu_percent = deque(maxlen=max_samples)
        self.cpu_per_core = deque(maxlen=max_samples)
        self.memory_percent = deque(maxlen=max_samples)
        self.memory_used = deque(maxlen=max_samples)
        self.memory_available = deque(maxlen=max_samples)
        self.disk_read = deque(maxlen=max_samples)
        self.disk_write = deque(maxlen=max_samples)
        self.net_sent = deque(maxlen=max_samples)
        self.net_recv = deque(maxlen=max_samples)

        # 선택 데이터
        self.cpu_temp = deque(maxlen=max_samples)
        self.gpu_info = deque(maxlen=max_samples)

        # 수집 제어
        self.is_running = False
        self.stop_event = Event()
        self.collection_thread = None

        # 초기 네트워크/디스크 카운터 값
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_net_io = psutil.net_io_counters()
        self.prev_time = time.time()

        # 시스템 정보 수집
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        """시스템 기본 정보 수집"""
        cpu_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory': psutil.virtual_memory().total,
        }

        try:
            import cpuinfo
            cpu_info['cpu_model'] = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown')
        except:
            cpu_info['cpu_model'] = platform.processor()

        return cpu_info

    def _collect_sample(self):
        """단일 샘플 수집"""
        current_time = time.time()
        time_delta = current_time - self.prev_time

        # 타임스탬프
        self.timestamps.append(datetime.now())

        # CPU
        self.cpu_percent.append(psutil.cpu_percent(interval=0))
        self.cpu_per_core.append(psutil.cpu_percent(interval=0, percpu=True))

        # 메모리
        mem = psutil.virtual_memory()
        self.memory_percent.append(mem.percent)
        self.memory_used.append(mem.used / (1024**3))  # GB
        self.memory_available.append(mem.available / (1024**3))  # GB

        # 디스크 I/O (속도 계산)
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io and self.prev_disk_io:
                read_speed = (disk_io.read_bytes - self.prev_disk_io.read_bytes) / time_delta / (1024**2)  # MB/s
                write_speed = (disk_io.write_bytes - self.prev_disk_io.write_bytes) / time_delta / (1024**2)  # MB/s
                self.disk_read.append(max(0, read_speed))
                self.disk_write.append(max(0, write_speed))
                self.prev_disk_io = disk_io
            else:
                self.disk_read.append(0)
                self.disk_write.append(0)
        except Exception as e:
            self.disk_read.append(0)
            self.disk_write.append(0)

        # 네트워크 트래픽 (속도 계산)
        try:
            net_io = psutil.net_io_counters()
            if net_io and self.prev_net_io:
                sent_speed = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / time_delta / (1024**2)  # MB/s
                recv_speed = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / time_delta / (1024**2)  # MB/s
                self.net_sent.append(max(0, sent_speed))
                self.net_recv.append(max(0, recv_speed))
                self.prev_net_io = net_io
            else:
                self.net_sent.append(0)
                self.net_recv.append(0)
        except Exception as e:
            self.net_sent.append(0)
            self.net_recv.append(0)

        # CPU 온도 (선택)
        temp = self._get_cpu_temperature()
        self.cpu_temp.append(temp)

        # GPU 정보 (선택)
        gpu = self._get_gpu_info()
        self.gpu_info.append(gpu)

        self.prev_time = current_time

    def _get_cpu_temperature(self):
        """CPU 온도 읽기 (가능한 경우)"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # coretemp (Intel) 또는 k10temp (AMD) 찾기
                for name, entries in temps.items():
                    if name in ['coretemp', 'k10temp', 'cpu_thermal']:
                        if entries:
                            return entries[0].current
            return None
        except:
            return None

    def _get_gpu_info(self):
        """GPU 정보 읽기 (NVIDIA GPU가 있는 경우)"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # 첫 번째 GPU
                return {
                    'load': gpu.load * 100,
                    'temp': gpu.temperature,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal
                }
        except:
            pass
        return None

    def _collection_loop(self):
        """데이터 수집 루프 (별도 스레드에서 실행)"""
        while not self.stop_event.is_set():
            self._collect_sample()
            time.sleep(1)  # 1초 대기

    def start_collection(self):
        """데이터 수집 시작"""
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.collection_thread = Thread(target=self._collection_loop, daemon=True)
            self.collection_thread.start()
            print("데이터 수집 시작")

    def stop_collection(self):
        """데이터 수집 중지"""
        if self.is_running:
            self.is_running = False
            self.stop_event.set()
            if self.collection_thread:
                self.collection_thread.join(timeout=2)
            print("데이터 수집 중지")

    def get_current_values(self):
        """현재 값 반환 (UI 표시용)"""
        if len(self.timestamps) == 0:
            return None

        return {
            'cpu': self.cpu_percent[-1] if self.cpu_percent else 0,
            'memory': self.memory_percent[-1] if self.memory_percent else 0,
            'memory_used': self.memory_used[-1] if self.memory_used else 0,
            'memory_available': self.memory_available[-1] if self.memory_available else 0,
            'disk_read': self.disk_read[-1] if self.disk_read else 0,
            'disk_write': self.disk_write[-1] if self.disk_write else 0,
            'net_sent': self.net_sent[-1] if self.net_sent else 0,
            'net_recv': self.net_recv[-1] if self.net_recv else 0,
            'cpu_temp': self.cpu_temp[-1] if self.cpu_temp and self.cpu_temp[-1] else None,
            'gpu': self.gpu_info[-1] if self.gpu_info and self.gpu_info[-1] else None,
        }

    def get_statistics(self):
        """통계 계산 (평균, 최소, 최대)"""
        if len(self.timestamps) == 0:
            return None

        def calc_stats(data):
            if not data:
                return {'avg': 0, 'min': 0, 'max': 0}
            return {
                'avg': sum(data) / len(data),
                'min': min(data),
                'max': max(data)
            }

        return {
            'cpu': calc_stats(self.cpu_percent),
            'memory': calc_stats(self.memory_percent),
            'disk_read': calc_stats(self.disk_read),
            'disk_write': calc_stats(self.disk_write),
            'net_sent': calc_stats(self.net_sent),
            'net_recv': calc_stats(self.net_recv),
        }

    def get_top_processes(self, n=5):
        """리소스 사용 상위 N개 프로세스"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # CPU 기준 정렬
            cpu_top = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:n]

            # 메모리 기준 정렬
            mem_top = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:n]

            return {'cpu': cpu_top, 'memory': mem_top}
        except:
            return {'cpu': [], 'memory': []}
