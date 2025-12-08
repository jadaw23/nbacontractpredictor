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

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
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
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #f57c00;
    }
    .gold { border-left-color: #FFD700 !important; }
    .silver { border-left-color: #C0C0C0 !important; }
    .bronze { border-left-color: #CD7F32 !important; }
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
    ["HW Summary", "Player Search", "Analytics"],
    help="Select a page to navigate"
)
st.sidebar.markdown("---")
st.sidebar.info("NBA Player Statistics Dashboard")

# ============================================
# TAB 1: HW SUMMARY
# ============================================
if page == "HW Summary":
    st.markdown("# 📝 Homework Summary")
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
        # TOP 5 PLAYERS BY POINTS
        # ============================================
        st.markdown("### 🏆 Hall of Fame - Top 5 Scorers")
        
        top5 = df.nlargest(5, 'pts')[['player_name', 'team_name', 'pts', 'salary_usd']]
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        colors = ["gold", "silver", "bronze", "", ""]
        
        for idx, (_, row) in enumerate(top5.iterrows()):
            salary_m = row['salary_usd'] / 1000000
            st.markdown(f"""
                <div class='top-player {colors[idx]}'>
                    <span style='font-size: 1.5em;'>{medals[idx]}</span>
                    <strong style='font-size: 1.2em; margin-left: 10px;'>{row['player_name']}</strong>
                    <span style='float: right; font-size: 1.1em;'>⭐ {row['pts']:.1f} pts | 🏀 {row['team_name']} | 💰 ${salary_m:.1f}M</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Approach and Implementation")

        st.write("""
        This NBA dashboard was built using Streamlit and Pandas to analyze player statistics 
        and salary data. The application loads data from an Excel file and provides interactive 
        filtering and visualization capabilities. I used Plotly Express for creating the 
        scatter plot visualization which allows for interactive exploration of the relationship 
        between salary per point and salary per game. The dashboard demonstrates CRUD-like 
        read operations and analytics visualizations as required.
        """)

    with col2:
        st.subheader("🎨 Customizations Made")

        st.write("""
        I customized this application in several ways:
        
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
# TAB 2: PLAYER SEARCH
# ============================================
elif page == "Player Search":
    st.markdown("# 🔍 Player Search")
    st.markdown("---")

    if not data_loaded:
        st.error("Data not loaded. Please check your data file.")
    else:
        # Get min and max salary for slider
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

            # Team filter
            teams = ['All Teams'] + sorted(df['team_name'].unique().tolist())
            selected_team = st.selectbox("Select Team:", teams)

            # Salary range slider (in millions for better UX)
            salary_range = st.slider(
                "Salary Range (USD):",
                min_value=min_salary,
                max_value=max_salary,
                value=(min_salary, max_salary),
                format="$%d"
            )

            search_button = st.button(
                "🔍 Search Players",
                type="primary",
                use_container_width=True
            )

        with col2:
            st.markdown("### Search Results")

            if search_button:
                # Filter data
                filtered_df = df.copy()
                
                # Filter by name
                if name_pattern:
                    filtered_df = filtered_df[filtered_df['player_name'].str.contains(name_pattern, case=False, na=False)]
                
                # Filter by team
                if selected_team != 'All Teams':
                    filtered_df = filtered_df[filtered_df['team_name'] == selected_team]
                
                # Filter by salary range
                filtered_df = filtered_df[
                    (filtered_df['salary_usd'] >= salary_range[0]) & 
                    (filtered_df['salary_usd'] <= salary_range[1])
                ]
                
                if not filtered_df.empty:
                    st.success(f"Found {len(filtered_df)} players")
                    st.balloons()
                    
                    # Display results
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
        # Team filter for scatter plot
        st.markdown("### Filter by Team")
        teams_list = ['All Teams'] + sorted(df['team_name'].unique().tolist())
        selected_team_analytics = st.selectbox("Select Team to Display:", teams_list, key="analytics_team")
        
        # Filter data based on team selection
        if selected_team_analytics == 'All Teams':
            plot_df = df.copy()
        else:
            plot_df = df[df['team_name'] == selected_team_analytics].copy()
        
        st.markdown("---")
        st.markdown("### Dollars per Point vs Dollars per Game")
        st.caption("This scatter plot shows the relationship between salary efficiency metrics for NBA players.")
        
        # Create scatter plot
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
        
        # Additional stats
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