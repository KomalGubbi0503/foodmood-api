
import streamlit as st
import requests
import json
from datetime import datetime


# Configuration

API_BASE_URL = "https://foodmood-api-ium3.onrender.com"  # Will be your Render URL
# Fallback to localhost for local testing
if "localhost" in st.session_state.get("api_url", ""):
    API_BASE_URL = st.session_state.api_url
else:
    API_BASE_URL = "https://foodmood-api-ium3.onrender.com"

st.set_page_config(
    page_title="🥑 FoodMood",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom CSS

st.markdown("""
<style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .success-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# Session State

if "meal_history" not in st.session_state:
    st.session_state.meal_history = []

if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"

# Helper Functions

@st.cache_data(ttl=300)
def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def call_parse_meal_api(meal_description, user_profile=None, use_mock=False):
    """Call the parse-meal endpoint."""
    payload = {
        "meal_description": meal_description,
        "mock": use_mock,
    }
    if user_profile:
        payload["user_profile"] = user_profile

    try:
        response = requests.post(
            f"{API_BASE_URL}/parse-meal",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def call_recommendations_api(goal, diet_type):
    """Call the recommendations endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/recommendations",
            json={"goal": goal, "diet_type": diet_type},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Main App

st.title("🥑 FoodMood")
st.markdown("**AI-powered meal analysis and nutrition recommendations**")

# Sidebar: API Status & Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_alive = check_api_health()
    status_color = "🟢" if api_alive else "🔴"
    st.write(f"{status_color} API Status: {'Online' if api_alive else 'Offline'}")
    
    if not api_alive:
        st.warning("⚠️ API is offline. Using mock mode for demonstration.")
    
    use_mock = st.checkbox("🎭 Use Mock Mode", value=not api_alive, 
                           help="Returns simulated responses without API calls")
    
    st.divider()
    st.subheader("📊 Meal History")
    if st.button("Clear History"):
        st.session_state.meal_history = []
        st.rerun()
    
    if st.session_state.meal_history:
        for i, meal in enumerate(st.session_state.meal_history[-5:], 1):
            st.caption(f"{i}. {meal['description'][:40]}...")

# Tab 1: Meal Parser

tab1, tab2 = st.tabs(["🍽️ Parse Meal", "📈 Get Recommendations"])

with tab1:
    st.header("Parse Your Meal")
    st.markdown("Describe what you ate and get instant nutrition analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        meal_input = st.text_area(
            "What did you eat?",
            placeholder="E.g., 2 eggs, 1 slice whole wheat bread, avocado, glass of milk",
            height=100,
        )
    
    with col2:
        st.markdown("### Examples")
        examples = [
            "2 eggs, toast, avocado",
            "Chicken salad, olive oil",
            "Oatmeal, banana, peanut butter",
            "Salmon, brown rice, broccoli",
        ]
        for ex in examples:
            if st.button(ex, key=ex):
                meal_input = ex
    
    st.divider()
    
    # User Profile
    st.subheader("👤 Your Profile (Optional)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        goal = st.selectbox(
            "Goal",
            ["lose", "maintain", "gain"],
            format_func=lambda x: {"lose": "💪 Weight Loss", "maintain": "⚖️ Maintain", "gain": "🏋️ Muscle Gain"}[x],
        )
    
    with col2:
        diet_type = st.selectbox(
            "Diet Type",
            ["balanced", "low-carb", "high-protein", "vegetarian", "vegan", "keto"],
            format_func=lambda x: x.replace("-", " ").title(),
        )
    
    with col3:
        daily_target = st.number_input("Daily Calorie Target (optional)", min_value=500, max_value=5000, value=2000, step=100)
    
    st.divider()
    
    # Parse Button
    if st.button("🔍 Analyze Meal", type="primary", use_container_width=True):
        if not meal_input.strip():
            st.error("❌ Please describe your meal!")
        else:
            with st.spinner("🤖 Analyzing your meal..."):
                user_profile = {
                    "goal": goal,
                    "diet_type": diet_type,
                    "daily_calorie_target": daily_target,
                } if daily_target else None
                
                result = call_parse_meal_api(meal_input, user_profile, use_mock)
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                # Save to history
                st.session_state.meal_history.append({
                    "description": meal_input,
                    "timestamp": datetime.now(),
                })
                
                # Display Results
                st.success("✅ Analysis Complete!")
                
                # Macros Overview
                st.subheader("📊 Nutrition Overview")
                macros = result["total_macros"]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Calories", f"{macros['calories']:.0f}", "kcal")
                with col2:
                    st.metric("Protein", f"{macros['protein_g']:.1f}g", "")
                with col3:
                    st.metric("Carbs", f"{macros['carbs_g']:.1f}g", "")
                with col4:
                    st.metric("Fat", f"{macros['fat_g']:.1f}g", "")
                
                st.divider()
                
                # Food Items
                st.subheader("🥘 Food Items")
                for item in result["food_items"]:
                    with st.expander(f"**{item['name'].title()}** — {item['quantity']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Calories", f"{item['calories']:.0f}")
                        col2.metric("Protein", f"{item['protein_g']:.1f}g")
                        col3.metric("Carbs", f"{item['carbs_g']:.1f}g")
                        col4.metric("Fat", f"{item['fat_g']:.1f}g")
                
                st.divider()
                
                # AI Feedback
                st.subheader("💬 AI Analysis")
                st.info(result["ai_feedback"])
                
                # Personalised Feedback
                if result.get("personalised"):
                    st.subheader("🎯 Personalised Feedback")
                    pers = result["personalised"]
                    
                    alignment_color = {
                        "good": "🟢",
                        "moderate": "🟡",
                        "poor": "🔴",
                    }
                    st.markdown(f"**Goal Alignment:** {alignment_color.get(pers['goal_alignment'], '❓')} {pers['goal_alignment'].upper()}")
                    
                    st.write(pers["adjusted_feedback"])
                    
                    st.subheader("💡 Suggestions")
                    for i, suggestion in enumerate(pers["suggestions"], 1):
                        st.write(f"**{i}.** {suggestion}")
                
                # Cache info
                if result.get("cache_hit"):
                    st.caption("⚡ (Served from cache)")
                if result.get("mock"):
                    st.caption("🎭 (Mock response)")


# Tab 2: Recommendations

with tab2:
    st.header("Get Meal Recommendations")
    st.markdown("Based on your goal and diet type, get personalized meal suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal = st.selectbox(
            "Your Goal",
            ["lose", "maintain", "gain"],
            format_func=lambda x: {"lose": "💪 Weight Loss", "maintain": "⚖️ Maintain", "gain": "🏋️ Muscle Gain"}[x],
            key="rec_goal",
        )
    
    with col2:
        diet_type = st.selectbox(
            "Diet Type",
            ["balanced", "low-carb", "high-protein", "vegetarian", "vegan", "keto"],
            format_func=lambda x: x.replace("-", " ").title(),
            key="rec_diet",
        )
    
    if st.button("📋 Get Recommendations", type="primary", use_container_width=True):
        with st.spinner("Finding recommendations..."):
            result = call_recommendations_api(goal, diet_type)
        
        if "error" in result:
            st.error(f"❌ Error: {result['error']}")
        else:
            st.success("✅ Here are your recommendations!")
            
            st.subheader("🍽️ Recommended Meals")
            for i, meal in enumerate(result.get("recommended_meals", []), 1):
                st.write(f"**{i}. {meal}**")
            
            st.divider()
            
            st.subheader("💡 Tips")
            for tip in result.get("tips", []):
                st.info(tip)


# Footer

st.divider()
st.markdown("""
---
**FoodMood** — AI-powered nutrition analysis  
Built with FastAPI + Streamlit + OpenRouter (Mistral-7B)  
[GitHub](https://github.com/KomalGubbi0503/foodmood-api) | [API Docs](https://foodmood-api.onrender.com/docs)
""")