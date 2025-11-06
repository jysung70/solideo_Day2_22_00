# 시스템 리소스 실시간 모니터링 (웹 버전)

웹 기반 시스템 리소스 실시간 모니터링 애플리케이션입니다. HTML, CSS, JavaScript (Node.js)로 구현되었습니다.

## 🌟 특징

- **실시간 모니터링**: WebSocket을 통한 1초 간격 실시간 데이터 업데이트
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 기기에서 작동
- **인터랙티브 그래프**: Chart.js를 사용한 실시간 차트
- **PDF 보고서**: 브라우저에서 직접 PDF 생성
- **현대적인 UI**: 그라데이션과 애니메이션을 활용한 세련된 디자인

## 🏗️ 프로젝트 구조

```
.
├── server.js              # Node.js 백엔드 서버 (WebSocket + REST API)
├── package.json           # Node.js 의존성 설정
├── public/                # 프론트엔드 파일
│   ├── index.html        # HTML 구조
│   ├── style.css         # CSS 스타일
│   └── app.js            # JavaScript 로직
└── README-WEB.md         # 이 문서
```

## 📋 요구사항

- **Node.js**: v14 이상
- **npm**: v6 이상
- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전)

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

설치되는 패키지:
- `express`: 웹 서버
- `systeminformation`: 시스템 정보 수집
- `ws`: WebSocket 서버
- `cors`: CORS 지원

### 2. 서버 실행

```bash
npm start
```

또는 개발 모드 (자동 재시작):
```bash
npm run dev
```

### 3. 브라우저에서 열기

서버 실행 후 브라우저에서 접속:
```
http://localhost:3000
```

## 📱 사용 방법

### 기본 워크플로우

1. **페이지 로드**
   - 자동으로 시스템 정보가 표시됩니다
   - WebSocket 연결이 자동으로 설정됩니다

2. **모니터링 시작**
   - "▶️ 모니터링 시작" 버튼 클릭
   - 1초마다 실시간으로 데이터가 업데이트됩니다
   - 최대 5분(300초) 자동 모니터링

3. **실시간 확인**
   - 상단: 현재 리소스 사용률 (카드 형태)
   - 하단: 4개의 실시간 그래프
   - 프로세스: CPU/메모리 Top 5 프로세스

4. **모니터링 중지**
   - "⏸️ 모니터링 중지" 버튼으로 언제든 중지 가능
   - 데이터는 메모리에 유지됩니다

5. **PDF 생성**
   - "📄 PDF 보고서 생성" 버튼 클릭
   - 브라우저에서 자동으로 PDF 다운로드

6. **데이터 초기화**
   - "🗑️ 데이터 초기화" 버튼으로 모든 데이터 삭제

## 🎨 화면 구성

### 헤더
- 타이틀 및 설명

### 제어 패널
- 시작/중지/PDF생성/초기화 버튼
- 경과 시간 표시 (0~300초)
- 현재 상태 표시

### 시스템 정보
- 운영체제
- CPU 모델 및 코어 수
- 총 메모리

### 실시간 대시보드
5개의 메트릭 카드:
- 🔴 CPU 사용률
- 🔵 메모리 사용률 (상세 정보 포함)
- 🟣 디스크 I/O (읽기/쓰기)
- 🟢 네트워크 (송신/수신)
- 🌡️ CPU 온도

### 실시간 그래프 (Chart.js)
4개의 라인 차트:
- CPU Usage (빨간색)
- Memory Usage (파란색)
- Network Traffic (녹색/주황색)
- Disk I/O (보라색/분홍색)

### Top 5 프로세스
- CPU 사용률 Top 5 테이블
- 메모리 사용률 Top 5 테이블

## 🔧 기술 스택

### 백엔드
- **Node.js**: JavaScript 런타임
- **Express**: 웹 서버 프레임워크
- **WebSocket (ws)**: 실시간 양방향 통신
- **systeminformation**: 시스템 정보 수집 라이브러리

### 프론트엔드
- **HTML5**: 웹 구조
- **CSS3**: 스타일링 (그라데이션, 애니메이션, flexbox, grid)
- **JavaScript (ES6+)**: 동적 기능
- **Chart.js**: 실시간 차트 라이브러리
- **jsPDF**: PDF 생성 라이브러리
- **html2canvas**: 차트를 이미지로 변환

## 📡 API 엔드포인트

### REST API

- `GET /api/system-info`: 시스템 정보 조회
- `POST /api/start`: 모니터링 시작
- `POST /api/stop`: 모니터링 중지
- `GET /api/statistics`: 통계 조회
- `GET /api/all-data`: 전체 데이터 조회
- `POST /api/clear`: 데이터 초기화

