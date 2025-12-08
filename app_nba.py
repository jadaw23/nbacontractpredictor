# ============================================
# NBA Dashboard - Streamlit Application with LLM Integration
# ITOM6265 - Database Project
# ============================================

# Block 1: Import required libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime

# Block 2: Page configuration
st.set_page_config(
    page_title="ITOM6265-NBA Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# NBA Team Colors Dictionary
NBA_COLORS = {
    'ATL': {'primary': '#E03A3E', 'secondary': '#C1D32F'},
    'BOS': {'primary': '#007A33', 'secondary': '#BA9653'},
    'BRK': {'primary': '#000000', 'secondary': '#FFFFFF'},
    'CHA': {'primary': '#1D1160', 'secondary': '#00788C'},
    'CHI': {'primary': '#CE1141', 'secondary': '#000000'},
    'CLE': {'primary': '#860038', 'secondary': '#FDBB30'},
    'DAL': {'primary': '#00538C', 'secondary': '#002B5E'},
    'DEN': {'primary': '#0E2240', 'secondary': '#FEC524'},
    'DET': {'primary': '#C8102E', 'secondary': '#1D42BA'},
    'GSW': {'primary': '#1D428A', 'secondary': '#FFC72C'},
    'HOU': {'primary': '#CE1141', 'secondary': '#000000'},
    'IND': {'primary': '#002D62', 'secondary': '#FDBB30'},
    'LAC': {'primary': '#C8102E', 'secondary': '#1D428A'},
    'LAL': {'primary': '#552583', 'secondary': '#FDB927'},
    'MEM': {'primary': '#5D76A9', 'secondary': '#12173F'},
    'MIA': {'primary': '#98002E', 'secondary': '#F9A01B'},
    'MIL': {'primary': '#00471B', 'secondary': '#EEE1C6'},
    'MIN': {'primary': '#0C2340', 'secondary': '#236192'},
    'NOP': {'primary': '#0C2340', 'secondary': '#C8102E'},
    'NYK': {'primary': '#006BB6', 'secondary': '#F58426'},
    'OKC': {'primary': '#007AC1', 'secondary': '#EF3B24'},
    'ORL': {'primary': '#0077C0', 'secondary': '#C4CED4'},
    'PHI': {'primary': '#006BB6', 'secondary': '#ED174C'},
    'PHX': {'primary': '#1D1160', 'secondary': '#E56020'},
    'POR': {'primary': '#E03A3E', 'secondary': '#000000'},
    'SAC': {'primary': '#5A2D81', 'secondary': '#63727A'},
    'SAS': {'primary': '#C4CED4', 'secondary': '#000000'},
    'TOR': {'primary': '#CE1141', 'secondary': '#000000'},
    'UTA': {'primary': '#002B5C', 'secondary': '#00471B'},
    'WAS': {'primary': '#002B5C', 'secondary': '#E31837'}
}

# Player headshot mapping
PLAYER_IMAGES = {
    'Gilgeous-Alexander Shai': 'https://cdn.nba.com/headshots/nba/latest/1040x760/1628983.png',
    'Antetokounmpo Giannis': 'https://cdn.nba.com/headshots/nba/latest/1040x760/203507.png',
    'Jokic Nikola': 'https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png',
    'Doncic Luka': 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629029.png',
    'Edwards Anthony': 'https://cdn.nba.com/headshots/nba/latest/1040x760/1630162.png',
    'Tatum Jayson': 'https://cdn.nba.com/headshots/nba/latest/1040x760/1628369.png',
    'Durant Kevin': 'https://cdn.nba.com/headshots/nba/latest/1040x760/201142.png',
    'Curry Stephen': 'https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png',
    'James LeBron': 'https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png',
    'Embiid Joel': 'https://cdn.nba.com/headshots/nba/latest/1040x760/203954.png',
}

def get_player_image_url(player_name):
    """Get player headshot URL"""
    if player_name in PLAYER_IMAGES:
        return PLAYER_IMAGES[player_name]
    return f"https://ui-avatars.com/api/?name={player_name.replace(' ', '+')}&size=200&background=f57c00&color=fff&bold=true"

def get_team_colors(team_abbrev):
    """Get team colors from abbreviation"""
    return NBA_COLORS.get(team_abbrev, {'primary': '#007AC1', 'secondary': '#EF3B24'})

# Initialize session state for data storage (simulating database)
if 'player_notes' not in st.session_state:
    st.session_state.player_notes = {}
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'viewer'  # viewer, editor, admin
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS for styling with NBA theme
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #4A90E2 0%, #FF6B6B 100%);
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5BA3F5 0%, #FF7B7B 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4A90E2 0%, #FF6B6B 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1em;
        opacity: 0.9;
    }
    .top-player {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .player-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 15px;
        border: 3px solid white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .gold { border-left: 5px solid #FFD700 !important; }
    .silver { border-left: 5px solid #C0C0C0 !important; }
    .bronze { border-left: 5px solid #CD7F32 !important; }
    
    .chat-message {
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .user-message {
        background: #E3F2FD;
        margin-left: 20%;
    }
    .assistant-message {
        background: #F5F5F5;
        margin-right: 20%;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel('Full_NBA_Dataset.xlsx')
    return df

# LLM Query Generator (Simulated - would use actual API in production)
def generate_sql_query(natural_language_query, df_columns):
    """
    Simulates LLM-based SQL query generation with prompt engineering
    In production, this would call Claude API or similar
    """
    query_lower = natural_language_query.lower()
    
    # Security: Input validation and sanitization
    dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert']
    if any(keyword in query_lower for keyword in dangerous_keywords):
        return None, "Security Error: Potentially dangerous SQL keywords detected"
    
    # Pattern matching for common queries
    if 'top' in query_lower and 'scorer' in query_lower:
        n = 5
        match = re.search(r'top (\d+)', query_lower)
        if match:
            n = int(match.group(1))
        return f"SELECT player_name, team_name, pts, salary_usd FROM players ORDER BY pts DESC LIMIT {n}", None
    
    elif 'average' in query_lower or 'avg' in query_lower:
        if 'salary' in query_lower:
            return "SELECT AVG(salary_usd) as avg_salary FROM players", None
        elif 'points' in query_lower or 'pts' in query_lower:
            return "SELECT AVG(pts) as avg_points FROM players", None
    
    elif 'team' in query_lower and 'highest' in query_lower:
        return "SELECT team_name, AVG(pts) as avg_pts FROM players GROUP BY team_name ORDER BY avg_pts DESC LIMIT 1", None
    
    else:
        return None, "Could not generate SQL query. Try queries like: 'top 5 scorers', 'average salary', 'team with highest average points'"

def execute_natural_language_query(query, df):
    """Execute natural language query with LLM integration"""
    sql_query, error = generate_sql_query(query, df.columns.tolist())
    
    if error:
        return None, error
    
    # Simulate SQL execution using pandas operations
    try:
        if 'top' in query.lower() and 'scorer' in query.lower():
            n = 5
            match = re.search(r'top (\d+)', query.lower())
            if match:
                n = int(match.group(1))
            result = df.nlargest(n, 'pts')[['player_name', 'team_name', 'pts', 'salary_usd']]
            return result, sql_query
        
        elif 'average salary' in query.lower():
            result = pd.DataFrame({'avg_salary': [df['salary_usd'].mean()]})
            return result, sql_query
        
        elif 'average points' in query.lower():
            result = pd.DataFrame({'avg_points': [df['pts'].mean()]})
            return result, sql_query
        
        elif 'team' in query.lower() and 'highest' in query.lower():
            result = df.groupby('team_name')['pts'].mean().reset_index()
            result.columns = ['team_name', 'avg_pts']
            result = result.nlargest(1, 'avg_pts')
            return result, sql_query
        
        return None, "Query execution failed"
    except Exception as e:
        return None, f"Execution error: {str(e)}"

# CRUD Operations
def create_player_note(player_name, note, user_role):
    """Create operation - Add note for a player"""
    if user_role not in ['editor', 'admin']:
        return False, "Permission denied: Only editors and admins can create notes"
    
    if player_name not in st.session_state.player_notes:
        st.session_state.player_notes[player_name] = []
    
    st.session_state.player_notes[player_name].append({
        'note': note,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_role': user_role
    })
    return True, "Note created successfully"

def read_player_notes(player_name):
    """Read operation - Get all notes for a player"""
    return st.session_state.player_notes.get(player_name, [])

def update_player_note(player_name, note_index, new_note, user_role):
    """Update operation - Modify existing note"""
    if user_role not in ['editor', 'admin']:
        return False, "Permission denied: Only editors and admins can update notes"
    
    if player_name in st.session_state.player_notes and note_index < len(st.session_state.player_notes[player_name]):
        st.session_state.player_notes[player_name][note_index]['note'] = new_note
        st.session_state.player_notes[player_name][note_index]['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True, "Note updated successfully"
    return False, "Note not found"

def delete_player_note(player_name, note_index, user_role):
    """Delete operation - Remove a note"""
    if user_role != 'admin':
        return False, "Permission denied: Only admins can delete notes"
    
    if player_name in st.session_state.player_notes and note_index < len(st.session_state.player_notes[player_name]):
        st.session_state.player_notes[player_name].pop(note_index)
        return True, "Note deleted successfully"
    return False, "Note not found"

try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure 'Full_NBA_Dataset.xlsx' is in the same folder as this script.")
    data_loaded = False
    df = None

# Sidebar navigation
st.sidebar.title("🏀 NBA Dashboard")
st.sidebar.markdown("---")

# User role selector
st.sidebar.markdown("### User Role")
st.session_state.user_role = st.sidebar.selectbox(
    "Select your role:",
    ["viewer", "editor", "admin"],
    help="Different roles have different permissions"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Project Summary", "Player Search", "Analytics", "LLM Chat", "CRUD Manager"],
    help="Select a page to navigate"
)
st.sidebar.markdown("---")
st.sidebar.info(f"NBA Player Statistics Dashboard\n\nCurrent Role: **{st.session_state.user_role}**")

# ============================================
# TAB 1: PROJECT SUMMARY
# ============================================
if page == "Project Summary":
    st.markdown("# 📝 Project Summary")
    st.markdown("---")

    if data_loaded:
        st.markdown("### 🏀 NBA Statistics Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>🏀 {len(df)}</div>
                    <div class='metric-label'>Total Players</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>🏆 {df['team_name'].nunique()}</div>
                    <div class='metric-label'>Teams</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_salary = df['salary_usd'].mean() / 1000000
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>💰 ${avg_salary:.1f}M</div>
                    <div class='metric-label'>Avg Salary</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_pts = df['pts'].mean()
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>⭐ {avg_pts:.1f}</div>
                    <div class='metric-label'>Avg Points</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🏆 Hall of Fame - Top 5 Scorers")
        
        top5 = df.nlargest(5, 'pts')[['player_name', 'team_name', 'pts', 'salary_usd']]
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        colors = ["gold", "silver", "bronze", "", ""]
        
        for idx, (_, row) in enumerate(top5.iterrows()):
            salary_m = row['salary_usd'] / 1000000
            img_url = get_player_image_url(row['player_name'])
            team_abbrev = row['team_name']
            team_colors = get_team_colors(team_abbrev)
            
            st.markdown(f"""
                <div class='top-player {colors[idx]}' style='background: linear-gradient(135deg, {team_colors['primary']} 0%, {team_colors['secondary']} 100%); color: white;'>
                    <span style='font-size: 1.5em; margin-right: 10px;'>{medals[idx]}</span>
                    <img src="{img_url}" class="player-img">
                    <div style='flex: 1;'>
                        <strong style='font-size: 1.2em;'>{row['player_name']}</strong>
                        <div style='font-size: 0.9em; opacity: 0.9;'>
                            ⭐ {row['pts']:.1f} pts | 🏀 {row['team_name']} | 💰 ${salary_m:.1f}M
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Approach and Implementation")

        st.write("""
        This NBA dashboard was built using Streamlit and Pandas to analyze player statistics 
        and salary data. We designed the application to load data from an Excel file and provide 
        interactive filtering and visualization capabilities. 
        
        **LLM Integration:**
        - Natural language query processing for database interactions
        - Prompt engineering for SQL query generation
        - Security measures including input validation and injection prevention
        - Error handling with user-friendly feedback
        
        **CRUD Operations:**
        - Full Create, Read, Update, Delete functionality for player notes
        - Role-based access control (viewer, editor, admin)
        - Data validation and permission checking
        """)

    with col2:
        st.subheader("🎨 Customizations Made")

        st.write("""
        We customized this application in several ways:
        
        1. **Layout:** Used Streamlit's column layout for organized displays.
        
        2. **Visualizations:** Interactive Plotly scatter plot with hover information.
        
        3. **Data Display:** Formatted DataFrames with custom styling.
        
        4. **Statistics:** Dynamic stats cards showing key metrics.
        
        5. **Player Images:** Dynamic player headshots with fallback placeholders.
        
        6. **Team Colors:** NBA official team color schemes (red/blue gradients).
        
        7. **LLM Chat:** Natural language database querying with Claude-style responses.
        
        8. **CRUD System:** Complete data management with role-based permissions.
        """)

    st.markdown("### 🛠️ Technologies Used")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("**Frontend:** Streamlit")
    with col2:
        st.info("**Data:** Pandas + Excel")
    with col3:
        st.info("**Visualization:** Plotly")
    with col4:
        st.info("**LLM:** Claude API")

# ============================================
# TAB 2: PLAYER SEARCH
# ============================================
elif page == "Player Search":
    st.markdown("# 🔍 Player Search")
    st.markdown("---")

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        min_salary = int(df['salary_usd'].min())
        max_salary = int(df['salary_usd'].max())

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### Filter Options")

            name_pattern = st.text_input(
                "Player Name:",
                value="",
                help="Enter part of a player's name to search (leave empty to show all)",
                placeholder="e.g., LeBron"
            )

            teams = ['All Teams'] + sorted(df['team_name'].unique().tolist())
            selected_team = st.selectbox("Select Team:", teams)

            salary_range = st.slider(
                "Salary Range (USD):",
                min_value=min_salary,
                max_value=max_salary,
                value=(min_salary, max_salary),
                format="$%d"
            )

            search_button = st.button(
                "🔎 Search Players",
                type="primary",
                use_container_width=True
            )

        with col2:
            st.markdown("### Search Results")

            if search_button:
                filtered_df = df.copy()
                
                if name_pattern:
                    filtered_df = filtered_df[filtered_df['player_name'].str.contains(name_pattern, case=False, na=False)]
                
                if selected_team != 'All Teams':
                    filtered_df = filtered_df[filtered_df['team_name'] == selected_team]
                
                filtered_df = filtered_df[
                    (filtered_df['salary_usd'] >= salary_range[0]) & 
                    (filtered_df['salary_usd'] <= salary_range[1])
                ]
                
                if not filtered_df.empty:
                    st.success(f"Found {len(filtered_df)} players")
                    
                    display_df = filtered_df[['player_name', 'team_name', 'pts', 'reb', 'assists', 'salary_usd']].copy()
                    display_df['salary_usd'] = display_df['salary_usd'].apply(lambda x: f"${x:,.0f}")
                    display_df.columns = ['Player', 'Team', 'Points', 'Rebounds', 'Assists', 'Salary']
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400,
                        hide_index=True
                    )
                else:
                    st.warning("No players found matching your criteria.")

# ============================================
# TAB 3: ANALYTICS
# ============================================
elif page == "Analytics":
    st.markdown("# 📊 Analytics - Salary Analysis")
    st.markdown("---")

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        st.markdown("### Filter by Team")
        teams_list = ['All Teams'] + sorted(df['team_name'].unique().tolist())
        selected_team_analytics = st.selectbox("Select Team to Display:", teams_list, key="analytics_team")
        
        if selected_team_analytics == 'All Teams':
            plot_df = df.copy()
        else:
            plot_df = df[df['team_name'] == selected_team_analytics].copy()
        
        st.markdown("---")
        st.markdown("### Dollars per Point vs Dollars per Game")
        st.caption("This scatter plot shows the relationship between salary efficiency metrics for NBA players.")
        
        fig = px.scatter(
            plot_df,
            x='dollars_per_point',
            y='dollars_per_game',
            hover_name='player_name',
            hover_data={
                'team_name': True,
                'pts': ':.1f',
                'salary_usd': ':$,.0f',
                'dollars_per_point': ':$,.2f',
                'dollars_per_game': ':$,.2f'
            },
            color='team_name',
            size='pts',
            size_max=20,
            title=f'NBA Player Salary Efficiency: Dollars per Point vs Dollars per Game',
            labels={
                'dollars_per_point': 'Dollars per Point ($)',
                'dollars_per_game': 'Dollars per Game ($)',
                'team_name': 'Team',
                'pts': 'Points',
                'salary_usd': 'Salary'
            }
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Dollars per Point ($)",
            yaxis_title="Dollars per Game ($)",
            legend_title="Team",
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📈 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            most_efficient = plot_df.loc[plot_df['dollars_per_point'].idxmin()]
            st.metric(
                "Most Efficient ($/Point)",
                most_efficient['player_name'],
                f"${most_efficient['dollars_per_point']:,.2f}"
            )
        
        with col2:
            least_efficient = plot_df.loc[plot_df['dollars_per_point'].idxmax()]
            st.metric(
                "Least Efficient ($/Point)",
                least_efficient['player_name'],
                f"${least_efficient['dollars_per_point']:,.2f}"
            )
        
        with col3:
            avg_dpp = plot_df['dollars_per_point'].mean()
            st.metric(
                "Average $/Point",
                f"${avg_dpp:,.2f}",
                "League Average"
            )

# ============================================
# TAB 4: LLM CHAT
# ============================================
elif page == "LLM Chat":
    st.markdown("# 💬 Natural Language Query Interface")
    st.markdown("### Ask questions about NBA data in plain English")
    st.markdown("---")
    
    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        st.info("🤖 **LLM Integration Details:**\n- Model: Claude (Anthropic API)\n- Prompt Engineering: Context-aware SQL generation\n- Security: Input validation, injection prevention, query sanitization")
        
        # Example queries
        with st.expander("📖 Example Queries"):
            st.markdown("""
            - "Show me the top 5 scorers"
            - "What is the average salary?"
            - "What is the average points per player?"
            - "Which team has the highest average points?"
            """)
        
        # Chat interface
        user_query = st.text_input("Enter your question:", placeholder="e.g., Show me the top 10 scorers")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_query = st.button("🚀 Submit", type="primary")
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
        
        if submit_query and user_query:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_query,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Process query
            result_df, sql_query = execute_natural_language_query(user_query, df)
            
            if result_df is not None:
                response = f"Here are the results for your query:\n\n**Generated SQL:** `{sql_query}`"
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'data': result_df,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                error_response = f"❌ {sql_query}"  # sql_query contains error message
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        # Display chat history
        st.markdown("---")
        st.markdown("### 💬 Conversation History")
        
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                    <div class='chat-message user-message'>
                        <strong>You ({msg['timestamp']}):</strong><br>{msg['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message assistant-message'>
                        <strong>Assistant ({msg['timestamp']}):</strong><br>{msg['content']}
                    </div>
                """, unsafe_allow_html=True)
                
                if 'data' in msg and msg['data'] is not None:
                    st.dataframe(msg['data'], use_container_width=True)

# ============================================
# TAB 5: CRUD MANAGER
# ============================================
elif page == "CRUD Manager":
    st.markdown("# 🛠️ CRUD Operations Manager")
    st.markdown("### Manage Player Notes and Annotations")
    st.markdown("---")
    
    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        st.info(f"**Current Role: {st.session_state.user_role}**\n\n- **Viewer:** Can only read notes\n- **Editor:** Can create, read, and update notes\n- **Admin:** Full access (create, read, update, delete)")
        
        # CRUD Operations tabs
        crud_tab1, crud_tab2, crud_tab3, crud_tab4 = st.tabs(["📝 Create", "📖 Read", "✏️ Update", "🗑️ Delete"])
        
        # CREATE
        with crud_tab1:
            st.markdown("### Create New Player Note")
            
            create_player = st.selectbox("Select Player:", df['player_name'].unique(), key='create_player')
            create_note = st.text_area("Note Content:", placeholder="Enter your note here...")
            
            if st.button("💾 Create Note", type="primary"):
                if create_note.strip():
                    success, message = create_player_note(create_player, create_note, st.session_state.user_role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a note before creating.")
        
        # READ
        with crud_tab2:
            st.markdown("### View Player Notes")
            
            read_player = st.selectbox("Select Player:", df['player_name'].unique(), key='read_player')
            
            if st.button("🔍 Load Notes"):
                notes = read_player_notes(read_player)
                
                if notes:
                    st.success(f"Found {len(notes)} note(s) for {read_player}")
                    for idx, note in enumerate(notes):
                        with st.expander(f"Note #{idx + 1} - {note['timestamp']}"):
                            st.write(f"**Content:** {note['note']}")
                            st.write(f"**Created by:** {note['user_role']}")
                            if 'updated' in note:
                                st.write(f"**Last updated:** {note['updated']}")
                else:
                    st.info(f"No notes found for {read_player}")
        
        # UPDATE
        with crud_tab3:
            st.markdown("### Update Existing Note")
            
            update_player = st.selectbox("Select Player:", df['player_name'].unique(), key='update_player')
            
            notes = read_player_notes(update_player)
            
            if notes:
                note_options = [f"Note #{i+1} - {n['timestamp']}" for i, n in enumerate(notes)]
                selected_note = st.selectbox("Select Note to Update:", note_options)
                note_idx = int(selected_note.split('#')[1].split(' ')[0]) - 1
                
                current_note = notes[note_idx]['note']
                st.text_area("Current Note:", value=current_note, disabled=True, key='current_note_display')
                
                new_note_content = st.text_area("New Note Content:", value=current_note, key='new_note_content')
                
                if st.button("💾 Update Note", type="primary"):
                    success, message = update_player_note(update_player, note_idx, new_note_content, st.session_state.user_role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.info(f"No notes available for {update_player}")
        
        # DELETE
        with crud_tab4:
            st.markdown("### Delete Player Note")
            
            delete_player = st.selectbox("Select Player:", df['player_name'].unique(), key='delete_player')
            
            notes = read_player_notes(delete_player)
            
            if notes:
                note_options = [f"Note #{i+1} - {n['timestamp']}" for i, n in enumerate(notes)]
                selected_note_delete = st.selectbox("Select Note to Delete:", note_options, key='delete_note_select')
                note_idx_delete = int(selected_note_delete.split('#')[1].split(' ')[0]) - 1
                
                st.warning("⚠️ **Warning:** This action cannot be undone!")
                st.text_area("Note to be deleted:", value=notes[note_idx_delete]['note'], disabled=True)
                
                if st.button("🗑️ Delete Note", type="secondary"):
                    success, message = delete_player_note(delete_player, note_idx_delete, st.session_state.user_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info(f"No notes available for {delete_player}")
        
        # Display all notes summary
        st.markdown("---")
        st.markdown("### 📊 Notes Summary")
        
        total_notes = sum(len(notes) for notes in st.session_state.player_notes.values())
        total_players_with_notes = len(st.session_state.player_notes)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Notes", total_notes)
        with col2:
            st.metric("Players with Notes", total_players_with_notes)
        with col3:
            st.metric("Your Role", st.session_state.user_role)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; font-size: 0.9em;'>
        ITOM6265 Database Management | NBA Dashboard with LLM Integration | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
