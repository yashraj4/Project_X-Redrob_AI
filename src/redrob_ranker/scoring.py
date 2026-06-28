from .features import bounded


def score_candidate(features):
    career_evidence = bounded(
        0.32 * min(features["core_career_hits"] / 8, 1)
        + 0.18 * min(features["infra_career_hits"] / 4, 1)
        + 0.16 * min(features["eval_hits"] / 3, 1)
        + 0.20 * min(features["production_hits"] / 5, 1)
        + 0.14 * min(features["shipper_hits"] / 5, 1)
    )

    company_fit = bounded(0.25 + 0.28 * features["product_roles"])
    if features["service_only"]:
        company_fit = 0.05

    logistics = (
        0.45 * features["experience_fit"]
        + 0.35 * features["location_fit"]
        + 0.20 * bounded(1 - features["notice_days"] / 120)
    )

    role_fit = features["title_fit"]
    if features["non_target_title"] and career_evidence < 0.45:
        role_fit *= 0.25

    score = (
        3.2 * career_evidence
        + 1.35 * role_fit
        + 0.75 * features["skill_score"]
        + 0.85 * company_fit
        + 0.75 * logistics
        + 0.8 * features["behavioral_score"]
        + 0.4 * features["external_validation"]
    )

    penalties = 0.0
    if features["service_only"]:
        penalties += 0.55
    if features["non_target_title"] and features["skill_keyword_gap"] >= 5:
        penalties += 0.9
    if features["cv_speech_hits"] >= 2 and features["core_career_hits"] < 3:
        penalties += 0.25
    if features["impossible_skill_count"] >= 4:
        penalties += 0.45
    if features["hop_risk"] > 0.6:
        penalties += 0.25
    if not features["open_to_work"] and features["behavioral_score"] < 0.35:
        penalties += 0.35
    if features["last_active_months"] >= 7:
        penalties += 0.3
    if features["country"] != "India":
        penalties += 0.55
        if not features["willing_to_relocate"]:
            penalties += 0.25

    final = score - penalties
    components = {
        "career_evidence": career_evidence,
        "role_fit": role_fit,
        "company_fit": company_fit,
        "logistics": logistics,
        "behavioral": features["behavioral_score"],
        "penalties": penalties,
    }
    return final, components
