import streamlit as st
import pandas as pd

from src.parser import extract_resume_text
from src.preprocessing import clean_text
from src.skills import extract_job_keywords, extract_skills
from src.resume_analyzer import analyze_resume
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

        job_skills = extract_skills(clean_job)
        job_keywords = extract_job_keywords(job_description)

        with st.expander("Job keywords this checker will look for"):
            st.caption("These are suggestions extracted from the job description. Add them only when they accurately reflect your experience.")
            st.write(", ".join(job_keywords) or "No keywords could be extracted.")

        if not job_skills:
            st.info(
                "No skills from the built-in skill list were found in the job description. "
                "The ranking will rely on text similarity; skill match scores will be 0%."
            )

        results = []

        errors = []
        for file in uploaded_files:
            try:
                resume_text = extract_resume_text(file)
            except Exception as error:
                errors.append(f"{file.name}: could not read file ({error})")
                continue

            if not resume_text.strip():
                errors.append(
                    f"{file.name}: no text could be extracted. It may be scanned or empty."
                )
                continue

            # Clean resume
            clean_resume = clean_text(
                resume_text
            )

            # Extract skills
            resume_skills = extract_skills(
                clean_resume
            )
            resume_report = analyze_resume(
                resume_text,
                job_skills,
                job_keywords,
                filename=file.name,
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
            matching_skills = [skill for skill in job_skills if skill in resume_skills]

            # Missing skills
            missing_skills = [skill for skill in job_skills if skill not in resume_skills]

            results.append({

                "Candidate": file.name,

                "Similarity": similarity_score,

                "Skill Match": skill_score,

                "Final Score": final_score,

                "Matching Skills":
                    ", ".join(matching_skills),

                "Missing Skills":
                    ", ".join(missing_skills),

                "Resume Report": resume_report,
            })


        for error in errors:
            st.warning(error)

        if not results:
            st.error("No readable resume text was found, so candidates could not be ranked.")
            st.stop()

        # Convert results to DataFrame
        results_df = pd.DataFrame(
            [{key: value for key, value in result.items() if key != "Resume Report"}
             for result in results]
        )

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
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Candidate details")
        results_by_name = {result["Candidate"]: result for result in results}
        for candidate_name in results_df["Candidate"]:
            result = results_by_name[candidate_name]
            with st.expander(f"{result['Candidate']} · {result['Final Score']}%"):
                st.write(f"**Text similarity:** {result['Similarity']}%")
                st.write(f"**Skill match:** {result['Skill Match']}%")
                st.write("**Matching skills:** " + (result["Matching Skills"] or "None found"))
                st.write("**Missing job skills:** " + (result["Missing Skills"] or "None"))
                report = result["Resume Report"]
                passed_checks = sum(check["passed"] for check in report["checks"])
                st.write(f"**Resume quality checks:** {passed_checks}/{len(report['checks'])} passed")
                for check in report["checks"]:
                    icon = "✅" if check["passed"] else "💡"
                    st.write(f"{icon} **{check['name']}:** {check['detail']}")
                st.write("**Job keywords found:** " + (", ".join(report["matched_keywords"]) or "None"))
                st.write("**Job keywords not found:** " + (", ".join(report["missing_keywords"]) or "None"))


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
