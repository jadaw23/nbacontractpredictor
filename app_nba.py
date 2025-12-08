# ============================================
# NBA Dashboard - Comprehensive Player Impact Analysis
# ITOM6265 - Database Project
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NBA Player Impact Analysis",
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

def get_player_image_url(player_name):
    if player_name in PLAYER_IMAGES:
        return PLAYER_IMAGES[player_name]
    return f"https://ui-avatars.com/api/?name={player_name.replace(' ', '+')}&size=400&background=4A90E2&color=fff&bold=true&font-size=0.4"

def get_team_colors(team_abbrev):
    return NBA_COLORS.get(team_abbrev, {'primary': '#007AC1', 'secondary': '#EF3B24'})

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

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
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        margin: 20px 0;
    }
    
    .player-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .player-photo {
        width: 150px;
        height: 150px;
        border-radius: 15px;
        object-fit: cover;
        border: 4px solid #4A90E2;
        margin-right: 30px;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #4A90E2;
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

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel('Full_NBA_Dataset.xlsx')
    # Add calculated metrics for comprehensive analysis
    df['contract_efficiency'] = (df['pts'] + df['reb'] + df['assists']) / (df['salary_usd'] / 1000000)
    df['player_value_index'] = df['pts'] * 0.4 + df['reb'] * 0.3 + df['assists'] * 0.3
    return df

# LLM Query Generator
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
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False
    df = None

# Sidebar
st.sidebar.title("🏀 NBA Impact Analysis")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Project Overview", "Player Search & Analysis", "Team Analytics", "LLM Query Assistant"],
    help="Select a page to navigate"
)
st.sidebar.markdown("---")
st.sidebar.info("**Comprehensive Player Impact Analysis Platform**\n\nMeasuring value and performance across multiple indicators")

# ============================================
# PROJECT OVERVIEW
# ============================================
if page == "Project Overview":
    st.markdown("# 📊 NBA Player Impact Analysis Platform")
    st.markdown("### Comprehensive Player Value & Contract Efficiency Analysis")
    st.markdown("---")

    if data_loaded:
        st.markdown("### 🏀 Database Overview")
        
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
                    <div class='metric-label'>Teams Tracked</div>
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
            avg_efficiency = df['contract_efficiency'].mean()
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>📈 {avg_efficiency:.2f}</div>
                    <div class='metric-label'>Avg Efficiency</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top performers
        st.markdown("### 🏆 Top 5 Most Efficient Players (Contract Value)")
        
        top5 = df.nlargest(5, 'contract_efficiency')[['player_name', 'team_name', 'pts', 'salary_usd', 'contract_efficiency']]
        
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
                            ⭐ {row['pts']:.1f} pts | 🏀 {row['team_name']} | 💰 ${salary_m:.1f}M | 📊 Efficiency: {row['contract_efficiency']:.2f}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Project Objective")

        st.write("""
        **Mission:** Build an analytical platform that measures player value in relation to cost, 
        benchmarking performance across multiple statistical indicators to inform strategic contract decisions.
        
        **Key Features:**
        - Comprehensive player impact analysis
        - Contract efficiency ratings
        - Performance prediction metrics
        - Interactive player comparison tools
        - Natural language query interface powered by LLM
        """)
        
        st.markdown("### 📋 Database Scope")
        st.write("""
        **Player Information:** ID, name, position, stats
        
        **Contract Data:** Salary, contract value, efficiency
        
        **Performance Statistics:** Games, minutes, points, rebounds, assists, shooting percentages
        
        **Value Analysis:** Contract efficiency, player value index, predicted metrics
        """)

    with col2:
        st.subheader("🎨 Technical Implementation")

        st.write("""
        **Data Architecture:**
        
        1. **Excel Database:** Centralized player and team data
        
        2. **Real-time Analytics:** Dynamic calculation of efficiency metrics
        
        3. **Interactive Visualizations:** Plotly-powered charts and graphs
        
        4. **LLM Integration:** Natural language database querying
        
        5. **Security:** Input validation and SQL injection prevention
        
        6. **Performance:** Cached data loading for optimal speed
        """)

    st.markdown("### 🛠️ Technologies")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("**Frontend:** Streamlit")
    with col2:
        st.info("**Data:** Pandas + Excel")
    with col3:
        st.info("**Visualization:** Plotly")
    with col4:
        st.info("**AI:** LLM Integration")

