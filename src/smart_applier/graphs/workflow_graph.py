from langgraph.graph import StateGraph, END
from typing import TypedDict
import pandas as pd

from smart_applier.agents.profile_agent import UserProfileAgent
from smart_applier.agents.job_scraper_agent import JobScraperAgent
from smart_applier.agents.job_matching_agent import JobMatchingAgent
from smart_applier.agents.skill_gap_agent import SkillGapAgent
from smart_applier.agents.resume_tailor_agent import ResumeTailorAgent
from smart_applier.agents.resume_builder_agent import ResumeBuilderAgent
from smart_applier.utils.path_utils import get_data_dirs


# -------------------------
# Graph State Definition
# -------------------------
class JobApplicationState(TypedDict):
    user_id: str
    profile: dict
    scraped_jobs: pd.DataFrame
    matched_jobs: pd.DataFrame
    tailored_profile: dict
    recommendations: dict


# -------------------------
# Step 1: Load Profile
# -------------------------
def load_profile(state: JobApplicationState):
    agent = UserProfileAgent()
    profile = agent.load_profile(state["user_id"])

    # 🧠 Display user skills
    user_skills = [
        s.lower().strip()
        for subcat, skills in profile.get("skills", {}).items()
        for s in skills if s.strip()
    ]
    print("\n🎯 User Skills:")
    print(", ".join(sorted(set(user_skills))))

    return {**state, "profile": profile}


# -------------------------
# Step 2: Build Resume (Base Resume)
# -------------------------
def build_resume(state: JobApplicationState):
    builder = ResumeBuilderAgent(state["profile"])
    builder.build_resume()
    pdf_path = builder.save_to_file()
    print(f"📄 Base resume built and saved at: {pdf_path}")
    return state


# -------------------------
# Step 3: Scrape Jobs
# -------------------------
def scrape_jobs(state: JobApplicationState):
    scraper = JobScraperAgent()
    scraped_state = scraper.scrape_karkidi({"job_data": pd.DataFrame()}, pages=2)
    return {**state, "scraped_jobs": scraped_state["job_data"]}


# -------------------------
# Step 4: Match Jobs
# -------------------------
def match_jobs(state: JobApplicationState):
    matcher = JobMatchingAgent()
    jobs_df = state["scraped_jobs"]

    profile_vector = matcher.embed_user_profile(state["profile"])
    job_vectors = matcher.embed_jobs(jobs_df)
    top_jobs = matcher.match_jobs(profile_vector, jobs_df, job_vectors, top_k=10)

    # 💡 Show skills extracted from top matched jobs
    if "Skills" in top_jobs.columns:
        print("\n💼 Skills from Top Matched Jobs:")
        job_skills_series = top_jobs["Skills"].dropna().head(10)
        all_job_skills = set()
        for skills in job_skills_series:
            for s in str(skills).split(","):
                if s.strip():
                    all_job_skills.add(s.strip().lower())
        print(", ".join(sorted(all_job_skills)))

    return {**state, "matched_jobs": top_jobs}


# -------------------------
# Step 5: Analyze Skill Gaps
# -------------------------
def analyze_skills(state: JobApplicationState):
    paths = get_data_dirs()
    jobs_file = paths["jobs"] / "top_matched_jobs.csv"
    state["matched_jobs"].to_csv(jobs_file, index=False)

    skill_agent = SkillGapAgent(user_id=state["user_id"], jobs_file=jobs_file)
    recommendations = skill_agent.get_recommendations()

    # 🔍 Extract and show missing skills (optional)
    missing_skills = list(recommendations.keys())
    print("\n🚧 Missing Skills (from gap analysis):")
    print(", ".join(missing_skills) if missing_skills else "No missing skills detected.")

    return {**state, "recommendations": recommendations}


# -------------------------
# Step 6: Tailor Resume
# -------------------------
def tailor_resume(state: JobApplicationState):
    tailor = ResumeTailorAgent()
    tailored_profile = tailor.tailor_profile(state["profile"])
    return {**state, "tailored_profile": tailored_profile}


# -------------------------
# Graph Definition
# -------------------------
def build_job_workflow():
    graph = StateGraph(JobApplicationState)

    graph.add_node("load_profile", load_profile)
    graph.add_node("build_resume", build_resume)
    graph.add_node("scrape_jobs", scrape_jobs)
    graph.add_node("match_jobs", match_jobs)
    graph.add_node("analyze_skills", analyze_skills)
    graph.add_node("tailor_resume", tailor_resume)

    # 🧭 Define the new logical flow
    graph.add_edge("load_profile", "build_resume")
    graph.add_edge("build_resume", "scrape_jobs")
    graph.add_edge("scrape_jobs", "match_jobs")
    graph.add_edge("match_jobs", "analyze_skills")
    graph.add_edge("analyze_skills", "tailor_resume")
    graph.add_edge("tailor_resume", END)

    graph.set_entry_point("load_profile")
    return graph.compile()


# -------------------------
# Run the graph manually
# -------------------------
if __name__ == "__main__":
    app = build_job_workflow()
    config = {"configurable": {"thread_id": "default_workflow"}}

    result = app.invoke({"user_id": "anaghaasdas"}, config=config)

    print("\n✅ Workflow complete!")

    