from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(resume_text, job_description):

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    return round(similarity[0][0] * 100, 2)


def calculate_skill_score(resume_skills, job_skills):

    if not job_skills:
        return 0

    matched_skills = set(resume_skills) & set(job_skills)

    score = (
        len(matched_skills) /
        len(set(job_skills))
    ) * 100

    return round(score, 2)


def calculate_final_score(
    similarity_score,
    skill_score
):

    final_score = (
        similarity_score * 0.60 +
        skill_score * 0.40
    )

    return round(final_score, 2)