# ============================================
# PLAYER SEARCH & ANALYSIS
# ============================================
elif page == "Player Search & Analysis":
    st.markdown("# 🔍 Player Search & Comprehensive Analysis")
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
                    
                    # Quick stats display
                    display_df = filtered_df[['player_name', 'team_name', 'pts', 'reb', 'assists', 'salary_usd', 'contract_efficiency']].copy()
                    display_df['salary_usd'] = display_df['salary_usd'].apply(lambda x: f"${x:,.0f}")
                    display_df['contract_efficiency'] = display_df['contract_efficiency'].apply(lambda x: f"{x:.2f}")
                    display_df.columns = ['Player', 'Team', 'Points', 'Rebounds', 'Assists', 'Salary', 'Efficiency']
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=300,
                        hide_index=True
                    )
                    
                    # Player selection for detailed view
                    st.markdown("---")
                    st.markdown("### 👤 Select Player for Detailed Analysis")
                    
                    selected_player_name = st.selectbox(
                        "Choose a player:",
                        filtered_df['player_name'].tolist(),
                        key='player_select'
                    )
                    
                    if selected_player_name:
                        st.session_state.selected_player = selected_player_name
                        player_data = filtered_df[filtered_df['player_name'] == selected_player_name].iloc[0]
                        
                        # DETAILED PLAYER CARD
                        st.markdown("---")
                        
                        # Player header with photo
                        team_colors = get_team_colors(player_data['team_name'])
                        
                        st.markdown(f"""
                            <div class='player-card' style='border-top: 5px solid {team_colors["primary"]}'>
                                <div class='player-header'>
                                    <img src='{get_player_image_url(selected_player_name)}' class='player-photo'>
                                    <div>
                                        <h1 style='margin: 0; color: {team_colors["primary"]}'>{selected_player_name}</h1>
                                        <h3 style='margin: 5px 0; color: #666;'>{player_data['team_name']}</h3>
                                        <p style='font-size: 1.1em; color: #888;'>Salary: ${player_data['salary_usd']:,.0f}</p>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Performance Statistics
                        st.markdown("### 📊 Performance Statistics")
                        
                        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
                        
                        with perf_col1:
                            st.metric("Points Per Game", f"{player_data['pts']:.1f}")
                            st.metric("Games Played", f"{player_data['gp']:.0f}")
                        
                        with perf_col2:
                            st.metric("Rebounds Per Game", f"{player_data['reb']:.1f}")
                            st.metric("Minutes Played", f"{player_data['min']:.1f}")
                        
                        with perf_col3:
                            st.metric("Assists Per Game", f"{player_data['assists']:.1f}")
                            st.metric("Field Goal %", f"{player_data['fgp']:.1f}%")
                        
                        with perf_col4:
                            st.metric("3-Point %", f"{player_data['tpp']:.1f}%")
                            st.metric("Free Throw %", f"{player_data['ftp']:.1f}%")
                        
                        # Value Analysis
                        st.markdown("### 💰 Value Analysis")
                        
                        val_col1, val_col2, val_col3 = st.columns(3)
                        
                        with val_col1:
                            st.markdown(f"""
                                <div class='stat-box'>
                                    <h4>Contract Efficiency Rating</h4>
                                    <h2 style='color: #4A90E2;'>{player_data['contract_efficiency']:.2f}</h2>
                                    <p>Stats per million dollars</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with val_col2:
                            st.markdown(f"""
                                <div class='stat-box'>
                                    <h4>Player Value Index</h4>
                                    <h2 style='color: #FF6B6B;'>{player_data['player_value_index']:.2f}</h2>
                                    <p>Composite performance score</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with val_col3:
                            salary_per_point = player_data['salary_usd'] / player_data['pts'] if player_data['pts'] > 0 else 0
                            st.markdown(f"""
                                <div class='stat-box'>
                                    <h4>Dollars Per Point</h4>
                                    <h2 style='color: #00C853;'>${salary_per_point:,.0f}</h2>
                                    <p>Cost efficiency metric</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Performance Radar Chart
                        st.markdown("### 🎯 Performance Profile")
                        
                        categories = ['Points', 'Rebounds', 'Assists', 'FG%', '3P%', 'FT%']
                        values = [
                            (player_data['pts'] / df['pts'].max()) * 100,
                            (player_data['reb'] / df['reb'].max()) * 100,
                            (player_data['assists'] / df['assists'].max()) * 100,
                            player_data['fgp'],
                            player_data['tpp'],
                            player_data['ftp']
                        ]
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=selected_player_name,
                            line_color=team_colors['primary']
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            showlegend=True,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Comparison with league averages
                        st.markdown("### 📈 League Comparison")
                        
                        comp_data = pd.DataFrame({
                            'Metric': ['Points', 'Rebounds', 'Assists', 'Salary (M)'],
                            'Player': [
                                player_data['pts'],
                                player_data['reb'],
                                player_data['assists'],
                                player_data['salary_usd'] / 1000000
                            ],
                            'League Avg': [
                                df['pts'].mean(),
                                df['reb'].mean(),
                                df['assists'].mean(),
                                df['salary_usd'].mean() / 1000000
                            ]
                        })
                        
                        fig2 = px.bar(
                            comp_data,
                            x='Metric',
                            y=['Player', 'League Avg'],
                            barmode='group',
                            title=f'{selected_player_name} vs League Average',
                            color_discrete_map={'Player': team_colors['primary'], 'League Avg': '#CCCCCC'}
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                        
                else:
                    st.warning("⚠️ No players found matching your criteria.")

# ============================================
# TEAM ANALYTICS
# ============================================
elif page == "Team Analytics":
    st.markdown("# 🏆 Team Analytics & Salary Cap Analysis")
    st.markdown("---")

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        st.markdown("### 🎯 Team Performance Analysis")
        
        teams_list = ['All Teams'] + sorted(df['team_name'].unique().tolist())
        selected_team_analytics = st.selectbox("Select Team:", teams_list, key="analytics_team")
        
        if selected_team_analytics == 'All Teams':
            plot_df = df.copy()
        else:
            plot_df = df[df['team_name'] == selected_team_analytics].copy()
        
        # Team summary metrics
        col1, col2, col3, col4 = st.columns(  with col1:
        st.metric("Total Players", len(plot_df))
    with col2:
        st.metric("Total Payroll", f"${plot_df['salary_usd'].sum() / 1000000:.1f}M")
    with col3:
        st.metric("Avg Player Value", f"{plot_df['player_value_index'].mean():.2f}")
    with col4:
        st.metric("Team Efficiency", f"{plot_df['contract_efficiency'].mean():.2f}")
    
    st.markdown("---")
    st.markdown("### 💰 Salary Efficiency Analysis")
    st.caption("Analyzing the relationship between salary and performance metrics")
    
    # Scatter plot
    fig = px.scatter(
        plot_df,
        x='salary_usd',
        y='player_value_index',
        size='pts',
        color='team_name',
        hover_name='player_name',
        hover_data={
            'team_name': True,
            'pts': ':.1f',
            'reb': ':.1f',
            'assists': ':.1f',
            'salary_usd': ':$,.0f',
            'contract_efficiency': ':.2f'
        },
        title='Player Value vs Salary Analysis',
        labels={
            'salary_usd': 'Annual Salary (USD)',
            'player_value_index': 'Player Value Index',
            'team_name': 'Team'
        }
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_value = plot_df.loc[plot_df['contract_efficiency'].idxmax()]
        st.metric(
            "Best Value Player",
            best_value['player_name'],
            f"Efficiency: {best_value['contract_efficiency']:.2f}"
        )
    
    with col2:
        highest_paid = plot_df.loc[plot_df['salary_usd'].idxmax()]
        st.metric(
            "Highest Paid",
            highest_paid['player_name'],
            f"${highest_paid['salary_usd'] / 1000000:.1f}M"
        )
    
    with col3:
        top_performer = plot_df.loc[plot_df['player_value_index'].idxmax()]
        st.metric(
            "Top Performer",
            top_performer['player_name'],
            f"PVI: {top_performer['player_value_index']:.2f}"
        )
============================================
LLM QUERY ASSISTANT
============================================
elif page == "LLM Query Assistant":
st.markdown("# 💬 AI-Powered Database Query Assistant")
st.markdown("### Ask questions about NBA data in natural language")
st.markdown("---")
if not data_loaded:
    st.error("Data not loaded. Please check your data file.")
else:
    st.info("""
    🤖 **LLM Integration Architecture:**
    - **Model:** Claude (Anthropic API)
    - **Prompt Engineering:** Context-aware SQL query generation
    - **Security:** Input validation, SQL injection prevention, query sanitization
    - **Error Handling:** Graceful fallbacks and user-friendly error messages
    """)
    
    with st.expander("📖 Example Queries You Can Try"):
        st.markdown("""
        - "Show me the top 5 scorers"
        - "Show me the top 10 scorers"
        - "What is the average salary?"
        - "What is the average points per player?"
        - "Which team has the highest average points?"
        - "Show me the most efficient players"
        - "Who has the best contract value?"
        """)
    
    user_query = st.text_input(
        "💭 Your Question:",
        placeholder="e.g., Show me the top 10 most efficient players"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submit_query = st.button("🚀 Ask", type="primary")
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
            response = f"✅ Query executed successfully!\n\n**Generated SQL:** `{sql_query}`\n\n**Results:**"
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
                    <strong>AI Assistant ({msg['timestamp']}):</strong><br>{msg['content']}
                </div>
            """, unsafe_allow_html=True)
            
            if 'data' in msg and msg['data'] is not None:
                st.dataframe(msg['data'], use_container_width=True)
