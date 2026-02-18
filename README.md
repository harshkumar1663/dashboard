# SSC Weekly Planner 📚

A read-only smart study planner dashboard that fetches data from your existing SSC trackers and generates intelligent study priorities.

## Quick Start

1. **Install**:
```bash
pip install -r requirements.txt
```

2. **Run**:
```bash
streamlit run ssc_weekly_planner.py
```

3. **Configure** (first time):
   - Click **⚙️** icon (top-right)
   - Click **"Secrets"**
   - Add two secrets:
   ```
   GITHUB_TOKEN = "ghp_your_token"
   GITHUB_REPO = "owner/repo"
   ```
   - **Refresh the page**

4. **Done!** Dashboard loads instantly after this.

## How It Works

### Data Sources
- Fetches `gk_data.json` from your GitHub repository (base64 encoded)
- Fetches `maths_data.json` from your GitHub repository (base64 encoded)
- Data is cached for 5 minutes for performance

### Priority Logic

#### 🎯 GK Priority Levels
1. **Overdue**: Past due date revisions
2. **Due Today**: Revisions scheduled for today
3. **Weak Areas**: Low success rate sections
4. **Upcoming**: Scheduled future topics

#### 📊 Maths/Reasoning Priority
- **HIGH**: Chapters due today with <70% accuracy
- **MEDIUM**: Other due chapters
- Respects maintenance schedule (only suggests if scheduled)

#### ⚡ Daily Load Control
- **Light Task** = GK revision batch
- **Medium Task** = Reasoning session  
- **Heavy Task** = Maths practice session

**Daily Rules**:
- Max 1 Heavy task/day
- Max 2 Medium tasks/day
- GK revisions fill remaining slots

#### 🚫 Anti-Zero-Day Rule
If no tasks are due, system suggests:
- Practice weak maths chapters, OR
- Take a mixed GK quiz

#### 📅 Exam Proximity Mode (<60 days)
- Increase weak-area suggestions
- Suggest mixed practice sets
- Reduce new-topic suggestions

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure GitHub Secrets
Open the app and:
1. Click the **⚙️ settings icon** (top-right)
2. Click **"Secrets"**
3. Add two secrets:
```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO = "your-username/your-repo"
```

**To generate a GitHub token**:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select `repo` scope (read-only access)
4. Copy the token and paste in Streamlit Secrets

### 3. Prepare Data Files
Ensure your GitHub repo has:
- `gk_data.json` (base64 encoded via GitHub API)
- `maths_data.json` (base64 encoded via GitHub API)

### 4. Run the App
```bash
streamlit run ssc_weekly_planner.py
```

## Data Format

### gk_data.json Structure
```json
{
  "revisions": {
    "Polity": [
      {
        "due_date": "2026-02-18T10:00:00",
        "success_rate": 0.85
      }
    ]
  }
}
```

### maths_data.json Structure
```json
{
  "exam_date": "2026-06-01T00:00:00",
  "chapters": {
    "Percentages": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.65
    }
  },
  "reasoning": {
    "Syllogism": {
      "next_practice_date": "2026-02-20T00:00:00",
      "accuracy": 0.80
    }
  }
}
```

## UI Components

### Section 1 - Today's Plan 📅
- **GK Revisions Count**: Total revisions due (overdue + today)
- **Maths Chapter**: Primary high-priority chapter to practice
- **Reasoning**: Primary reasoning session to focus on
- **Key Focus**: Smart suggestion (zero-day, load guidance, etc.)

### Section 2 - 7-Day Plan 📊
Simple table showing:
- Date
- GK revision count
- Maths sessions due
- Reasoning sessions due
- Daily load indicator (Light/Medium/Heavy)

### Section 3 - Guidance 💡
Contextual recommendations:
- Weak area alerts with accuracy percentages
- Exam proximity warnings
- Load management advice
- Backlog clearing suggestions

## Important Notes

⚠️ **This is a READ-ONLY dashboard**
- ❌ No editing capabilities
- ❌ No data modification
- ❌ No saving features
- ✅ Only fetches and displays data

## Performance

- **Data caching**: 5-minute cache to avoid API rate limits
- **Fast load**: Deterministic rules, no heavy computations
- **Clean UI**: Minimal animations, focus on clarity

## Troubleshooting

### "GitHub token not configured"
→ Check `.streamlit/secrets.toml` exists and has valid token

### "Error fetching gk_data.json"
→ Ensure file exists in repository and is committed
→ Check GitHub token has `repo` scope
→ Verify GITHUB_REPO and GITHUB_BRANCH settings

### Data not updating
→ Cached data refreshes every 5 minutes
→ Click "Refresh" in Streamlit UI for immediate update
→ Check GitHub repo has latest data files

## License

Read-only dashboard for SSC exam preparation tracking.
