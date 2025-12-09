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


def supports_plotly_click():
    try:
        return 'on_click' in inspect.signature(st.plotly_chart).parameters
    except Exception:
        return False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None
if 'plot_click_player' not in st.session_state:
    st.session_state.plot_click_player = None
if 'analytics_click_player' not in st.session_state:
    st.session_state.analytics_click_player = None

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

def ensure_salary_efficiency_columns(df):
    """Guarantee salary efficiency metrics exist and are numeric for visualizations."""
    numeric_cols = ['salary_usd', 'pts', 'gp']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'dollars_per_point' in df.columns:
        df['dollars_per_point'] = pd.to_numeric(df['dollars_per_point'], errors='coerce')
    base_points = df['pts'].replace({0: pd.NA}) if 'pts' in df.columns else pd.NA
    df['dollars_per_point'] = df.get('dollars_per_point', pd.NA).combine_first(
        df.get('salary_usd', pd.NA) / base_points
    )

    if 'dollars_per_game' in df.columns:
        df['dollars_per_game'] = pd.to_numeric(df['dollars_per_game'], errors='coerce')
    base_games = df['gp'].replace({0: pd.NA}) if 'gp' in df.columns else pd.NA
    df['dollars_per_game'] = df.get('dollars_per_game', pd.NA).combine_first(
        df.get('salary_usd', pd.NA) / base_games
    )

    df['dollars_per_point'] = df['dollars_per_point'].fillna(0)
    df['dollars_per_game'] = df['dollars_per_game'].fillna(0)

    return df


def calculate_contract_efficiency(df):
    """Derive the Contract Efficiency Score (CES) with normalized production and value tiers."""
    work_df = df.copy()

    numeric_cols = ['salary_usd', 'pts', 'reb', 'assists']
    for col in numeric_cols:
        if col in work_df.columns:
            work_df[col] = pd.to_numeric(work_df[col], errors='coerce').fillna(0)
        else:
            work_df[col] = 0

    stat_max = {
        'pts': max(work_df['pts'].max(), 1),
        'reb': max(work_df['reb'].max(), 1),
        'assists': max(work_df['assists'].max(), 1),
    }

    work_df['norm_pts'] = work_df['pts'] / stat_max['pts']
    work_df['norm_reb'] = work_df['reb'] / stat_max['reb']
    work_df['norm_assists'] = work_df['assists'] / stat_max['assists']

    salary_millions = work_df['salary_usd'] / 1_000_000
    salary_millions = salary_millions.replace({0: pd.NA})

    normalized_performance = (
        (work_df['norm_pts'] * 0.6)
        + (work_df['norm_reb'] * 0.25)
        + (work_df['norm_assists'] * 0.15)
    )
    work_df['contract_efficiency_score'] = (normalized_performance / salary_millions).fillna(0)

    percentiles = work_df['contract_efficiency_score'].quantile([0.4, 0.75]).to_list()
    lower_cutoff, upper_cutoff = percentiles if len(percentiles) == 2 else (0, 0)

    def value_tier(score):
        if score >= upper_cutoff:
            return "Underpaid"
        if score >= lower_cutoff:
            return "Fair"
        return "Overpaid"

    work_df['contract_value_label'] = work_df['contract_efficiency_score'].apply(value_tier)
    return work_df


@st.cache_data
def load_data():
    df = pd.read_excel('Full_NBA_Dataset.xlsx')
    df = ensure_salary_efficiency_columns(df)
    return df


def get_contract_records(base_df):
    """Return session-scoped contract data with CES columns applied."""
    if 'contract_records' not in st.session_state:
        st.session_state.contract_records = calculate_contract_efficiency(base_df)
    return st.session_state.contract_records


def persist_contract_records(updated_df):
    """Recalculate CES and persist updated contract records back into session state."""
    st.session_state.contract_records = calculate_contract_efficiency(updated_df)
    return st.session_state.contract_records


