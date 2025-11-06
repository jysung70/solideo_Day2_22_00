#!/usr/bin/env python3
"""
데이터 수집 모듈 테스트 스크립트
GUI 없이 데이터 수집 기능만 테스트
"""

import time
from data_collector import SystemDataCollector


def test_basic_collection():
    """기본 데이터 수집 테스트"""
    print("=" * 60)
    print("데이터 수집 모듈 테스트")
    print("=" * 60)

    # 수집기 생성
    collector = SystemDataCollector(max_samples=10)

    # 시스템 정보 출력
    print("\n[시스템 정보]")
    sys_info = collector.system_info
    print(f"운영체제: {sys_info['platform']} {sys_info['platform_release']}")
    print(f"CPU 모델: {sys_info['cpu_model']}")
    print(f"CPU 코어: {sys_info['cpu_count']}개 (논리: {sys_info['cpu_count_logical']}개)")
    print(f"총 메모리: {sys_info['total_memory'] / (1024**3):.2f} GB")

    # 데이터 수집 시작
    print("\n[데이터 수집 시작]")
    print("10초간 데이터를 수집합니다...\n")
    collector.start_collection()

    # 10초간 실시간 값 출력
    for i in range(10):
        time.sleep(1)
        current = collector.get_current_values()
        if current:
            print(f"[{i+1}초] CPU: {current['cpu']:.1f}% | "
                  f"메모리: {current['memory']:.1f}% | "
                  f"디스크 읽기: {current['disk_read']:.2f} MB/s | "
                  f"네트워크 송신: {current['net_sent']:.3f} MB/s")

    # 수집 중지
    collector.stop_collection()
    print("\n[데이터 수집 완료]")

    # 통계 출력
    print("\n[통계 정보]")
    stats = collector.get_statistics()
    if stats:
        print(f"CPU 평균: {stats['cpu']['avg']:.2f}% | "
              f"최소: {stats['cpu']['min']:.2f}% | "
              f"최대: {stats['cpu']['max']:.2f}%")
        print(f"메모리 평균: {stats['memory']['avg']:.2f}% | "
              f"최소: {stats['memory']['min']:.2f}% | "
              f"최대: {stats['memory']['max']:.2f}%")
        print(f"디스크 읽기 평균: {stats['disk_read']['avg']:.2f} MB/s | "
              f"최소: {stats['disk_read']['min']:.2f} MB/s | "
              f"최대: {stats['disk_read']['max']:.2f} MB/s")
        print(f"네트워크 송신 평균: {stats['net_sent']['avg']:.3f} MB/s | "
              f"최소: {stats['net_sent']['min']:.3f} MB/s | "
              f"최대: {stats['net_sent']['max']:.3f} MB/s")

    # 프로세스 정보
    print("\n[Top 5 프로세스]")
    top_procs = collector.get_top_processes(n=5)
    print("\nCPU 사용률 Top 5:")
    for i, proc in enumerate(top_procs['cpu'], 1):
        print(f"  {i}. {proc['name'][:30]:30s} - "
              f"CPU: {proc.get('cpu_percent', 0):.2f}% | "
              f"메모리: {proc.get('memory_percent', 0):.2f}%")

    print("\n메모리 사용률 Top 5:")
    for i, proc in enumerate(top_procs['memory'], 1):
        print(f"  {i}. {proc['name'][:30]:30s} - "
              f"CPU: {proc.get('cpu_percent', 0):.2f}% | "
              f"메모리: {proc.get('memory_percent', 0):.2f}%")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_collection()
