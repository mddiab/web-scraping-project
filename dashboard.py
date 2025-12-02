import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(page_title="Game Deals Dashboard", layout="wide", page_icon="🎮")

# Custom CSS for professional look
st.markdown("""
<style>
    .main {
        background-color: #222831;
    }
    h1, h2, h3 {
        color: #00adb5 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stMetric {
        background-color: #393e46;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .stMetric label {
        color: #eeeeee !important;
    }
    .stMetric .css-1wivap2 {
        color: #00adb5 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #393e46;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎮 Game Deals Dashboard")

# Data Loading
@st.cache_data
def load_data():
    data_dir = "data/cleaned"
    datasets = []
    
    # Define file mappings and specific processing
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
                
                # Normalize Epic Games
                if source == "Epic Games":
                    if 'price' in df.columns:
                        df.rename(columns={'price': 'price_eur'}, inplace=True)
                    for col in ['discount_pct', 'original_price_eur', 'storefront']:
                        if col not in df.columns:
                            df[col] = None
                
                # Ensure common columns exist
                if 'price_eur' not in df.columns:
                    df['price_eur'] = None
                if 'discount_pct' not in df.columns:
                    df['discount_pct'] = 0
                
                datasets.append(df)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        return combined_df
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found. Please check the data directory.")
else:
    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Store Filter
    all_stores = df['source_file'].unique().tolist()
    selected_stores = st.sidebar.multiselect("Select Stores", all_stores, default=all_stores)
    
    # Price Filter (Min/Max Input Boxes)
    st.sidebar.subheader("Price Range (€)")
    col_min, col_max = st.sidebar.columns(2)
    
    min_val = float(df['price_eur'].min()) if not df['price_eur'].isnull().all() else 0.0
    max_val = float(df['price_eur'].max()) if not df['price_eur'].isnull().all() else 100.0
    
    with col_min:
        min_price = st.number_input("Min", min_value=0.0, max_value=max_val, value=min_val)
    with col_max:
        max_price = st.number_input("Max", min_value=0.0, max_value=1000.0, value=max_val) # Allow higher max manually
    
    # Filter Data
    filtered_df = df[
        (df['source_file'].isin(selected_stores)) &
        (df['price_eur'] >= min_price) &
        (df['price_eur'] <= max_price)
    ]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Games", len(filtered_df))
    avg_price = filtered_df['price_eur'].mean()
    col2.metric("Average Price", f"€{avg_price:.2f}" if pd.notnull(avg_price) else "N/A")
    avg_discount = filtered_df['discount_pct'].mean()
    col3.metric("Average Discount", f"{avg_discount:.1f}%" if pd.notnull(avg_discount) else "N/A")
    
    st.markdown("---")
    
    # Visualizations
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("Price Distribution by Store")
        fig_price = px.box(filtered_df, x="source_file", y="price_eur", color="source_file", 
                           title="Price Distribution", labels={"price_eur": "Price (€)", "source_file": "Store"},
                           template="plotly_dark")
        fig_price.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_price, use_container_width=True)
        
    with col_viz2:
        st.subheader("Discount Distribution by Store")
        discount_df = filtered_df[filtered_df['discount_pct'] > 0]
        if not discount_df.empty:
            fig_discount = px.histogram(discount_df, x="discount_pct", color="source_file", 
                                      nbins=20, title="Discount Percentage Distribution",
                                      labels={"discount_pct": "Discount (%)", "source_file": "Store"},
                                      template="plotly_dark")
            fig_discount.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_discount, use_container_width=True)
        else:
            st.info("No discount data available for selected filters.")

    # Platform Breakdown
    if 'platform' in filtered_df.columns:
        st.subheader("Games by Platform")
        platform_counts = filtered_df['platform'].value_counts().reset_index()
        platform_counts.columns = ['platform', 'count']
        fig_platform = px.bar(platform_counts, x='platform', y='count', title="Game Count by Platform",
                              template="plotly_dark", color='count', color_continuous_scale='Teal')
        fig_platform.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_platform, use_container_width=True)

    # Data Table
    st.subheader("Detailed Game Data")
    st.dataframe(filtered_df[['title', 'price_eur', 'discount_pct', 'source_file', 'platform', 'product_url']].sort_values(by='discount_pct', ascending=False), use_container_width=True)
