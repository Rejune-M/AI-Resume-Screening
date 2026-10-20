import re
from collections import Counter


SECTION_PATTERNS = {
    "Experience": r"\b(experience|employment|work history|professional background)\b",
    "Education": r"\b(education|academic background|qualifications)\b",
    "Skills": r"\b(skills|technical skills|core competencies)\b",
}


def analyze_resume(text, job_skills, job_keywords=None, filename="resume"):
    """Return transparent, lightweight resume checks and actionable feedback."""
    normalized = text.lower()
    checks = []

    sections = [name for name, pattern in SECTION_PATTERNS.items()
                if re.search(pattern, normalized)]
    missing_sections = [name for name in SECTION_PATTERNS if name not in sections]
    checks.append({
        "name": "Core sections",
        "passed": not missing_sections,
        "detail": ("Found: " + ", ".join(sections)) if not missing_sections
        else "Consider adding: " + ", ".join(missing_sections),
    })

    has_email = bool(re.search(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", normalized))
    checks.append({
        "name": "Email address",
        "passed": has_email,
        "detail": "An email address was detected." if has_email
        else "Add a professional email address in your contact details.",
    })

    has_phone = bool(re.search(r"(?:\+?\d[\d ().-]{7,}\d)", text))
    checks.append({
        "name": "Phone number",
        "passed": has_phone,
        "detail": "A phone number was detected." if has_phone
        else "Add a reachable phone number if appropriate for your applications.",
    })

    quantified = bool(re.search(
        r"(?:[$₹]\s*\d[\d,.]*|\b\d+(?:\.\d+)?\s*(?:%|percent|x|k|m|million|billion|users?|customers?|projects?|hours?|days?|weeks?|months?|years?|revenue|sales)\b)",
        normalized,
    ))
    checks.append({
        "name": "Measurable achievements",
        "passed": quantified,
        "detail": "Numbers or measurable outcomes were detected." if quantified
        else "Where accurate, add numbers that show the scale or outcome of your work.",
    })

    action_verbs = re.findall(
        r"\b(achieved|built|created|delivered|designed|developed|improved|increased|led|launched|managed|reduced|implemented)\b",
        normalized,
    )
    checks.append({
        "name": "Specific action language",
        "passed": bool(action_verbs),
        "detail": "Action verbs were detected." if action_verbs
        else "Start experience bullets with specific actions, such as built, led, or improved.",
    })

    matched = [skill for skill in job_skills if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", normalized)]
    missing = [skill for skill in job_skills if skill not in matched]
    checks.append({
        "name": "Job skill alignment",
        "passed": bool(job_skills) and not missing,
        "detail": (
            "No supported skills were detected in the job description."
            if not job_skills else
            ("Matching skills: " + (", ".join(matched) or "none"))
            + (". Missing: " + ", ".join(missing) if missing else ".")
        ),
    })

    job_keywords = job_keywords or []
    matched_keywords = [term for term in job_keywords
                        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized)]
    missing_keywords = [term for term in job_keywords if term not in matched_keywords]
    checks.append({
        "name": "Job-specific keywords",
        "passed": bool(job_keywords) and len(matched_keywords) / len(job_keywords) >= 0.5,
        "detail": (
            f"Found {len(matched_keywords)} of {len(job_keywords)} suggested terms. "
            + ("Consider adding naturally where accurate: " + ", ".join(missing_keywords)
               if missing_keywords else "All suggested terms were found.")
        ) if job_keywords else "No job-specific keywords were available to check.",
    })

    filename_ok = len(filename.rsplit(".", 1)[0]) <= 60 and bool(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.-]*", filename)
    )
    checks.append({
        "name": "Resume filename",
        "passed": filename_ok,
        "detail": "Filename is simple and readable." if filename_ok
        else "Use a clear filename with your name and target role; avoid special characters.",
    })

    date_spans = re.findall(
        r"\b(?:19|20)\d{2}\s*(?:-|–|—|to)\s*(?:(?:19|20)\d{2}|present|current)\b",
        normalized,
    )
    checks.append({
        "name": "Employment date ranges",
        "passed": bool(date_spans),
        "detail": "A year-based date range was detected." if date_spans
        else "Use clear, consistent date ranges (for example, 2022–2025) for roles and education.",
    })

    words = re.findall(r"\b\w+\b", normalized)
    trigrams = [tuple(words[index:index + 3]) for index in range(max(0, len(words) - 2))]
    repeated = [" ".join(phrase) for phrase, count in Counter(trigrams).items()
                if count > 1]
    checks.append({
        "name": "Repeated wording",
        "passed": not repeated,
        "detail": "No repeated three-word phrases detected." if not repeated
        else "Review repeated wording: " + ", ".join(repeated[:3]),
    })

    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    long_lines = sum(len(line.split()) > 45 for line in paragraphs)
    checks.append({
        "name": "Readable bullet length",
        "passed": bool(paragraphs) and long_lines == 0,
        "detail": "Text blocks are concise." if long_lines == 0
        else f"{long_lines} text block(s) exceed 45 words; consider shortening long bullets.",
    })

    return {
        "checks": checks,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }
