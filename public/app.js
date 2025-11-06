/**
 * System Resource Monitoring - Frontend JavaScript
 * 실시간 데이터 수신, 그래프 업데이트, PDF 생성
 */

// 전역 변수
let ws = null;
let monitoring = false;
let startTime = null;
let timerInterval = null;
let charts = {};

// 데이터 저장소
const maxSamples = 300;
const dataStore = {
    timestamps: [],
    cpu: [],
    memory: [],
    diskRead: [],
    diskWrite: [],
    netSent: [],
    netRecv: []
};

// DOM 요소
const elements = {
    startBtn: document.getElementById('startBtn'),
    stopBtn: document.getElementById('stopBtn'),
    pdfBtn: document.getElementById('pdfBtn'),
    clearBtn: document.getElementById('clearBtn'),
    timer: document.getElementById('timer'),
    status: document.getElementById('status'),
    cpuValue: document.getElementById('cpuValue'),
    memoryValue: document.getElementById('memoryValue'),
    memoryDetail: document.getElementById('memoryDetail'),
    diskValue: document.getElementById('diskValue'),
    netValue: document.getElementById('netValue'),
    tempValue: document.getElementById('tempValue')
};

/**
 * WebSocket 연결
 */
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateStatus('연결됨');
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === 'systemInfo') {
            updateSystemInfo(message.data);
        } else if (message.type === 'data') {
            handleNewData(message.data);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus('연결 오류');
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateStatus('연결 끊김');
        // 5초 후 재연결 시도
        setTimeout(connectWebSocket, 5000);
    };
}

/**
 * 시스템 정보 업데이트
 */
function updateSystemInfo(info) {
    document.getElementById('os').textContent = `${info.distro} ${info.release}`;
    document.getElementById('cpuModel').textContent = info.cpuBrand;
    document.getElementById('cpuCores').textContent = `${info.cpuPhysicalCores}개 (논리: ${info.cpuCores}개)`;
    document.getElementById('totalMemory').textContent = `${(info.totalMemory / (1024**3)).toFixed(2)} GB`;
}

/**
 * 새 데이터 처리
 */
function handleNewData(data) {
    // 데이터 저장
    addDataToStore(data);

    // 대시보드 업데이트
    updateDashboard(data);

    // 그래프 업데이트
    updateCharts();

    // 프로세스 테이블 업데이트
    if (data.topProcesses) {
        updateProcessTables(data.topProcesses);
    }
}

/**
 * 데이터 저장소에 추가
 */
function addDataToStore(data) {
    const timestamp = new Date(data.timestamps);

    dataStore.timestamps.push(timestamp);
    dataStore.cpu.push(data.cpu);
    dataStore.memory.push(data.memory);
    dataStore.diskRead.push(data.diskRead);
    dataStore.diskWrite.push(data.diskWrite);
    dataStore.netSent.push(data.netSent);
    dataStore.netRecv.push(data.netRecv);

    // 최대 개수 초과 시 오래된 데이터 제거
    Object.keys(dataStore).forEach(key => {
        if (dataStore[key].length > maxSamples) {
            dataStore[key].shift();
        }
    });
}

/**
 * 대시보드 업데이트
 */
function updateDashboard(data) {
    elements.cpuValue.textContent = `${data.cpu.toFixed(2)}%`;
    elements.memoryValue.textContent = `${data.memory.toFixed(2)}%`;
    elements.memoryDetail.textContent = `${data.memoryUsedGB.toFixed(2)} GB / ${data.memoryAvailableGB.toFixed(2)} GB`;
    elements.diskValue.textContent = `${data.diskRead.toFixed(2)} / ${data.diskWrite.toFixed(2)} MB/s`;
    elements.netValue.textContent = `${data.netSent.toFixed(3)} / ${data.netRecv.toFixed(3)} MB/s`;

    if (data.cpuTemp) {
        elements.tempValue.textContent = `${data.cpuTemp.toFixed(1)} °C`;
    } else {
        elements.tempValue.textContent = 'N/A';
    }
}

/**
 * 프로세스 테이블 업데이트
 */
function updateProcessTables(processes) {
    // CPU Top 5
    const cpuTable = document.getElementById('cpuProcessTable').querySelector('tbody');
    cpuTable.innerHTML = '';
    processes.cpu.forEach(proc => {
        const row = cpuTable.insertRow();
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name.substring(0, 30)}</td>
            <td>${proc.cpu.toFixed(2)}</td>
            <td>${proc.mem.toFixed(2)}</td>
        `;
    });

    // Memory Top 5
    const memTable = document.getElementById('memProcessTable').querySelector('tbody');
    memTable.innerHTML = '';
    processes.memory.forEach(proc => {
        const row = memTable.insertRow();
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name.substring(0, 30)}</td>
            <td>${proc.cpu.toFixed(2)}</td>
            <td>${proc.mem.toFixed(2)}</td>
        `;
    });
}

/**
 * Chart.js 그래프 초기화
 */
