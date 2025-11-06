/**
 * System Resource Monitoring - Node.js Backend Server
 * 실시간 시스템 리소스 데이터를 수집하고 WebSocket으로 전송
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const si = require('systeminformation');
const path = require('path');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 포트 설정
const PORT = process.env.PORT || 3000;

// 데이터 저장소 (최대 300개 샘플)
class DataCollector {
    constructor(maxSamples = 300) {
        this.maxSamples = maxSamples;
        this.data = {
            timestamps: [],
            cpu: [],
            memory: [],
            diskRead: [],
            diskWrite: [],
            netSent: [],
            netRecv: [],
            cpuTemp: []
        };
        this.previousDiskIO = null;
        this.previousNetIO = null;
        this.previousTime = Date.now();
    }

    addSample(sample) {
        // 각 배열에 데이터 추가
        Object.keys(this.data).forEach(key => {
            if (sample[key] !== undefined) {
                this.data[key].push(sample[key]);
                // 최대 개수 초과 시 오래된 데이터 제거
                if (this.data[key].length > this.maxSamples) {
                    this.data[key].shift();
                }
            }
        });
    }

    getAllData() {
        return this.data;
    }

    getStatistics() {
        const calcStats = (arr) => {
            if (arr.length === 0) return { avg: 0, min: 0, max: 0 };
            return {
                avg: arr.reduce((a, b) => a + b, 0) / arr.length,
                min: Math.min(...arr),
                max: Math.max(...arr)
            };
        };

        return {
            cpu: calcStats(this.data.cpu),
            memory: calcStats(this.data.memory),
            diskRead: calcStats(this.data.diskRead),
            diskWrite: calcStats(this.data.diskWrite),
            netSent: calcStats(this.data.netSent),
            netRecv: calcStats(this.data.netRecv)
        };
    }

    clear() {
        Object.keys(this.data).forEach(key => {
            this.data[key] = [];
        });
    }
}

const collector = new DataCollector();

/**
 * 시스템 정보 수집
 */
async function getSystemInfo() {
    try {
        const [cpu, mem, osInfo] = await Promise.all([
            si.cpu(),
            si.mem(),
            si.osInfo()
        ]);

        return {
            platform: osInfo.platform,
            distro: osInfo.distro,
            release: osInfo.release,
            cpuManufacturer: cpu.manufacturer,
            cpuBrand: cpu.brand,
            cpuCores: cpu.cores,
            cpuPhysicalCores: cpu.physicalCores,
            totalMemory: mem.total
        };
    } catch (error) {
        console.error('Error getting system info:', error);
        return null;
    }
}

/**
 * 실시간 시스템 리소스 데이터 수집
 */
