# Raqib verification and benchmarks

Measurements below are from [GitHub Actions run 5](https://github.com/wahibi404/fraud-service/actions/runs/45218451002) on Ubuntu with Python 3.12. They describe that runner, not a production latency guarantee.

| Check | Observed result |
| --- | --- |
| Fast suite | 70 passed, 1 slow deselected, 5.35 s |
| Branch coverage | 98.46%, threshold 80% |
| Golden behavioural test | 1 passed, 70 deselected, 11.43 s |
| Batch scoring | 5,000 transactions in 10.9 s |
| Batch comparison | **5,000/5,000 rows match** `data/golden_scores_v3.csv` |
| FastAPI load | 2,000 requests, 25 concurrent, 11.2 s wall time |
| API latency | p50 140.7 ms; p99 209.0 ms; max 230.3 ms |
| API throughput | 178 requests/s; 0 non-2xx responses |
| Docker image smoke | Built; readiness, prediction and non-root `appuser` checks passed |

The course's before/after warm-up timing, naive-image comparison, four-worker comparison, local Docker memory and cache rebuild timings were not measured in this environment. The final workflow also measures image size and checks the Compose stack; see its latest run for their results.
