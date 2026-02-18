# 📱 SSC Weekly Planner - User Guide

## What is the SSC Weekly Planner?

A **read-only smart study dashboard** that:
- 📊 Fetches your GK and Maths study data from GitHub
- 🧠 Analyzes your progress intelligently
- 📅 Generates today's priorities and weekly plan
- 💡 Provides smart study guidance
- ⚖️ Controls daily workload to prevent burnout

## Quick Start (3 Steps)

### 1. Install & Run
```bash
pip install -r requirements.txt
streamlit run ssc_weekly_planner.py
```

### 2. Configure Secrets (First Time)
When the app loads:
1. Click the **⚙️ icon** (top-right corner)
2. Click **"Secrets"**
3. Add:
```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO = "your-username/your-repo"
```

### 3. Refresh & Use
- Refresh the browser
- Dashboard loads your study data
- Use it to plan your week!

## Understanding the Dashboard

### 📅 Section 1: Today's Study Plan

Shows exactly what you should study today:

| Card | Meaning |
|------|---------|
| **GK Revisions** | Number of GK topics to revise (includes overdue) |
| **Maths Chapter** | Which maths chapter to practice (if any high-priority) |
| **Reasoning** | Which reasoning topic to focus on |
| **Key Focus** | Smart suggestion to reduce decision fatigue |

#### How Priorities are Calculated

**GK Revisions**:
1. Overdue revisions come first
2. Then revisions due today
3. Weak sections (low success rate) get flagged
4. Upcoming topics appear below

