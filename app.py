import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf2 import FPDF
from io import BytesIO
import os

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
if 'df' not in st.session_state:
    st.session_state.df = None

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
st.markdown("# 📊 DataInsight Pro")
st.markdown("*Enterprise Analytics Platform - Simplified*")

# If no file selected, show welcome
if not st.session_state.uploaded_files or st.session_state.selected_file is None:
    st.info("👈 **Upload a file or load sample data from the sidebar to get started!**")
    st.markdown("""
    ### ✨ Features
    - 📁 Upload CSV/Excel files
    - 📊 Auto-generated statistics
    - 📈 Interactive charts
    - 📄 Download PDF reports
    - 📱 Mobile responsive
    """)
else:
    # Load selected file
    df = st.session_state.uploaded_files[st.session_state.selected_file]
    st.success(f"✅ Loaded: **{st.session_state.selected_file}** ({len(df)} rows, {len(df.columns)} columns)")
    
    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Preview", 
        "📊 Statistics", 
        "📈 Charts", 
        "📄 Report",
        "⬇️ Export"
    ])
    
    # TAB 1: DATA PREVIEW
    with tab1:
        st.subheader("Data Preview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card"><div class="metric-label">Rows</div><div class="metric-value">' + str(len(df)) + '</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><div class="metric-label">Columns</div><div class="metric-value">' + str(len(df.columns)) + '</div></div>', unsafe_allow_html=True)
        with col3:
            missing = df.isnull().sum().sum()
            st.markdown('<div class="metric-card"><div class="metric-label">Missing Values</div><div class="metric-value">' + str(missing) + '</div></div>', unsafe_allow_html=True)
        with col4:
            duplicates = df.duplicated().sum()
            st.markdown('<div class="metric-card"><div class="metric-label">Duplicates</div><div class="metric-value">' + str(duplicates) + '</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.write(df.head(10))
        
        if st.checkbox("Show data types"):
            st.write(df.dtypes)
        
        if st.checkbox("Show missing values"):
            missing_data = pd.DataFrame({
                'Column': df.columns,
                'Missing': df.isnull().sum(),
                'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.dataframe(missing_data)
    
    # TAB 2: STATISTICS
    with tab2:
        st.subheader("Summary Statistics")
        
        # Basic statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            st.markdown("#### Numeric Columns")
            st.dataframe(df[numeric_cols].describe().round(3))
            
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
                fig.update_layout(height=500, width=600)
                st.plotly_chart(fig, use_container_width=True)
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.markdown("#### Categorical Columns")
            for col in categorical_cols:
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
            "Box Plot",
            "Violin Plot"
        ])
        
        if chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
            col1 = st.selectbox("X-axis", numeric_cols)
            col2 = st.selectbox("Y-axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
            color_by = st.selectbox("Color by (optional)", ["None"] + categorical_cols)
            
            if color_by == "None":
                fig = px.scatter(df, x=col1, y=col2, title=f"{col1} vs {col2}", trendline="ols")
            else:
                fig = px.scatter(df, x=col1, y=col2, color=color_by, title=f"{col1} vs {col2}", trendline="ols")
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Line Chart" and len(numeric_cols) >= 1:
            cols = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:min(3, len(numeric_cols))])
            if cols:
                fig = px.line(df, y=cols, title="Line Chart")
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Bar Chart" and len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = st.selectbox("Category", categorical_cols)
            num_col = st.selectbox("Value", numeric_cols)
            
            bar_data = df.groupby(cat_col)[num_col].sum().reset_index()
            fig = px.bar(bar_data, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Histogram" and len(numeric_cols) > 0:
            col = st.selectbox("Select column", numeric_cols)
            fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Box Plot" and len(numeric_cols) > 0:
            cols = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:min(3, len(numeric_cols))])
            if cols:
                fig = go.Figure()
                for col in cols:
                    fig.add_trace(go.Box(y=df[col], name=col))
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Violin Plot" and len(numeric_cols) > 0:
            col = st.selectbox("Select column", numeric_cols)
            if categorical_cols:
                cat_col = st.selectbox("Group by (optional)", ["None"] + categorical_cols)
                if cat_col == "None":
                    fig = px.violin(df, y=col, title=f"Distribution of {col}")
                else:
                    fig = px.violin(df, y=col, x=cat_col, title=f"Distribution of {col}")
            else:
                fig = px.violin(df, y=col, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: PDF REPORT
    with tab4:
        st.subheader("Generate PDF Report")
        
        report_title = st.text_input("Report Title", value=f"Analysis Report - {st.session_state.selected_file}")
        
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(0, 10, report_title, ln=True)
                    
                    pdf.set_font("Arial", "", 10)
                    pdf.ln(5)
                    
                    # File info
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "File Information", ln=True)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 5, f"File: {st.session_state.selected_file}", ln=True)
                    pdf.cell(0, 5, f"Rows: {len(df)}", ln=True)
                    pdf.cell(0, 5, f"Columns: {len(df.columns)}", ln=True)
                    
                    # Summary statistics
                    pdf.ln(5)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Summary Statistics", ln=True)
                    pdf.set_font("Arial", "", 10)
                    
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        for col in numeric_cols[:5]:  # Limit to first 5 columns
                            pdf.cell(0, 5, f"{col}: Mean={df[col].mean():.2f}, Std={df[col].std():.2f}", ln=True)
                    
                    # Generate PDF bytes
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"report_{st.session_state.selected_file.replace('.csv', '.pdf')}",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF Report generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    # TAB 5: EXPORT
    with tab5:
        st.subheader("Export Data")
        
        # Export as CSV
        csv = df.to_csv(index=False).encode()
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"analysis_{st.session_state.selected_file}",
            mime="text/csv"
        )
        
        # Export as Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"analysis_{st.session_state.selected_file.replace('.csv', '.xlsx')}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Export summary statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            stats_df = df[numeric_cols].describe()
            stats_csv = stats_df.to_csv().encode()
            st.download_button(
                label="📥 Download Statistics",
                data=stats_csv,
                file_name=f"statistics_{st.session_state.selected_file}",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>DataInsight Pro v1.2.0 • Simplified Analytics Platform</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
