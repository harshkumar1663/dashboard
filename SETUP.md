# 🚀 Quick Start Guide - SSC Weekly Planner

## 1️⃣ Prerequisites
- Python 3.8+
- GitHub account with read access to your tracker repository
- Personal GitHub token (for API access)

## 2️⃣ Installation Steps

### Step 1: Clone or Navigate to Project
```bash
cd /media/harsh/Projects/Dashboard
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup GitHub Token

#### Generate Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: `ssc-weekly-planner`
4. Select scope: ✅ `repo` (for read-only access)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

#### Configure Secrets:
Create `.streamlit/secrets.toml` in this directory:
```toml
GITHUB_TOKEN = "ghp_YourActualTokenHere"
GITHUB_REPO = "your-username/your-tracker-repo"
GITHUB_BRANCH = "main"
```

**Example**:
```toml
GITHUB_TOKEN = "ghp_ABC123DEF456GHI789JKL012MNO345PQR"
GITHUB_REPO = "harsh-singhania/SSC-Tracker"
GITHUB_BRANCH = "main"
```

## 3️⃣ Prepare Your Data Files

Your GitHub repository must have these files at the root:

### `gk_data.json`
```json
{
  "revisions": {
    "Topic Name": [
      {
        "due_date": "2026-02-18T10:00:00",
        "success_rate": 0.85
      }
    ]
  },
  "last_updated": "2026-02-18T09:00:00"
}
```

### `maths_data.json`
```json
{
  "exam_date": "2026-05-30T00:00:00",
  "chapters": {
    "Chapter Name": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.75
    }
  },
  "reasoning": {
    "Topic Name": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.80
    }
  },
  "last_updated": "2026-02-18T09:00:00"
}
```

## 4️⃣ Run the App

```bash
streamlit run ssc_weekly_planner.py
```

The app will open in your browser at `http://localhost:8501`

## 5️⃣ Understanding the UI

### 📅 Today's Study Plan
Shows:
- **GK Revisions**: Count of revisions due today (including overdue)
- **Maths Chapter**: Primary high-priority chapter to practice today
- **Reasoning**: Primary reasoning topic to focus on
- **Key Focus**: System suggestion (zero-day prevention, load guidance, etc.)

### 📊 Next 7 Days Plan
Table with:
- **Date**: Day of the week
- **GK**: Number of GK revisions due
- **Maths**: Number of maths chapters due
- **Reasoning**: Number of reasoning topics due
- **Load**: Daily load indicator 🟢 Light / 🟡 Medium / 🔴 Heavy

### 💡 Study Guidance
Smart recommendations:
- Weak areas that need focus
- Load management advice
- Exam proximity warnings
- Backlog clearing suggestions

## 🔑 Key Features

✅ **Smart Prioritization**
- Overdue revisions appear first
- Low-accuracy chapters get flagged
- Weak areas highlighted

✅ **Daily Load Control**
- Light: GK revisions
- Medium: Reasoning sessions
- Heavy: Maths practice

✅ **Exam Proximity Mode**
- Auto-activates when exam <60 days away
- Increases weak-area suggestions
- Suggests mixed practice sets

✅ **Zero-Day Prevention**
- Always has a suggestion if no tasks are due
- Prevents procrastination with maintenance tasks

✅ **Performance Optimized**
- 5-minute data cache (reduces API calls)
- Fast load times
- Deterministic rules (no heavy computation)

## ⚙️ Customization

### Change Cache Duration
Edit `ssc_weekly_planner.py` line with `@st.cache_data(ttl=300)`:
```python
@st.cache_data(ttl=600)  # 10 minutes instead of 5
```

### Change Weak Area Threshold
Edit the accuracy threshold (currently 70%):
```python
if accuracy < 0.70:  # Change to 0.75 for 75%, etc.
```

### Add More Data Fields
Edit the data parsing functions:
```python
def get_gk_priorities(gk_data: dict, today: datetime) -> Dict:
    # Add custom logic here
```

## 🐛 Troubleshooting

### "GitHub token not configured"
✅ **Fix**: Create `.streamlit/secrets.toml` with valid token

### "Error fetching gk_data.json"
✅ **Checks**:
- File exists in GitHub repo
- Token has `repo` scope
- GITHUB_REPO is correct format: `owner/repo`
- File is committed (not just in local repo)

### "Module not found"
✅ **Fix**: `pip install -r requirements.txt`

### Data not updating
✅ **Solution**: Click "Refresh" in Streamlit UI (top-right icon)

### Slow load times
✅ **Solution**: Cache will speed up subsequent loads

## 📚 Example Workflow

1. **Setup** (first time)
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Create .streamlit/secrets.toml with GitHub token
   ```

2. **Run** (every time)
   ```bash
   streamlit run ssc_weekly_planner.py
   ```

3. **Use**
   - Check today's priorities
   - Plan your week using 7-day view
   - Follow guidance recommendations

4. **Update Data**
   - Update your tracker in GitHub
   - Refresh the Streamlit app
   - New priorities appear instantly

## 📞 Support

For data format issues, check:
- `example_gk_data.json` - GK data structure
- `example_maths_data.json` - Maths/reasoning data structure

## License

Read-only dashboard for SSC exam preparation.
