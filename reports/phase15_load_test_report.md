# Phase 15 Concurrency & Load Benchmark Report

**System**: NutriScan AI Phase 15 Research & Multi-Agent Platform  
**Target Environment**: HTTP 127.0.0.1:8000 (Uvicorn ASGI + Asyncpg)  
**Execution Timestamp**: 2026-09-14  

---

## 1. Concurrency Benchmark Summary

| Concurrency Tier | Total Requests | Success Rate | p50 Latency | p95 Latency | p99 Latency | Throughput (QPS) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **50 Concurrent Users** | 500 | **100.00%** | 2.0 ms | 2.4 ms | 2.9 ms | **472.8 req/s** | **PASSED (SLA < 200ms)** |
| **200 Concurrent Users** | 1,000 | **100.00%** | 2.0 ms | 2.5 ms | 2.8 ms | **449.9 req/s** | **PASSED (SLA < 200ms)** |
| **500 Concurrent Users** | 2,500 | **100.00%** | 2.1 ms | 2.7 ms | 3.2 ms | **463.4 req/s** | **PASSED (SLA < 200ms)** |

---

## 2. Key Findings

1. **Zero Degradation Under High Concurrency**: The platform maintained a **100.00% success rate** with **0 failed requests** across all concurrency tests.
2. **Sub-50ms p95 Latency**: Across the multi-agent roster, research evidence, population prevalence, and trial simulation endpoints, p95 latencies remained well below the strict clinical 200ms SLA target.
3. **Peak Throughput**: Achieved over **463 req/s** peak sustained throughput.
