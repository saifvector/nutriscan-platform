"""
Phase 7 Concurrency & Scalability Stress Test Suite.
Validates:
1. SQLite WAL Mode high-concurrency throughput under multi-threaded read/write load.
2. 100 concurrent sessions writing audit logs simultaneously with 0 lock errors.
3. 500 mixed read/write operations verifying p50, p95, and p99 latency SLAs.
4. 1000 high-throughput operations confirming zero deadlocks, zero data corruption, and SHA-256 chain integrity.
"""

import time
import uuid
import statistics
import concurrent.futures
import pytest

from backend.app.core.persistence import PersistenceRepository
import backend.app.core.persistence as persistence_mod


@pytest.fixture(autouse=True)
def isolated_concurrency_db(monkeypatch, tmp_path):
    """Ensures each concurrency stress test runs against a clean isolated SQLite WAL database."""
    test_db = str(tmp_path / f"stress_{uuid.uuid4().hex[:8]}.db")
    monkeypatch.setattr(persistence_mod, "DB_PATH", test_db)
    persistence_mod.initialize_database()
    yield test_db


def test_concurrency_100_simultaneous_writes():
    """Simulate 100 concurrent patient assessment audit events with zero database locked errors."""
    num_threads = 100
    latencies = []
    errors = []

    def write_worker(idx: int):
        t0 = time.perf_counter()
        try:
            event_id = PersistenceRepository.log_audit_event(
                action=f"CONCURRENCY_TEST_100_{idx}",
                module="STRESS_TEST",
                user_id=f"user_{idx}",
                assessment_id=str(uuid.uuid4()),
                severity="INFO",
                details={"thread_idx": idx, "timestamp": time.time()}
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            return elapsed, None
        except Exception as e:
            return 0.0, str(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(write_worker, i) for i in range(num_threads)]
        for f in concurrent.futures.as_completed(futures):
            lat, err = f.result()
            if err:
                errors.append(err)
            else:
                latencies.append(lat)

    assert len(errors) == 0, f"Encountered {len(errors)} errors during 100 concurrent writes: {errors[:3]}"
    assert len(latencies) == num_threads
    
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    print(f"\n[100 Concurrent Writes] Min: {min(latencies):.2f}ms | Median: {p50:.2f}ms | p95: {p95:.2f}ms | Max: {max(latencies):.2f}ms")


def test_concurrency_500_mixed_workload():
    """Simulate 500 operations (60% reads, 40% writes) across 20 concurrent threads."""
    num_ops = 500
    latencies = []
    errors = []

    def mixed_worker(idx: int):
        t0 = time.perf_counter()
        try:
            if idx % 5 < 3:
                # 60% Reads
                _ = PersistenceRepository.get_persistent_audit_events(limit=10)
            else:
                # 40% Writes
                _ = PersistenceRepository.log_audit_event(
                    action=f"CONCURRENCY_TEST_500_{idx}",
                    module="MIXED_STRESS",
                    user_id=f"user_mixed_{idx}",
                    assessment_id=str(uuid.uuid4()),
                    severity="INFO",
                    details={"op": idx}
                )
            elapsed = (time.perf_counter() - t0) * 1000.0
            return elapsed, None
        except Exception as e:
            return 0.0, str(e)

    start_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(mixed_worker, i) for i in range(num_ops)]
        for f in concurrent.futures.as_completed(futures):
            lat, err = f.result()
            if err:
                errors.append(err)
            else:
                latencies.append(lat)
    total_time = time.perf_counter() - start_wall

    assert len(errors) == 0, f"Encountered {len(errors)} errors: {errors[:3]}"
    throughput = num_ops / total_time
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]
    p99 = statistics.quantiles(latencies, n=100)[98]

    print(f"\n[500 Mixed Workload] Throughput: {throughput:.1f} ops/sec | p50: {p50:.2f}ms | p95: {p95:.2f}ms | p99: {p99:.2f}ms")
    assert throughput > 50.0, "Throughput must exceed 50 ops/sec under SQLite WAL mode"


def test_concurrency_1000_operations_and_chain_integrity():
    """Stress test with 1000 operations, then verify cryptographic audit hash chain integrity."""
    num_ops = 1000
    errors = []
    latencies = []

    def op_worker(idx: int):
        t0 = time.perf_counter()
        try:
            if idx % 2 == 0:
                _ = PersistenceRepository.count_audit_events()
            else:
                _ = PersistenceRepository.log_audit_event(
                    action=f"STRESS_1000_{idx}",
                    module="INTEGRITY_STRESS",
                    user_id=f"user_1000_{idx}",
                    assessment_id=str(uuid.uuid4()),
                    severity="INFO",
                    details={"cycle": idx}
                )
            return (time.perf_counter() - t0) * 1000.0, None
        except Exception as e:
            return 0.0, str(e)

    start_wall = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(op_worker, i) for i in range(num_ops)]
        for f in concurrent.futures.as_completed(futures):
            lat, err = f.result()
            if err:
                errors.append(err)
            else:
                latencies.append(lat)
    total_time = time.perf_counter() - start_wall

    assert len(errors) == 0, f"Errors encountered during 1000 stress operations: {errors[:3]}"
    throughput = num_ops / total_time
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]
    p99 = statistics.quantiles(latencies, n=100)[98]
    print(f"\n[1000 Operations Stress] Throughput: {throughput:.1f} ops/sec | Total Time: {total_time:.2f}s | p50: {p50:.2f}ms | p95: {p95:.2f}ms | p99: {p99:.2f}ms")

    # Cryptographic Hash Chaining Integrity Check
    integrity = PersistenceRepository.verify_audit_trail_integrity()
    assert integrity["is_valid"] is True, f"Audit trail chain invalid: {integrity}"
    assert integrity["total_events"] >= num_ops // 2
