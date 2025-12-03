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
# Custom CSS & Styling (Neon Black/Purple Theme)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700;800&display=swap');

    /* General App Styling */
    .stApp {
        background-color: #000000;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF !important;
        text-shadow: 0 0 10px rgba(213, 0, 249, 0.3);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        background: #121212;
    }
    ::-webkit-scrollbar-thumb {
        background: #D500F9;
        border-radius: 5px;
        box-shadow: 0 0 5px #D500F9;
    }

    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: #121212;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #D500F9, #651FFF);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(213, 0, 249, 0.2);
        border-color: #D500F9;
    }
    div[data-testid="stMetricLabel"] {
        color: #B0B0B0 !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(213, 0, 249, 0.6);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #333;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #651FFF, #D500F9);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(213, 0, 249, 0.3);
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(213, 0, 249, 0.6);
        transform: scale(1.02);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #121212 !important;
        color: #FFFFFF !important;
        border: 1px solid #333;
        border-radius: 8px !important;
    }
    
    /* Dataframe Styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0,0,0,0.5);
    }
    
    /* Custom Header Gradient */
    .hero-header {
        background: linear-gradient(90deg, #D500F9 0%, #651FFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(213, 0, 249, 0.3);
    }
    .hero-subheader {
        color: #B0B0B0;
        font-size: 1.2rem;
        margin-top: -10px;
        margin-bottom: 40px;
        font-weight: 300;
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

    # -------------------------------------------------------------------------
    # Visualizations
    # -------------------------------------------------------------------------
    
    # Row 1: Price Distribution & Top Discounts
    col_charts_1, col_charts_2 = st.columns([1.5, 1])

    with col_charts_1:
        st.subheader("📊 Price Distribution by Store")
        if not filtered_df.empty:
            fig_box = px.box(
                filtered_df, 
                x="source_file", 
                y="price_eur", 
                color="source_file",
                color_discrete_sequence=px.colors.qualitative.Bold, # Will be overridden by theme usually, but good fallback
                labels={"price_eur": "Price (€)", "source_file": "Store"}
            )
            fig_box.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(family="Inter", color="#E0E0E0")
            )
            # Custom marker colors for neon look
            fig_box.update_traces(marker=dict(color='#D500F9', opacity=0.7))
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
                color_discrete_sequence=['#D500F9'],
                labels={"discount_pct": "Discount (%)"}
            )
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                bargap=0.1,
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(family="Inter", color="#E0E0E0")
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No discounts found.")

    # Row 2: New Visualizations
    col_charts_3, col_charts_4 = st.columns(2)
    
    with col_charts_3:
        st.subheader("💎 Deal Hunter: Price vs. Discount")
        if not filtered_df.empty:
            fig_scatter = px.scatter(
                filtered_df,
                x="price_eur",
                y="discount_pct",
                color="source_file",
                hover_data=['title'],
                labels={"price_eur": "Price (€)", "discount_pct": "Discount (%)"},
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(family="Inter", color="#E0E0E0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=1, color='white')))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    with col_charts_4:
        st.subheader("🍩 Games by Store")
        if not filtered_df.empty:
            store_counts = filtered_df['source_file'].value_counts().reset_index()
            store_counts.columns = ['Store', 'Count']
            
            fig_donut = px.pie(
                store_counts,
                values='Count',
                names='Store',
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_donut.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(family="Inter", color="#E0E0E0"),
                showlegend=True
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)

    # Row 3: Platform Comparison
    st.subheader("🎮 Average Price by Platform")
    if not filtered_df.empty and 'platform' in filtered_df.columns:
        # Clean platform data slightly if needed, or just group
        # Assuming platform column exists and has data
        platform_stats = filtered_df.groupby('platform')['price_eur'].mean().reset_index().sort_values('price_eur', ascending=False)
        
        fig_bar = px.bar(
            platform_stats,
            x='platform',
            y='price_eur',
            color='price_eur',
            color_continuous_scale='Purples',
            labels={'price_eur': 'Avg Price (€)', 'platform': 'Platform'}
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(family="Inter", color="#E0E0E0")
        )
        st.plotly_chart(fig_bar, use_container_width=True)


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

