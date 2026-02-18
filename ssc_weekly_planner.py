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
    initial_sidebar_state="collapsed"
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_github_file(file_name: str) -> dict:
    """Fetch and decode base64 file from GitHub"""
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        branch = "main"  # Default branch
        
        url = f"https://api.github.com/repos/{repo}/contents/{file_name}?ref={branch}"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Decode base64 content
        content = response.json()["content"]
        decoded = base64.b64decode(content).decode('utf-8')
        return json.loads(decoded)
    
    except KeyError as e:
        st.error(f"❌ Missing secret: {str(e)}")
        st.info("Add secrets via Streamlit Settings:\n1. Click ⚙️ (settings) → Secret management\n2. Add: GITHUB_TOKEN, GITHUB_REPO")
        return {}
    
    except Exception as e:
        st.error(f"❌ Error fetching {file_name}: {str(e)}")
        return {}

def load_data() -> Tuple[dict, dict]:
    """Load GK and Maths data from GitHub"""
    gk_data = fetch_github_file("gk_data.json")
    maths_data = fetch_github_file("maths_data.json")
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
    
    for topic, rev_list in revisions.items():
        if not isinstance(rev_list, list):
            continue
        
        for revision in rev_list:
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
    
    return priorities

def get_maths_priorities(maths_data: dict, today: datetime) -> List[Dict]:
    """Calculate Maths priorities based on practice dates and accuracy"""
    priorities = []
    
    if "chapters" not in maths_data:
        return priorities
    
    chapters = maths_data["chapters"]
    
    for chapter_name, chapter_info in chapters.items():
        if not isinstance(chapter_info, dict):
            continue
        
        next_practice = datetime.fromisoformat(chapter_info.get("next_practice_date", today.isoformat()))
        accuracy = chapter_info.get("accuracy", 1.0)
        
        if next_practice.date() <= today.date():
            priority = "HIGH" if accuracy < 0.7 else "MEDIUM"
            priorities.append({
                "chapter": chapter_name,
                "next_practice_date": next_practice,
                "accuracy": accuracy,
                "priority": priority
            })
    
    return priorities

def get_reasoning_priorities(maths_data: dict, today: datetime) -> List[Dict]:
    """Calculate Reasoning priorities (similar to Maths)"""
    priorities = []
    
    if "reasoning" not in maths_data:
        return priorities
    
    reasoning_chapters = maths_data["reasoning"]
    
    for chapter_name, chapter_info in reasoning_chapters.items():
        if not isinstance(chapter_info, dict):
            continue
        
        next_practice = datetime.fromisoformat(chapter_info.get("next_practice_date", today.isoformat()))
        accuracy = chapter_info.get("accuracy", 1.0)
        
        if next_practice.date() <= today.date():
            priority = "HIGH" if accuracy < 0.7 else "MEDIUM"
            priorities.append({
                "chapter": chapter_name,
                "next_practice_date": next_practice,
                "accuracy": accuracy,
                "priority": priority
            })
    
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
        weak_maths = [
            (name, info.get("accuracy", 1.0)) 
            for name, info in maths_data["chapters"].items() 
            if isinstance(info, dict) and info.get("accuracy", 1.0) < 0.7
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
    
    # Load data
    with st.spinner("📥 Fetching your study data..."):
        gk_data, maths_data = load_data()
    
    if not gk_data or not maths_data:
        st.error("❌ Unable to load study data. Please configure GitHub secrets.")
        st.info("""
### Setup Instructions:

1. **Click the ⚙️ icon** in the top-right corner
2. **Select "Secrets"**
3. **Add these secrets**:
   ```
   GITHUB_TOKEN = "ghp_your_token_here"
   GITHUB_REPO = "your-username/your-repo"
   ```

**To generate a GitHub token**:
- Go to https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select `repo` scope only
- Copy and paste above
        """)
        return
    
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
