import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Game Deals Tracker",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS & Styling
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700&display=swap');

    /* General App Styling */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ADB5;
        border-radius: 5px;
    }

    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: #1E2329;
        border: 1px solid #2C333D;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #00ADB5;
    }
    div[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-size: 0.9rem;
    }
    div[data-testid="stMetricValue"] {
        color: #00ADB5 !important;
        font-weight: 700;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #2C333D;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #1E2329 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* Dataframe Styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #2C333D;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Custom Header Gradient */
    .hero-header {
        background: linear-gradient(90deg, #00ADB5 0%, #007B81 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0;
    }
    .hero-subheader {
        color: #9CA3AF;
        font-size: 1.2rem;
        margin-top: -10px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    data_dir = "data/cleaned"
    datasets = []
    
    files = {
        "Steam": "cleaned_steam.csv",
        "Epic Games": "cleaned_epicgames.csv",
        "Instant Gaming": "cleaned_instantgaming.csv",
        "Loaded": "cleaned_loaded.csv",
        "Xbox": "cleaned_xbox.csv"
    }
    
    for source, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                df['source_file'] = source
                
                # Normalize Columns
                if source == "Epic Games":
                    if 'price' in df.columns:
                        df.rename(columns={'price': 'price_eur'}, inplace=True)
                
                # Ensure essential columns
                required_cols = ['price_eur', 'discount_pct', 'title', 'platform', 'product_url']
                for col in required_cols:
                    if col not in df.columns:
                        if col == 'discount_pct':
                            df[col] = 0
                        elif col == 'price_eur':
                            df[col] = 0.0
                        else:
                            df[col] = None
                
                # Data Type Cleaning
                df['price_eur'] = pd.to_numeric(df['price_eur'], errors='coerce').fillna(0.0)
                df['discount_pct'] = pd.to_numeric(df['discount_pct'], errors='coerce').fillna(0)
                
                datasets.append(df)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        return combined_df
    return pd.DataFrame()

df = load_data()

# -----------------------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Filters")
    
    if not df.empty:
        # Store Filter
        all_stores = sorted(df['source_file'].unique().tolist())
        selected_stores = st.multiselect("Select Stores", all_stores, default=all_stores)
        
        st.markdown("---")
        
        # Price Filter
        st.markdown("#### Price Range (€)")
        min_price_val = float(df['price_eur'].min())
        max_price_val = float(df['price_eur'].max())
        
        price_range = st.slider(
            "Select Price Range",
            min_value=0.0,
            max_value=max_price_val if max_price_val > 0 else 100.0,
            value=(0.0, max_price_val if max_price_val > 0 else 100.0),
            step=1.0,
            label_visibility="collapsed"
        )
        st.caption(f"Showing games from €{price_range[0]} to €{price_range[1]}")
        
        st.markdown("---")
        
        # Discount Filter
        st.markdown("#### Minimum Discount (%)")
        min_discount = st.slider("Min Discount", 0, 100, 0, step=5)
        
        # Search
        st.markdown("---")
        search_query = st.text_input("🔍 Search Game", placeholder="E.g., Elden Ring")

# -----------------------------------------------------------------------------
# Main Content
# -----------------------------------------------------------------------------

# Hero Section
st.markdown('<h1 class="hero-header">Game Deals Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subheader">Aggregating the best prices from Steam, Epic, Xbox, and more.</p>', unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No data found. Please check your data directory.")
else:
    # Apply Filters
    filtered_df = df[
        (df['source_file'].isin(selected_stores)) &
        (df['price_eur'] >= price_range[0]) &
        (df['price_eur'] <= price_range[1]) &
        (df['discount_pct'] >= min_discount)
    ]
    
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, case=False, na=False)]

    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total Games", f"{len(filtered_df):,}")
    with m2:
        avg_price = filtered_df['price_eur'].mean()
        st.metric("Avg Price", f"€{avg_price:.2f}")
    with m3:
        avg_discount = filtered_df['discount_pct'].mean()
        st.metric("Avg Discount", f"{avg_discount:.1f}%")
    with m4:
        # Count of "Great Deals" (>50% off)
        great_deals = len(filtered_df[filtered_df['discount_pct'] >= 50])
        st.metric("Great Deals (50%+)", f"{great_deals:,}")

    st.markdown("---")

    # Visualizations Layout
    col_charts_1, col_charts_2 = st.columns([1.5, 1])

    with col_charts_1:
        st.subheader("📊 Price Distribution by Store")
        if not filtered_df.empty:
            fig_box = px.box(
                filtered_df, 
                x="source_file", 
                y="price_eur", 
                color="source_file",
                color_discrete_sequence=px.colors.qualitative.Bold,
                labels={"price_eur": "Price (€)", "source_file": "Store"}
            )
            fig_box.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No data for visualization.")

    with col_charts_2:
        st.subheader("🔥 Top Discounts")
        if not filtered_df.empty:
            # Histogram of discounts
            fig_hist = px.histogram(
                filtered_df[filtered_df['discount_pct'] > 0],
                x="discount_pct",
                nbins=20,
                color_discrete_sequence=['#00ADB5'],
                labels={"discount_pct": "Discount (%)"}
            )
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                bargap=0.1,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No discounts found.")

    # Detailed Data Table
    st.subheader("📋 Game List")
    
    if not filtered_df.empty:
        # Configure columns for better display
        st.dataframe(
            filtered_df[['title', 'price_eur', 'discount_pct', 'source_file', 'platform', 'product_url']].sort_values(by='discount_pct', ascending=False),
            column_config={
                "title": "Game Title",
                "price_eur": st.column_config.NumberColumn(
                    "Price",
                    format="€%.2f"
                ),
                "discount_pct": st.column_config.ProgressColumn(
                    "Discount",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100,
                ),
                "source_file": "Store",
                "platform": "Platform",
                "product_url": st.column_config.LinkColumn("Link")
            },
            use_container_width=True,
            height=600
        )
    else:
        st.info("No games match your filters.")
