import math
from datetime import date
import re

REFERENCE_DATE = date(2026, 6, 28)

RELEVANT_TITLE_PATTERNS = [
    "ai engineer",
    "machine learning",
    "ml engineer",
    "applied ml",
    "nlp engineer",
    "search engineer",
    "recommendation",
    "data scientist",
    "data engineer",
    "analytics engineer",
    "software engineer",
    "backend engineer",
]

CORE_EVIDENCE_TERMS = [
    "semantic search",
    "embedding",
    "embeddings",
    "retrieval",
    "ranking",
    "ranker",
    "recommendation",
    "recommender",
    "search",
    "vector search",
    "hybrid search",
    "rag",
    "llm",
    "nlp",
    "candidate-jd matching",
    "discovery feed",
]

INFRA_TERMS = [
    "faiss",
    "milvus",
    "qdrant",
    "pinecone",
    "weaviate",
    "elasticsearch",
    "opensearch",
    "vector database",
    "sentence-transformers",
    "bge",
    "e5",
    "openai embeddings",
]

EVAL_TERMS = [
    "ndcg",
    "mrr",
    "map",
    "offline evaluation",
    "online evaluation",
    "a/b test",
    "ab test",
    "experiment",
    "relevance",
    "ranking metric",
]

PRODUCTION_TERMS = [
    "production",
    "deployed",
    "shipped",
    "serving",
    "users",
    "scale",
    "latency",
    "monitoring",
    "index refresh",
    "real-time",
    "realtime",
    "pipeline",
    "operated",
]

SHIPPER_TERMS = [
    "built",
    "owned",
    "led",
    "implemented",
    "migrated",
    "rolled out",
    "launched",
    "designed",
    "end-to-end",
]

PRODUCT_COMPANIES = {
    "Zomato",
    "Paytm",
    "Flipkart",
    "Razorpay",
    "Dream11",
    "Swiggy",
    "Ola",
    "Freshworks",
    "Zoho",
    "Postman",
    "BrowserStack",
    "Meesho",
    "CRED",
    "PhonePe",
    "LinkedIn",
    "Google",
    "Meta",
    "Microsoft",
    "Apple",
    "Amazon",
    "Netflix",
    "Uber",
    "Airbnb",
    "Sarvam AI",
    "Rephrase.ai",
    "Verloop.io",
    "Observe.AI",
    "Haptik",
    "Yellow.ai",
    "upGrad",
    "Vedantu",
}

SERVICE_COMPANIES = {
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Cognizant",
    "Capgemini",
    "Mindtree",
    "Tech Mahindra",
    "Genpact",
    "HCLTech",
}

PREFERRED_CITIES = [
    "pune",
    "noida",
    "delhi",
    "gurgaon",
    "gurugram",
    "mumbai",
    "hyderabad",
    "bangalore",
    "bengaluru",
]

ADJACENT_INDIA_CITIES = ["chennai", "ahmedabad", "jaipur", "coimbatore", "kochi", "trivandrum"]

NON_TARGET_TITLES = [
    "hr manager",
    "accountant",
    "sales executive",
    "marketing manager",
    "graphic designer",
    "civil engineer",
    "mechanical engineer",
    "customer support",
    "operations manager",
    "content writer",
]

CV_SPEECH_TERMS = ["computer vision", "image classification", "speech recognition", "tts", "robotics", "gan"]

# Precompute lists, sets, and regexes for speed
RELEVANT_SKILL_TERMS = tuple(CORE_EVIDENCE_TERMS + INFRA_TERMS + EVAL_TERMS)
PROFICIENCY_SCORES = {"beginner": 0.2, "intermediate": 0.45, "advanced": 0.75, "expert": 1.0}
LOG_61 = math.log(61)

# Precompile regex for skill matching
RELEVANT_SKILL_PAT = re.compile("|".join(re.escape(term) for term in RELEVANT_SKILL_TERMS))

def normalize(text):
    if not text:
        return ""
    return " ".join(text.lower().split())

def bounded(value, low=0.0, high=1.0):
    return max(low, min(high, value))

def count_terms(text, terms):
    return sum(1 for term in terms if term in text)

def parse_date(value):
    try:
        parts = value.split("-")
        return int(parts[0]), int(parts[1])
    except Exception:
        return None

def months_since(value):
    parsed = parse_date(value)
    if not parsed:
        return 24
    year, month = parsed
    return max(0, (2026 - year) * 12 + 6 - month)

def skill_quality(skills, assessments):
    if not skills:
        return 0.0, 0, 0

    relevant = []
    impossible = 0
    for skill in skills:
        skill_name = skill.get("name") or ""
        name = normalize(skill_name)
        duration = skill.get("duration_months", 0) or 0
        proficiency = skill.get("proficiency", "")
        endorsements = skill.get("endorsements", 0) or 0
        is_relevant = bool(RELEVANT_SKILL_PAT.search(name))
        if is_relevant:
            prof_score = PROFICIENCY_SCORES.get(proficiency, 0.3)
            duration_score = bounded(duration / 48)
            endorsement_score = bounded(math.log1p(endorsements) / LOG_61)
            assessment_score = assessments.get(skill_name, assessments.get(skill_name.lower(), None))
            if assessment_score is not None:
                assessment_component = bounded(float(assessment_score) / 100)
            else:
                assessment_component = 0.45
            relevant.append(0.35 * prof_score + 0.25 * duration_score + 0.15 * endorsement_score + 0.25 * assessment_component)
        if proficiency in {"advanced", "expert"} and duration < 6:
            impossible += 1

    if not relevant:
        return 0.0, 0, impossible
    return sum(sorted(relevant, reverse=True)[:8]) / min(len(relevant), 8), len(relevant), impossible

