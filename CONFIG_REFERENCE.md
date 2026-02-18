# 📋 Configuration & Data Structure Reference

## Secrets Configuration

### Using Streamlit's Built-in Secrets Management

The easiest way to add secrets:

1. **Open the app in Streamlit**
2. **Click the ⚙️ settings icon** (top-right corner)
3. **Click "Secrets"**
4. **Add these two secrets**:

```toml
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GITHUB_REPO = "your-username/your-tracker-repo"
```

**That's it!** The app automatically reads from this secrets UI.

### How to Generate GITHUB_TOKEN

1. **Navigate to GitHub Settings**
   - Go to https://github.com/settings/tokens

2. **Create New Token**
   - Click "Generate new token (classic)"
   - Token name: `ssc-weekly-planner`

3. **Select Permissions**
   - Check only: ✅ `repo` (read-only access)
   - Recommended expiry: 90 days

4. **Copy & Save**
   - Copy the token immediately (you won't see it again!)
   - Paste into Streamlit Secrets UI

### (Optional) Manual .streamlit/secrets.toml

If you prefer file-based configuration, create `.streamlit/secrets.toml`:

```toml
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GITHUB_REPO = "your-username/your-tracker-repo"
```

**Note**: This file is in `.gitignore` so it won't be committed to version control.

### Token Security

⚠️ **IMPORTANT**:
- Never share your token
- Never commit to version control
- Regenerate if compromised
- Use minimal scopes (read-only)

---

## Data Structures

### GK Data Format (`gk_data.json`)

```json
{
  "revisions": {
    "TopicName": [
      {
        "due_date": "2026-02-18T10:00:00",      // ISO format datetime
        "success_rate": 0.85,                    // 0.0 to 1.0 (0% to 100%)
        "attempts": 5,                           // Optional: total attempts
        "correct": 4,                            // Optional: correct answers
        "last_attempted": "2026-02-15T14:30:00" // Optional: when last practiced
      }
    ]
  },
  "last_updated": "2026-02-18T09:00:00"
}
```

#### Field Details

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `due_date` | String (ISO8601) | Required | When revision is due |
| `success_rate` | Float | 0.0 - 1.0 | Accuracy percentage (0.85 = 85%) |
| `attempts` | Integer | 0+ | Optional: total practice attempts |
| `correct` | Integer | 0+ | Optional: correct answers in attempts |
| `last_attempted` | String | Optional | ISO format of last practice date |

#### Priority Rules Applied

```
Overdue (due_date < today)
    ↓
Due Today (due_date == today)
    ↓
Weak Areas (success_rate < 0.70)
    ↓
Upcoming (due_date > today)
```

#### Example GK Data

```json
{
  "revisions": {
    "Polity": [
      {
        "due_date": "2026-02-18T10:00:00",
        "success_rate": 0.92,
        "attempts": 3,
        "correct": 3
      },
      {
        "due_date": "2026-02-17T10:00:00",
        "success_rate": 0.65,
        "attempts": 5,
        "correct": 3
      }
    ],
    "History": [
      {
        "due_date": "2026-02-25T10:00:00",
        "success_rate": 0.55,
        "attempts": 2,
        "correct": 1
      }
    ]
  },
  "last_updated": "2026-02-18T09:00:00"
}
```

---

### Maths & Reasoning Data Format (`maths_data.json`)

```json
{
  "exam_date": "2026-05-30T00:00:00",
  
  "chapters": {
    "ChapterName": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.75,                          // 0.0 to 1.0
      "total_problems": 150,                     // Optional
      "correct": 112,                            // Optional
      "last_practiced": "2026-02-15T14:30:00"   // Optional
    }
  },
  
  "reasoning": {
    "ReasoningTopic": {
      "next_practice_date": "2026-02-20T00:00:00",
      "accuracy": 0.80,
      "total_problems": 100,
      "correct": 80,
      "last_practiced": "2026-02-14T10:00:00"
    }
  },
  
  "last_updated": "2026-02-18T09:00:00"
}
```

#### Field Details

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `exam_date` | String (ISO8601) | Required | Target exam date |
| `next_practice_date` | String (ISO8601) | Required | When to practice next |
| `accuracy` | Float | 0.0 - 1.0 | Performance metric |
| `total_problems` | Integer | 0+ | Optional: total practice problems |
| `correct` | Integer | 0+ | Optional: problems solved correctly |

#### Priority Rules Applied

```
High Priority (accuracy < 0.70 AND next_practice_date <= today)
    ↓
Medium Priority (next_practice_date == today)
    ↓
Scheduled (next_practice_date > today) - shown only if in schedule
```

#### Exam Proximity Calculation

- **Exam <60 days away**: Triggers "Exam Proximity Mode"
  - Increases weak-area suggestions
  - Suggests mixed practice sets
  - Reduces new-topic suggestions

```python
days_to_exam = (exam_date - today).days
exam_proximity = (0 <= days_to_exam <= 60)
```

#### Example Maths Data

```json
{
  "exam_date": "2026-05-30T00:00:00",
  
  "chapters": {
    "Percentages": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.65,
      "total_problems": 150,
      "correct": 98
    },
    "Time & Work": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.55,
      "total_problems": 95,
      "correct": 52
    },
    "Ratio": {
      "next_practice_date": "2026-02-25T00:00:00",
      "accuracy": 0.91,
      "total_problems": 110,
      "correct": 101
    }
  },
  
  "reasoning": {
    "Analogy": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.75,
      "total_problems": 80,
      "correct": 60
    },
    "Series": {
      "next_practice_date": "2026-02-25T00:00:00",
      "accuracy": 0.85,
      "total_problems": 90,
      "correct": 77
    }
  },
  
  "last_updated": "2026-02-18T09:00:00"
}
```

---

## Daily Load Classification

### Load Types

```
🟢 LIGHT    = GK revision batches
🟡 MEDIUM   = Reasoning practice sessions
🔴 HEAVY    = Maths practice & problem solving
```

### Daily Load Limits

| Task Type | Max per Day | Load |
|-----------|------------|------|
| Maths practice | 1 | Heavy |
| Reasoning sessions | 2 | Medium |
| GK revisions | ∞ | Light |

### Daily Load Priority Order

1. **High Priority Maths** (accuracy <70% and due today)
   - Max: 1 per day
   - Category: Heavy
   
2. **High Priority Reasoning** (due today)
   - Max: 2 per day
   - Category: Medium

3. **GK Revisions** (overdue + due today)
   - Fills remaining slots
   - Category: Light

### Example Load Allocation

**Scenario: Today's tasks**
- 2 GK revisions due
- 1 Maths (weak area, accuracy 65%)
- 2 Reasoning topics due

**Result**:
1. ✅ Add Maths chapter (Heavy)
2. ✅ Add Reasoning #1 (Medium)
3. ✅ Add Reasoning #2 (Medium)
4. ✅ Add GK revisions (Light)

**Daily Load**: 1 Heavy + 2 Medium + 1 Light = **MIXED**

---

## Anti-Zero-Day Rule

**Activation**: When no tasks are due (due_date > today for all items)

**Behavior**:
```python
if total_due_tasks == 0:
    if weak_maths_chapters:
        suggest("Practice weak area: " + weakest_chapter)
    else:
        suggest("Take a mixed GK quiz to maintain momentum")
```

### Examples

**Scenario 1**: No tasks due, but weak Maths chapter
- ✅ Suggestion: "Practice weak area: Percentages (65% accuracy)"

**Scenario 2**: No tasks due, all chapters strong
- ✅ Suggestion: "Take a mixed GK quiz to maintain momentum"

---

## Time Zone Handling

All dates are in **ISO 8601 format** with timezone information.

```
✅ Valid: "2026-02-18T10:30:00+00:00"  (UTC with offset)
✅ Valid: "2026-02-18T10:30:00"         (Local timezone)
❌ Invalid: "2026-02-18 10:30:00"      (Space instead of T)
```

### Datetime Parsing

```python
# Will parse both formats:
due_date = datetime.fromisoformat("2026-02-18T10:30:00")

# Use UTC for consistency:
today = datetime.now()
```

---

## Performance Optimization

### Caching Strategy

```python
@st.cache_data(ttl=300)  # 5-minute cache
def fetch_github_file(file_name: str) -> dict:
    # Fetches only once per 5 minutes
    pass
```

### Cache Invalidation

- Cache automatically expires after 5 minutes
- Manual refresh: Click "Refresh" in Streamlit UI
- Data updated on each app reload

### API Rate Limits

GitHub API limits: **60 requests/hour (unauthenticated)** or **5000/hour (authenticated)**

With caching:
- App makes 2 API calls every 5 minutes
- ~24 API calls/hour (well under the 5000 limit)

---

## Data Validation

### Minimum Required Fields

**gk_data.json**:
```json
{
  "revisions": {
    "any_topic": [
      {
        "due_date": "2026-02-18T10:00:00",
        "success_rate": 0.5
      }
    ]
  }
}
```

**maths_data.json**:
```json
{
  "chapters": {
    "any_chapter": {
      "next_practice_date": "2026-02-18T00:00:00",
      "accuracy": 0.5
    }
  }
}
```

### Handling Missing Fields

| Missing Field | Default Behavior |
|---------------|------------------|
| `success_rate` | 1.0 (100% - excellent) |
| `accuracy` | 1.0 (100% - excellent) |
| `next_practice_date` | Today (schedule immediately) |
| `reasoning` section | Skipped (optional) |

---

## Updating Data

### When to Update

The dashboard reads data **every 5 minutes**. To see updates immediately:

1. **Update your tracker data** in the GitHub repository
2. **Commit & push** to the specified branch
3. **Click Refresh** in Streamlit UI (or wait 5 minutes)

### Data Flow

```
Your Tracker (local)
      ↓ (commit & push)
GitHub Repository
      ↓ (API fetch + cache)
Streamlit App
      ↓ (display)
Your Dashboard
```

---

## Troubleshooting Data Issues

### "Cannot parse dates"
✅ Ensure ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

### "Accuracy/success_rate out of range"
✅ Convert to 0.0 - 1.0 range (not 0-100)

### "Missing chapters"
✅ Check both `chapters` and `reasoning` sections exist

### "Zero-day rule not triggering"
✅ Ensure all `due_date` values are in the future

---

## Building Your Data

### GK Data Template

```bash
# Generate from your GK tracker
python -c "
import json
gk = {
    'revisions': {
        'Current Affairs': [],
        'Polity': [],
        'History': []
    }
}
print(json.dumps(gk, indent=2))
"
```

### Maths Data Template

```bash
python -c "
import json
from datetime import datetime, timedelta

maths = {
    'exam_date': (datetime.now() + timedelta(days=120)).isoformat(),
    'chapters': {},
    'reasoning': {}
}
print(json.dumps(maths, indent=2))
"
```

---

## Advanced: Customizing Priority Logic

Edit the following functions in `ssc_weekly_planner.py`:

```python
def get_gk_priorities(gk_data, today):
    # Modify to change GK priority order
    pass

def get_maths_priorities(maths_data, today):
    # Modify to change accuracy threshold (currently 0.70)
    pass

def generate_daily_plan(today, gk, maths, reasoning):
    # Modify to change load control rules
    pass
```

---

## Support

For help with data formats, check:
- `example_gk_data.json`
- `example_maths_data.json`
- `SETUP.md` for configuration help