function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 0
        },
        scales: {
            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Time (seconds)'
                }
            },
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        }
    };

    // CPU 차트
    charts.cpu = new Chart(document.getElementById('cpuChart'), {
        type: 'line',
        data: {
            datasets: [{
                label: 'CPU Usage (%)',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    max: 100,
                    title: {
                        display: true,
                        text: 'CPU (%)'
                    }
                }
            }
        }
    });

    // 메모리 차트
    charts.memory = new Chart(document.getElementById('memoryChart'), {
        type: 'line',
        data: {
            datasets: [{
                label: 'Memory Usage (%)',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Memory (%)'
                    }
                }
            }
        }
    });

    // 네트워크 차트
    charts.network = new Chart(document.getElementById('networkChart'), {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Sent (MB/s)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1
                },
                {
                    label: 'Received (MB/s)',
                    data: [],
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Speed (MB/s)'
                    }
                }
            }
        }
    });

    // 디스크 차트
    charts.disk = new Chart(document.getElementById('diskChart'), {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Read (MB/s)',
                    data: [],
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.1)',
                    tension: 0.1
                },
                {
                    label: 'Write (MB/s)',
                    data: [],
                    borderColor: 'rgb(255, 99, 255)',
                    backgroundColor: 'rgba(255, 99, 255, 0.1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Speed (MB/s)'
                    }
                }
            }
        }
    });
}

/**
 * 그래프 업데이트
 */
function updateCharts() {
    // X축 데이터 (초 단위)
    const timeData = dataStore.timestamps.map((_, index) => index);

    // CPU 차트
    charts.cpu.data.datasets[0].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.cpu[i]
    }));
    charts.cpu.update();

    // 메모리 차트
    charts.memory.data.datasets[0].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.memory[i]
    }));
    charts.memory.update();

    // 네트워크 차트
    charts.network.data.datasets[0].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.netSent[i]
    }));
    charts.network.data.datasets[1].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.netRecv[i]
    }));
    charts.network.update();

    // 디스크 차트
    charts.disk.data.datasets[0].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.diskRead[i]
    }));
    charts.disk.data.datasets[1].data = timeData.map((time, i) => ({
        x: time,
        y: dataStore.diskWrite[i]
    }));
    charts.disk.update();
}

/**
 * 모니터링 시작
 */
async function startMonitoring() {
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const result = await response.json();

        if (result.status === 'started') {
            monitoring = true;
            startTime = Date.now();

            // UI 업데이트
            elements.startBtn.disabled = true;
            elements.stopBtn.disabled = false;
            elements.pdfBtn.disabled = true;
            updateStatus('모니터링 중...');

            // 타이머 시작
            timerInterval = setInterval(updateTimer, 1000);
        }
    } catch (error) {
        console.error('Failed to start monitoring:', error);
        alert('모니터링 시작 실패');
    }
}

/**
 * 모니터링 중지
 */
async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const result = await response.json();

        if (result.status === 'stopped') {
            monitoring = false;

            // UI 업데이트
            elements.startBtn.disabled = false;
            elements.stopBtn.disabled = true;
            elements.pdfBtn.disabled = false;
            updateStatus('중지됨');

            // 타이머 중지
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }
    } catch (error) {
        console.error('Failed to stop monitoring:', error);
        alert('모니터링 중지 실패');
    }
}

/**
 * 데이터 초기화
 */
