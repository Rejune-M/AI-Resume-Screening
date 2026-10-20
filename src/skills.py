import re
from collections import Counter


SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "nlp",
    "natural language processing",
    "computer vision",
    "opencv",
    "html",
    "css",
    "javascript",
    "react",
    "android",
    "kotlin",
    "git",
    "github",
    "data structures",
    "data analysis",
    "flask",
    "django",
    "streamlit"
]

KEYWORD_STOPWORDS = {
    "about", "across", "able", "and", "are", "as", "at", "be", "been",
    "best", "but", "by", "can", "candidate", "company", "experience",
    "for", "from", "have", "having", "into", "job", "join", "looking",
    "must", "our", "role", "team", "their", "this", "through", "to",
    "use", "using", "we", "will", "with", "work", "you", "your",
    "years", "preferred", "required", "requirements", "responsibilities",
}


def extract_job_keywords(text, limit=18):
    """Extract frequent, readable one- and two-word terms from a job ad."""
    tokens = re.findall(r"[a-z][a-z0-9+#.-]*", text.lower())
    tokens = [token.strip(".-") for token in tokens]
    tokens = [token for token in tokens if len(token) > 1 and token not in KEYWORD_STOPWORDS]
    counts = Counter(token for token in tokens if len(token) >= 3)

    for first, second in zip(tokens, tokens[1:]):
        if first not in KEYWORD_STOPWORDS and second not in KEYWORD_STOPWORDS:
            counts[f"{first} {second}"] += 1

    return [term for term, _ in counts.most_common(limit)]


def extract_skills(text):
    """Return known skills found as whole terms, avoiding substring matches."""
    normalized_text = text.lower()
    found_skills = []

    for skill in SKILLS:
        # Treat punctuation in skill names literally, while requiring word
        # boundaries around their first and last alphanumeric characters.
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return found_skills
