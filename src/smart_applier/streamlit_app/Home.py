import sys
from pathlib import Path
import streamlit as st

# -------------------------
# Add project src to path
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src" / "smart_applier"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from smart_applier.utils.path_utils import get_data_dirs

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Smart Applier AI", layout="wide")

# -------------------------
# Load directories (for verification)
# -------------------------
dirs = get_data_dirs()
profile_dir = dirs["profiles"]
jobs_dir = dirs["jobs"]
resumes_dir = dirs["resumes"]

# -------------------------
# UI Layout
# -------------------------
st.title("🚀 Smart Applier AI")
st.markdown("""
Welcome to **Smart Applier AI** — your all-in-one intelligent career assistant!  

This app helps you create, optimize, and tailor your professional portfolio for better job matches.  

---

### 🧠 Available Modules

1. **👤 Profile Creator** – Build your professional profile with education, projects, and skills.  
2. **🔍 Job Matcher** – Scrape the latest jobs and match them to your profile.  
3. **🧩 Skill Gap Analyzer** – Identify missing skills and get personalized learning resources.  
4. **📄 Resume Builder** – Generate an ATS-optimized resume PDF directly from your profile.  
5. **🎯 Resume Tailor** – Customize your resume for specific job descriptions.  

---

### 📁 Data Directories (Auto-Managed)
| Type | Path |
|------|------|
| **Profiles** | `{profile_dir}` |
| **Jobs** | `{jobs_dir}` |
| **Resumes** | `{resumes_dir}` |

---

👈 Use the **sidebar** to navigate through different tools.
""")

# -------------------------
# Footer
# -------------------------
st.divider()
st.caption("Developed with ❤️ by Aparna S | Smart Applier AI © 2025")
