# 🏗️ Construction Intelligence Hub

A Streamlit dashboard for construction **cost estimation**, **project analytics**,
**risk scoring**, and an **AI assistant** — powered by a locally-running **Ollama**
LLM, so no project data ever leaves your machine.

```
construction_intelligence_hub/
├── app.py                  # main entry point / page router
├── requirements.txt
├── assets/
│   └── style.css             # custom theme
├── modules/
│   ├── estimation.py          # cost estimation calculator
│   ├── compare.py              # side-by-side comparison of construction options
│   ├── analytics.py             # project dashboards (upload CSV or use sample data)
│   ├── labour.py                 # labour directory + daily attendance + wages
│   ├── risk.py                    # risk scoring + radar chart
│   └── ai_assistant.py             # chat + document analyzer (Ollama)
├── utils/
│   ├── ollama_client.py          # HTTP wrapper for the local Ollama API
│   ├── data_store.py              # CSV-backed persistence (labour + attendance)
│   └── helpers.py                  # formatting + sample data generator
└── data/                              # auto-created: labour_master.csv, attendance.csv
```

## 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed locally (free, runs on CPU or GPU)

## 2. Set up the Python environment

```bash
cd construction_intelligence_hub
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Set up Ollama

```bash
# in a separate terminal, start the Ollama server
ollama serve

# pull a model (llama3.1 is a good general default; 8B fits most laptops)
ollama pull llama3.1
```

Leave `ollama serve` running in the background whenever you want the AI
features (estimation summaries, risk notes, chat, document analysis) to work.
The rest of the app (estimation math, analytics dashboards) works fine even
if Ollama is off — you'll just see a "not connected" notice on AI-only
features.

## 4. Run the app

```bash
streamlit run app.py
```

It opens at `http://localhost:8501`.

## 5. What each module does

| Module | What it does | Uses Ollama? |
|---|---|---|
| **Cost Estimation** | Rule-based sq.ft cost calculator (quality tier, city tier, structure type, floors) with a cost breakdown chart | Optional — AI narrative summary |
| **Compare Options** | Configure 2-4 construction options side by side (different structure types, quality, location) and compare total cost | Optional — AI recommendation |
| **Project Analytics** | Upload a CSV of your projects (or use built-in sample data) to see budget vs. actual, schedule variance, status mix | No |
| **Labour & Attendance** | Add labourers to a directory, mark daily attendance (Present/Half Day/Absent/Paid Leave), auto-calculates wages payable, monthly wage summary | No |
| **Risk Analysis** | Slider-based scoring across 6 risk factors, radar chart, overall risk score | Optional — AI mitigation notes |
| **AI Assistant** | Free-form chat about construction topics, plus a document analyzer that summarizes uploaded specs/RFPs (.txt/.pdf) | Yes |

## 6. Extending it (suggested next steps)

- **Swap the estimation rule-table** in `modules/estimation.py` for real
  historical cost data (e.g. load a CSV of past project costs and fit a
  simple regression instead of fixed rates).
- **Persist analytics data**: replace the CSV upload with a SQLite/Postgres
  connection in `utils/` so project data survives between sessions.
- **Add a materials/BOQ module**: a new file `modules/materials.py` that
  takes a quantity takeoff and prices it against a materials-rate table.
- **Swap models**: any model you've pulled with `ollama pull <name>` shows
  up automatically in the model dropdown on the AI Assistant page.
- **Add authentication** if you deploy this for a team — Streamlit supports
  this via `st.secrets` + a simple login gate, or `streamlit-authenticator`.

## 7. Troubleshooting

- **"Ollama not running" everywhere** → run `ollama serve` in a terminal and
  keep it open; refresh the Streamlit page.
- **Model dropdown is empty** → you haven't pulled a model yet: `ollama pull llama3.1`.
- **Slow AI responses** → larger models (13B, 70B) need more RAM/VRAM; try a
  smaller model like `llama3.1:8b` or `phi3` for faster local inference.
