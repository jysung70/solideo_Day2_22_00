# 시스템 리소스 실시간 모니터링 시스템

Python을 사용하여 시스템 리소스를 실시간으로 모니터링하고, 수집한 데이터를 시각화된 PDF 보고서로 생성하는 시스템입니다.

## 주요 기능

### 모니터링 대상
- **CPU 사용률**: 전체 및 코어별 사용률
- **메모리 사용률**: 전체, 사용 가능, 사용 중 메모리
- **디스크 I/O**: 읽기/쓰기 속도 (MB/s)
- **네트워크 트래픽**: 송신/수신 속도 (MB/s)
- **CPU 온도**: 센서 접근 가능 시 표시
- **GPU 정보**: NVIDIA GPU가 있는 경우 사용률 및 온도
- **프로세스 분석**: CPU/메모리 사용 Top 5 프로세스

### 실시간 모니터링
- **업데이트 주기**: 1초마다 데이터 수집 및 그래프 업데이트
- **모니터링 기간**: 최대 5분 (300개 데이터 포인트)
- **실시간 UI**: Tkinter 기반 GUI로 실시간 시각화

### PDF 보고서
- **자동 생성**: 모니터링 완료 후 PDF 보고서 생성
- **포함 내용**:
  - 시스템 정보 및 모니터링 기간
  - 요약 통계 (평균, 최소, 최대)
  - 시계열 그래프
  - 프로세스 분석 표

## 설치

### 1. Python 환경
Python 3.7 이상 필요

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 한글 폰트 설치 (선택)
PDF에 한글을 표시하려면 한글 폰트가 필요합니다.

**Ubuntu/Debian:**
```bash
sudo apt-get install fonts-nanum
```

**macOS:**
이미 AppleGothic 폰트가 설치되어 있습니다.

**Windows:**
이미 맑은 고딕 폰트가 설치되어 있습니다.

## 사용 방법

### 기본 실행
```bash
python system_monitor.py
```

### GUI 사용 방법

1. **모니터링 시작**
   - "모니터링 시작" 버튼 클릭
   - 실시간으로 데이터가 수집되고 그래프가 업데이트됩니다
   - 최대 5분(300초) 동안 자동으로 모니터링됩니다

2. **모니터링 중지**
   - "모니터링 중지" 버튼으로 언제든지 중지 가능
   - 수집된 데이터는 메모리에 유지됩니다

3. **PDF 보고서 생성**
   - "PDF 보고서 생성" 버튼 클릭
   - `system_report_YYYYMMDD_HHMMSS.pdf` 파일이 현재 디렉토리에 생성됩니다

### 화면 구성

#### 상단: 제어 패널
- 시작/중지 버튼
- PDF 생성 버튼
- 타이머 표시
- 상태 표시

#### 중단: 실시간 대시보드
현재 리소스 사용 현황을 수치로 표시:
- CPU 사용률 (%)
- 메모리 사용률 (%) 및 상세 정보
- 디스크 I/O 속도 (MB/s)
- 네트워크 속도 (MB/s)
- CPU 온도 (가능한 경우)
- GPU 정보 (가능한 경우)

#### 하단: 실시간 그래프
4개의 실시간 그래프:
- CPU 사용률 (빨간색)
- 메모리 사용률 (파란색)
- 네트워크 트래픽 (송신: 녹색, 수신: 주황색)
- 디스크 I/O (읽기: 보라색, 쓰기: 분홍색)

## 프로젝트 구조

```
.
├── requirements.txt          # 의존성 패키지
├── README.md                # 프로젝트 문서
├── system_monitor.py        # 메인 GUI 애플리케이션
├── data_collector.py        # 데이터 수집 모듈
└── pdf_generator.py         # PDF 보고서 생성 모듈
```

## 기술 스택

### 필수 라이브러리
- **psutil**: 시스템 리소스 정보 수집
- **tkinter**: GUI 프레임워크 (Python 기본 내장)
- **matplotlib**: 실시간 그래프 시각화
- **reportlab**: PDF 문서 생성
- **Pillow**: 이미지 처리

### 선택 라이브러리
- **GPUtil**: NVIDIA GPU 모니터링
- **py3nvml**: GPU 온도 센서
- **py-cpuinfo**: CPU 상세 정보

## 주요 클래스

### SystemDataCollector
시스템 리소스 데이터를 수집하는 클래스
- 별도 스레드에서 1초마다 데이터 수집
- 최대 300개 샘플 저장 (5분)
- deque 사용으로 메모리 효율적 관리

### PDFReportGenerator
수집된 데이터를 PDF 보고서로 생성
- A4 사이즈 문서
- 한글 폰트 지원
- 표지, 통계 표, 그래프, 프로세스 분석 포함

### SystemMonitorGUI
Tkinter 기반 GUI 애플리케이션
- 실시간 대시보드 및 그래프
- 사용자 제어 인터페이스
- 자동 업데이트 (1초 주기)

## 예외 처리

### 권한 문제
일부 시스템 정보는 관리자 권한이 필요할 수 있습니다. 접근 불가 시 "N/A"로 표시됩니다.

### GPU 감지
GPU가 없거나 드라이버가 설치되지 않은 경우 해당 정보는 표시되지 않습니다.

### 한글 폰트
시스템에 한글 폰트가 없는 경우 기본 폰트(Helvetica)를 사용합니다.

### 센서 접근
일부 시스템에서는 온도 센서에 접근할 수 없을 수 있습니다. 이 경우 "N/A"로 표시됩니다.

## 문제 해결

### 모듈을 찾을 수 없음
```bash
pip install -r requirements.txt
```

### tkinter가 없음 (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### 권한 오류
일부 시스템 정보는 관리자 권한으로 실행해야 할 수 있습니다:
```bash
# Linux/macOS
sudo python system_monitor.py

# Windows
관리자 권한으로 명령 프롬프트 실행
```

## 성능 고려사항

- **메모리 사용**: deque를 사용하여 최대 300개 샘플만 유지
- **CPU 오버헤드**: psutil은 매우 가볍지만, 1초마다 수집하므로 약간의 CPU 사용
- **GUI 업데이트**: matplotlib 그래프 업데이트 시 약간의 지연 가능

## 개발 정보

### Phase 1: 데이터 수집 (data_collector.py)
- psutil로 시스템 리소스 수집
- 별도 스레드에서 1초 주기 수집
- deque로 효율적 데이터 관리

### Phase 2: 실시간 UI (system_monitor.py)
- Tkinter GUI 구성
- matplotlib 그래프 임베딩
- 1초마다 자동 업데이트

### Phase 3: PDF 생성 (pdf_generator.py)
- reportlab로 PDF 문서 생성
- matplotlib 그래프를 이미지로 변환
- 한글 폰트 지원

### Phase 4: 고급 기능
- GPU 모니터링 (선택)
- 온도 센서 읽기 (선택)
- Top 프로세스 분석

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 작성자

System Resource Monitoring System
Version 1.0