async function collectSystemData() {
    try {
        const currentTime = Date.now();
        const timeDelta = (currentTime - collector.previousTime) / 1000; // 초 단위

        // 병렬로 데이터 수집
        const [cpuData, memData, diskIO, networkIO, cpuTemp, processes] = await Promise.all([
            si.currentLoad(),
            si.mem(),
            si.disksIO(),
            si.networkStats(),
            si.cpuTemperature(),
            si.processes()
        ]);

        // CPU 사용률
        const cpuPercent = cpuData.currentLoad || 0;

        // 메모리
        const memPercent = (memData.used / memData.total) * 100;
        const memUsedGB = memData.used / (1024 ** 3);
        const memAvailableGB = memData.available / (1024 ** 3);

        // 디스크 I/O 속도 계산 (MB/s)
        let diskReadSpeed = 0;
        let diskWriteSpeed = 0;
        if (collector.previousDiskIO && timeDelta > 0) {
            diskReadSpeed = (diskIO.rIO - collector.previousDiskIO.rIO) / timeDelta / (1024 ** 2);
            diskWriteSpeed = (diskIO.wIO - collector.previousDiskIO.wIO) / timeDelta / (1024 ** 2);
        }
        collector.previousDiskIO = diskIO;

        // 네트워크 속도 계산 (MB/s)
        let netSentSpeed = 0;
        let netRecvSpeed = 0;
        if (collector.previousNetIO && timeDelta > 0 && networkIO.length > 0) {
            const currentNet = networkIO[0];
            netSentSpeed = (currentNet.tx_bytes - collector.previousNetIO.tx_bytes) / timeDelta / (1024 ** 2);
            netRecvSpeed = (currentNet.rx_bytes - collector.previousNetIO.rx_bytes) / timeDelta / (1024 ** 2);
        }
        if (networkIO.length > 0) {
            collector.previousNetIO = networkIO[0];
        }

        // CPU 온도
        const temperature = cpuTemp.main || null;

        // Top 5 프로세스
        const sortedByCpu = [...processes.list]
            .sort((a, b) => b.cpu - a.cpu)
            .slice(0, 5)
            .map(p => ({
                pid: p.pid,
                name: p.name,
                cpu: p.cpu,
                mem: p.mem
            }));

        const sortedByMem = [...processes.list]
            .sort((a, b) => b.mem - a.mem)
            .slice(0, 5)
            .map(p => ({
                pid: p.pid,
                name: p.name,
                cpu: p.cpu,
                mem: p.mem
            }));

        collector.previousTime = currentTime;

        const sample = {
            timestamps: new Date().toISOString(),
            cpu: cpuPercent,
            memory: memPercent,
            memoryUsedGB: memUsedGB,
            memoryAvailableGB: memAvailableGB,
            diskRead: Math.max(0, diskReadSpeed),
            diskWrite: Math.max(0, diskWriteSpeed),
            netSent: Math.max(0, netSentSpeed),
            netRecv: Math.max(0, netRecvSpeed),
            cpuTemp: temperature,
            topProcesses: {
                cpu: sortedByCpu,
                memory: sortedByMem
            }
        };

        // 데이터 저장
        collector.addSample(sample);

        return sample;

    } catch (error) {
        console.error('Error collecting system data:', error);
        return null;
    }
}

// WebSocket 연결 관리
const clients = new Set();

wss.on('connection', (ws) => {
    console.log('New WebSocket client connected');
    clients.add(ws);

    // 시스템 정보 전송
    getSystemInfo().then(sysInfo => {
        ws.send(JSON.stringify({
            type: 'systemInfo',
            data: sysInfo
        }));
    });

    ws.on('close', () => {
        console.log('Client disconnected');
        clients.delete(ws);
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        clients.delete(ws);
    });
});

// 1초마다 데이터 수집 및 브로드캐스트
let monitoringInterval = null;

function startMonitoring() {
    if (monitoringInterval) return;

    console.log('Starting monitoring...');
    monitoringInterval = setInterval(async () => {
        const data = await collectSystemData();
        if (data) {
            // 모든 연결된 클라이언트에게 데이터 전송
            const message = JSON.stringify({
                type: 'data',
                data: data
            });

            clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(message);
                }
            });
        }
    }, 1000); // 1초마다
}

function stopMonitoring() {
    if (monitoringInterval) {
        clearInterval(monitoringInterval);
        monitoringInterval = null;
        console.log('Monitoring stopped');
    }
}

// REST API 엔드포인트

// 시스템 정보 조회
app.get('/api/system-info', async (req, res) => {
    const sysInfo = await getSystemInfo();
    res.json(sysInfo);
});

// 모니터링 시작
app.post('/api/start', (req, res) => {
    startMonitoring();
    res.json({ status: 'started' });
});

// 모니터링 중지
app.post('/api/stop', (req, res) => {
    stopMonitoring();
    res.json({ status: 'stopped' });
});

// 통계 조회
app.get('/api/statistics', (req, res) => {
    const stats = collector.getStatistics();
    res.json(stats);
});

// 전체 데이터 조회 (PDF 생성용)
app.get('/api/all-data', (req, res) => {
    const allData = collector.getAllData();
    res.json(allData);
});

// 데이터 초기화
app.post('/api/clear', (req, res) => {
    collector.clear();
    res.json({ status: 'cleared' });
});

// 서버 시작
server.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('System Resource Monitoring Server');
    console.log('='.repeat(60));
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`WebSocket server ready on ws://localhost:${PORT}`);
    console.log('='.repeat(60));
});

// 프로세스 종료 시 정리
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    stopMonitoring();
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