def simulate_ces_for_salary(player_name, new_salary, current_df):
    """Simulate a CES and value label for a player after changing their salary."""
    work_df = current_df.copy()
    player_mask = work_df['player_name'] == player_name
    if not player_mask.any():
        return None

    work_df.loc[player_mask, 'salary_usd'] = new_salary
    recalculated_df = calculate_contract_efficiency(work_df)
    return recalculated_df.loc[player_mask].iloc[0]


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
    [
        "Project Summary",
        "Player Search",
        "Analytics",
        "Contract Efficiency Score",
        "LLM Chat",
    ],
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

        st.markdown("### 📊 Quick Player Insights")

        top_ppg = df.nlargest(10, 'pts')[['player_name', 'pts', 'team_name']]
        top_salary = df.nlargest(10, 'salary_usd')[['player_name', 'salary_usd', 'team_name']]

        col_ppg, col_salary = st.columns(2)

        with col_ppg:
            ppg_fig = px.bar(
                top_ppg,
                x='player_name',
                y='pts',
                color='team_name',
                title='Top 10 Scorers (PPG)',
                labels={'player_name': 'Player', 'pts': 'Points per Game', 'team_name': 'Team'},
                text='pts',
            )
            ppg_fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            ppg_fig.update_layout(xaxis_tickangle=-45, height=400, showlegend=False, uniformtext_minsize=8)
            st.plotly_chart(ppg_fig, use_container_width=True)

        with col_salary:
            salary_fig = px.bar(
                top_salary,
                x='player_name',
                y='salary_usd',
                color='team_name',
                title='Top 10 Highest Salaries',
                labels={'player_name': 'Player', 'salary_usd': 'Salary (USD)', 'team_name': 'Team'},
                text='salary_usd',
            )
            salary_fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            salary_fig.update_layout(xaxis_tickangle=-45, height=400, yaxis_tickformat='$,', showlegend=False, uniformtext_minsize=8)
            st.plotly_chart(salary_fig, use_container_width=True)

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

        if (
            st.session_state.analytics_click_player
            and st.session_state.analytics_click_player not in plot_df['player_name'].values
        ):
            st.session_state.analytics_click_player = None

        st.markdown("---")
        st.markdown("### Dollars per Point vs Dollars per Game")
        st.caption("This scatter plot shows the relationship between salary efficiency metrics for NBA players.")

        fig = px.scatter(
            plot_df,
            x='dollars_per_point',
            y='dollars_per_game',
            custom_data=['player_name'],
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

        def on_analytics_click(trace, points, state):
            if points.point_inds:
                idx = points.point_inds[0]
                st.session_state.analytics_click_player = trace.customdata[idx][0]

        plot_kwargs = {"use_container_width": True}
        if supports_plotly_click():
            plot_kwargs["on_click"] = on_analytics_click

        st.plotly_chart(fig, **plot_kwargs)

        clicked_player = st.session_state.analytics_click_player
        if clicked_player and clicked_player in plot_df['player_name'].values:
            player_row = plot_df[plot_df['player_name'] == clicked_player].iloc[0]
            team_colors = get_team_colors(player_row['team_name'])

            st.markdown("#### Selected Player")
            st.markdown(f"""
                <div class='player-card'>
                    <div class='player-header'>
                        <img src='{get_player_image_url(clicked_player, player_row['player_id'])}' class='player-photo-large'>
                        <div>
                            <h2 style='margin: 0; color: {team_colors["primary"]};'>{clicked_player}</h2>
                            <h4 style='margin: 8px 0; color: #666;'>{player_row['team_name']}</h4>
                            <p style='margin: 0; color: #4A90E2;'>Salary per Game: ${player_row['dollars_per_game']:,.2f}</p>
                            <p style='margin: 0; color: #4A90E2;'>Salary per Point: ${player_row['dollars_per_point']:,.2f}</p>
                            <p style='margin: 10px 0 0; color: #555;'>PPG: {player_row['pts']:.1f} • RPG: {player_row['reb']:.1f} • APG: {player_row['assists']:.1f}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ============================================
# TOP FEATURE - CONTRACT EFFICIENCY SCORE
# ============================================
elif page == "Contract Efficiency Score":
    st.markdown("# 🔥 Contract Efficiency Score (CES)")
    st.markdown("---")

    st.markdown(
        """
        **One score that compares player performance vs salary**

        - Instantly shows who is underpaid, fairly paid, or overpaid
        - Front offices can sort rosters by best contract value
        - Perfect for executives because it turns complex stats into one decision metric
        """
    )

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        contract_df = get_contract_records(df)

        st.markdown("### 🧮 How CES is calculated")
        st.info(
            "Impact Score = normalized points (60%) + rebounds (25%) + assists (15%), divided by salary in millions for a normalized CES."
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Median CES",
                f"{contract_df['contract_efficiency_score'].median():.2f}",
                help="Higher = more production for every $1M in salary"
            )

        with col2:
            top_player = contract_df.loc[contract_df['contract_efficiency_score'].idxmax()]
            st.metric(
                "Top Value Player",
                top_player['player_name'],
                f"CES {top_player['contract_efficiency_score']:.2f}"
            )

        with col3:
            value_counts = contract_df['contract_value_label'].value_counts()
            underpaid = value_counts.get("Underpaid", 0)
            st.metric(
                "High-Value Contracts",
                f"{underpaid} players",
                help="Count of players in the top CES tier"
            )

        with col4:
            total_cap = contract_df['salary_usd'].sum()
            st.metric(
                "Total Salary Commitments",
                f"${total_cap:,.0f}",
                help="Updates live as you add or edit contracts"
            )

        st.markdown("---")
        st.markdown("### 🛠️ Manage Contracts and Performance (CRUD)")

        management_col1, management_col2 = st.columns(2)
        with management_col1:
            st.subheader("Create a Contract")
            with st.form("create_contract_form"):
                new_player = st.text_input("Player Name")
                new_team = st.selectbox("Team", sorted(contract_df['team_name'].dropna().unique()))
                new_salary = st.number_input("Salary (USD)", min_value=0.0, step=250000.0)
                new_pts = st.number_input("Points per Game", min_value=0.0, step=0.1)
                new_reb = st.number_input("Rebounds per Game", min_value=0.0, step=0.1)
                new_ast = st.number_input("Assists per Game", min_value=0.0, step=0.1)
                submitted_new = st.form_submit_button("Create Player Contract", use_container_width=True)

            if submitted_new:
                if new_player.strip() == "":
                    st.warning("Please provide a player name before creating a contract.")
                elif new_player in contract_df['player_name'].values:
                    st.warning("Player already exists. Use the update panel to edit the contract.")
                else:
                    base_columns = contract_df.columns
                    new_record = {col: 0 for col in base_columns}
                    new_record.update({
                        'player_name': new_player,
                        'team_name': new_team,
                        'salary_usd': new_salary,
                        'pts': new_pts,
                        'reb': new_reb,
                        'assists': new_ast,
                    })
                    updated_df = pd.concat([contract_df, pd.DataFrame([new_record])], ignore_index=True)
                    contract_df = persist_contract_records(updated_df)
                    st.success(f"Added {new_player} and recalculated CES.")

        with management_col2:
            st.subheader("Update or Delete")
            selected_player = st.selectbox("Select Player", contract_df['player_name'].tolist())
            selected_row = contract_df[contract_df['player_name'] == selected_player].iloc[0]

            new_salary_slider = st.slider(
                "Simulate Salary (What-if)",
                min_value=0.0,
                max_value=float(max(contract_df['salary_usd'].max(), selected_row['salary_usd'])),
                value=float(selected_row['salary_usd']),
                step=250000.0,
                help="Adjust to see updated CES without committing changes",
            )

            simulated_row = simulate_ces_for_salary(selected_player, new_salary_slider, contract_df)
            if simulated_row is not None:
                st.info(
                    f"Simulated CES: {simulated_row['contract_efficiency_score']:.2f} ({simulated_row['contract_value_label']})"
                )

            with st.form("update_contract_form"):
                upd_salary = st.number_input("Salary (USD)", value=float(selected_row['salary_usd']), step=250000.0)
                upd_pts = st.number_input("Points per Game", value=float(selected_row['pts']), step=0.1)
                upd_reb = st.number_input("Rebounds per Game", value=float(selected_row['reb']), step=0.1)
                upd_ast = st.number_input("Assists per Game", value=float(selected_row['assists']), step=0.1)
                update_btn, delete_btn = st.columns(2)
                with update_btn:
                    submitted_update = st.form_submit_button("Update", use_container_width=True)
                with delete_btn:
                    submitted_delete = st.form_submit_button("Delete", use_container_width=True)

            if submitted_update:
                contract_df.loc[contract_df['player_name'] == selected_player, ['salary_usd', 'pts', 'reb', 'assists']] = [
                    upd_salary,
                    upd_pts,
                    upd_reb,
                    upd_ast,
                ]
                contract_df = persist_contract_records(contract_df)
                st.success(f"Updated {selected_player} and recalculated CES.")

            if submitted_delete:
                contract_df = persist_contract_records(
                    contract_df[contract_df['player_name'] != selected_player].reset_index(drop=True)
                )
                st.success(f"Deleted {selected_player} and refreshed the leaderboard.")

        st.markdown("---")
        st.markdown("### 🧭 CES Classifications")
        st.caption("Automatically labels each contract based on percentile cutoffs of CES.")

        label_colors = {
            "Underpaid": "#4CAF50",
            "Fair": "#FFC107",
            "Overpaid": "#F44336",
        }

        for label, color in label_colors.items():
            st.markdown(
                f"<div class='stat-box' style='border-left-color:{color};'><strong style='color:{color};'>{label}:</strong> {contract_df[contract_df['contract_value_label'] == label].shape[0]} players</div>",
                unsafe_allow_html=True
            )

        st.markdown("### 💰 Team Salary Cap Snapshot")
        cap_df = contract_df.groupby('team_name', as_index=False)['salary_usd'].sum().rename(columns={'salary_usd': 'team_salary_total'})
        cap_df = cap_df.sort_values('team_salary_total', ascending=False)
        st.dataframe(
            cap_df,
            use_container_width=True,
            height=300,
            column_config={
                'team_salary_total': st.column_config.NumberColumn("Team Salary Total", format="$%,d"),
                'team_name': st.column_config.TextColumn("Team"),
            },
        )

        st.markdown("---")
        st.markdown("### 📋 CES Leaderboard (Best to Worst Value)")

        display_cols = [
            'player_name',
            'team_name',
            'contract_efficiency_score',
            'contract_value_label',
            'salary_usd',
            'pts',
            'reb',
            'assists',
        ]

        leaderboard_df = contract_df[display_cols].sort_values(
            by='contract_efficiency_score', ascending=False
        )
        leaderboard_df = leaderboard_df.rename(columns={
            'player_name': 'Player',
            'team_name': 'Team',
            'contract_efficiency_score': 'CES',
            'contract_value_label': 'Value Label',
            'salary_usd': 'Salary (USD)',
            'pts': 'PTS',
            'reb': 'REB',
            'assists': 'AST',
        })

        st.dataframe(
            leaderboard_df,
            use_container_width=True,
            column_config={
                "Salary (USD)": st.column_config.NumberColumn(format="$%,d"),
                "CES": st.column_config.NumberColumn(format="%.2f"),
            },
            height=500,
        )


# ============================================
# LLM CHAT
# ============================================
if page == "LLM Chat":
    st.markdown("# 💬 Chat 67")
    st.markdown("### Ask questions about NBA")
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