async function clearData() {
    if (!confirm('모든 수집된 데이터를 초기화하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch('/api/clear', { method: 'POST' });
        const result = await response.json();

        if (result.status === 'cleared') {
            // 로컬 데이터 초기화
            Object.keys(dataStore).forEach(key => {
                dataStore[key] = [];
            });

            // 그래프 초기화
            updateCharts();

            // 대시보드 초기화
            elements.cpuValue.textContent = '0.00%';
            elements.memoryValue.textContent = '0.00%';
            elements.memoryDetail.textContent = '0.00 GB / 0.00 GB';
            elements.diskValue.textContent = '0.00 / 0.00 MB/s';
            elements.netValue.textContent = '0.00 / 0.00 MB/s';
            elements.tempValue.textContent = 'N/A';

            // 타이머 초기화
            elements.timer.textContent = '0초 / 300초';

            updateStatus('데이터 초기화됨');
        }
    } catch (error) {
        console.error('Failed to clear data:', error);
        alert('데이터 초기화 실패');
    }
}

/**
 * 타이머 업데이트
 */
function updateTimer() {
    if (!startTime) return;

    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    elements.timer.textContent = `${elapsed}초 / 300초`;

    // 5분(300초) 경과 시 자동 중지
    if (elapsed >= 300) {
        stopMonitoring();
        alert('5분 모니터링이 완료되었습니다.\nPDF 보고서를 생성할 수 있습니다.');
    }
}

/**
 * 상태 업데이트
 */
function updateStatus(status) {
    elements.status.textContent = status;
}

/**
 * PDF 생성
 */
async function generatePDF() {
    if (dataStore.timestamps.length < 10) {
        alert('충분한 데이터가 수집되지 않았습니다.\n최소 10초 이상 모니터링해주세요.');
        return;
    }

    updateStatus('PDF 생성 중...');

    try {
        // jsPDF 인스턴스 생성
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // 통계 데이터 가져오기
        const response = await fetch('/api/statistics');
        const stats = await response.json();

        const sysInfo = {
            os: document.getElementById('os').textContent,
            cpu: document.getElementById('cpuModel').textContent,
            cores: document.getElementById('cpuCores').textContent,
            memory: document.getElementById('totalMemory').textContent
        };

        // 페이지 1: 표지
        doc.setFontSize(24);
        doc.text('시스템 리소스 모니터링 보고서', 105, 50, { align: 'center' });

        doc.setFontSize(12);
        const startTimeStr = dataStore.timestamps[0].toLocaleString('ko-KR');
        const endTimeStr = dataStore.timestamps[dataStore.timestamps.length - 1].toLocaleString('ko-KR');

        doc.text(`Monitoring Period:`, 20, 80);
        doc.text(`Start: ${startTimeStr}`, 20, 90);
        doc.text(`End: ${endTimeStr}`, 20, 100);
        doc.text(`Samples: ${dataStore.timestamps.length}`, 20, 110);

        doc.text('System Information:', 20, 130);
        doc.text(`OS: ${sysInfo.os}`, 20, 140);
        doc.text(`CPU: ${sysInfo.cpu}`, 20, 150);
        doc.text(`Cores: ${sysInfo.cores}`, 20, 160);
        doc.text(`Memory: ${sysInfo.memory}`, 20, 170);

        // 페이지 2: 통계
        doc.addPage();
        doc.setFontSize(16);
        doc.text('Summary Statistics', 20, 20);

        doc.setFontSize(10);
        let y = 40;
        doc.text(`CPU: Avg ${stats.cpu.avg.toFixed(2)}% | Min ${stats.cpu.min.toFixed(2)}% | Max ${stats.cpu.max.toFixed(2)}%`, 20, y);
        y += 10;
        doc.text(`Memory: Avg ${stats.memory.avg.toFixed(2)}% | Min ${stats.memory.min.toFixed(2)}% | Max ${stats.memory.max.toFixed(2)}%`, 20, y);
        y += 10;
        doc.text(`Disk Read: Avg ${stats.diskRead.avg.toFixed(2)} MB/s | Min ${stats.diskRead.min.toFixed(2)} MB/s | Max ${stats.diskRead.max.toFixed(2)} MB/s`, 20, y);
        y += 10;
        doc.text(`Disk Write: Avg ${stats.diskWrite.avg.toFixed(2)} MB/s | Min ${stats.diskWrite.min.toFixed(2)} MB/s | Max ${stats.diskWrite.max.toFixed(2)} MB/s`, 20, y);
        y += 10;
        doc.text(`Network Sent: Avg ${stats.netSent.avg.toFixed(3)} MB/s | Min ${stats.netSent.min.toFixed(3)} MB/s | Max ${stats.netSent.max.toFixed(3)} MB/s`, 20, y);
        y += 10;
        doc.text(`Network Recv: Avg ${stats.netRecv.avg.toFixed(3)} MB/s | Min ${stats.netRecv.min.toFixed(3)} MB/s | Max ${stats.netRecv.max.toFixed(3)} MB/s`, 20, y);

        // 그래프를 이미지로 변환하여 추가
        const chartElements = [
            { id: 'cpuChart', title: 'CPU Usage' },
            { id: 'memoryChart', title: 'Memory Usage' },
            { id: 'networkChart', title: 'Network Traffic' },
            { id: 'diskChart', title: 'Disk I/O' }
        ];

        for (let i = 0; i < chartElements.length; i++) {
            const canvas = document.getElementById(chartElements[i].id);
            const imgData = canvas.toDataURL('image/png');

            if (i % 2 === 0 && i > 0) {
                doc.addPage();
                y = 20;
            } else if (i === 0) {
                y = 80;
            }

            doc.text(chartElements[i].title, 20, y);
            doc.addImage(imgData, 'PNG', 20, y + 5, 170, 80);
            y += 95;
        }

        // PDF 저장
        const filename = `system_report_${new Date().toISOString().replace(/[:.]/g, '-')}.pdf`;
        doc.save(filename);

        updateStatus('PDF 생성 완료');
        alert(`PDF 보고서가 생성되었습니다:\n${filename}`);

    } catch (error) {
        console.error('Failed to generate PDF:', error);
        alert('PDF 생성 중 오류가 발생했습니다.');
        updateStatus('PDF 생성 실패');
    }
}

/**
 * 이벤트 리스너 등록
 */
function initEventListeners() {
    elements.startBtn.addEventListener('click', startMonitoring);
    elements.stopBtn.addEventListener('click', stopMonitoring);
    elements.pdfBtn.addEventListener('click', generatePDF);
    elements.clearBtn.addEventListener('click', clearData);
}

/**
 * 초기화
 */
function init() {
    console.log('Initializing System Monitor...');

    // 그래프 초기화
    initCharts();

    // 이벤트 리스너 등록
    initEventListeners();

    // WebSocket 연결
    connectWebSocket();

    console.log('System Monitor initialized');
}

// 페이지 로드 시 초기화
window.addEventListener('DOMContentLoaded', init);
