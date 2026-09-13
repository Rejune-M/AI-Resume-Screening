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


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill in text:
            found_skills.append(skill)

    return found_skills