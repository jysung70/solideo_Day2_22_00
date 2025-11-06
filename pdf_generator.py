"""
PDF 보고서 생성 모듈
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')  # 백그라운드 모드
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io


class PDFReportGenerator:
    """PDF 보고서 생성 클래스"""

    def __init__(self, data_collector):
        """
        Args:
            data_collector: SystemDataCollector 인스턴스
        """
        self.collector = data_collector
        self.filename = None
        self.story = []

        # 한글 폰트 등록 시도
        self._register_korean_font()

    def _register_korean_font(self):
        """한글 폰트 등록"""
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
            '/System/Library/Fonts/AppleGothic.ttf',
            'C:\\Windows\\Fonts\\malgun.ttf',
        ]

        self.korean_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    self.korean_font = 'Korean'
                    print(f"한글 폰트 등록 성공: {font_path}")
                    break
                except:
                    continue

        if not self.korean_font:
            print("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
            self.korean_font = 'Helvetica'

    def _get_style(self, font_size=12, bold=False):
        """텍스트 스타일 생성"""
        font_name = self.korean_font
        if bold and self.korean_font == 'Helvetica':
            font_name = 'Helvetica-Bold'

        return ParagraphStyle(
            'CustomStyle',
            fontName=font_name,
            fontSize=font_size,
            leading=font_size * 1.2,
        )

    def _create_cover_page(self):
        """표지 페이지 생성"""
        # 제목
        title_style = self._get_style(font_size=24, bold=True)
        title = Paragraph("시스템 리소스 모니터링 보고서", title_style)
        self.story.append(Spacer(1, 3*cm))
        self.story.append(title)
        self.story.append(Spacer(1, 1*cm))

        # 모니터링 기간
        if self.collector.timestamps:
            start_time = self.collector.timestamps[0].strftime('%Y-%m-%d %H:%M:%S')
            end_time = self.collector.timestamps[-1].strftime('%Y-%m-%d %H:%M:%S')
            duration = len(self.collector.timestamps)

            info_style = self._get_style(font_size=12)
            info_text = f"""
            <b>모니터링 기간:</b><br/>
            시작: {start_time}<br/>
            종료: {end_time}<br/>
            수집 샘플: {duration}개 ({duration} 초)<br/>
            """
            info = Paragraph(info_text, info_style)
            self.story.append(info)
            self.story.append(Spacer(1, 1*cm))

        # 시스템 정보
        sys_info = self.collector.system_info
        sys_text = f"""
        <b>시스템 정보:</b><br/>
        운영체제: {sys_info['platform']} {sys_info['platform_release']}<br/>
        CPU: {sys_info['cpu_model']}<br/>
        CPU 코어: {sys_info['cpu_count']}개 (논리: {sys_info['cpu_count_logical']}개)<br/>
        총 메모리: {sys_info['total_memory'] / (1024**3):.2f} GB<br/>
        """
        sys_info_para = Paragraph(sys_text, self._get_style(font_size=11))
        self.story.append(sys_info_para)

        self.story.append(PageBreak())

    def _create_summary_table(self):
        """요약 통계 표 생성"""
        title_style = self._get_style(font_size=16, bold=True)
        title = Paragraph("요약 통계", title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*cm))

        stats = self.collector.get_statistics()
        if not stats:
            return

        # 표 데이터
        data = [
            ['리소스', '평균', '최소', '최대', '단위'],
            ['CPU 사용률', f"{stats['cpu']['avg']:.2f}", f"{stats['cpu']['min']:.2f}",
             f"{stats['cpu']['max']:.2f}", '%'],
            ['메모리 사용률', f"{stats['memory']['avg']:.2f}", f"{stats['memory']['min']:.2f}",
             f"{stats['memory']['max']:.2f}", '%'],
            ['디스크 읽기', f"{stats['disk_read']['avg']:.2f}", f"{stats['disk_read']['min']:.2f}",
             f"{stats['disk_read']['max']:.2f}", 'MB/s'],
            ['디스크 쓰기', f"{stats['disk_write']['avg']:.2f}", f"{stats['disk_write']['min']:.2f}",
             f"{stats['disk_write']['max']:.2f}", 'MB/s'],
            ['네트워크 송신', f"{stats['net_sent']['avg']:.2f}", f"{stats['net_sent']['min']:.2f}",
             f"{stats['net_sent']['max']:.2f}", 'MB/s'],
            ['네트워크 수신', f"{stats['net_recv']['avg']:.2f}", f"{stats['net_recv']['min']:.2f}",
             f"{stats['net_recv']['max']:.2f}", 'MB/s'],
        ]

        # 표 스타일
        table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        self.story.append(table)
        self.story.append(PageBreak())

    def _create_graph(self, title, x_data, y_data, y_label, color, y_data2=None, label1='', label2='', color2=None):
        """그래프 생성 및 이미지로 변환"""
        fig, ax = plt.subplots(figsize=(10, 4))

        # 시간 축 (초 단위)
        time_axis = list(range(len(x_data)))

        # 첫 번째 데이터
        ax.plot(time_axis, y_data, color=color, linewidth=1.5, label=label1 if label1 else None)

        # 두 번째 데이터 (있는 경우)
        if y_data2 is not None and color2:
            ax.plot(time_axis, y_data2, color=color2, linewidth=1.5, label=label2)
            ax.legend(loc='upper right')

        ax.set_xlabel('Time (seconds)', fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 이미지로 변환
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close(fig)

        return buf

    def _add_graphs(self):
        """모든 그래프 추가"""
        if not self.collector.timestamps:
            return

        # CPU 그래프
        title_style = self._get_style(font_size=16, bold=True)
        self.story.append(Paragraph("시계열 그래프", title_style))
        self.story.append(Spacer(1, 0.5*cm))

        # CPU 사용률
        cpu_graph = self._create_graph(
            'CPU Usage',
            self.collector.timestamps,
            list(self.collector.cpu_percent),
            'CPU (%)',
            'red'
        )
        self.story.append(Image(cpu_graph, width=15*cm, height=6*cm))
        self.story.append(Spacer(1, 0.5*cm))

        # 메모리 사용률
        mem_graph = self._create_graph(
            'Memory Usage',
            self.collector.timestamps,
            list(self.collector.memory_percent),
            'Memory (%)',
            'blue'
        )
        self.story.append(Image(mem_graph, width=15*cm, height=6*cm))
        self.story.append(PageBreak())

        # 네트워크 트래픽
        net_graph = self._create_graph(
            'Network Traffic',
            self.collector.timestamps,
            list(self.collector.net_sent),
            'Speed (MB/s)',
            'green',
            y_data2=list(self.collector.net_recv),
            label1='Sent',
            label2='Received',
            color2='orange'
        )
        self.story.append(Image(net_graph, width=15*cm, height=6*cm))
        self.story.append(Spacer(1, 0.5*cm))

        # 디스크 I/O
        disk_graph = self._create_graph(
            'Disk I/O',
            self.collector.timestamps,
            list(self.collector.disk_read),
            'Speed (MB/s)',
            'purple',
            y_data2=list(self.collector.disk_write),
            label1='Read',
            label2='Write',
            color2='pink'
        )
        self.story.append(Image(disk_graph, width=15*cm, height=6*cm))
        self.story.append(PageBreak())

    def _add_process_table(self):
        """프로세스 분석 표 추가"""
        title_style = self._get_style(font_size=16, bold=True)
        self.story.append(Paragraph("프로세스 분석", title_style))
        self.story.append(Spacer(1, 0.5*cm))

        top_procs = self.collector.get_top_processes(n=5)

        # CPU Top 5
        subtitle_style = self._get_style(font_size=12, bold=True)
        self.story.append(Paragraph("CPU 사용률 Top 5", subtitle_style))
        self.story.append(Spacer(1, 0.3*cm))

        cpu_data = [['PID', '프로세스 이름', 'CPU (%)', '메모리 (%)']]
        for proc in top_procs['cpu']:
            cpu_data.append([
                str(proc.get('pid', 'N/A')),
                proc.get('name', 'N/A')[:30],
                f"{proc.get('cpu_percent', 0):.2f}",
                f"{proc.get('memory_percent', 0):.2f}"
            ])

        cpu_table = Table(cpu_data, colWidths=[2*cm, 7*cm, 3*cm, 3*cm])
        cpu_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        self.story.append(cpu_table)
        self.story.append(Spacer(1, 0.5*cm))

        # 메모리 Top 5
        self.story.append(Paragraph("메모리 사용률 Top 5", subtitle_style))
        self.story.append(Spacer(1, 0.3*cm))

        mem_data = [['PID', '프로세스 이름', 'CPU (%)', '메모리 (%)']]
        for proc in top_procs['memory']:
            mem_data.append([
                str(proc.get('pid', 'N/A')),
                proc.get('name', 'N/A')[:30],
                f"{proc.get('cpu_percent', 0):.2f}",
                f"{proc.get('memory_percent', 0):.2f}"
            ])

        mem_table = Table(mem_data, colWidths=[2*cm, 7*cm, 3*cm, 3*cm])
        mem_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        self.story.append(mem_table)

    def generate_report(self, output_dir='.'):
        """PDF 보고서 생성"""
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = os.path.join(output_dir, f'system_report_{timestamp}.pdf')

        # PDF 문서 생성
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 내용 생성
        self._create_cover_page()
        self._create_summary_table()
        self._add_graphs()
        self._add_process_table()

        # PDF 빌드
        try:
            doc.build(self.story)
            print(f"PDF 보고서 생성 완료: {self.filename}")
            return self.filename
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {e}")
            return None
