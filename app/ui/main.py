import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
import time
from dotenv import load_dotenv
import asyncio
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="GoldMiner 2.0 - AI Startup Validator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .idea-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .idea-card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .validation-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .score-high { 
        background-color: #28a745; 
        color: white; 
    }
    .score-medium { 
        background-color: #ffc107; 
        color: black; 
    }
    .score-low { 
        background-color: #dc3545; 
        color: white; 
    }
    
    .progress-indicator {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background-color: #e3f2fd;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .kanban-column {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        min-height: 400px;
    }
    
    .kanban-header {
        font-weight: bold;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #e0e0e0;
        border-radius: 4px;
    }
    
    .filter-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'all_ideas' not in st.session_state:
        st.session_state.all_ideas = {}  # Store ideas by ID
    if 'goldmine_active' not in st.session_state:
        st.session_state.goldmine_active = False
    if 'goldmine_progress' not in st.session_state:
        st.session_state.goldmine_progress = {
            'generated': 0,
            'validated': 0,
            'target': 0,
            'current_idea': None
        }
    if 'selected_idea_id' not in st.session_state:
        st.session_state.selected_idea_id = None
    if 'filter_settings' not in st.session_state:
        st.session_state.filter_settings = {
            'status': 'all',
            'min_score': 0,
            'market_focus': 'all',
            'sort_by': 'created_at',
            'sort_order': 'desc'
        }
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = {}

def load_ideas_from_db():
    """Load all ideas from database"""
    try:
        response = requests.get(f"{API_URL}/api/ideas/")
        if response.status_code == 200:
            ideas = response.json()
            # Convert to dictionary for easier access
            st.session_state.all_ideas = {idea['id']: idea for idea in ideas}
    except Exception as e:
        st.error(f"Failed to load ideas: {str(e)}")

def main():
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 GoldMiner 2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">AI-Powered Startup Idea Generator & Validator with Full Control</p>', unsafe_allow_html=True)
    
    # Load ideas on startup
    if not st.session_state.all_ideas:
        load_ideas_from_db()
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("🎯 Configuration")
        
        market_focus = st.selectbox(
            "Market Focus",
            ["Technology", "Healthcare", "Fintech", "E-commerce", "Education", "Sustainability", "Other"]
        )
        
        innovation_type = st.radio(
            "Innovation Type",
            ["Product", "Service", "Business Model", "Platform"]
        )
        
        target_demographic = st.text_input(
            "Target Demographic",
            placeholder="e.g., Small businesses, Gen Z consumers"
        )
        
        problem_area = st.text_area(
            "Problem Area",
            placeholder="e.g., Remote work challenges, Healthcare access",
            height=100
        )
        
        st.divider()
        
        # Quick Stats
        st.header("📊 Quick Stats")
        total_ideas = len(st.session_state.all_ideas)
        validated_ideas = sum(1 for idea in st.session_state.all_ideas.values() 
                            if idea.get('status') == 'validated')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Ideas", total_ideas)
            st.metric("Validated", validated_ideas)
        with col2:
            st.metric("Pending", total_ideas - validated_ideas)
            if validated_ideas > 0:
                avg_score = sum(idea.get('validation', {}).get('overall_score', 0) 
                              for idea in st.session_state.all_ideas.values() 
                              if idea.get('status') == 'validated') / validated_ideas
                st.metric("Avg Score", f"{avg_score:.1f}%")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Idea Board", 
        "⛏️ Gold Mining", 
        "💡 Quick Generate", 
        "📊 Analytics", 
        "🔧 Settings"
    ])
    
    with tab1:
        idea_board_tab()
    
    with tab2:
        goldmining_tab(market_focus, innovation_type, target_demographic, problem_area)
    
    with tab3:
        quick_generate_tab(market_focus, innovation_type, target_demographic, problem_area)
    
    with tab4:
        analytics_tab()
    
    with tab5:
        settings_tab()

