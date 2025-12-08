# ============================================
# NBA Dashboard - Streamlit Application with LLM Integration
# ITOM6265 - Database Project
# ============================================

import inspect
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime

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

PLAYER_ID_MAP = {}


def get_player_image_url(player_name, player_id=None):
    if player_name in PLAYER_IMAGES:
        return PLAYER_IMAGES[player_name]

    resolved_id = player_id
    if resolved_id is None and PLAYER_ID_MAP:
        resolved_id = PLAYER_ID_MAP.get(player_name)

    if resolved_id is not None:
        return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{int(resolved_id)}.png"

    return f"https://ui-avatars.com/api/?name={player_name.replace(' ', '+')}&size=400&background=4A90E2&color=fff&bold=true&font-size=0.4"

def get_team_colors(team_abbrev):
    return NBA_COLORS.get(team_abbrev, {'primary': '#007AC1', 'secondary': '#EF3B24'})

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None
if 'plot_click_player' not in st.session_state:
    st.session_state.plot_click_player = None

# Custom CSS
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
    
    .player-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        margin: 20px 0;
        border: 2px solid #4A90E2;
    }
    
    .player-header {
        display: flex;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .player-photo-large {
        width: 180px;
        height: 180px;
        border-radius: 15px;
        object-fit: cover;
        border: 5px solid #4A90E2;
        margin-right: 30px;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #e3f2fd 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4A90E2;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
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

@st.cache_data
def load_data():
    df = pd.read_excel('Full_NBA_Dataset.xlsx')
    df['contract_efficiency'] = (df['pts'] + df['reb'] + df['assists']) / (df['salary_usd'] / 1000000)
    df['player_value_index'] = df['pts'] * 0.4 + df['reb'] * 0.3 + df['assists'] * 0.3
    return df


def format_player_metric(player_data, key, fmt="{:.1f}", default="N/A"):
    """Format a player's metric safely, returning a friendly fallback when missing."""
    if key in player_data.index and pd.notnull(player_data[key]):
        try:
            return fmt.format(player_data[key])
        except Exception:
            pass
    return default


def get_numeric_stat(player_data, key, default=0):
    """Safely fetch a numeric stat for visualizations without raising KeyError."""
    try:
        value = player_data.get(key, default)
        if pd.notnull(value):
            return value
    except Exception:
        pass
    return default

def generate_sql_query(natural_language_query, df_columns):
    query_lower = natural_language_query.lower()
    
    dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert']
    if any(keyword in query_lower for keyword in dangerous_keywords):
        return None, "Security Error: Potentially dangerous SQL keywords detected"
    
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
    
    elif 'efficient' in query_lower or 'value' in query_lower:
        return "SELECT player_name, contract_efficiency FROM players ORDER BY contract_efficiency DESC LIMIT 10", None
    
    else:
        return None, "Could not generate SQL query. Try: 'top 5 scorers', 'average salary', 'most efficient players'"

def execute_natural_language_query(query, df):
    sql_query, error = generate_sql_query(query, df.columns.tolist())
    
    if error:
        return None, error
    
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
        
        elif 'efficient' in query.lower() or 'value' in query.lower():
            result = df.nlargest(10, 'contract_efficiency')[['player_name', 'team_name', 'contract_efficiency', 'salary_usd']]
            return result, sql_query
        
        elif 'team' in query.lower() and 'highest' in query.lower():
            result = df.groupby('team_name')['pts'].mean().reset_index()
            result.columns = ['team_name', 'avg_pts']
            result = result.nlargest(1, 'avg_pts')
            return result, sql_query
        
        return None, "Query execution failed"
    except Exception as e:
        return None, f"Execution error: {str(e)}"

try:
    df = load_data()
    PLAYER_ID_MAP = dict(zip(df['player_name'], df['player_id']))
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False
    df = None

st.sidebar.title("🏀 NBA Impact Analysis")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Project Summary", "Player Search", "Analytics", "LLM Chat"],
    help="Select a page to navigate"
)
st.sidebar.markdown("---")
st.sidebar.info("**NBA Player Impact Analysis**\n\nMeasuring value and performance")

# ============================================
# PROJECT SUMMARY
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
        
        top5 = df.nlargest(5, 'pts')[['player_name', 'player_id', 'team_name', 'pts', 'salary_usd']]
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        colors = ["gold", "silver", "bronze", "", ""]
        
        for idx, (_, row) in enumerate(top5.iterrows()):
            salary_m = row['salary_usd'] / 1000000
            img_url = get_player_image_url(row['player_name'], row['player_id'])
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
        interactive filtering and visualization capabilities. We used Plotly Express for creating the 
        scatter plot visualization which allows for interactive exploration of the relationship 
        between salary per point and salary per game. The dashboard demonstrates CRUD-like read operations and analytics visualizations as required.
        """)

    with col2:
        st.subheader("🎨 Customizations Made")

        st.write("""
        We customized this application in several ways:
        
        1. **Layout:** Used Streamlit's column layout for organized displays.
        
        2. **Visualizations:** Interactive Plotly scatter plot with hover information.
        
        3. **Data Display:** Formatted DataFrames with custom styling.
        
        4. **Statistics:** Dynamic stats cards showing key metrics.
        """)

    st.markdown("### 🛠️ Technologies Used")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Frontend:** Streamlit")
    with col2:
        st.info("**Data:** Pandas + Excel")
    with col3:
        st.info("**Visualization:** Plotly")

# ============================================
# PLAYER SEARCH
# ============================================
elif page == "Player Search":
    st.markdown("# 🔍 Player Search & Analysis")
    st.markdown("---")

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### 🎯 Search Filters")

            name_pattern = st.text_input(
                "Player Name:",
                value="",
                help="Search for a player",
                placeholder="e.g., LeBron"
            )

            teams = ['All Teams'] + sorted(df['team_name'].unique().tolist())
            selected_team = st.selectbox("Team:", teams)

            min_salary = int(df['salary_usd'].min())
            max_salary = int(df['salary_usd'].max())
            
            salary_range = st.slider(
                "Salary Range (USD):",
                min_value=min_salary,
                max_value=max_salary,
                value=(min_salary, max_salary),
                format="$%d"
            )
            
            min_pts = st.number_input("Minimum Points:", min_value=0.0, value=0.0, step=1.0)

            search_button = st.button(
                "🔎 Search Players",
                type="primary",
                use_container_width=True
            )

        with col2:
            st.markdown("### 📊 Search Results")

            if search_button:
                filtered_df = df.copy()
                
                if name_pattern:
                    filtered_df = filtered_df[filtered_df['player_name'].str.contains(name_pattern, case=False, na=False)]
                
                if selected_team != 'All Teams':
                    filtered_df = filtered_df[filtered_df['team_name'] == selected_team]
                
                filtered_df = filtered_df[
                    (filtered_df['salary_usd'] >= salary_range[0]) & 
                    (filtered_df['salary_usd'] <= salary_range[1]) &
                    (filtered_df['pts'] >= min_pts)
                ]
                
                if not filtered_df.empty:
                    st.success(f"✅ Found {len(filtered_df)} players")
                    
                    # Display results table
                    display_df = filtered_df[
                        ['player_name', 'player_id', 'team_name', 'pts', 'reb', 'assists', 'salary_usd']
                    ].copy()
                    display_df['Headshot'] = display_df.apply(
                        lambda row: get_player_image_url(row['player_name'], row['player_id']), axis=1
                    )
                    display_df['salary_usd'] = display_df['salary_usd'].apply(lambda x: f"${x:,.0f}")
                    display_df = display_df[
                        ['Headshot', 'player_name', 'team_name', 'pts', 'reb', 'assists', 'salary_usd']
                    ]
                    display_df.columns = ['Headshot', 'Player', 'Team', 'Points', 'Rebounds', 'Assists', 'Salary']

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=300,
                        hide_index=True,
                        column_config={
                            'Headshot': st.column_config.ImageColumn("Headshot", width=80),
                        },
                    )
                    # Interactive scatter chart to click players instead of dropdown selection
                    st.markdown("---")
                    st.markdown("### 🖱️ Click a Player on the Chart")
                    st.caption("Use the scatter plot to select a player directly from the filtered results.")

                    search_fig = px.scatter(
                        filtered_df,
                        x='dollars_per_point',
                        y='pts',
                        color='team_name',
                        hover_name='player_name',
                        hover_data={
                            'team_name': True,
                            'pts': ':.1f',
                            'salary_usd': ':$,.0f',
                            'dollars_per_point': ':$,.2f'
                        },
                        size='pts',
                        size_max=18,
                        labels={
                            'dollars_per_point': 'Dollars per Point ($)',
                            'pts': 'Points per Game',
                            'team_name': 'Team'
                        },
                        title='Click a player to view quick info'
                    )

                    search_fig.update_traces(customdata=filtered_df['player_name'])
                    search_fig.update_layout(height=500)

                    def supports_plotly_click():
                        try:
                            return 'on_click' in inspect.signature(st.plotly_chart).parameters
                        except Exception:
                            return False

                    def on_player_click(trace, points, state):
                        if points.point_inds:
                            idx = points.point_inds[0]
                            st.session_state.plot_click_player = trace.customdata[idx]

                    plot_kwargs = {"use_container_width": True}
                    if supports_plotly_click():
                        plot_kwargs["on_click"] = on_player_click

                    st.plotly_chart(search_fig, **plot_kwargs)

                    clicked_player = st.session_state.plot_click_player
                    if clicked_player and clicked_player in filtered_df['player_name'].values:
                        player_data = filtered_df[filtered_df['player_name'] == clicked_player].iloc[0]
                        team_colors = get_team_colors(player_data['team_name'])

                        st.markdown(f"""
                            <div class='player-card'>
                                <div class='player-header'>
                                    <img src='{get_player_image_url(clicked_player, player_data['player_id'])}' class='player-photo-large'>
                                    <div>
                                        <h1 style='margin: 0; color: {team_colors["primary"]};'>{clicked_player}</h1>
                                        <h2 style='margin: 10px 0; color: #666;'>{player_data['team_name']}</h2>
                                        <h3 style='color: #4A90E2; margin: 5px 0;'>Salary: ${player_data['salary_usd']:,.0f}</h3>
                                        <p style='margin: 0; color: #555;'>Points: {player_data['pts']:.1f} • Rebounds: {player_data['reb']:.1f} • Assists: {player_data['assists']:.1f}</p>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                else:
                    st.warning("⚠️ No players found matching your criteria.")

# ============================================
# ANALYTICS
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


# ============================================
# LLM CHAT
# ============================================
if page == "LLM Chat":
    st.markdown("# 💬 Natural Language Query Interface")
    st.markdown("### Ask questions about NBA data in plain English")
    st.markdown("---")
    
    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        st.info(
            "🤖 **LLM Integration Details:**\n"
            "- Model: Claude (Anthropic API)\n"
            "- Prompt Engineering: Context-aware SQL generation\n"
            "- Security: Input validation, injection prevention, query sanitization"
        )
        
        with st.expander("📖 Example Queries"):
            st.markdown("""
            - "Show me the top 5 scorers"
            - "What is the average salary?"
            - "What is the average points per player?"
            - "Which team has the highest average points?"
            """)
        
        user_query = st.text_input("Enter your question:", placeholder="e.g., Show me the top 10 scorers")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_query = st.button("🚀 Submit", type="primary")
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
        
        if submit_query and user_query:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_query,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
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
                error_response = f"❌ {sql_query}"
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
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
                    result_df = msg['data']
                    st.dataframe(result_df, use_container_width=True)

                    # 🏀 Show player headshots if the result has player_name
                    if 'player_name' in result_df.columns:
                        players = (
                            result_df['player_name']
                            .dropna()
                            .astype(str)
                            .unique()[:3]  # show first 3 players
                        )

                        if len(players) > 0:
                            st.markdown("#### 🏀 Players in this result")
                            cols = st.columns(len(players))
                            for col, name in zip(cols, players):
                                player_id = None
                                if 'player_id' in result_df.columns:
                                    matching_ids = result_df.loc[
                                        result_df['player_name'] == name, 'player_id'
                                    ]
                                    if not matching_ids.empty:
                                        player_id = matching_ids.iloc[0]

                                if player_id is None:
                                    player_id = PLAYER_ID_MAP.get(name)

                                with col:
                                    st.image(
                                        get_player_image_url(name, player_id),
                                        caption=name,
                                        use_column_width=True
                                    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: right; color: #7f8c8d; font-size: 0.9em; padding-right: 20px;'>
        ITOM6265 Database Management | NBA Dashboard with LLM Integration | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
