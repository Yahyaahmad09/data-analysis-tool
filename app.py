import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="DataInsight Pro", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# STYLING & CONFIG
# ============================================================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #0072B2 0%, #009E73 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# ============================================================
# SIDEBAR - FILE UPLOAD & SAMPLES
# ============================================================
with st.sidebar:
    st.markdown("### 📁 File Upload")
    uploaded_files = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'], accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.uploaded_files:
                try:
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)
                    st.session_state.uploaded_files[file.name] = df
                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 🧪 Sample Data")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 Sales", use_container_width=True):
            try:
                df = pd.read_csv("sample_data/sample_sales.csv")
                st.session_state.uploaded_files["sample_sales.csv"] = df
                st.session_state.selected_file = "sample_sales.csv"
                st.rerun()
            except:
                st.error("Sample data not found")
    
    with col2:
        if st.button("🔬 Research", use_container_width=True):
            try:
                df = pd.read_csv("sample_data/sample_research.csv")
                st.session_state.uploaded_files["sample_research.csv"] = df
                st.session_state.selected_file = "sample_research.csv"
                st.rerun()
            except:
                st.error("Sample data not found")
    
    with col3:
        if st.button("📡 IoT", use_container_width=True):
            try:
                df = pd.read_csv("sample_data/sample_temperature.csv")
                st.session_state.uploaded_files["sample_temperature.csv"] = df
                st.session_state.selected_file = "sample_temperature.csv"
                st.rerun()
            except:
                st.error("Sample data not found")
    
    st.markdown("---")
    st.markdown("### 📊 Files Uploaded")
    if st.session_state.uploaded_files:
        for fname in st.session_state.uploaded_files.keys():
            if st.button(f"📄 {fname}", use_container_width=True):
                st.session_state.selected_file = fname
                st.rerun()

# ============================================================
# MAIN CONTENT
# ============================================================
st.markdown("# 📊 DataInsight Pro v1.2.0")
st.markdown("*Simplified Analytics Platform*")

# If no file selected, show welcome
if not st.session_state.uploaded_files or st.session_state.selected_file is None:
    st.info("👈 **Upload a file or load sample data from the sidebar to get started!**")
    st.markdown("""
    ### ✨ Features
    - 📁 Upload CSV/Excel files
    - 📊 Auto-generated statistics
    - 📈 Interactive charts
    - 📄 Export results
    """)
else:
    # Load selected file
    df = st.session_state.uploaded_files[st.session_state.selected_file]
    st.success(f"✅ Loaded: **{st.session_state.selected_file}** ({len(df)} rows, {len(df.columns)} columns)")
    
    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Preview", 
        "📊 Statistics", 
        "📈 Charts", 
        "⬇️ Export"
    ])
    
    # TAB 1: DATA PREVIEW
    with tab1:
        st.subheader("Data Preview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            missing = df.isnull().sum().sum()
            st.metric("Missing Values", missing)
        with col4:
            duplicates = df.duplicated().sum()
            st.metric("Duplicates", duplicates)
        
        st.markdown("---")
        st.write("**First 10 rows:**")
        st.dataframe(df.head(10), use_container_width=True)
        
        if st.checkbox("Show data types"):
            st.write(df.dtypes)
    
    # TAB 2: STATISTICS
    with tab2:
        st.subheader("Summary Statistics")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            st.markdown("#### Numeric Columns")
            st.dataframe(df[numeric_cols].describe().round(3), use_container_width=True)
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                st.markdown("#### Correlation Matrix")
                corr_matrix = df[numeric_cols].corr()
                
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0
                ))
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.markdown("#### Categorical Columns")
            for col in categorical_cols[:5]:
                st.write(f"**{col}**")
                st.write(df[col].value_counts())
    
    # TAB 3: CHARTS
    with tab3:
        st.subheader("Interactive Visualizations")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        chart_type = st.selectbox("Select Chart Type", [
            "Scatter Plot",
            "Line Chart",
            "Bar Chart",
            "Histogram",
            "Box Plot"
        ])
        
        if chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
            col1 = st.selectbox("X-axis", numeric_cols, key="scatter_x")
            col2 = st.selectbox("Y-axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key="scatter_y")
            
            fig = px.scatter(df, x=col1, y=col2, title=f"{col1} vs {col2}", trendline="ols")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Line Chart" and len(numeric_cols) >= 1:
            cols = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:min(2, len(numeric_cols))])
            if cols:
                fig = px.line(df, y=cols, title="Line Chart")
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Bar Chart" and len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = st.selectbox("Category", categorical_cols, key="bar_cat")
            num_col = st.selectbox("Value", numeric_cols, key="bar_val")
            
            bar_data = df.groupby(cat_col)[num_col].sum().reset_index()
            fig = px.bar(bar_data, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Histogram" and len(numeric_cols) > 0:
            col = st.selectbox("Select column", numeric_cols, key="hist_col")
            fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Box Plot" and len(numeric_cols) > 0:
            cols = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:min(2, len(numeric_cols))], key="box_cols")
            if cols:
                fig = go.Figure()
                for col in cols:
                    fig.add_trace(go.Box(y=df[col], name=col))
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: EXPORT
    with tab4:
        st.subheader("Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False).encode()
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"analysis_{st.session_state.selected_file}",
                mime="text/csv"
            )
        
        with col2:
            try:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"analysis_{st.session_state.selected_file.replace('.csv', '.xlsx')}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except:
                st.info("Excel export not available")
        
        with col3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                stats_df = df[numeric_cols].describe()
                stats_csv = stats_df.to_csv().encode()
                st.download_button(
                    label="📥 Download Stats",
                    data=stats_csv,
                    file_name=f"statistics_{st.session_state.selected_file}",
                    mime="text/csv"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>DataInsight Pro v1.2.0 • Simplified Analytics</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
