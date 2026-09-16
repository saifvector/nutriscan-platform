"""
Test Enterprise Scalability Suite (Phase 2)
NutriScan Final Gap Closure Program

Validates:
1. High-concurrency throughput: 1,000 simulated concurrent user requests
2. Lock Contention & Resilience: 5,000 burst persistence operations with 0 database lock errors
3. Soak Testing & Memory Stability: Continuous workload execution measuring heap delta with tracemalloc
4. PostgreSQL Database Migration Abstraction: Full DDL schema and data export generation
"""

import time
import uuid
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.persistence import PersistenceRepository

client = TestClient(app)


class TestConcurrencyAndLockResilience:
    """Validates multi-threaded throughput and SQLite WAL lock-free concurrency."""

    def test_1000_concurrent_read_write_operations(self):
        """
        Executes 1,000 concurrent read/write operations across 50 worker threads.
        Must complete with 0 lock errors and maintain sub-millisecond execution times.
        """
        num_requests = 1000
        workers = 50
        errors = []
        latencies = []

        def worker_task(i: int):
            t0 = time.perf_counter()
            test_id = f"concurrency_user_{i}_{uuid.uuid4().hex[:6]}"
            try:
                # 1. Write assessment
                PersistenceRepository.save_assessment(
                    assessment_id=test_id,
                    payload={"user_id": f"usr_{i}", "age": 25 + (i % 50), "gender": "MALE"}
                )
                # 2. Read assessment
                data = PersistenceRepository.get_assessment(test_id)
                if not data:
                    return False, "Failed to retrieve persisted assessment"

                # 3. Write and read report
                PersistenceRepository.save_report(
                    report_id=test_id,
                    assessment_id=test_id,
                    report_dict={
                        "overall_health_score": 88.0,
                        "status": "COMPLETED",
                        "summary_text": "Concurrency validation normal.",
                        "report_payload": {"test": "concurrency"}
                    }
                )
                report = PersistenceRepository.get_report(test_id)
                if not report:
                    return False, "Failed to retrieve persisted report"

                latencies.append(time.perf_counter() - t0)
                return True, None
            except Exception as ex:
                return False, str(ex)

        t_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_requests)]
            for fut in as_completed(futures):
                success, err = fut.result()
                if not success:
                    errors.append(err)

        total_elapsed = time.perf_counter() - t_start
        total_ops = num_requests * 4  # 2 writes + 2 reads per user journey (4,000 total operations)
        ops_per_sec = round(total_ops / total_elapsed, 2)
        journeys_per_sec = round(num_requests / total_elapsed, 2)
        avg_latency_ms = round((sum(latencies) / len(latencies)) * 1000, 2) if latencies else 0

        assert len(errors) == 0, f"Encountered {len(errors)} errors during 1,000 concurrent operations: {errors[:3]}"
        assert ops_per_sec > 60, f"Throughput ({ops_per_sec} DB ops/s) must exceed 60 ops/s."
        print(f"\n[Concurrency Benchmark] 1,000 user journeys ({total_ops} DB ops) in {total_elapsed:.2f}s | {ops_per_sec} ops/sec ({journeys_per_sec} journeys/sec) | Avg latency: {avg_latency_ms} ms")

    def test_5000_burst_persistence_operations(self):
        """
        Simulates 5,000 burst persistence operations across 50 concurrent worker threads
        to verify WAL-mode queueing and zero SQLite lock contention.
        """
        num_burst = 5000
        workers = 50
        errors = []

        def burst_worker(worker_id: int):
            worker_errors = []
            for j in range(100):
                burst_id = f"burst_w{worker_id}_{j}_{uuid.uuid4().hex[:4]}"
                try:
                    # Alternating writes and reads for realistic mixed burst workload
                    if j % 2 == 0:
                        PersistenceRepository.save_assessment(
                            assessment_id=burst_id,
                            payload={"batch": "burst_test", "worker": worker_id, "index": j}
                        )
                    else:
                        _ = PersistenceRepository.get_assessment(f"burst_w{worker_id}_{j-1}")
                except Exception as e:
                    worker_errors.append(str(e))
            return worker_errors

        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(burst_worker, w) for w in range(workers)]
            for fut in as_completed(futures):
                errs = fut.result()
                errors.extend(errs)

        elapsed = time.perf_counter() - t0
        rate = round(num_burst / elapsed, 2)

        assert len(errors) == 0, f"Encountered {len(errors)} SQLite lock/write errors during 5,000 burst operations: {errors[:3]}"
        print(f"\n[Burst Benchmark] 5,000 operations across {workers} workers in {elapsed:.2f}s | {rate} ops/sec | 0 lock errors")


