import argparse
import csv
import gzip
import json
from pathlib import Path

from .features import extract_features
from .reasoning import build_reasoning
from .scoring import score_candidate


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def rank_candidates(candidates_path: Path, limit: int = 100):
    scored = []
    with _open_text(candidates_path) as handle:
        for line in handle:
            if not line.strip():
                continue
            candidate = json.loads(line)
            features = extract_features(candidate)
            score, components = score_candidate(features)
            scored.append((score, candidate["candidate_id"], candidate, features, components))

    scored.sort(key=lambda row: (-row[0], row[1]))
    top = scored[:limit]
    if not top:
        return []

    best = top[0][0]
    worst = top[-1][0]
    spread = best - worst if best != worst else 1.0
    rows = []
    for index, (raw_score, candidate_id, candidate, features, components) in enumerate(top, start=1):
        normalized = 0.2 + 0.79 * ((raw_score - worst) / spread)
        rows.append(
            {
                "candidate_id": candidate_id,
                "rank": index,
                "score": f"{normalized:.4f}",
                "reasoning": build_reasoning(candidate, features, components, index),
            }
        )
    return rows


def write_submission(rows, out_path: Path):
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Rank Redrob candidates for the Senior AI Engineer JD.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument("--out", default="submission.csv", help="Output CSV path")
    parser.add_argument("--limit", type=int, default=100, help="Number of candidates to output")
    args = parser.parse_args()

    rows = rank_candidates(Path(args.candidates), args.limit)
    write_submission(rows, Path(args.out))
    print(f"Wrote {len(rows)} rows to {args.out}")

