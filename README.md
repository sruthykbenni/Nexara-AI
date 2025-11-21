# 🚀 **Nexara AI: Intelligent Resume Tailoring and Job-Matching System**

Nexara AI is an intelligent, AI-driven career assistance system designed to streamline the job preparation journey for students, fresh graduates, and early-career professionals.
Using NLP, semantic similarity, multi-agent orchestration, and automated resume tailoring, the system empowers users to identify suitable jobs, bridge skill gaps, and create job-aligned resumes effortlessly.

---

## 🧠 **Project Overview**

In the modern job market, applicants often struggle with:

* Identifying missing skills
* Selecting relevant job roles
* Tailoring resumes for each application

Traditional platforms typically generate static resumes or provide generic job lists.
**Nexara AI solves these challenges** by leveraging AI agents that analyze profiles, scrape and match jobs semantically, extract skill gaps, and tailor resumes dynamically.

The system is built as a **Streamlit-based web application** orchestrated via **LangGraph**, enabling modularity, reusability, and intelligent state management.

---

## 🎯 **Key Features**

### ✅ **1. AI-Powered Resume Builder**

* Generates professional resumes from user-provided details
* Uses structured templates and AI refinement
* Produces downloadable, clean PDF-style output

### ✅ **2. Skill Gap Analysis (NLP-based)**

* Extracts skills from job descriptions
* Compares with user profile
* Identifies missing/weak skills
* Suggests courses and learning resources

### ✅ **3. Semantic Job Matching**

* Scrapes job listings or accepts uploaded job descriptions
* Converts text into embeddings using **Sentence Transformers (SBERT)**
* Compares jobs and user profiles using **FAISS** similarity search
* Ranks opportunities by relevance

### ✅ **4. Automated Resume Tailoring**

* Dynamically adapts resume content for:

  * The user-selected job, or
  * The system’s top-matched job
* Highlights relevant experience and keywords for ATS optimization

### ✅ **5. Agent-Orchestrated Pipeline using LangGraph**

* Each feature runs as an independent “agent”
* LangGraph manages workflow transitions and shared state
* Ensures modularity, error handling, and reusability

---

## 🛠️ **Tech Stack**

### **Frontend**

* Streamlit

### **Backend / AI**

* Python 3.10
* LangGraph for multi-agent orchestration
* Sentence Transformers (SBERT)
* Hugging Face Transformers
* FAISS for semantic similarity search
* Google Generative AI API (for resume improvement & text generation)

### **Database**

* SQLite (lightweight & portable)

### **Other Libraries**

* Pandas, NumPy
* Matplotlib / Seaborn
* Requests, BeautifulSoup (for job scraping)

---

## 🧩 **System Architecture**

```
┌────────────────────────────┐
│       Streamlit UI         │
└─────────────┬──────────────┘
              │
┌─────────────▼──────────────┐
│   LangGraph Orchestration  │
│ (Profile → Resume → Jobs → │
│  Matching → Skill Gap →    │
│        Tailoring)          │
└─────────────┬──────────────┘
              │
┌─────────────▼──────────────┐
│      AI Processing Layer   │
│  - SBERT Embeddings        │
│  - FAISS Search            │
│  - NLP Pipelines           │
└─────────────┬──────────────┘
              │
┌─────────────▼──────────────┐
│       SQLite Database       │
└────────────────────────────┘
```

---

## 🧪 **How It Works (Workflow)**

### **1️⃣ User Input Phase**

* User enters profile details (education, skills, experience)
* System stores data in SQLite

### **2️⃣ Resume Generation**

* Base resume is created automatically
* Option for polishing via Generative AI

### **3️⃣ Job Scraping / Upload**

* User can paste job descriptions or scrape job data

### **4️⃣ Semantic Job Matching**

* Both the profile and jobs are embedded using SBERT
* FAISS computes similarity scores
* Jobs are ranked

### **5️⃣ Skill Gap Extraction**

* NLP extracts required skills from job descriptions
* Compares with user’s skills
* Suggests learning resources

### **6️⃣ Resume Tailoring**

* Resume is rewritten for a chosen job or top match
* Includes targeted keywords for ATS systems

---

## 📸 **Screenshots**

> *(Replace with your own images in the `/assets/screenshots/` folder)*

* Home Dashboard
* Resume Builder Interface
* Job Matching Dashboard
* Skill Gap Analysis Charts

---

## 📂 **Project Structure**

```
Nexara-AI/
│
├── agents/
│   ├── profile_agent.py
│   ├── resume_builder_agent.py
│   ├── job_scrap_agent.py
│   ├── job_match_agent.py
│   ├── skill_gap_agent.py
│   └── resume_tailor_agent.py
│
├── data/
│   ├── database.sqlite
│   └── sample_jobs.json
│
├── main.py
├── langgraph_workflow.py
├── requirements.txt
└── README.md
```

---

## ▶️ **How to Run Locally**

### **1. Clone the repository**

```bash
git clone https://github.com/<your-username>/Nexara-AI.git
cd Nexara-AI
```

### **2. Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run the application**

```bash
streamlit run main.py
```

---

## 📈 **Future Enhancements**

* Integration with LinkedIn, Indeed, and Naukri APIs
* AI-driven interview preparation module
* Automated cover letter generator
* Multi-language support
* Cloud deployment (GCP / AWS)
* Integrated analytics dashboard for institutions

---

## 📜 **License**

This project is developed as part of the Mini Project – Semester 3
Kerala University of Digital Sciences, Innovation and Technology (DUK).

---

