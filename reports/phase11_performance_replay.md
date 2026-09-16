# NutriScan AI — Phase 11 Performance Replay Benchmark
**Benchmarking Mode:** Live Replay Execution (`time.perf_counter()`)  
**Date:** September 13, 2026  
**Auditor:** MLOps Engineer & Systems Performance Lead  
**SLA Status:** **ALL TARGET PERFORMANCE SLAs SATISFIED**

---

## 1. Single Patient Prediction Latency

Benchmarked across 30 consecutive single patient evaluations against `ClinicalRiskEngine.predict_patient()`:

| Metric | Target SLA | Measured Value | Performance Verdict |
| :--- | :---: | :---: | :---: |
| **Mean Latency** | < 500 ms | **151.73 ms** | **MEETS SLA** |
| **Median Latency** | < 500 ms | **149.24 ms** | **MEETS SLA** |
| **95th Percentile (P95)** | < 500 ms | **162.46 ms** | **MEETS SLA** |
| **Maximum Latency** | < 500 ms | **172.14 ms** | **MEETS SLA** |
| **Minimum Latency** | N/A | **144.57 ms** | **OPTIMAL** |

*Analysis:* Single patient execution latency is roughly **3.3x faster** than the 500ms production ceiling, providing ample headroom for network transport and gateway serialization.

---

## 2. Vectorized Batch Scalability Benchmark

Batches of sizes 10, 50, and 100 patient profiles were replayed sequentially:

| Batch Workload | Total Duration (ms) | Per-Record Latency (ms) | Peak Heap Memory | Heap Post-GC Delta | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Batch 10** | 1,643.52 ms | 164.35 ms / rec | 757.7 KB | 0.0 KB | **PASS** |
| **Batch 50** | 7,713.80 ms | 154.28 ms / rec | 2,240.7 KB | 0.0 KB | **PASS** |
| **Batch 100** | 15,603.00 ms | 156.03 ms / rec | 3,727.0 KB | 0.0 KB | **PASS** |

### Key Scaling Observations:
1. **Linear Scaling $O(N)$:** Per-record execution remains flat between $154\text{ ms}$ and $164\text{ ms}$ regardless of batch size.
2. **Predictable Throughput:** 100 patient assessments can be completely screened across all 9 deficiency models in approximately $15.6\text{ seconds}$.
3. **Memory Boundedness:** Heap consumption remains under $4\text{ MB}$ even at $N=100$, with zero memory leaks detected.

**Performance Replay Gate: PASS**
