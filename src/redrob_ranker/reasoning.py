def _top_evidence(features):
    parts = []
    if features["core_career_hits"] >= 6:
        parts.append("strong search/retrieval/ranking evidence")
    elif features["core_career_hits"] >= 3:
        parts.append("clear applied ML retrieval evidence")
    if features["infra_career_hits"] >= 2:
        parts.append("vector/hybrid search infrastructure")
    if features["eval_hits"] >= 1:
        parts.append("ranking evaluation exposure")
    if features["product_roles"] >= 1:
        parts.append("product-company background")
    return parts[:3]


def build_reasoning(candidate, features, components, rank):
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    title = profile["current_title"]
    years = profile["years_of_experience"]
    location = profile["location"]

    evidence = _top_evidence(features)
    if evidence:
        evidence_text = ", ".join(evidence)
    else:
        evidence_text = "adjacent ML/backend evidence"

    concerns = []
    if features["notice_days"] >= 90:
        concerns.append(f"{int(features['notice_days'])}-day notice")
    if features["response_rate"] < 0.35:
        concerns.append(f"lower recruiter response rate ({features['response_rate']:.2f})")
    if features["service_only"]:
        concerns.append("services-only career history")
    if features["location_fit"] < 0.2:
        concerns.append("outside India logistics")
    if features["non_target_title"] and components["career_evidence"] < 0.5:
        concerns.append("title is not an AI/ML engineering role")

    availability = (
        f"open-to-work, response rate {signals.get('recruiter_response_rate', 0):.2f}"
        if signals.get("open_to_work_flag")
        else f"not marked open-to-work, response rate {signals.get('recruiter_response_rate', 0):.2f}"
    )

    if rank <= 25:
        lead = f"{title} with {years:.1f} yrs in {location}; {evidence_text} matches the JD's production intelligence-layer needs."
    elif rank <= 70:
        lead = f"{title} with {years:.1f} yrs; {evidence_text}, though fit is less complete than the top group."
    else:
        lead = f"{title} with {years:.1f} yrs; included as a lower-confidence profile with some relevant evidence."

    if concerns:
        return f"{lead} Availability: {availability}; concern: {', '.join(concerns[:2])}."
    return f"{lead} Availability: {availability}; logistics and behavioral signals are supportive."