### WebSocket

- 연결: `ws://localhost:3000`
- 메시지 타입:
  - `systemInfo`: 시스템 정보
  - `data`: 실시간 모니터링 데이터

## 🎯 데이터 수집 항목

### 실시간 데이터 (1초 간격)
- **CPU**: 전체 사용률 (%)
- **메모리**: 사용률 (%), 사용량 (GB), 가용량 (GB)
- **디스크 I/O**: 읽기/쓰기 속도 (MB/s)
- **네트워크**: 송신/수신 속도 (MB/s)
- **온도**: CPU 온도 (°C, 가능한 경우)
- **프로세스**: CPU/메모리 Top 5

### 저장
- 최대 300개 샘플 (5분)
- deque 방식으로 오래된 데이터 자동 제거

## 💾 PDF 보고서

### 구성
1. **표지**
   - 보고서 제목
   - 모니터링 기간 (시작/종료)
   - 샘플 수
   - 시스템 정보

2. **통계 페이지**
   - 각 리소스별 평균/최소/최대 값

3. **그래프 페이지**
   - 4개의 차트 이미지
   - CPU, 메모리, 네트워크, 디스크

### 다운로드
- 파일명: `system_report_YYYY-MM-DD_HH-MM-SS.pdf`
- 자동 다운로드 (브라우저 기본 위치)

## 🔐 보안 고려사항

- WebSocket은 같은 도메인에서만 연결 가능
- CORS 설정으로 외부 접근 제어
- 시스템 정보는 읽기 전용
- 민감한 프로세스 정보 필터링 가능

## 🐛 문제 해결

### 서버가 시작되지 않음
```bash
# 포트가 이미 사용 중인 경우
lsof -i :3000
kill -9 <PID>

# 또는 다른 포트 사용
PORT=8080 npm start
```

### WebSocket 연결 실패
- 방화벽 설정 확인
- 브라우저 콘솔에서 에러 확인
- 서버 로그 확인

### 그래프가 표시되지 않음
- 브라우저 콘솔에서 Chart.js 로딩 확인
- 캐시 삭제 후 새로고침 (Ctrl+F5)

### PDF 생성 실패
- 팝업 차단 해제
- 브라우저 다운로드 권한 확인
- 충분한 데이터 수집 확인 (최소 10초)

## 🌐 네트워크 접근

### 로컬 네트워크에서 접근
```bash
# 서버의 IP 주소 확인
ifconfig  # Linux/Mac
ipconfig  # Windows

# 같은 네트워크의 다른 기기에서 접속
http://<서버-IP>:3000
```

### 외부 접근 (주의)
- 방화벽 포트 3000 열기
- 보안을 위해 프록시/VPN 사용 권장

## 📊 성능 최적화

- **차트 애니메이션**: 비활성화하여 성능 향상
- **데이터 제한**: 최대 300개 샘플로 메모리 사용 제한
- **WebSocket**: HTTP 폴링보다 효율적인 실시간 통신
- **비동기 처리**: Promise.all로 병렬 데이터 수집

## 🔄 Python 버전과의 차이

| 항목 | Python 버전 | Web 버전 |
|------|-------------|----------|
| UI | Tkinter (데스크톱) | HTML/CSS (브라우저) |
| 실행 | 로컬 실행 | 웹 서버 필요 |
| 그래프 | Matplotlib | Chart.js |
| PDF | reportlab | jsPDF |
| 통신 | 직접 접근 | WebSocket/API |
| 접근성 | 단일 PC | 네트워크 전체 |

## 🎓 개발 가이드

### 코드 수정

**백엔드 수정** (server.js):
```javascript
// 수집 주기 변경 (기본 1초)
setInterval(async () => {
    // ...
}, 2000); // 2초로 변경
```

**프론트엔드 수정** (app.js):
```javascript
// 최대 샘플 수 변경 (기본 300)
const maxSamples = 600; // 10분으로 변경
```

### 새로운 메트릭 추가

1. server.js에서 데이터 수집 추가
2. app.js에서 데이터 처리 추가
3. index.html에 UI 요소 추가
4. style.css에 스타일 추가

## 📦 배포

### PM2로 프로덕션 실행
```bash
npm install -g pm2
pm2 start server.js --name system-monitor
pm2 save
pm2 startup
```

### Docker로 배포
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 📄 라이선스

MIT License

## 🤝 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.

---

**Made with ❤️ using HTML, CSS, JavaScript, and Node.js**
