import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Page configuration
st.set_page_config(
    page_title="SSC Weekly Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "SSC Weekly Planner v1.0 - Smart Study Dashboard"
    }
)

# Styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .light-load {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #333;
    }
    .medium-load {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
    }
    .heavy-load {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
    }
    .today-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA FETCHING
# ============================================================================

def get_default_branch(token: str, repo: str) -> str:
    """Get the default branch of the repo"""
    # Clean up repo URL if user pasted full GitHub URL
    if repo.startswith("https://github.com/"):
        repo = repo.replace("https://github.com/", "").rstrip("/")
    
    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()["default_branch"]
    except:
        pass
    return "main"

def list_repo_files(token: str, repo: str, branch: str = "main") -> list:
    """List all JSON files in the repo root"""
    # Clean up repo URL if user pasted full GitHub URL
    if repo.startswith("https://github.com/"):
        repo = repo.replace("https://github.com/", "").rstrip("/")
    
    try:
        url = f"https://api.github.com/repos/{repo}/contents?ref={branch}"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            files = response.json()
            # Extract JSON files silently
            json_files = []
            for f in files:
                if f['name'].endswith('.json'):
                    json_files.append(f['name'])
            return json_files
        else:
            st.error(f"Can't list files - API Status: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_github_file(file_name: str, branch: str = "main") -> dict:
    """Fetch and decode base64 file from GitHub"""
    try:
        token = st.secrets.get("GITHUB_TOKEN")
        repo = st.secrets.get("GITHUB_REPO")
        
        # Clean up repo URL if user pasted full GitHub URL
        if repo and repo.startswith("https://github.com/"):
            repo = repo.replace("https://github.com/", "").rstrip("/")
        
        if not token or not repo:
            st.error("❌ Secrets not configured!")
            st.info("""
### Setup Secrets:
1. Click ⚙️ (top-right corner)
2. Click "Secrets"
3. Add these exactly:
```
GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
GITHUB_REPO = "owner/repo"
```
4. Refresh page (F5)
            """)
            return {}
        
        url = f"https://api.github.com/repos/{repo}/contents/{file_name}?ref={branch}"
        headers = {"Authorization": f"token {token}"}
        
        with st.spinner(f"Fetching {file_name} from {branch}..."):
            response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 401:
            st.error("❌ GitHub token is invalid or expired!")
            return {}
        
        if response.status_code == 403:
            st.error("❌ Access denied! Check token has 'repo' scope.")
            return {}
        
        if response.status_code == 404:
            # Try master branch if main fails
            if branch == "main":
                return fetch_github_file(file_name, branch="master")
            else:
                st.error(f"❌ File not found: {file_name}")
                st.info(f"""
File `{file_name}` not found on branch '{branch}'

**Debug Info**:
- URL: {url}
- Status: 404
- Token: {token[:20]}...
- Repo: {repo}
- Branch: {branch}

Try running: git log --all --oneline -- {file_name}
To see if file exists on any branch
                """)
                return {}
        
        if response.status_code == 200:
            # Decode base64 content
            content = response.json()["content"]
            decoded = base64.b64decode(content).decode('utf-8')
            data = json.loads(decoded)
            return data
        
        response.raise_for_status()
        return {}
    
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Timeout fetching {file_name} (network slow)")
        return {}
    
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON in {file_name}: {str(e)}")
        return {}
    
    except Exception as e:
        st.error(f"❌ Error fetching {file_name}: {str(e)}")
        st.write(f"Full error: {e}")
        return {}

def load_data() -> Tuple[dict, dict]:
    """Load GK and Maths data from GitHub"""
    token = st.secrets.get("GITHUB_TOKEN")
    repo = st.secrets.get("GITHUB_REPO")
    
    # Auto-detect the default branch
    branch = get_default_branch(token, repo) if token and repo else "main"
    
    gk_data = fetch_github_file("gk_data.json", branch=branch)
    maths_data = fetch_github_file("maths_data.json", branch=branch)
    return gk_data, maths_data

# ============================================================================
# PRIORITY CALCULATION LOGIC
# ============================================================================

def get_gk_priorities(gk_data: dict, today: datetime) -> Dict:
    """Calculate GK priorities based on revisions"""
    priorities = {
        "overdue": [],
        "due_today": [],
        "weak_areas": [],
        "upcoming": []
    }
    
    if "revisions" not in gk_data:
        return priorities
    
    revisions = gk_data["revisions"]
    
    # Handle different data structures
    if not isinstance(revisions, dict):
        return priorities
    
    for topic, rev_list in revisions.items():
        if not isinstance(rev_list, list):
            st.warning(f"⚠️ Skipping {topic} - not a list")
            continue
        
        for revision in rev_list:
            if not isinstance(revision, dict):
                continue
            
            try:
                due_date = datetime.fromisoformat(revision["due_date"])
                success_rate = revision.get("success_rate", 1.0)
                
                if due_date < today:
                    priorities["overdue"].append({
                        "topic": topic,
                        "due_date": due_date,
                        "success_rate": success_rate
                    })
                elif due_date.date() == today.date():
                    priorities["due_today"].append({
                        "topic": topic,
                        "due_date": due_date,
                        "success_rate": success_rate
                    })
                elif success_rate < 0.7:
                    priorities["weak_areas"].append({
                        "topic": topic,
                        "due_date": due_date,
                        "success_rate": success_rate
                    })
                else:
                    priorities["upcoming"].append({
                        "topic": topic,
                        "due_date": due_date,
                        "success_rate": success_rate
                    })
            except Exception as e:
                st.warning(f"⚠️ Error processing {topic}: {e}")
                continue
    
    return priorities

def get_maths_priorities(maths_data: dict, today: datetime) -> List[Dict]:
    """Calculate Maths priorities based on practice dates and accuracy. Chapters is a list."""
    priorities = []
    
    if not maths_data:
        return priorities
    
    if "chapters" not in maths_data:
        return priorities
    
    chapters = maths_data["chapters"]
    
    # Handle chapters as a list
    if not isinstance(chapters, list):
        st.warning(f"⚠️ chapters is not a list, it's a {type(chapters).__name__}")
        return priorities
    
    for chapter_item in chapters:
        if not isinstance(chapter_item, dict):
            continue
        
        try:
            # Get chapter name from 'name' or 'chapter' field
            chapter_name = chapter_item.get("name") or chapter_item.get("chapter") or "Unknown"
            next_practice_str = chapter_item.get("next_practice_date", today.isoformat())
            accuracy = chapter_item.get("accuracy", 1.0)
            
            # Parse date
            try:
                next_practice = datetime.fromisoformat(next_practice_str)
            except:
                continue
            
            if next_practice.date() <= today.date():
                priority = "HIGH" if accuracy < 0.7 else "MEDIUM"
                priorities.append({
                    "chapter": chapter_name,
                    "next_practice_date": next_practice,
                    "accuracy": accuracy,
                    "priority": priority
                })
        except Exception as e:
            continue
    
    return priorities

def get_reasoning_priorities(maths_data: dict, today: datetime) -> List[Dict]:
    """Calculate Reasoning priorities. Reasoning is a list."""
    priorities = []
    
    if "reasoning" not in maths_data:
        return priorities
    
    reasoning_list = maths_data["reasoning"]
    
    # Handle reasoning as a list
    if not isinstance(reasoning_list, list):
        return priorities
    
    for topic_item in reasoning_list:
        if not isinstance(topic_item, dict):
            continue
        
        try:
            # Get topic name from 'name' or 'topic' field
            topic_name = topic_item.get("name") or topic_item.get("topic") or "Unknown"
            next_practice_str = topic_item.get("next_practice_date", today.isoformat())
            accuracy = topic_item.get("accuracy", 1.0)
            
            # Parse date
            try:
                next_practice = datetime.fromisoformat(next_practice_str)
            except:
                continue
            
            if next_practice.date() <= today.date():
                priority = "HIGH" if accuracy < 0.7 else "MEDIUM"
                priorities.append({
                    "topic": topic_name,
                    "next_practice_date": next_practice,
                    "accuracy": accuracy,
                    "priority": priority
                })
        except Exception as e:
            continue
    
    return priorities

def classify_task_load(task_type: str) -> str:
    """Classify task by load"""
    if task_type == "maths_practice":
        return "Heavy"
    elif task_type == "reasoning":
        return "Medium"
    else:  # gk_revision
        return "Light"

def generate_daily_plan(today: datetime, gk_priorities: Dict, maths_priorities: List, reasoning_priorities: List) -> Dict:
    """Generate plan with load control"""
    plan = {
        "heavy_count": 0,
        "medium_count": 0,
        "light_count": 0,
        "tasks": [],
        "available_slots": []
    }
    
    # Add high-priority tasks first
    for task in maths_priorities:
        if task["priority"] == "HIGH" and plan["heavy_count"] < 1:
            plan["tasks"].append({"type": "maths", "name": task["chapter"], "load": "Heavy"})
            plan["heavy_count"] += 1
    
    for task in reasoning_priorities:
        if task["priority"] == "HIGH" and plan["medium_count"] < 2:
            plan["tasks"].append({"type": "reasoning", "name": task["chapter"], "load": "Medium"})
            plan["medium_count"] += 1
    
    # Add overdue and due-today GK tasks
    overdue_count = len(gk_priorities["overdue"])
    due_today_count = len(gk_priorities["due_today"])
    
    if overdue_count > 0 or due_today_count > 0:
        plan["tasks"].append({"type": "gk", "name": "GK Revisions", "load": "Light", "count": overdue_count + due_today_count})
    
    return plan

def anti_zero_day_rule(gk_priorities: Dict, maths_priorities: List, reasoning_priorities: List) -> str:
    """Apply anti-zero-day rule"""
    total_tasks = len(gk_priorities["overdue"]) + len(gk_priorities["due_today"]) + len(maths_priorities) + len(reasoning_priorities)
    
    if total_tasks == 0:
        weak_maths = [t for t in maths_priorities if t.get("accuracy", 1.0) < 0.7]
        if weak_maths:
            return f"Practice weak area: {weak_maths[0]['chapter']}"
        return "Take a mixed GK quiz to maintain momentum"
    
    return ""

def exam_proximity_mode(maths_data: dict, today: datetime) -> bool:
    """Check if exam is within 60 days"""
    exam_date = maths_data.get("exam_date")
    if not exam_date:
        return False
    
    exam_date = datetime.fromisoformat(exam_date)
    days_to_exam = (exam_date - today).days
    return 0 <= days_to_exam <= 60

# ============================================================================
# 7-DAY PLAN GENERATION
# ============================================================================

def generate_7day_plan(today: datetime, gk_data: dict, maths_data: dict) -> List[Dict]:
    """Generate 7-day study plan"""
    plan = []
    
    for day_offset in range(7):
        current_date = today + timedelta(days=day_offset)
        
        gk_priorities = get_gk_priorities(gk_data, current_date)
        maths_priorities = get_maths_priorities(maths_data, current_date)
        reasoning_priorities = get_reasoning_priorities(maths_data, current_date)
        
        gk_count = len(gk_priorities["overdue"]) + len(gk_priorities["due_today"])
        maths_count = len([t for t in maths_priorities if t["priority"] == "HIGH"])
        reasoning_count = len([t for t in reasoning_priorities if t["priority"] == "HIGH"])
        
        # Determine load
        load = "Light"
        if maths_count > 0 or (gk_count == 0 and reasoning_count > 0):
            load = "Medium" if reasoning_count > 0 else "Heavy"
        elif gk_count > 3:
            load = "Medium"
        
        plan.append({
            "date": current_date,
            "gk_count": gk_count,
            "maths_count": maths_count,
            "reasoning_count": reasoning_count,
            "load": load
        })
    
    return plan

# ============================================================================
# UI RENDERING
# ============================================================================

def render_today_section(gk_priorities: Dict, maths_priorities: List, reasoning_priorities: List, guidance: str):
    """Render today's priorities"""
    st.markdown("## 📅 Today's Study Plan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gk_count = len(gk_priorities["overdue"]) + len(gk_priorities["due_today"])
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="margin: 0; font-size: 14px">GK Revisions</h3>
        <h1 style="margin: 10px 0 0 0; font-size: 32px">{gk_count}</h1>
        <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8">Due Today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        maths_high = next((t for t in maths_priorities if t["priority"] == "HIGH"), None)
        maths_text = maths_high["chapter"][:15] if maths_high else "None scheduled"
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="margin: 0; font-size: 14px">Maths Chapter</h3>
        <p style="margin: 10px 0 0 0; font-size: 14px">{maths_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reasoning_high = next((t for t in reasoning_priorities if t["priority"] == "HIGH"), None)
        reasoning_text = reasoning_high["chapter"][:15] if reasoning_high else "None scheduled"
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="margin: 0; font-size: 14px">Reasoning</h3>
        <p style="margin: 10px 0 0 0; font-size: 14px">{reasoning_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if guidance:
            st.markdown(f"""
            <div class="metric-card">
            <h3 style="margin: 0; font-size: 14px">⚡ Key Focus</h3>
            <p style="margin: 10px 0 0 0; font-size: 12px">{guidance}</p>
            </div>
            """, unsafe_allow_html=True)

def render_7day_section(plan: List[Dict]):
    """Render 7-day plan as table"""
    st.markdown("## 📊 Next 7 Days Plan")
    
    table_data = []
    for item in plan:
        date_str = item["date"].strftime("%a, %b %d")
        table_data.append({
            "Date": date_str,
            "GK": item["gk_count"],
            "Maths": item["maths_count"],
            "Reasoning": item["reasoning_count"],
            "Load": f"{'🟢' if item['load'] == 'Light' else '🟡' if item['load'] == 'Medium' else '🔴'} {item['load']}"
        })
    
    # Display as dataframe
    st.dataframe(table_data, use_container_width=True, hide_index=True)

def render_guidance_section(gk_data: dict, maths_data: dict, today: datetime, exam_proximity: bool):
    """Render guidance card"""
    st.markdown("## 💡 Study Guidance")
    
    guidance_items = []
    
    # Check for weak areas in Maths
    if "chapters" in maths_data:
        chapters = maths_data["chapters"]
        if isinstance(chapters, list):
            weak_maths = [
                (item.get("name") or item.get("chapter") or "Unknown", item.get("accuracy", 1.0)) 
                for item in chapters 
                if isinstance(item, dict) and item.get("accuracy", 1.0) < 0.7
            ]
            if weak_maths:
                weakest = min(weak_maths, key=lambda x: x[1])
                guidance_items.append(f"⚠️ **Maths Focus**: {weakest[0]} accuracy is {weakest[1]:.0%} - prioritize practice")
    
    # Check for weak GK sections
    if "revisions" in gk_data:
        weak_gk = []
        for topic, revisions in gk_data["revisions"].items():
            if isinstance(revisions, list):
                for rev in revisions:
                    if rev.get("success_rate", 1.0) < 0.7:
                        weak_gk.append(topic)
        if weak_gk:
            guidance_items.append(f"📖 **GK Focus**: {weak_gk[0]} needs improvement")
    
    # Exam proximity
    if exam_proximity:
        guidance_items.append("🎯 **Exam Mode**: Prioritize weak areas and mixed practice sets")
    
    # Load guidance
    gk_priorities = get_gk_priorities(gk_data, today)
    gk_count = len(gk_priorities["overdue"]) + len(gk_priorities["due_today"])
    if gk_count == 0:
        guidance_items.append("✅ **Light Load Day**: Great time to clear backlog or take a mock test")
    elif gk_count > 10:
        guidance_items.append("⚠️ **Heavy GK Load**: Break into 2-3 sessions to avoid burnout")
    
    if not guidance_items:
        guidance_items.append("✅ You're on track! Keep up the consistent practice.")
    
    for item in guidance_items:
        st.info(item)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.title("📚 SSC Weekly Planner")
    st.markdown("**Smart study priorities • Zero decision fatigue • Read-only dashboard**")
    st.markdown("---")
    
    # Check if secrets are configured
    token = st.secrets.get("GITHUB_TOKEN")
    repo = st.secrets.get("GITHUB_REPO")
    
    if not token or not repo:
        st.error("❌ GitHub secrets not configured.")
        st.info("""
### ⚙️ Setup in 30 Seconds:

1. **Click the settings icon** ⚙️ (top-right corner)
2. **Click "Secrets"**
3. **Copy-paste this** (replace values):
```toml
GITHUB_TOKEN = "ghp_your_actual_token_here"
GITHUB_REPO = "your-username/your-repo"
```

**Get a GitHub token**:
1. https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Name: `ssc-planner`
4. Check ✅ `repo` only
5. Copy token → paste above
6. **Refresh page** (F5)
        """)
        st.stop()
    
    # Clean up repo URL if user pasted full GitHub URL
    if repo.startswith("https://github.com/"):
        original_repo = repo
        repo = repo.replace("https://github.com/", "").rstrip("/")
    
    # Get the actual default branch
    default_branch = get_default_branch(token, repo)
    
    with st.spinner("📥 Fetching available files..."):
        available_files = list_repo_files(token, repo, branch=default_branch)
    
    with st.spinner("📥 Fetching your study data..."):
        # Try original names first
        gk_data, maths_data = load_data()
        
        # If gk_data not found, try alternative names
        if not gk_data:
            for alt_name in ["revision.json", "gk.json", "gk_revisions.json"]:
                if alt_name in available_files:
                    st.warning(f"⚠️ Found `{alt_name}` instead of `gk_data.json`")
                    st.info("Please rename the file to `gk_data.json` or let me know the exact name")
                    break
    
    # Check what we got
    if not gk_data:
        st.error("❌ Could not fetch `gk_data.json`")
        
        # Show what files are available
        available_files = list_repo_files(token, repo, branch=default_branch)
        
        if available_files:
            st.info(f"""
**Files found in {repo}:**
{available_files}

**Your file might have a different name!**

If you see `gk_data.json` in the list above, the file exists but:
- Check if it's valid JSON
- Verify it has the right structure

If you see a DIFFERENT file name, tell me the exact name!

Example:
- `gk_revisions.json`
- `gk.json`
- `data.json`
- etc.
            """)
        else:
            st.info(f"""
**No JSON files found in {repo}**

Checklist:
1. Files should be at **root level** (not in a folder)
2. Files must be **committed to git** (not just local)
3. Files must be **valid JSON**

Files needed:
- `gk_data.json` 
- `maths_data.json`

Or if they have different names, let me know!
            """)
        st.stop()
    
    if not maths_data:
        st.error("❌ Could not fetch `maths_data.json`")
        
        # Show what files are available
        available_files = list_repo_files(token, repo, branch=default_branch)
        
        if available_files:
            st.info(f"""
**Files found in {repo}:**
{available_files}

**Your file might have a different name!**

If you see `maths_data.json` in the list above, the file exists but:
- Check if it's valid JSON
- Verify it has the right structure

If you see a DIFFERENT file name, tell me the exact name!
            """)
        else:
            st.info(f"""
**No JSON files found in {repo}**

Checklist:
1. Files should be at **root level** (not in a folder)
2. Files must be **committed to git** (not just local)
3. Files must be **valid JSON**
            """)
        st.stop()
    
    today = datetime.now()
    
    # Calculate priorities for today
    gk_priorities = get_gk_priorities(gk_data, today)
    maths_priorities = get_maths_priorities(maths_data, today)
    reasoning_priorities = get_reasoning_priorities(maths_data, today)
    
    # Generate guidance
    zero_day_guidance = anti_zero_day_rule(gk_priorities, maths_priorities, reasoning_priorities)
    exam_proximity = exam_proximity_mode(maths_data, today)
    
    # Render sections
    render_today_section(gk_priorities, maths_priorities, reasoning_priorities, zero_day_guidance)
    
    st.markdown("---")
    
    # 7-day plan
    plan_7day = generate_7day_plan(today, gk_data, maths_data)
    render_7day_section(plan_7day)
    
    st.markdown("---")
    
    # Guidance
    render_guidance_section(gk_data, maths_data, today, exam_proximity)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <p style="text-align: center; color: gray; font-size: 12px;">
    📊 Last updated: {today.strftime('%Y-%m-%d %H:%M:%S')} | 🔒 Read-only dashboard | 📱 Refresh to update
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
