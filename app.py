import streamlit as st
import pandas as pd

from src.parser import extract_resume_text
from src.preprocessing import clean_text
from src.skills import extract_skills
from src.matcher import (
    calculate_similarity,
    calculate_skill_score,
    calculate_final_score
)


st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 AI Resume Screening & Candidate Ranking")

st.write(
    "Analyze and rank resumes against a job description "
    "using NLP and machine learning techniques."
)


# ------------------------------------------------
# JOB DESCRIPTION
# ------------------------------------------------

st.header("1. Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=250,
    placeholder=(
        "Example: Looking for an AI/ML developer "
        "with Python, Machine Learning, Pandas, "
        "NumPy and SQL experience."
    )
)


# ------------------------------------------------
# RESUME UPLOAD
# ------------------------------------------------

st.header("2. Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload PDF or DOCX resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)


# ------------------------------------------------
# ANALYZE
# ------------------------------------------------

if st.button("🚀 Analyze Candidates"):

    if not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

    elif not uploaded_files:

        st.warning(
            "Please upload at least one resume."
        )

    else:

        clean_job = clean_text(
            job_description
        )

        job_skills = extract_skills(
            clean_job
        )

        results = []

        for file in uploaded_files:

            # Extract resume
            resume_text = extract_resume_text(file)

            # Clean resume
            clean_resume = clean_text(
                resume_text
            )

            # Extract skills
            resume_skills = extract_skills(
                clean_resume
            )

            # Similarity
            similarity_score = calculate_similarity(
                clean_resume,
                clean_job
            )

            # Skill score
            skill_score = calculate_skill_score(
                resume_skills,
                job_skills
            )

            # Final score
            final_score = calculate_final_score(
                similarity_score,
                skill_score
            )

            # Matching skills
            matching_skills = list(
                set(resume_skills)
                &
                set(job_skills)
            )

            # Missing skills
            missing_skills = list(
                set(job_skills)
                -
                set(resume_skills)
            )

            results.append({

                "Candidate": file.name,

                "Similarity": similarity_score,

                "Skill Match": skill_score,

                "Final Score": final_score,

                "Matching Skills":
                    ", ".join(matching_skills),

                "Missing Skills":
                    ", ".join(missing_skills)
            })


        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Rank candidates
        results_df = results_df.sort_values(
            by="Final Score",
            ascending=False
        ).reset_index(drop=True)

        # Ranking number
        results_df.insert(
            0,
            "Rank",
            range(1, len(results_df) + 1)
        )


        # ------------------------------------------------
        # RESULTS
        # ------------------------------------------------

        st.header("3. Candidate Ranking")

        st.dataframe(
            results_df,
            use_container_width=True
        )


        # ------------------------------------------------
        # TOP CANDIDATE
        # ------------------------------------------------

        top_candidate = results_df.iloc[0]

        st.header("🏆 Top Candidate")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Candidate",
                top_candidate["Candidate"]
            )

        with col2:

            st.metric(
                "Final Score",
                f"{top_candidate['Final Score']}%"
            )

        with col3:

            st.metric(
                "Skill Match",
                f"{top_candidate['Skill Match']}%"
            )


        # ------------------------------------------------
        # DOWNLOAD RESULTS
        # ------------------------------------------------

        csv = results_df.to_csv(
            index=False
        )

        st.download_button(
            "📥 Download Ranking CSV",
            csv,
            "candidate_ranking.csv",
            "text/csv"
        )