**Maths & Reasoning**:
- If due today AND accuracy <70% → ✅ HIGH priority (do today!)
- Other due chapters → MEDIUM priority
- Future chapters → Not suggested (focus on what's due)

### 📊 Section 2: Next 7 Days Plan

Simple table showing your **entire week**:

| Column | Meaning |
|--------|---------|
| **Date** | Which day |
| **GK** | Number of GK revisions due |
| **Maths** | Maths chapters due |
| **Reasoning** | Reasoning sessions due |
| **Load** | 🟢 Light / 🟡 Medium / 🔴 Heavy |

#### Understanding Load Indicators

```
🟢 LIGHT    = Mostly GK revisions (easy, quick)
🟡 MEDIUM   = Mix of GK + Reasoning + maybe Maths
🔴 HEAVY    = Multiple maths chapters (requires focus)
```

**Daily Load Rules**:
```
Max 1 Heavy task/day    (Maths problem-solving)
Max 2 Medium tasks/day  (Reasoning sessions)
GK revisions fill rest  (As many as you want!)
```

## Core Features

### 🎯 Smart Priority System

The system uses **4-level priority classification**:

```
LEVEL 1: OVERDUE
├─ Revisions past due date
└─ Status: 🔴 CRITICAL - Do TODAY

LEVEL 2: DUE TODAY
├─ Scheduled for today
└─ Status: 🟠 URGENT - Do TODAY

LEVEL 3: WEAK AREAS
├─ Success rate <70%
└─ Status: 🟡 IMPORTANT - Do SOON

LEVEL 4: WEAK + WEAK ACCURACY
├─ Due AND accuracy <70%
└─ Status: 🔴 CRITICAL - HIGHEST PRIORITY
```

### 💪 Load Balancing

Prevents you from:
- ❌ Taking too many heavy tasks
- ❌ Overloading with reasoning
- ✅ Having manageable daily workload
- ✅ Making steady progress

**Example Day**:
- 1 Maths chapter (Heavy) ✓
- 2 Reasoning topics (Medium) ✓
- 5 GK revisions (Light) ✓
- = Balanced, sustainable day

### 📈 Exam Proximity Mode

**When**: Exam is <60 days away

**Auto-activates**: 
- Shows more weak-area suggestions
- Recommends mixed practice sets
- Reduces new-topic suggestions
- Focuses on what needs improvement

### 🚫 Zero-Day Prevention

**Problem**: What if nothing is due?

**Solution**: System always suggests:
1. Practice your weakest maths chapter (if any)
2. OR take a mixed GK quiz

**Result**: Never have to wonder what to study!

## Working with Data

### Where Your Data Comes From

```
Your Study Trackers
    ↓
GitHub (gk_data.json, maths_data.json)
    ↓
SSC Weekly Planner
    ↓
Smart Recommendations
```

**Data Refresh**: Every 5 minutes automatically

### Data Requirements

Your trackers must have:

**GK Data**:
- Topic names
- Due dates
- Success/accuracy rate

**Maths Data**:
- Chapter names
- Next practice date
- Accuracy percentage
- Exam date (optional but recommended)

## Tips for Best Results

### 1. Keep Data Updated
- Update your tracker regularly
- Push changes to GitHub
- Dashboard will fetch automatically

### 2. Track Accuracy
- Mark correct/incorrect problems
- Keep success rate accurate
- System learns from this data

### 3. Set Realistic Due Dates
- Don't schedule everything for today
- Spread tasks throughout week
- System will balance automatically

### 4. Review Weekly
- Check the 7-day plan every Sunday
- Plan your week ahead
- Adjust if needed (in your tracker)

### 5. Trust the Load Indicators
- 🟢 Light day? Great for backlog!
- 🔴 Heavy day? Focus on quality over quantity
- 🟡 Medium? Balanced pace

## Common Scenarios

### Scenario 1: Weak in Percentages

**Dashboard Shows**:
- ⚠️ "Maths accuracy dropping in Percentages (65%)"
- ✅ "Percentages" appears in today's Maths card if due

**What to Do**:
1. Practice Percentages today
2. Dashboard will track accuracy
3. Once you improve to >70%, it moves to lower priority

### Scenario 2: Too Many GK Revisions Due

**Dashboard Shows**:
- GK Revisions: 15
- Load: 🟡 Medium

**What to Do**:
1. System broke them into batches (won't exceed 2 hours)
2. Do 2-3 batches today, rest tomorrow
3. Dashboard guided the spacing for you

### Scenario 3: Exam is 45 Days Away

**Dashboard Shows**:
- 🎯 "Exam Mode: Prioritize weak areas"
- More weak-area suggestions
- Mixed practice set recommendations

**What to Do**:
1. Focus heavily on weak subjects
2. Less time on strong subjects
3. Prepare for final push

### Scenario 4: Nothing is Due Tomorrow

**Dashboard Shows**:
- Next Day GK: 0, Maths: 0, Reasoning: 0
- ⚡ "Light day — good for backlog clearing"

**What to Do**:
1. Clear any pending work
2. Do a mock test
3. Review previous weak areas

## Customization

### Change Weak Area Threshold

Default: 70% accuracy triggers "weak area"

To change to 75%:
1. Open `ssc_weekly_planner.py`
2. Find: `if accuracy < 0.70:`
3. Change to: `if accuracy < 0.75:`
4. Restart the app

### Change Cache Duration

Default: 5 minutes

To change to 10 minutes:
1. Find: `@st.cache_data(ttl=300)`
2. Change to: `@st.cache_data(ttl=600)`
3. Restart the app

### Add Custom Guidance

To add your own smart suggestions:
1. Edit `render_guidance_section()` function
2. Add custom logic based on data
3. Restart the app

## Troubleshooting

### Dashboard shows "Error fetching gk_data.json"

**Checklist**:
- ✓ File exists in GitHub repository
- ✓ File is committed (not just local)
- ✓ GitHub token is valid (starts with `ghp_`)
- ✓ Token has `repo` scope permission
- ✓ GITHUB_REPO is correct format: `owner/repo`

**Fix**: Run `python verify_setup.py` to diagnose

### Data not updating

**Solution**: 
1. Wait 5 minutes (cache duration)
2. OR click "Refresh" in Streamlit UI (top-right)
3. OR restart the app

### Dashboard loads slowly

**Tips**:
- First load takes longer (caches data)
- Subsequent loads are instant
- Check internet connection
- Verify GitHub token validity

## What This Dashboard DOES

✅ Fetch data from GitHub  
✅ Show today's priorities  
✅ Plan your full week  
✅ Provide smart guidance  
✅ Control daily load  
✅ Prevent zero-days  
✅ Cache for performance  
✅ Read-only (safe!)  

## What This Dashboard DOESN'T Do

❌ Modify your data  
❌ Allow editing  
❌ Store data locally (read-only fetch)  
❌ Create charts/analytics  
❌ Track time spent  
❌ Send notifications  
❌ Require subscriptions  

## Support & Help

### For Setup Issues
→ Click ⚙️ → Secrets to add GitHub credentials
→ Verify token has `repo` scope

### For Data Format Issues
→ Check `SETUP.md` and `CONFIG_REFERENCE.md`

### For Configuration Issues
→ Run `python verify_setup.py` for diagnostics

### For Customization
→ Edit `ssc_weekly_planner.py` directly

## Final Tips

🎯 **Trust the System**
- Let the dashboard decide priorities
- Reduces decision fatigue
- Focus on executing, not planning

📊 **Keep Data Accurate**
- Accurate data = accurate recommendations
- Mark problems correct/incorrect
- Update success rates after each session

⏰ **Follow the Load**
- 🟢 Light days are great for backlog
- 🟡 Medium days need focus
- 🔴 Heavy days require dedication

🎓 **Review Weekly**
- Check 7-day plan every Sunday
- Adjust if life circumstances change
- Celebrate progress!

---

**Version**: 1.0  
**Last Updated**: Feb 2026  
**Status**: Read-only Dashboard ✅