def idea_board_tab():
    """Kanban-style idea management board"""
    st.header("🎯 Idea Management Board")
    
    # Filter Section
    with st.expander("🔍 Filters & Sorting", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox(
                "Status Filter",
                ["all", "pending", "validated", "rejected"],
                index=["all", "pending", "validated", "rejected"].index(st.session_state.filter_settings['status'])
            )
            st.session_state.filter_settings['status'] = status_filter
        
        with col2:
            min_score = st.slider(
                "Minimum Score",
                0, 100, 
                st.session_state.filter_settings['min_score']
            )
            st.session_state.filter_settings['min_score'] = min_score
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                ["created_at", "overall_score", "title"],
                index=["created_at", "overall_score", "title"].index(st.session_state.filter_settings['sort_by'])
            )
            st.session_state.filter_settings['sort_by'] = sort_by
        
        with col4:
            sort_order = st.radio(
                "Order",
                ["desc", "asc"],
                index=["desc", "asc"].index(st.session_state.filter_settings['sort_order'])
            )
            st.session_state.filter_settings['sort_order'] = sort_order
    
    # Apply filters
    filtered_ideas = filter_ideas(st.session_state.all_ideas, st.session_state.filter_settings)
    
    # Kanban Board View
    st.subheader("📋 Kanban Board")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_idea_column("📝 Pending", 
                          [idea for idea in filtered_ideas if idea.get('status', 'pending') == 'pending'])
    
    with col2:
        display_idea_column("✅ Validated", 
                          [idea for idea in filtered_ideas if idea.get('status') == 'validated'])
    
    with col3:
        display_idea_column("❌ Rejected", 
                          [idea for idea in filtered_ideas if idea.get('status') == 'rejected'])