def extract_features(candidate):
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    history = candidate["career_history"]
    skills = candidate.get("skills", [])
    assessments = signals.get("skill_assessment_scores", {})

    history_text = " ".join(
        f"{item.get('title') or ''} {item.get('industry') or ''} {item.get('description') or ''}" for item in history
    )
    skills_text = " ".join(skill.get("name") or "" for skill in skills)
    profile_text = f"{profile.get('headline') or ''} {profile.get('summary') or ''} {profile.get('current_title') or ''} {profile.get('current_industry') or ''}"
    
    career_only_text = normalize(f"{profile_text} {history_text}")
    skills_text_norm = normalize(skills_text)
    all_text = f"{career_only_text} {skills_text_norm}"

    num_roles = len(history)
    service_roles = 0
    product_roles = 0
    short_hops = 0
    for item in history:
        company = item.get("company", "")
        if company in SERVICE_COMPANIES:
            service_roles += 1
        if company in PRODUCT_COMPANIES:
            product_roles += 1
        duration = item.get("duration_months", 0) or 0
        if duration and duration < 18:
            short_hops += 1

    service_only = num_roles > 0 and service_roles == num_roles
    hop_risk = bounded(short_hops / max(1, num_roles))

    current_title = normalize(profile.get("current_title", ""))
    headline = normalize(profile.get("headline", ""))
    
    title_fit = 0.0
    for pattern in RELEVANT_TITLE_PATTERNS:
        if pattern in current_title:
            title_fit = 1.0
            break
        elif title_fit < 0.75 and pattern in headline:
            title_fit = 0.75

    non_target_title = False
    for title in NON_TARGET_TITLES:
        if title in current_title:
            non_target_title = True
            break

    years = float(profile.get("years_of_experience", 0) or 0)
    experience_fit = bounded(1 - abs(years - 7) / 5)
    if 5 <= years <= 9:
        experience_fit = max(experience_fit, 0.9)
    elif 4 <= years < 5 or 9 < years <= 11:
        experience_fit = max(experience_fit, 0.65)

    location = normalize(profile.get("location", ""))
    country = profile.get("country", "")
    
    location_fit = 0.05
    if country == "India":
        location_fit = 0.55
        for city in PREFERRED_CITIES:
            if city in location:
                location_fit = 1.0
                break
        if location_fit == 0.55:
            for city in ADJACENT_INDIA_CITIES:
                if city in location:
                    location_fit = 0.7
                    break

    core_career_hits = count_terms(career_only_text, CORE_EVIDENCE_TERMS)
    infra_career_hits = count_terms(career_only_text, INFRA_TERMS)
    eval_hits = count_terms(career_only_text, EVAL_TERMS)
    production_hits = count_terms(career_only_text, PRODUCTION_TERMS)
    shipper_hits = count_terms(career_only_text, SHIPPER_TERMS)
    cv_speech_hits = count_terms(career_only_text, CV_SPEECH_TERMS)

    skill_score, relevant_skill_count, impossible_skill_count = skill_quality(skills, assessments)
    skill_keyword_gap = max(0, relevant_skill_count - core_career_hits - infra_career_hits)

    response_rate = float(signals.get("recruiter_response_rate", 0) or 0)
    response_time = float(signals.get("avg_response_time_hours", 999) or 999)
    notice = float(signals.get("notice_period_days", 180) or 180)
    last_active_months = months_since(signals.get("last_active_date", ""))
    github_activity = max(0.0, float(signals.get("github_activity_score", -1) or -1)) / 100

    activity_score = bounded(1 - last_active_months / 8)
    response_time_score = bounded(1 - response_time / 168)
    notice_score = bounded(1 - notice / 120)
    behavioral_score = (
        0.22 * (1.0 if signals.get("open_to_work_flag") else 0.0)
        + 0.24 * response_rate
        + 0.18 * response_time_score
        + 0.16 * notice_score
        + 0.12 * activity_score
        + 0.08 * float(signals.get("interview_completion_rate", 0) or 0)
    )

    profile_completeness = bounded(float(signals.get("profile_completeness_score", 0) or 0) / 100)
    external_validation = 0.5 * github_activity + 0.25 * (1 if signals.get("linkedin_connected") else 0) + 0.25 * profile_completeness

    return {
        "candidate_id": candidate["candidate_id"],
        "years": years,
        "title_fit": title_fit,
        "non_target_title": non_target_title,
        "experience_fit": experience_fit,
        "location_fit": location_fit,
        "core_career_hits": core_career_hits,
        "infra_career_hits": infra_career_hits,
        "eval_hits": eval_hits,
        "production_hits": production_hits,
        "shipper_hits": shipper_hits,
        "skill_score": skill_score,
        "relevant_skill_count": relevant_skill_count,
        "skill_keyword_gap": skill_keyword_gap,
        "behavioral_score": behavioral_score,
        "external_validation": external_validation,
        "service_only": service_only,
        "product_roles": product_roles,
        "cv_speech_hits": cv_speech_hits,
        "impossible_skill_count": impossible_skill_count,
        "hop_risk": hop_risk,
        "last_active_months": last_active_months,
        "notice_days": notice,
        "response_rate": response_rate,
        "response_time_hours": response_time,
        "github_activity": github_activity,
        "open_to_work": bool(signals.get("open_to_work_flag")),
        "willing_to_relocate": bool(signals.get("willing_to_relocate")),
        "country": country,
        "location": profile.get("location", ""),
        "career_only_text": career_only_text,
        "all_text": all_text,
    }
