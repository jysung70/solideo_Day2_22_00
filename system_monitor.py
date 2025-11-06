#!/usr/bin/env python3
"""
시스템 리소스 실시간 모니터링 시스템
메인 애플리케이션
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime, timedelta

from data_collector import SystemDataCollector
from pdf_generator import PDFReportGenerator


class SystemMonitorGUI:
    """시스템 모니터 GUI 애플리케이션"""

    def __init__(self, root):
        self.root = root
        self.root.title("시스템 리소스 실시간 모니터링 시스템")
        self.root.geometry("1400x900")

        # 데이터 수집기
        self.collector = SystemDataCollector(max_samples=300)

        # 모니터링 상태
        self.monitoring = False
        self.start_time = None
        self.monitoring_duration = 300  # 5분 (초)

        # UI 구성
        self._create_ui()

        # 업데이트 스레드
        self.update_thread = None
        self.running = True

        # 그래프 업데이트 시작
        self._start_update_loop()

    def _create_ui(self):
        """UI 구성"""
        # 상단: 제어 패널
        self._create_control_panel()

        # 중단: 실시간 수치 대시보드
        self._create_dashboard()

        # 하단: 실시간 그래프
        self._create_graphs()

    def _create_control_panel(self):
        """제어 패널 생성"""
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), columnspan=2)

        # 시작/중지 버튼
        self.start_btn = ttk.Button(
            control_frame,
            text="모니터링 시작",
            command=self._start_monitoring
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="모니터링 중지",
            command=self._stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)

        # PDF 생성 버튼
        self.pdf_btn = ttk.Button(
            control_frame,
            text="PDF 보고서 생성",
            command=self._generate_pdf,
            state=tk.DISABLED
        )
        self.pdf_btn.grid(row=0, column=2, padx=5)

        # 타이머 표시
        self.timer_label = ttk.Label(
            control_frame,
            text="경과 시간: 0초 / 300초",
            font=('Arial', 12, 'bold')
        )
        self.timer_label.grid(row=0, column=3, padx=20)

        # 상태 표시
        self.status_label = ttk.Label(
            control_frame,
            text="상태: 대기 중",
            font=('Arial', 10)
        )
        self.status_label.grid(row=0, column=4, padx=20)

    def _create_dashboard(self):
        """실시간 수치 대시보드 생성"""
        dashboard_frame = ttk.LabelFrame(self.root, text="실시간 리소스 현황", padding="10")
        dashboard_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=2, padx=10, pady=10)

        # 2열 레이아웃
        # CPU
        ttk.Label(dashboard_frame, text="CPU 사용률:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cpu_value = ttk.Label(dashboard_frame, text="0.00 %", font=('Arial', 11), foreground='red')
        self.cpu_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # 메모리
        ttk.Label(dashboard_frame, text="메모리 사용률:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mem_value = ttk.Label(dashboard_frame, text="0.00 %", font=('Arial', 11), foreground='blue')
        self.mem_value.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # 메모리 상세
        ttk.Label(dashboard_frame, text="메모리 사용/가능:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.mem_detail = ttk.Label(dashboard_frame, text="0.00 GB / 0.00 GB", font=('Arial', 11))
        self.mem_detail.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # 디스크 I/O
        ttk.Label(dashboard_frame, text="디스크 읽기/쓰기:", font=('Arial', 11, 'bold')).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.disk_value = ttk.Label(dashboard_frame, text="0.00 / 0.00 MB/s", font=('Arial', 11), foreground='purple')
        self.disk_value.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # 네트워크
        ttk.Label(dashboard_frame, text="네트워크 송신/수신:", font=('Arial', 11, 'bold')).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.net_value = ttk.Label(dashboard_frame, text="0.00 / 0.00 MB/s", font=('Arial', 11), foreground='green')
        self.net_value.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        # CPU 온도 (선택)
        ttk.Label(dashboard_frame, text="CPU 온도:", font=('Arial', 11, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=20, pady=5)
        self.temp_value = ttk.Label(dashboard_frame, text="N/A", font=('Arial', 11))
        self.temp_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        # GPU (선택)
        ttk.Label(dashboard_frame, text="GPU 사용률:", font=('Arial', 11, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=20, pady=5)
        self.gpu_value = ttk.Label(dashboard_frame, text="N/A", font=('Arial', 11))
        self.gpu_value.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

    def _create_graphs(self):
        """실시간 그래프 생성"""
        graph_frame = ttk.LabelFrame(self.root, text="실시간 그래프", padding="10")
        graph_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=2, padx=10, pady=10)

        # Configure row/column weights for resizing
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Figure 생성 (2x2 그리드)
        self.fig = Figure(figsize=(14, 8))

        # 서브플롯
        self.ax_cpu = self.fig.add_subplot(2, 2, 1)
        self.ax_mem = self.fig.add_subplot(2, 2, 2)
        self.ax_net = self.fig.add_subplot(2, 2, 3)
        self.ax_disk = self.fig.add_subplot(2, 2, 4)

        # 초기 설정
        self._setup_graph(self.ax_cpu, "CPU Usage (%)", 'red')
        self._setup_graph(self.ax_mem, "Memory Usage (%)", 'blue')
        self._setup_graph(self.ax_net, "Network (MB/s)", 'green')
        self._setup_graph(self.ax_disk, "Disk I/O (MB/s)", 'purple')

        self.fig.tight_layout()

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _setup_graph(self, ax, ylabel, color):
        """그래프 초기 설정"""
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 300)
        ax.set_ylim(0, 100)

    def _update_graphs(self):
        """그래프 업데이트"""
        if len(self.collector.timestamps) == 0:
            return

        # 시간 축 (초 단위)
        time_axis = list(range(len(self.collector.timestamps)))

        # CPU 그래프
        self.ax_cpu.clear()
        self._setup_graph(self.ax_cpu, "CPU Usage (%)", 'red')
        self.ax_cpu.plot(time_axis, list(self.collector.cpu_percent), color='red', linewidth=1.5)
        self.ax_cpu.set_xlim(0, max(300, len(time_axis)))

        # 메모리 그래프
        self.ax_mem.clear()
        self._setup_graph(self.ax_mem, "Memory Usage (%)", 'blue')
        self.ax_mem.plot(time_axis, list(self.collector.memory_percent), color='blue', linewidth=1.5)
        self.ax_mem.set_xlim(0, max(300, len(time_axis)))

        # 네트워크 그래프
        self.ax_net.clear()
        self.ax_net.set_xlabel('Time (seconds)')
        self.ax_net.set_ylabel('Speed (MB/s)')
        self.ax_net.grid(True, alpha=0.3)
        self.ax_net.plot(time_axis, list(self.collector.net_sent), color='green', linewidth=1.5, label='Sent')
        self.ax_net.plot(time_axis, list(self.collector.net_recv), color='orange', linewidth=1.5, label='Recv')
        self.ax_net.legend(loc='upper right')
        self.ax_net.set_xlim(0, max(300, len(time_axis)))
        # 동적 y축
        max_net = max(max(self.collector.net_sent, default=1), max(self.collector.net_recv, default=1))
        self.ax_net.set_ylim(0, max_net * 1.1)

        # 디스크 I/O 그래프
        self.ax_disk.clear()
        self.ax_disk.set_xlabel('Time (seconds)')
        self.ax_disk.set_ylabel('Speed (MB/s)')
        self.ax_disk.grid(True, alpha=0.3)
        self.ax_disk.plot(time_axis, list(self.collector.disk_read), color='purple', linewidth=1.5, label='Read')
        self.ax_disk.plot(time_axis, list(self.collector.disk_write), color='pink', linewidth=1.5, label='Write')
        self.ax_disk.legend(loc='upper right')
        self.ax_disk.set_xlim(0, max(300, len(time_axis)))
        # 동적 y축
        max_disk = max(max(self.collector.disk_read, default=1), max(self.collector.disk_write, default=1))
        self.ax_disk.set_ylim(0, max_disk * 1.1)

        self.canvas.draw()

    def _update_dashboard(self):
        """대시보드 수치 업데이트"""
        current = self.collector.get_current_values()
        if current:
            self.cpu_value.config(text=f"{current['cpu']:.2f} %")
            self.mem_value.config(text=f"{current['memory']:.2f} %")
            self.mem_detail.config(text=f"{current['memory_used']:.2f} GB / {current['memory_available']:.2f} GB")
            self.disk_value.config(text=f"{current['disk_read']:.2f} / {current['disk_write']:.2f} MB/s")
            self.net_value.config(text=f"{current['net_sent']:.2f} / {current['net_recv']:.2f} MB/s")

            # CPU 온도
            if current['cpu_temp']:
                self.temp_value.config(text=f"{current['cpu_temp']:.1f} °C")
            else:
                self.temp_value.config(text="N/A")

            # GPU
            if current['gpu']:
                gpu_text = f"{current['gpu']['load']:.1f} % ({current['gpu']['temp']:.1f} °C)"
                self.gpu_value.config(text=gpu_text)
            else:
                self.gpu_value.config(text="N/A")

    def _update_timer(self):
        """타이머 업데이트"""
        if self.monitoring and self.start_time:
            elapsed = int((datetime.now() - self.start_time).total_seconds())
            self.timer_label.config(text=f"경과 시간: {elapsed}초 / {self.monitoring_duration}초")

            # 5분 경과 시 자동 중지
            if elapsed >= self.monitoring_duration:
                self._stop_monitoring()
                messagebox.showinfo("완료", "5분 모니터링이 완료되었습니다.\nPDF 보고서를 생성할 수 있습니다.")

    def _start_update_loop(self):
        """업데이트 루프 시작"""
        def update():
            while self.running:
                try:
                    self._update_dashboard()
                    self._update_graphs()
                    self._update_timer()
                except:
                    pass
                time.sleep(1)

        self.update_thread = threading.Thread(target=update, daemon=True)
        self.update_thread.start()

    def _start_monitoring(self):
        """모니터링 시작"""
        self.monitoring = True
        self.start_time = datetime.now()
        self.collector.start_collection()

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.pdf_btn.config(state=tk.DISABLED)
        self.status_label.config(text="상태: 모니터링 중...")

    def _stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False
        self.collector.stop_collection()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.pdf_btn.config(state=tk.NORMAL)
        self.status_label.config(text="상태: 중지됨")

    def _generate_pdf(self):
        """PDF 보고서 생성"""
        if len(self.collector.timestamps) < 10:
            messagebox.showwarning("경고", "충분한 데이터가 수집되지 않았습니다.\n최소 10초 이상 모니터링해주세요.")
            return

        try:
            self.status_label.config(text="상태: PDF 생성 중...")
            self.root.update()

            generator = PDFReportGenerator(self.collector)
            filename = generator.generate_report()

            if filename:
                messagebox.showinfo("성공", f"PDF 보고서가 생성되었습니다:\n{filename}")
                self.status_label.config(text="상태: PDF 생성 완료")
            else:
                messagebox.showerror("오류", "PDF 생성 중 오류가 발생했습니다.")
                self.status_label.config(text="상태: PDF 생성 실패")
        except Exception as e:
            messagebox.showerror("오류", f"PDF 생성 중 오류 발생:\n{str(e)}")
            self.status_label.config(text="상태: PDF 생성 실패")

    def on_closing(self):
        """윈도우 닫기"""
        if self.monitoring:
            if messagebox.askokcancel("종료", "모니터링이 진행 중입니다. 종료하시겠습니까?"):
                self.running = False
                self.collector.stop_collection()
                self.root.destroy()
        else:
            self.running = False
            self.root.destroy()


def main():
    """메인 함수"""
    root = tk.Tk()
    app = SystemMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
