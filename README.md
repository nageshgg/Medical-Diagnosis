# 🏥 Medical Multi-Agent Diagnostic System

5 specialized AI agents powered by **Groq (free)** + LangGraph + PubMed + OpenFDA.

## 🚀 Setup (3 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get free Groq API key
1. Go to **console.groq.com**
2. Sign up (free, no credit card)
3. Click API Keys → Create API Key

### 3. Add API key & run
```bash
cp .env.example .env
# Edit .env → add your GROQ_API_KEY

streamlit run ui/app.py
```

Open http://localhost:8501

---

## 🤖 Agent Pipeline

```
Patient Input
     ↓
🩺 Intake Agent      → Structures symptoms into JSON
     ↓
🔬 Research Agent    → Searches PubMed, generates diagnoses
     ↓
💊 Drug Agent        → Checks OpenFDA interactions
     ↓
🔍 Critic Agent      → Peer reviews everything
     ↓
📝 Report Agent      → Final report + PDF export
```

## 🛠️ Tech Stack

| Tool | Purpose | Cost |
|------|---------|------|
| Groq API (Llama 3.3 70B) | Powers all 5 agents | FREE |
| PubMed API | Real medical literature | FREE |
| OpenFDA API | Real drug interaction data | FREE |
| LangGraph | Agent orchestration | FREE |
| Streamlit | Web UI | FREE |

## 📁 Structure

```
medical-multi-agent/
├── agents/
│   ├── intake_agent.py
│   ├── research_agent.py
│   ├── drug_agent.py
│   ├── critic_agent.py
│   └── report_agent.py
├── tools/
│   ├── pubmed_search.py
│   └── fda_checker.py
├── graph/
│   └── workflow.py
├── ui/
│   └── app.py
├── utils/
│   └── pdf_export.py
├── .env.example
├── requirements.txt
└── README.md
```

## 🌐 Deploy Free on Streamlit Cloud

1. Push to GitHub
2. Go to share.streamlit.io
3. Set main file: `ui/app.py`
4. Add secret: `GROQ_API_KEY = your_key`
5. Deploy!

## ⚠️ Disclaimer

Educational/demo purposes only. NOT for clinical use.
Always consult a qualified healthcare professional.# MEDICAL-DIAGNOSIS-SYSTEM