def display_idea_column(title: str, ideas: List[Dict]):
    """Display a column of ideas in the Kanban board"""
    st.markdown(f'<div class="kanban-header">{title} ({len(ideas)})</div>', unsafe_allow_html=True)
    
    for idea in ideas:
        with st.container():
            # Create idea card
            score = idea.get('validation', {}).get('overall_score', 0) if idea.get('validation') else 0
            score_class = get_score_class(score)
            
            # Check if in edit mode
            if st.session_state.edit_mode.get(idea['id'], False):
                # Edit mode UI
                with st.form(f"edit_form_{idea['id']}"):
                    new_title = st.text_input("Title", value=idea['title'])
                    new_problem = st.text_area("Problem Statement", value=idea['problem_statement'], height=100)
                    new_solution = st.text_area("Solution", value=idea['solution_outline'], height=100)
                    new_target = st.text_input("Target Market", value=idea['target_market'])
                    new_uvp = st.text_area("Value Proposition", value=idea.get('unique_value_proposition', ''), height=80)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", type="primary"):
                            update_idea(idea['id'], {
                                'title': new_title,
                                'problem_statement': new_problem,
                                'solution_outline': new_solution,
                                'target_market': new_target,
                                'unique_value_proposition': new_uvp
                            })
                            st.session_state.edit_mode[idea['id']] = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state.edit_mode[idea['id']] = False
                            st.rerun()
            else:
                # Display mode
                st.markdown(f"""
                <div class="idea-card">
                    {f'<span class="validation-badge {score_class}">{score:.0f}%</span>' if score > 0 else ''}
                    <h4>{idea['title']}</h4>
                    <p><strong>Problem:</strong> {idea['problem_statement'][:100]}...</p>
                    <p><strong>Target:</strong> {idea['target_market']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("👁️", key=f"view_{idea['id']}", help="View details"):
                        st.session_state.selected_idea_id = idea['id']
                        show_idea_details(idea)
                with col2:
                    if st.button("✏️", key=f"edit_{idea['id']}", help="Edit"):
                        st.session_state.edit_mode[idea['id']] = True
                        st.rerun()
                with col3:
                    if st.button("🔍", key=f"validate_{idea['id']}", help="Validate"):
                        validate_single_idea(idea['id'])
                with col4:
                    if st.button("🗑️", key=f"delete_{idea['id']}", help="Delete"):
                        # Use session state for confirmation
                        confirm_key = f"confirm_delete_{idea['id']}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False
                        
                        if st.session_state[confirm_key]:
                            delete_idea(idea['id'])
                            st.session_state[confirm_key] = False
                        else:
                            st.session_state[confirm_key] = True
                            st.warning(f"Click delete again to confirm deletion of '{idea['title']}'")
                            st.rerun()

def goldmining_tab(market_focus, innovation_type, target_demographic, problem_area):
    """Enhanced Gold Mining tab with real-time progress"""
    st.header("⛏️ Gold Mining - Automated Idea Discovery")
    
    st.info("""
    🏆 **Gold Mining Mode**: Generate multiple ideas, validate them automatically, and see results in real-time.
    You can stop the process at any time and keep the ideas generated so far.
    """)
    
    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        num_ideas = st.slider("Target number of ideas", min_value=1, max_value=20, value=5)
        st.session_state.goldmine_progress['target'] = num_ideas
    
    with col2:
        if not st.session_state.goldmine_active:
            if st.button("⛏️ Start Mining", type="primary", use_container_width=True):
                st.session_state.goldmine_active = True
                st.session_state.goldmine_progress = {
                    'generated': 0,
                    'validated': 0,
                    'target': num_ideas,
                    'current_idea': None
                }
                st.rerun()
        else:
            if st.button("⏹️ Stop Mining", type="secondary", use_container_width=True):
                st.session_state.goldmine_active = False
                st.rerun()
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            load_ideas_from_db()
            st.rerun()
    
    # Progress Display
    if st.session_state.goldmine_active:
        st.markdown("### 📊 Mining Progress")
        
        # Progress bars
        progress_container = st.container()
        with progress_container:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Ideas Generated", st.session_state.goldmine_progress['generated'])
                st.progress(st.session_state.goldmine_progress['generated'] / st.session_state.goldmine_progress['target'])
            with col2:
                st.metric("Ideas Validated", st.session_state.goldmine_progress['validated'])
                if st.session_state.goldmine_progress['generated'] > 0:
                    st.progress(st.session_state.goldmine_progress['validated'] / st.session_state.goldmine_progress['generated'])
            
            # Current idea being processed
            if st.session_state.goldmine_progress['current_idea']:
                st.info(f"🔄 Processing: {st.session_state.goldmine_progress['current_idea']}")
        
        # Start async goldmine process
        run_goldmine_process(market_focus, innovation_type, target_demographic, problem_area, num_ideas)
    
    # Display recent validated ideas
    st.divider()
    st.subheader("✨ Recently Validated Ideas")
    
    validated_ideas = [idea for idea in st.session_state.all_ideas.values() 
                      if idea.get('status') == 'validated']
    validated_ideas.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    if validated_ideas:
        for idea in validated_ideas[:5]:  # Show last 5
            display_validated_idea_card(idea)
    else:
        st.info("No validated ideas yet. Start mining to discover golden startup ideas!")

def run_goldmine_process(market_focus, innovation_type, target_demographic, problem_area, num_ideas):
    """Run the goldmine process with real-time updates"""
    # This would be better as a WebSocket or Server-Sent Events in production
    # For now, we'll simulate with a simple polling approach
    
    placeholder = st.empty()
    
    try:
        # Call the goldmine API
        response = requests.post(
            f"{API_URL}/api/ideas/goldmine",
            json={
                "market_focus": market_focus,
                "innovation_type": innovation_type,
                "target_demographic": target_demographic,
                "problem_area": problem_area
            },
            params={"num_ideas": num_ideas},
            stream=True  # Enable streaming if the API supports it
        )
        
        if response.status_code == 200:
            results = response.json()
            st.session_state.goldmine_active = False
            
            # Update ideas in session state
            for idea in results:
                st.session_state.all_ideas[idea['id']] = idea
            
            placeholder.success(f"✅ Mining complete! Found {len(results)} validated ideas.")
            time.sleep(2)
            st.rerun()
        else:
            placeholder.error(f"Mining failed: {response.text}")
            st.session_state.goldmine_active = False
    
    except Exception as e:
        placeholder.error(f"Error during mining: {str(e)}")
        st.session_state.goldmine_active = False

def display_validated_idea_card(idea):
    """Display a validated idea card with all details"""
    score = idea.get('validation', {}).get('overall_score', 0)
    score_class = get_score_class(score)
    
    with st.expander(f"💎 {idea['title']} - Score: {score:.0f}%", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Problem:** {idea['problem_statement']}")
            st.markdown(f"**Solution:** {idea['solution_outline']}")
            st.markdown(f"**Target Market:** {idea['target_market']}")
            st.markdown(f"**Value Proposition:** {idea.get('unique_value_proposition', 'N/A')}")
            
            # Pain point evidence if available
            if idea.get('pain_point_evidence'):
                st.markdown("**📍 Pain Point Evidence:**")
                for evidence in idea['pain_point_evidence'][:3]:  # Show top 3
                    st.caption(f"• {evidence.get('snippet', '')} - [{evidence.get('platform', '')}]")
        
        with col2:
            validation = idea.get('validation', {})
            st.metric("Problem Score", f"{validation.get('problem_score', 0):.0f}%")
            st.metric("Solution Score", f"{validation.get('solution_score', 0):.0f}%")
            st.metric("Market Score", f"{validation.get('market_score', 0):.0f}%")
            st.metric("Execution Score", f"{validation.get('execution_score', 0):.0f}%")
            
            st.divider()
            
            # Action buttons
            if st.button("✏️ Edit", key=f"edit_validated_{idea['id']}", use_container_width=True):
                st.session_state.edit_mode[idea['id']] = True
                st.rerun()
            
            if st.button("📊 Research", key=f"research_validated_{idea['id']}", use_container_width=True):
                st.info("Market research coming soon!")
            
            if st.button("📤 Export", key=f"export_validated_{idea['id']}", use_container_width=True):
                export_idea(idea)

def quick_generate_tab(market_focus, innovation_type, target_demographic, problem_area):
    """Quick generation of individual ideas"""
    st.header("💡 Quick Idea Generation")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("Generate individual ideas quickly without automatic validation.")
    
    with col2:
        if st.button("🚀 Generate Idea", type="primary", use_container_width=True):
            with st.spinner("Generating idea..."):
                generate_single_idea(market_focus, innovation_type, target_demographic, problem_area)
    
    with col3:
        if st.button("🎲 Generate 5 Ideas", use_container_width=True):
            with st.spinner("Generating ideas..."):
                for i in range(5):
                    generate_single_idea(market_focus, innovation_type, target_demographic, problem_area)
                    time.sleep(0.5)  # Small delay to avoid rate limits
    
    # Display recent unvalidated ideas
    st.divider()
    st.subheader("📝 Recent Ideas (Unvalidated)")
    
    pending_ideas = [idea for idea in st.session_state.all_ideas.values() 
                    if idea.get('status', 'pending') == 'pending']
    pending_ideas.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    if pending_ideas:
        for idea in pending_ideas[:10]:  # Show last 10
            display_simple_idea_card(idea)
    else:
        st.info("No pending ideas. Generate some ideas to get started!")

def display_simple_idea_card(idea):
    """Display a simple idea card for pending ideas"""
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {idea['title']}")
            st.caption(f"Created: {idea.get('created_at', 'Unknown')}")
            st.write(f"**Problem:** {idea['problem_statement'][:150]}...")
            st.write(f"**Target:** {idea['target_market']}")
        
        with col2:
            if st.button("🔍 Validate", key=f"validate_quick_{idea['id']}"):
                validate_single_idea(idea['id'])
            if st.button("✏️ Edit", key=f"edit_quick_{idea['id']}"):
                st.session_state.edit_mode[idea['id']] = True
                st.rerun()
            if st.button("🗑️ Delete", key=f"delete_quick_{idea['id']}"):
                # Use session state for confirmation
                confirm_key = f"confirm_delete_quick_{idea['id']}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                if st.session_state[confirm_key]:
                    delete_idea(idea['id'])
                    if confirm_key in st.session_state:
                        del st.session_state[confirm_key]
                else:
                    st.session_state[confirm_key] = True
                    st.warning(f"Click delete again to confirm deletion")
                    st.rerun()

def analytics_tab():
    """Analytics and insights dashboard"""
    st.header("📊 Analytics Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_ideas = len(st.session_state.all_ideas)
    validated_ideas = [idea for idea in st.session_state.all_ideas.values() 
                      if idea.get('status') == 'validated']
    
    with col1:
        st.metric("Total Ideas", total_ideas)
    
    with col2:
        st.metric("Validated Ideas", len(validated_ideas))
    
    with col3:
        if validated_ideas:
            avg_score = sum(idea.get('validation', {}).get('overall_score', 0) 
                          for idea in validated_ideas) / len(validated_ideas)
            st.metric("Avg Validation Score", f"{avg_score:.1f}%")
        else:
            st.metric("Avg Validation Score", "N/A")
    
    with col4:
        success_rate = (len(validated_ideas) / total_ideas * 100) if total_ideas > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Visualizations
    st.divider()
    
    if st.session_state.all_ideas:
        col1, col2 = st.columns(2)
        
        with col1:
            # Ideas by market focus
            st.subheader("Ideas by Market Focus")
            market_data = {}
            for idea in st.session_state.all_ideas.values():
                market = idea.get('market_focus', 'Unknown')
                market_data[market] = market_data.get(market, 0) + 1
            
            if market_data:
                fig = px.pie(
                    values=list(market_data.values()),
                    names=list(market_data.keys()),
                    title="Distribution by Market Focus"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Validation scores distribution
            st.subheader("Validation Score Distribution")
            scores = [idea.get('validation', {}).get('overall_score', 0) 
                     for idea in validated_ideas]
            
            if scores:
                fig = px.histogram(
                    x=scores,
                    nbins=10,
                    title="Distribution of Validation Scores",
                    labels={'x': 'Score', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Export section
    st.divider()
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export All Ideas (CSV)", use_container_width=True):
            export_all_ideas_csv()
    
    with col2:
        if st.button("📊 Export Validated Ideas (JSON)", use_container_width=True):
            export_validated_ideas_json()
    
    with col3:
        if st.button("📈 Generate Report (PDF)", use_container_width=True):
            st.info("PDF report generation coming soon!")

def settings_tab():
    """Settings and configuration"""
    st.header("🔧 Settings")
    
    # API Settings
    st.subheader("API Configuration")
    api_url = st.text_input("API URL", value=API_URL)
    if st.button("Test Connection"):
        try:
            response = requests.get(f"{api_url}/")
            if response.status_code == 200:
                st.success("✅ API connection successful!")
            else:
                st.error(f"❌ API connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
    
    # Data Management
    st.divider()
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reload All Ideas", use_container_width=True):
            load_ideas_from_db()
            st.success("Ideas reloaded!")
    
    with col2:
        if st.button("🗑️ Clear Local Cache", use_container_width=True):
            st.session_state.all_ideas = {}
            st.session_state.edit_mode = {}
            st.success("Local cache cleared!")
    
    # Display Settings
    st.divider()
    st.subheader("Display Settings")
    
    ideas_per_page = st.number_input("Ideas per page", min_value=5, max_value=50, value=20)
    auto_refresh = st.checkbox("Auto-refresh ideas every 30 seconds")
    
    if st.button("💾 Save Settings"):
        # Save settings to localStorage or database
        st.success("Settings saved!")

# Helper Functions

def filter_ideas(ideas: Dict, filters: Dict) -> List[Dict]:
    """Apply filters to ideas"""
    filtered = list(ideas.values())
    
    # Status filter
    if filters['status'] != 'all':
        filtered = [idea for idea in filtered if idea.get('status', 'pending') == filters['status']]
    
    # Score filter
    if filters['min_score'] > 0:
        filtered = [idea for idea in filtered 
                   if idea.get('validation', {}).get('overall_score', 0) >= filters['min_score']]
    
    # Sort
    sort_key = filters['sort_by']
    if sort_key == 'overall_score':
        filtered.sort(key=lambda x: x.get('validation', {}).get('overall_score', 0), 
                     reverse=(filters['sort_order'] == 'desc'))
    else:
        filtered.sort(key=lambda x: x.get(sort_key, ''), 
                     reverse=(filters['sort_order'] == 'desc'))
    
    return filtered

def get_score_class(score: float) -> str:
    """Get CSS class based on score"""
    if score >= 80:
        return "score-high"
    elif score >= 60:
        return "score-medium"
    else:
        return "score-low"

def show_idea_details(idea: Dict):
    """Show detailed view of an idea in a modal"""
    with st.expander(f"📋 Idea Details: {idea['title']}", expanded=True):
        # Basic Info
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Title:** {idea['title']}")
            st.markdown(f"**Status:** {idea.get('status', 'pending').upper()}")
            st.markdown(f"**Created:** {idea.get('created_at', 'Unknown')}")
            
            st.divider()
            
            st.markdown("**Problem Statement:**")
            st.info(idea['problem_statement'])
            
            st.markdown("**Solution Outline:**")
            st.success(idea['solution_outline'])
            
            st.markdown("**Target Market:**")
            st.warning(idea['target_market'])
            
            st.markdown("**Unique Value Proposition:**")
            st.info(idea.get('unique_value_proposition', 'Not specified'))
        
        with col2:
            if idea.get('validation'):
                st.markdown("**Validation Scores:**")
                validation = idea['validation']
                
                # Overall score with color
                score = validation.get('overall_score', 0)
                score_class = get_score_class(score)
                st.markdown(f"<h2 class='{score_class}'>{score:.0f}%</h2>", unsafe_allow_html=True)
                
                st.divider()
                
                # Individual scores
                st.metric("Problem", f"{validation.get('problem_score', 0):.0f}%")
                st.metric("Solution", f"{validation.get('solution_score', 0):.0f}%")
                st.metric("Market", f"{validation.get('market_score', 0):.0f}%")
                st.metric("Execution", f"{validation.get('execution_score', 0):.0f}%")
                
                # Validation notes
                if validation.get('validation_notes'):
                    st.divider()
                    st.markdown("**Notes:**")
                    st.caption(validation['validation_notes'])

def update_idea(idea_id: int, updates: Dict):
    """Update an idea via API"""
    try:
        response = requests.put(
            f"{API_URL}/api/ideas/{idea_id}",
            json=updates
        )
        if response.status_code == 200:
            # Update local state
            updated_idea = response.json()
            st.session_state.all_ideas[idea_id] = updated_idea
            st.success(f"✅ Updated '{updated_idea['title']}'")
        else:
            st.error(f"Failed to update idea: {response.text}")
    except Exception as e:
        st.error(f"Error updating idea: {str(e)}")

def delete_idea(idea_id: int):
    """Delete an idea"""
    try:
        response = requests.delete(f"{API_URL}/api/ideas/{idea_id}")
        if response.status_code == 200:
            # Remove from local state
            if idea_id in st.session_state.all_ideas:
                del st.session_state.all_ideas[idea_id]
            # Clean up any confirmation states
            confirm_key = f"confirm_delete_{idea_id}"
            if confirm_key in st.session_state:
                del st.session_state[confirm_key]
            st.success("✅ Idea deleted successfully")
            time.sleep(0.5)  # Brief pause to show success message
            st.rerun()
        else:
            st.error(f"Failed to delete idea: {response.text}")
    except Exception as e:
        st.error(f"Error deleting idea: {str(e)}")

def validate_single_idea(idea_id: int):
    """Validate a single idea"""
    with st.spinner("Validating idea..."):
        try:
            response = requests.post(
                f"{API_URL}/api/validation/{idea_id}",
                json={"validation_depth": "standard"}
            )
            if response.status_code == 200:
                validation = response.json()
                # Update local state
                if idea_id in st.session_state.all_ideas:
                    st.session_state.all_ideas[idea_id]['validation'] = validation
                    st.session_state.all_ideas[idea_id]['status'] = 'validated'
                st.success("✅ Validation complete!")
                st.rerun()
            else:
                st.error(f"Validation failed: {response.text}")
        except Exception as e:
            st.error(f"Error during validation: {str(e)}")

def generate_single_idea(market_focus, innovation_type, target_demographic, problem_area):
    """Generate a single idea"""
    try:
        response = requests.post(
            f"{API_URL}/api/ideas/generate",
            json={
                "market_focus": market_focus,
                "innovation_type": innovation_type,
                "target_demographic": target_demographic,
                "problem_area": problem_area
            }
        )
        if response.status_code == 200:
            idea = response.json()
            st.session_state.all_ideas[idea['id']] = idea
            st.success(f"✅ Generated: {idea['title']}")
            return idea
        else:
            st.error(f"Failed to generate idea: {response.text}")
    except Exception as e:
        st.error(f"Error generating idea: {str(e)}")
    return None

def export_idea(idea: Dict):
    """Export a single idea"""
    # Create download content
    content = f"""# {idea['title']}

## Problem Statement
{idea['problem_statement']}

## Solution
{idea['solution_outline']}

## Target Market
{idea['target_market']}

## Value Proposition
{idea.get('unique_value_proposition', 'N/A')}

## Validation Results
"""
    
    if idea.get('validation'):
        validation = idea['validation']
        content += f"""
- Overall Score: {validation.get('overall_score', 0):.1f}%
- Problem Score: {validation.get('problem_score', 0):.1f}%
- Solution Score: {validation.get('solution_score', 0):.1f}%
- Market Score: {validation.get('market_score', 0):.1f}%
- Execution Score: {validation.get('execution_score', 0):.1f}%

### Validation Notes
{validation.get('validation_notes', 'N/A')}
"""
    
    # Create download button
    st.download_button(
        label="📥 Download Idea",
        data=content,
        file_name=f"idea_{idea['id']}_{idea['title'].replace(' ', '_')}.md",
        mime="text/markdown"
    )

def export_all_ideas_csv():
    """Export all ideas to CSV"""
    if not st.session_state.all_ideas:
        st.warning("No ideas to export")
        return
    
    # Convert to DataFrame
    ideas_data = []
    for idea in st.session_state.all_ideas.values():
        row = {
            'ID': idea['id'],
            'Title': idea['title'],
            'Status': idea.get('status', 'pending'),
            'Problem': idea['problem_statement'],
            'Solution': idea['solution_outline'],
            'Target Market': idea['target_market'],
            'Value Proposition': idea.get('unique_value_proposition', ''),
            'Overall Score': idea.get('validation', {}).get('overall_score', 0) if idea.get('validation') else 0,
            'Created At': idea.get('created_at', '')
        }
        ideas_data.append(row)
    
    df = pd.DataFrame(ideas_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"goldminer_ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_validated_ideas_json():
    """Export validated ideas to JSON"""
    validated_ideas = [idea for idea in st.session_state.all_ideas.values() 
                      if idea.get('status') == 'validated']
    
    if not validated_ideas:
        st.warning("No validated ideas to export")
        return
    
    json_data = json.dumps(validated_ideas, indent=2, default=str)
    
    st.download_button(
        label="📥 Download JSON",
        data=json_data,
        file_name=f"goldminer_validated_ideas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()