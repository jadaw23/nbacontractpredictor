# ============================================
# NBA Dashboard - Streamlit Application
# ITOM6265 - Database Homework
# ============================================

# Block 1: Import required libraries
import streamlit as st
import pandas as pd
import plotly.express as px

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

# Player headshot mapping - add more players as needed
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
    # Check if we have a direct mapping
    if player_name in PLAYER_IMAGES:
        return PLAYER_IMAGES[player_name]
    
    # Otherwise return a placeholder with player initials
    return f"https://ui-avatars.com/api/?name={player_name.replace(' ', '+')}&size=200&background=f57c00&color=fff&bold=true"

def get_team_colors(team_abbrev):
    """Get team colors from abbreviation"""
    return NBA_COLORS.get(team_abbrev, {'primary': '#007AC1', 'secondary': '#EF3B24'})

# Custom CSS for styling with NBA theme
st.markdown("""
    <style>
    /* NBA themed background - lighter version */
    .stApp {
        background: linear-gradient(135deg, #4A90E2 0%, #FF6B6B 100%);
    }
    
    /* Main content area */
    .main .block-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
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
    </style>
""", unsafe_allow_html=True)

# Block 3: Load Data
@st.cache_data
def load_data():
    df = pd.read_excel('Full_NBA_Dataset.xlsx')
    return df

try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure 'Full_NBA_Dataset.xlsx' is in the same folder as this script.")
    data_loaded = False
    df = None

# Block 4: Sidebar navigation
st.sidebar.title("🏀 NBA Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Project Summary", "Player Search", "Analytics"],
    help="Select a page to navigate"
)
st.sidebar.markdown("---")
st.sidebar.info("NBA Player Statistics Dashboard")

# ============================================
# TAB 1: PROJECT SUMMARY
# ============================================
if page == "Project Summary":
    st.markdown("# 📝 Project Summary")
    st.markdown("---")

    # ============================================
    # STATS DASHBOARD
    # ============================================
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
        
        # ============================================
        # TOP 5 PLAYERS BY POINTS WITH IMAGES
        # ============================================
        st.markdown("### 🏆 Hall of Fame - Top 5 Scorers")
        
        top5 = df.nlargest(5, 'pts')[['player_name', 'team_name', 'pts', 'salary_usd']]
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        colors = ["gold", "silver", "bronze", "", ""]
        
        for idx, (_, row) in enumerate(top5.iterrows()):
            salary_m = row['salary_usd'] / 1000000
            img_url = get_player_image_url(row['player_name'])
            
            # Get team abbreviation from team_name (e.g., "OKC" from team_name column)
            team_abbrev = row['team_name']  # Assuming team_name is already abbreviated
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
        interactive filtering and visualization capabilities. We used Plotly Express for creating 
        the scatter plot visualization which allows for interactive exploration of the relationship 
        between salary per point and salary per game. Player images are dynamically loaded using 
        NBA's CDN headshot URLs with fallback avatars.
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
                    st.balloons()
                    
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
# TAB 3: ANALYTICS (SCATTER PLOT)
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
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; font-size: 0.9em;'>
        ITOM6265 Database Management | NBA Dashboard | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
