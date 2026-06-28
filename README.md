# Redrob AI Candidate Ranker

Career-first candidate ranking system for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

The ranker is built for the challenge constraints:

- CPU only
- no network calls during ranking
- under 5 minutes for 100k candidates
- reproducible from `candidates.jsonl`

## Demo Video

[Watch the walkthrough](https://1drv.ms/v/c/4c036607c49a6aa8/IQBMcAU0S0rPSJvRqDpt5nZzAfV034fiFyWGg8Jz9hMupkI?e=Fh8001)

## Approach

The job description asks for a Senior AI Engineer who has shipped production retrieval, ranking, search, recommender, or LLM systems. The dataset intentionally contains candidates with many AI keywords but weak career evidence, so this solution ranks candidates by demonstrated work rather than keyword count.

### Architecture

```mermaid
flowchart LR
    A["Job Description"] --> B["JD Requirement Parser"]

    B --> B1["Must-have signals<br/>retrieval, ranking, embeddings,<br/>vector search, evaluation"]
    B --> B2["Negative signals<br/>keyword stuffing, services-only history,<br/>inactive profile, suspicious skills"]
    B --> B3["Logistics signals<br/>experience band, India location,<br/>notice period, relocation"]

    C["Candidate Profiles<br/>candidates.jsonl"] --> D["Feature Extraction Layer"]

    D --> D1["Career Evidence<br/>profile summary + career history"]
    D --> D2["Skill Evidence<br/>skills, proficiency, duration,<br/>endorsements, assessments"]
    D --> D3["Behavioral Signals<br/>open to work, response rate,<br/>last active, interview completion"]
    D --> D4["Risk Signals<br/>inconsistencies, keyword stuffing,<br/>low-quality or suspicious profiles"]

    B1 --> E["Scoring Engine"]
    B2 --> E
    B3 --> E
    D1 --> E
    D2 --> E
    D3 --> E
    D4 --> E

    E --> F["Final Fit Score"]

    F --> G["Ranking Layer<br/>sort by score, tie-break by candidate_id"]

    G --> H["Top 100 Candidates"]

    H --> I["Reasoning Generator<br/>uses only extracted facts"]

    I --> J["submission.csv<br/>candidate_id, rank, score, reasoning"]

    J --> K["Official Validator"]
```

The score combines:

- career evidence from profile summaries and role descriptions
- role and title fit
- production search/ranking/retrieval experience
- product-company and startup fit
- location, notice period, and availability
- Redrob behavioral signals
- risk penalties for keyword stuffing, services-only history, inactive profiles, and honeypot-like inconsistencies

## Quick Start

```bash
python rank.py --candidates "./data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" --out submission.csv
```

Validate:

```bash
python "./data/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" submission.csv
```

## Files

- `rank.py` - CLI entrypoint
- `src/redrob_ranker/features.py` - feature extraction and text evidence
- `src/redrob_ranker/scoring.py` - scoring rubric
- `src/redrob_ranker/reasoning.py` - short recruiter-facing explanations
- `submission_metadata.yaml` - metadata template filled for this repo
- `submission.csv` - generated top-100 output


