from pathlib import Path
import pandas as pd
from smart_applier.agents.profile_agent import UserProfileAgent
from smart_applier.agents.job_matching_agent import JobMatchingAgent
from smart_applier.agents.skill_gap_agent import SkillGapAgent
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.agents.resume_tailor_agent import ResumeTailorAgent


def main():
    # ---------- Setup ----------
    user_id = "aparnassunils"
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"

    profile_dir = data_dir / "profiles"
    jobs_dir = data_dir / "jobs"
    resumes_dir = data_dir / "resumes"
    resumes_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting Smart Applier AI Workflow...\n")

    # ---------- Step 1: Load User Profile ----------
    profile_agent = UserProfileAgent(profile_dir)
    profile = profile_agent.load_profile(user_id)
    if not profile:
        print(f"❌ No profile found for {user_id}")
        return
    print(f"✅ Loaded profile for {user_id}")

    # ---------- Step 2: Job Matching ----------
    print("\n🔍 Matching jobs based on profile...")
    matcher = JobMatchingAgent()
    jobs_files = list(jobs_dir.glob("karkidi_jobs_*.csv"))
    if not jobs_files:
        print("❌ No job CSVs found in data/jobs/. Please run job_scraper_agent first.")
        return

    latest_jobs_file = max(jobs_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Using jobs file: {latest_jobs_file.name}")

    jobs_df = pd.read_csv(latest_jobs_file)
    user_vector = matcher.embed_user_profile(profile)
    job_vectors = matcher.embed_jobs(jobs_df)
    top_jobs = matcher.match_jobs(user_vector, jobs_df, job_vectors, top_k=10)

    top_jobs_file = jobs_dir / "top_matched_jobs.csv"
    top_jobs.to_csv(top_jobs_file, index=False, encoding="utf-8-sig")
    print(f"✅ Top matched jobs saved to {top_jobs_file}")

    # ---------- Step 3: Skill Gap Analysis ----------
    print("\n🧠 Running skill gap analysis...")
    gap_agent = SkillGapAgent(user_id=user_id, jobs_file=top_jobs_file)
    recommendations = gap_agent.get_recommendations()

    print("\n📚 Recommended Learning Resources:")
    for skill, resources in recommendations.items():
        print(f"\n{skill.title()}:")
        for r in resources:
            print(f" - {r}")

    # ---------- Step 4: Resume Builder ----------
    print("\n🧾 Building base resume PDF...")
    builder = ResumeBuilderAgent(profile)
    builder.build_resume()
    resume_path = builder.save_to_file()
    print(f"✅ Base resume generated at: {resume_path}")

    # ---------- Step 5: Resume Tailoring ----------
    jd_file = jobs_dir / "sample_job_description.txt"
    if jd_file.exists():
        print("\n🎯 Tailoring resume to job description...")
        with open(jd_file, "r", encoding="utf-8") as f:
            job_desc = f.read()
        tailor_agent = ResumeTailorAgent()
        tailor_agent.tailor_profile(profile, job_desc)
    else:
        print("\n⚠️ No sample_job_description.txt found in data/jobs/. Skipping tailoring step.")

    print("\n🎉 All tasks complete! Smart Applier AI pipeline finished successfully.")


if __name__ == "__main__":
    main()