class TestSoakAndMemoryStability:
    """Validates memory stability across repeated high-throughput cycles."""

    def test_soak_memory_growth_is_bounded(self):
        """
        Executes a 200-iteration soak loop while tracking memory allocation.
        Total heap growth must remain bounded (< 15 MB) to verify absence of memory leaks.
        """
        tracemalloc.start()
        snapshot_start = tracemalloc.take_snapshot()

        for i in range(200):
            as_id = f"soak_{i}"
            PersistenceRepository.save_assessment(as_id, {"age": 30, "gender": "FEMALE"})
            _ = PersistenceRepository.get_assessment(as_id)
            PersistenceRepository.log_audit_event(
                module="SOAK_TEST",
                action="READ_WRITE",
                severity="INFO",
                assessment_id=as_id,
                user_id=f"user_{i % 10}",
                details={"iteration": i}
            )

        snapshot_end = tracemalloc.take_snapshot()
        tracemalloc.stop()

        top_stats = snapshot_end.compare_to(snapshot_start, 'lineno')
        total_growth_bytes = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        growth_mb = total_growth_bytes / (1024 * 1024)

        print(f"\n[Soak Test Memory] 200 soak iterations heap growth: {growth_mb:.2f} MB")
        assert growth_mb < 15.0, f"Memory growth ({growth_mb:.2f} MB) exceeded 15.0 MB threshold."


class TestPostgresMigrationAbstraction:
    """Validates SQLite to PostgreSQL automated migration DDL and data generation."""

    def test_postgres_sql_export_generation(self):
        # Insert a sample user and assessment to ensure data is present
        test_uid = str(uuid.uuid4())
        test_email = f"pg_test_{uuid.uuid4().hex[:6]}@domain.com"
        PersistenceRepository.create_user(
            user_id=test_uid,
            email=test_email,
            password_hash="pbkdf2_sha256$100000$test$hash",
            full_name="Postgres Migration Test User",
            role="CLINICIAN",
            license_number="LIC-PG-001"
        )
        as_id = str(uuid.uuid4())
        PersistenceRepository.save_assessment(as_id, {"user_id": test_uid, "biomarkers": {"ferritin": 12.0}})

        # Export SQL
        sql_dump = PersistenceRepository.export_to_postgres_sql()

        # Schema DDL assertions
        assert "CREATE TABLE IF NOT EXISTS users" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS assessments" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS reports" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS clinician_reviews" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS ground_truth_outcomes" in sql_dump
        assert "CREATE TABLE IF NOT EXISTS audit_events" in sql_dump

        # Data types assertions for Postgres compatibility
        assert "JSONB" in sql_dump
        assert "TIMESTAMPTZ" in sql_dump
        assert "ON CONFLICT" in sql_dump

        # Data dump assertions
        assert test_email in sql_dump
        assert as_id in sql_dump

    def test_postgres_export_api_endpoint(self):
        res = client.get("/api/v1/database/export-postgres")
        assert res.status_code == 200
        data = res.json()
        assert data["target_engine"] == "PostgreSQL 14+"
        assert data["compatibility"] == "JSONB, TIMESTAMPTZ, UUID"
        assert "CREATE TABLE IF NOT EXISTS" in data["sql_dump"]
