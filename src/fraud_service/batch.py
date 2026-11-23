"""Batch entrypoint: score a CSV of transactions.

An entrypoint is a composition root: the only place where concrete
classes (SklearnModel) are wired into the use-case (FraudScorer).
"""
import argparse
import csv
import time
from collections import Counter
from pathlib import Path

from fraud_service.adapters.sklearn_model import SklearnModel
from fraud_service.domain.entities import Transaction
from fraud_service.service.scorer import FraudScorer


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a CSV of transactions")
    parser.add_argument("--input", type=Path, default=Path("data/transactions_sample.csv"))
    parser.add_argument("--output", type=Path, default=Path("scored.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/fraud_xgb_v3.joblib"))
    parser.add_argument("--threshold", type=float, default=0.85)
    args = parser.parse_args()

    t0 = time.perf_counter()
    model = SklearnModel.load(args.model)
    print(f"Loaded model fraud_xgb {model.model_version} in {time.perf_counter() - t0:.2f}s")
    scorer = FraudScorer(model=model, block_threshold=args.threshold)

    fields = list(Transaction.model_fields)
    counts: Counter[str] = Counter()
    t0 = time.perf_counter()
    with args.input.open(newline="", encoding="utf-8") as src, \
         args.output.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.writer(dst)
        writer.writerow(["transaction_id", "score", "decision", "model_version"])
        for row in csv.DictReader(src):
            txn = Transaction(**{name: row[name] for name in fields})
            result = scorer.score(txn)
            writer.writerow([result.transaction_id, f"{result.probability:.9f}",
                             result.decision.value, result.model_version])
            counts[result.decision.value] += 1

    total = sum(counts.values())
    print(f"Scored {total:,} transactions -> {args.output} in {time.perf_counter() - t0:.1f}s "
          f"(block: {counts['block']}, review: {counts['review']}, allow: {counts['allow']})")


if __name__ == "__main__":
    main()
