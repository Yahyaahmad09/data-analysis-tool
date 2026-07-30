"""
DataInsight Pro v1.1.0 - Main Application
Enterprise Analytics Platform
"""

import streamlit as st
import pandas as pd
import plotly.io as pio
from datetime import datetime
import json
import zipfile
import io

from config import (
    APP_NAME, APP_VERSION, APP_TAGLINE, MAX_FILE_SIZE_MB, SUPPORTED_FORMATS,
    COLOR_PALETTES, REPORT_TEMPLATES, QUALITY_THRESHOLDS
)
from modules.file_handler import FileHandler
from modules.data_analyzer import DataAnalyzer
from modules.visualization import Visualization
from modules.data_cleaner import DataCleaner
from modules.profile_manager import ProfileManager
from modules.template_manager import TemplateManager
from modules.report_generator import ReportGenerator
from modules.utils import (
    apply_theme, create_metric_card, create_file_item, create_status_badge,
    show_error, show_success, show_info, show_warning,
    export_dataframe_to_csv, export_dataframe_to_json, export_dataframe_to_excel,
    get_current_timestamp
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title=f"{APP_NAME} - {APP_TAGLINE}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': f"{APP_NAME} v{APP_VERSION}\n{APP_TAGLINE}\n\nEnterprise Analytics Platform"
    }
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session_state():
    """Initialize all session state variables"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'cleaned_data' not in st.session_state:
        st.session_state.cleaned_data = {}
    if 'color_palette' not in st.session_state:
        st.session_state.color_palette = 'Viridis'
    if 'chart_height' not in st.session_state:
        st.session_state.chart_height = 600
    if 'report_template' not in st.session_state:
        st.session_state.report_template = 'professional'
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = None


init_session_state()


# ============================================================
# APPLY THEME
# ============================================================
apply_theme(st.session_state.theme)


# ============================================================
# HEADER
# ============================================================
def render_header():
    """Render application header"""
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">📊</div>
            <div>
                <h1 style="margin: 0; font-size: 1.8rem; background: linear-gradient(90deg, #0072B2 0%, #009E73 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {APP_NAME}
                </h1>
                <p style="margin: 0; font-size: 0.85rem; color: #888;">{APP_TAGLINE} v{APP_VERSION}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        file_count = len(st.session_state.uploaded_files)
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem;">
            <div style="font-size: 0.75rem; color: #888; text-transform: uppercase;">Files</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #0072B2;">{file_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(f"{theme_icon} Theme", key="theme_toggle", use_container_width=True):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()

    with col4:
        if st.button("📖 Help", key="help_btn", use_container_width=True):
            st.session_state.show_help = not st.session_state.get('show_help', False)

    with col5:
        if st.button("⚙️ Settings", key="settings_btn", use_container_width=True):
            st.session_state.show_settings = not st.session_state.get('show_settings', False)

    st.markdown("---")


# ============================================================
# SIDEBAR - FILE UPLOAD
# ============================================================
def render_sidebar():
    """Render sidebar with file upload"""
    with st.sidebar:
        st.markdown("### 📁 File Upload")

        # Upload area
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help=f"Max file size: {MAX_FILE_SIZE_MB}MB | Formats: {', '.join(SUPPORTED_FORMATS)}"
        )

        st.markdown(f"""
        <div style="font-size: 0.8rem; color: #888; padding: 0.5rem; background: rgba(0,114,178,0.05); border-radius: 6px; margin: 0.5rem 0;">
            💡 <strong>Tip:</strong> You can upload multiple files at once!<br>
            Max size: <strong>{MAX_FILE_SIZE_MB}MB</strong> per file
        </div>
        """, unsafe_allow_html=True)

        # Sample data
        with st.expander("📊 Use Sample Data", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💰 Sales", use_container_width=True, key="sample_sales"):
                    load_sample_data('sales')
            with col2:
                if st.button("🔬 Research", use_container_width=True, key="sample_research"):
                    load_sample_data('research')
            with col3:
                if st.button("📡 IoT", use_container_width=True, key="sample_iot"):
                    load_sample_data('timeseries')

        st.markdown("---")

        # File list
        if st.session_state.uploaded_files:
            st.markdown("### 📂 Uploaded Files")

            # Select all / Clear all
            col1, col2 = st.columns(2)
            with col1:
                if st.button("☑️ Select All", use_container_width=True, key="select_all"):
                    st.session_state.selected_files = list(st.session_state.uploaded_files.keys())
                    st.rerun()
            with col2:
                if st.button("⬜ Clear All", use_container_width=True, key="clear_all"):
                    st.session_state.selected_files = []
                    st.rerun()

            st.markdown("---")

            # File list with checkboxes
            for file_name, file_data in st.session_state.uploaded_files.items():
                col1, col2 = st.columns([4, 1])
                with col1:
                    is_selected = st.checkbox(
                        file_data['metadata']['name'],
                        value=file_name in st.session_state.selected_files,
                        key=f"file_check_{file_name}",
                        help=f"{file_data['metadata']['rows']:,} rows × {file_data['metadata']['columns']} cols"
                    )
                    if is_selected and file_name not in st.session_state.selected_files:
                        st.session_state.selected_files.append(file_name)
                    elif not is_selected and file_name in st.session_state.selected_files:
                        st.session_state.selected_files.remove(file_name)

                with col2:
                    if st.button("🗑️", key=f"remove_{file_name}"):
                        del st.session_state.uploaded_files[file_name]
                        if file_name in st.session_state.selected_files:
                            st.session_state.selected_files.remove(file_name)
                        st.rerun()

                # File meta
                if file_data['status'] == 'success':
                    st.markdown(f"""
                    <div style="font-size: 0.75rem; color: #888; margin-left: 1.5rem; margin-bottom: 0.5rem;">
                        {file_data['metadata']['size_mb']} MB • {file_data['metadata']['rows']:,} rows • {file_data['metadata']['columns']} cols
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Error: {file_data.get('error', 'Unknown')}")

            st.markdown("---")

            # Action buttons
            if st.session_state.selected_files:
                if st.button("🚀 Analyze Selected Files", type="primary", use_container_width=True):
                    st.session_state.trigger_analysis = True
                    st.success(f"Ready to analyze {len(st.session_state.selected_files)} file(s)")

        # Settings
        with st.sidebar:
            with st.expander("⚙️ Settings", expanded=False):
                st.session_state.color_palette = st.selectbox(
                    "Color Palette",
                    options=list(COLOR_PALETTES.keys()),
                    index=list(COLOR_PALETTES.keys()).index(st.session_state.color_palette)
                )

                st.session_state.chart_height = st.slider(
                    "Chart Height",
                    min_value=300,
                    max_value=1000,
                    value=st.session_state.chart_height,
                    step=50
                )

                st.session_state.report_template = st.selectbox(
                    "Report Template",
                    options=list(REPORT_TEMPLATES.keys()),
                    format_func=lambda x: REPORT_TEMPLATES[x]['name'],
                    index=list(REPORT_TEMPLATES.keys()).index(st.session_state.report_template)
                )


def load_sample_data(sample_type: str):
    """Load sample data file"""
    sample_files = {
        'sales': 'sample_data/sample_sales.csv',
        'research': 'sample_data/sample_research.csv',
        'timeseries': 'sample_data/sample_temperature.csv'
    }

    file_path = sample_files.get(sample_type)
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        file_name = f"sample_{sample_type}.csv"

        # Create a fake uploaded file object
        class FakeUploadedFile:
            def __init__(self, name, df):
                self.name = name
                self._df = df
                buffer = io.BytesIO()
                df.to_csv(buffer, index=False)
                buffer.seek(0)
                self._buffer = buffer
                self.size = buffer.getbuffer().nbytes

            def read(self, *args, **kwargs):
                self._buffer.seek(0)
                return self._buffer.read()

            def seek(self, *args, **kwargs):
                return self._buffer.seek(*args, **kwargs)

        fake_file = FakeUploadedFile(file_name, df)

        handler = FileHandler()
        is_valid, message = handler.validate_file(fake_file)
        if is_valid:
            df_read, error = handler.read_file(fake_file)
            if df_read is not None:
                st.session_state.uploaded_files[file_name] = {
                    'dataframe': df_read,
                    'metadata': handler.get_file_metadata(fake_file, df_read),
                    'status': 'success',
                    'error': None
                }
                if file_name not in st.session_state.selected_files:
                    st.session_state.selected_files.append(file_name)
                show_success(f"Loaded sample: {file_name}")
                st.rerun()
            else:
                show_error(error)
        else:
            show_error(message)
    except Exception as e:
        show_error(f"Failed to load sample: {str(e)}")


# ============================================================
# PROCESS UPLOADED FILES
# ============================================================
def process_uploads(uploaded_files):
    """Process newly uploaded files"""
    if not uploaded_files:
        return

    handler = FileHandler()
    new_files = {}

    for uploaded_file in uploaded_files:
        if uploaded_file.name in st.session_state.uploaded_files:
            continue  # Skip already uploaded

        is_valid, message = handler.validate_file(uploaded_file)
        if not is_valid:
            st.session_state.uploaded_files[uploaded_file.name] = {
                'dataframe': None,
                'metadata': handler.get_file_metadata(uploaded_file),
                'status': 'error',
                'error': message
            }
            continue

        df, error = handler.read_file(uploaded_file)
        if df is not None:
            st.session_state.uploaded_files[uploaded_file.name] = {
                'dataframe': df,
                'metadata': handler.get_file_metadata(uploaded_file, df),
                'status': 'success',
                'error': None
            }
            new_files[uploaded_file.name] = True
        else:
            st.session_state.uploaded_files[uploaded_file.name] = {
                'dataframe': None,
                'metadata': handler.get_file_metadata(uploaded_file),
                'status': 'error',
                'error': error
            }

    # Auto-select newly uploaded files
    for file_name in new_files:
        if file_name not in st.session_state.selected_files:
            st.session_state.selected_files.append(file_name)


# ============================================================
# GET SELECTED DATA
# ============================================================
def get_selected_data():
    """Get the currently selected file's DataFrame"""
    if not st.session_state.selected_files:
        return None, None, None

    # Use first selected file
    file_name = st.session_state.selected_files[0]
    if file_name not in st.session_state.uploaded_files:
        return None, None, None

    file_data = st.session_state.uploaded_files[file_name]

    # Use cleaned data if available
    if file_name in st.session_state.cleaned_data:
        return st.session_state.cleaned_data[file_name], file_name, file_data

    return file_data.get('dataframe'), file_name, file_data


# ============================================================
# TAB 1: OVERVIEW
# ============================================================
def render_overview_tab():
    """Render overview tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar to begin")
        return

    st.markdown(f'<h2 class="section-header">📊 Overview: {file_name}</h2>', unsafe_allow_html=True)

    # File info cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(create_metric_card(
            "File Size",
            f"{file_data['metadata']['size_mb']} MB",
            "💾",
            file_data['metadata']['format'].upper()
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_card(
            "Rows",
            f"{len(df):,}",
            "📊",
            "Data Points"
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(create_metric_card(
            "Columns",
            f"{len(df.columns)}",
            "📋",
            "Features"
        ), unsafe_allow_html=True)

    with col4:
        handler = FileHandler()
        quality = handler.get_quality_score(df)
        score = quality['overall']
        if score >= QUALITY_THRESHOLDS['excellent']:
            icon, color = "✅", "#52C41A"
        elif score >= QUALITY_THRESHOLDS['good']:
            icon, color = "👍", "#1890FF"
        elif score >= QUALITY_THRESHOLDS['fair']:
            icon, color = "⚠️", "#FAAD14"
        else:
            icon, color = "❌", "#FF4D4F"

        st.markdown(create_metric_card(
            "Data Quality",
            f"{icon} {score:.0f}%",
            "🎯",
            "Overall Score"
        ), unsafe_allow_html=True)

    st.markdown("---")

    # Data quality gauge and suggestions
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🎯 Data Quality")
        handler = FileHandler()
        quality = handler.get_quality_score(df)

        # Create gauge
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=quality['overall'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Quality Score"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#0072B2"},
                'steps': [
                    {'range': [0, 60], 'color': "#FFE5E5"},
                    {'range': [60, 75], 'color': "#FFF4E5"},
                    {'range': [75, 90], 'color': "#E5F4FF"},
                    {'range': [90, 100], 'color': "#E5FFE5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Quality breakdown
        st.markdown(f"""
        <div style="padding: 0.5rem;">
            <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                <span>Completeness:</span> <strong>{quality['completeness']:.1f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                <span>Uniqueness:</span> <strong>{quality['uniqueness']:.1f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                <span>Consistency:</span> <strong>{quality['consistency']:.1f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0.25rem 0;">
                <span>Validity:</span> <strong>{quality['validity']:.1f}%</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 💡 Suggested Template")
        template_mgr = TemplateManager()
        suggested = template_mgr.detect_best_template(df)

        if suggested:
            template = template_mgr.get_template(suggested)
            st.markdown(f"""
            <div class="alert alert-info">
                <h4>{template['icon']} {template['name']}</h4>
                <p>{template['description']}</p>
                <p style="font-size: 0.85rem; color: #666;">
                    Auto-detected based on your column names. You can apply this template
                    or customize your analysis manually.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Apply {template['name']} Template", type="primary"):
                st.session_state.selected_template = suggested
                st.session_state.template_applied = True
                show_success(f"Template '{template['name']}' applied!")
                st.rerun()
        else:
            st.info("No specific template detected. You can proceed with custom analysis.")

        # Data types
        st.markdown("### 🏷️ Data Types")
        handler = FileHandler()
        types_summary = handler.get_data_types_summary(df)

        type_cols = st.columns(4)
        for idx, (type_name, cols) in enumerate(types_summary.items()):
            if idx < 4 and cols:
                with type_cols[idx]:
                    st.markdown(f"""
                    <div class="info-card" style="text-align: center; padding: 0.75rem;">
                        <div class="card-title">{type_name.title()}</div>
                        <div class="card-value" style="font-size: 1.5rem;">{len(cols)}</div>
                        <div class="card-label">{', '.join(cols[:3])}{'...' if len(cols) > 3 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # Data preview
    st.markdown("### 👀 Data Preview")

    preview_type = st.radio(
        "Show:",
        ["First 10 rows", "Last 10 rows", "Random 10 rows"],
        horizontal=True
    )

    if preview_type == "First 10 rows":
        preview_df = df.head(10)
    elif preview_type == "Last 10 rows":
        preview_df = df.tail(10)
    else:
        preview_df = df.sample(min(10, len(df)))

    st.dataframe(preview_df, use_container_width=True, height=350)


# ============================================================
# TAB 2: INSPECT
# ============================================================
def render_inspect_tab():
    """Render inspect/clean tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar")
        return

    st.markdown(f'<h2 class="section-header">🔍 Inspect: {file_name}</h2>', unsafe_allow_html=True)

    # Data quality report
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Data Quality Report")
        handler = FileHandler()
        quality = handler.get_quality_score(df)

        missing_count = quality.get('missing_cells', 0)
        duplicate_count = quality.get('duplicate_rows', 0)

        st.markdown(f"""
        <div class="info-card">
            <div class="card-title">Missing Values</div>
            <div class="card-value">{missing_count:,}</div>
            <div class="card-label">{100 - quality['completeness']:.2f}% of total</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="margin-top: 0.5rem;">
            <div class="card-title">Duplicate Rows</div>
            <div class="card-value">{duplicate_count:,}</div>
            <div class="card-label">{quality.get('uniqueness', 100):.2f}% unique</div>
        </div>
        """, unsafe_allow_html=True)

        # Column types
        st.markdown("### 🏷️ Column Types")
        type_counts = df.dtypes.value_counts()
        for dtype, count in type_counts.items():
            st.markdown(f"- **{dtype}**: {count} columns")

    with col2:
        st.markdown("### 📊 Missing Values by Column")
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)

        if len(missing) > 0:
            import plotly.graph_objects as go
            fig = go.Figure(go.Bar(
                x=missing.values,
                y=missing.index,
                orientation='h',
                marker_color='#D55E00',
                text=missing.values,
                textposition='auto'
            ))
            fig.update_layout(
                height=400,
                template='plotly_white' if st.session_state.theme == 'light' else 'plotly_dark',
                yaxis={'autorange': 'reversed'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing values!")

        # Numeric summary
        st.markdown("### 📈 Numeric Summary")
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe(), use_container_width=True)

    st.markdown("---")

    # Data cleaning
    st.markdown("### 🧹 Data Cleaning")

    cleaning_action = st.selectbox(
        "Choose cleaning action:",
        ["None", "Remove Duplicates", "Handle Missing Values", "Filter Rows",
         "Change Data Type", "Remove Outliers"]
    )

    cleaner = DataCleaner()

    if cleaning_action == "Remove Duplicates":
        if st.button("Apply", key="clean_dup"):
            df_clean, result = cleaner.remove_duplicates(df)
            st.session_state.cleaned_data[file_name] = df_clean
            show_success(f"Removed {result['rows_removed']} duplicate rows")
            st.rerun()

    elif cleaning_action == "Handle Missing Values":
        col1, col2 = st.columns(2)
        with col1:
            strategy = st.selectbox("Strategy", ["mean", "median", "mode", "ffill", "bfill", "drop_rows", "drop_cols"])
        with col2:
            cols_to_clean = st.multiselect("Columns (empty = all with missing)",
                                          options=df.columns[df.isnull().any()].tolist())

        if st.button("Apply", key="clean_missing"):
            df_clean, result = cleaner.handle_missing_values(df, strategy, cols_to_clean)
            if 'error' not in result:
                st.session_state.cleaned_data[file_name] = df_clean
                show_success(f"Handled {result.get('values_filled', 0)} missing values")
                st.rerun()
            else:
                show_error(result['error'])

    elif cleaning_action == "Filter Rows":
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_col = st.selectbox("Column", df.columns.tolist())
        with col2:
            operator = st.selectbox("Operator", ["==", "!=", ">", "<", ">=", "<=", "contains", "not_contains"])
        with col3:
            filter_val = st.text_input("Value")

        if st.button("Apply", key="clean_filter") and filter_val:
            try:
                # Try numeric conversion
                try:
                    filter_val_typed = float(filter_val) if '.' in filter_val else int(filter_val)
                except:
                    filter_val_typed = filter_val

                df_clean, result = cleaner.filter_rows(df, filter_col, operator, filter_val_typed)
                if 'error' not in result:
                    st.session_state.cleaned_data[file_name] = df_clean
                    show_success(f"Filtered to {result['rows_after']} rows")
                    st.rerun()
                else:
                    show_error(result['error'])
            except Exception as e:
                show_error(str(e))

    elif cleaning_action == "Change Data Type":
        col1, col2 = st.columns(2)
        with col1:
            dtype_col = st.selectbox("Column", df.columns.tolist())
        with col2:
            new_type = st.selectbox("New Type", ["int", "float", "str", "datetime", "category", "bool"])

        if st.button("Apply", key="clean_dtype"):
            df_clean, result = cleaner.change_data_type(df, dtype_col, new_type)
            if 'error' not in result:
                st.session_state.cleaned_data[file_name] = df_clean
                show_success(f"Changed {dtype_col} to {new_type}")
                st.rerun()
            else:
                show_error(result['error'])

    elif cleaning_action == "Remove Outliers":
        col1, col2, col3 = st.columns(3)
        with col1:
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            out_cols = st.multiselect("Columns", numeric_cols)
        with col2:
            out_method = st.selectbox("Method", ["iqr", "z_score"])
        with col3:
            out_action = st.selectbox("Action", ["remove", "flag", "cap"])

        if st.button("Apply", key="clean_outliers") and out_cols:
            df_clean, result = cleaner.remove_outliers(df, out_cols, out_method, out_action)
            st.session_state.cleaned_data[file_name] = df_clean
            show_success(f"Processed {result['outliers_found']} outliers")
            st.rerun()

    # Show cleaning log
    if cleaner.get_cleaning_log():
        with st.expander("📝 Cleaning History"):
            for entry in cleaner.get_cleaning_log():
                st.json(entry)


# ============================================================
# TAB 3: ANALYSIS
# ============================================================
def render_analysis_tab():
    """Render analysis tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar")
        return

    st.markdown(f'<h2 class="section-header">📈 Analysis: {file_name}</h2>', unsafe_allow_html=True)

    # Analysis options
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 🔧 Analysis Options")

        analysis_options = {
            'basic': st.checkbox("📊 Basic Statistics", value=True, help="Mean, median, std, etc."),
            'advanced': st.checkbox("🔬 Advanced Statistics", help="Normality tests, etc."),
            'correlation': st.checkbox("🔗 Correlations", value=True, help="Pearson, Spearman, Kendall"),
            'regression': st.checkbox("📐 Regression Analysis", help="Linear/polynomial regression"),
            'hypothesis': st.checkbox("🧪 Hypothesis Testing", help="T-tests, ANOVA, chi-square"),
            'anomaly': st.checkbox("⚠️ Anomaly Detection", help="Find outliers in data"),
            'forecast': st.checkbox("🔮 Time-Series Forecasting", help="Predict future values")
        }

        st.markdown("---")

        # Additional options
        with st.expander("⚙️ Advanced Options"):
            forecast_periods = st.slider("Forecast Periods", 7, 90, 30)
            anomaly_method = st.selectbox("Anomaly Method", ["iqr", "z_score", "isolation_forest"])
            confidence_level = st.slider("Confidence Level", 0.80, 0.99, 0.95, 0.01)

    with col2:
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing data..."):
                run_analysis(df, file_name, analysis_options, {
                    'forecast_periods': forecast_periods,
                    'anomaly_method': anomaly_method,
                    'confidence_level': confidence_level
                })


def run_analysis(df, file_name, options, advanced_opts):
    """Run selected analyses"""
    analyzer = DataAnalyzer()
    results = {}

    progress = st.progress(0)
    status = st.empty()

    # Basic statistics
    if options.get('basic'):
        status.text("📊 Calculating basic statistics...")
        progress.progress(15)
        results['statistics'] = analyzer.basic_statistics(df)

    # Advanced statistics
    if options.get('advanced'):
        status.text("🔬 Running advanced statistics...")
        progress.progress(30)
        results['advanced'] = analyzer.advanced_statistics(df)

    # Correlations
    if options.get('correlation'):
        status.text("🔗 Computing correlations...")
        progress.progress(45)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if len(numeric_cols) >= 2:
            results['correlations'] = analyzer.correlation_analysis(df, numeric_cols)

    # Regression
    if options.get('regression'):
        status.text("📐 Performing regression...")
        progress.progress(60)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if len(numeric_cols) >= 2:
            results['regression'] = analyzer.regression_analysis(
                df, numeric_cols[0], numeric_cols[1], degree=1
            )

    # Hypothesis testing
    if options.get('hypothesis'):
        status.text("🧪 Running hypothesis tests...")
        progress.progress(75)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if numeric_cols:
            results['hypothesis'] = analyzer.hypothesis_test(
                df, 't_test_one', column=numeric_cols[0], popmean=df[numeric_cols[0]].mean()
            )

    # Anomalies
    if options.get('anomaly'):
        status.text("⚠️ Detecting anomalies...")
        progress.progress(85)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        results['anomalies'] = analyzer.detect_anomalies(
            df, numeric_cols, method=advanced_opts['anomaly_method']
        )

    # Forecasting
    if options.get('forecast'):
        status.text("🔮 Forecasting future values...")
        progress.progress(95)
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        if not date_cols:
            # Try to detect date column
            for col in df.columns:
                try:
                    pd.to_datetime(df[col], errors='raise')
                    date_cols = [col]
                    break
                except:
                    pass

        if date_cols and numeric_cols:
            try:
                df_temp = df.copy()
                df_temp[date_cols[0]] = pd.to_datetime(df_temp[date_cols[0]], errors='coerce')
                df_temp = df_temp.dropna(subset=[date_cols[0]])

                results['forecasts'] = {
                    numeric_cols[0]: analyzer.time_series_forecast(
                        df_temp, date_cols[0], numeric_cols[0],
                        periods=advanced_opts['forecast_periods'],
                        method='linear'
                    )
                }
            except Exception as e:
                results['forecasts'] = {'error': str(e)}

    progress.progress(100)
    status.text("✅ Analysis complete!")

    # Store results
    st.session_state.analysis_results[file_name] = results

    # Display results
    display_analysis_results(results, df)


def display_analysis_results(results, df):
    """Display analysis results in expandable sections"""
    st.markdown("---")
    st.markdown("### 📊 Analysis Results")

    # Basic statistics
    if 'statistics' in results:
        with st.expander("📊 Basic Statistics", expanded=True):
            stats = results['statistics']
            stats_df = pd.DataFrame(stats).T
            st.dataframe(stats_df, use_container_width=True)

    # Advanced statistics
    if 'advanced' in results:
        with st.expander("🔬 Advanced Statistics", expanded=False):
            st.json(results['advanced'])

    # Correlations
    if 'correlations' in results:
        with st.expander("🔗 Correlation Analysis", expanded=True):
            corr = results['correlations']
            viz = Visualization(st.session_state.theme, st.session_state.color_palette)

            # Show heatmap
            if 'pearson' in corr:
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                if numeric_cols:
                    fig = viz.correlation_heatmap(df, numeric_cols, 'pearson')
                    st.plotly_chart(fig, use_container_width=True)

            # Show strong correlations
            if corr.get('pearson', {}).get('strong_pairs'):
                st.markdown("#### Strong Correlations (|r| ≥ 0.7)")
                pairs_df = pd.DataFrame(corr['pearson']['strong_pairs'])
                st.dataframe(pairs_df, use_container_width=True)

    # Regression
    if 'regression' in results and 'error' not in results['regression']:
        with st.expander("📐 Regression Analysis", expanded=True):
            reg = results['regression']
            viz = Visualization(st.session_state.theme, st.session_state.color_palette)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("R²", f"{reg['r_squared']:.4f}")
            with col2:
                st.metric("RMSE", f"{reg['rmse']:.4f}")
            with col3:
                st.metric("MAE", f"{reg['mae']:.4f}")
            with col4:
                st.metric("Degree", reg['degree'])

            st.markdown(f"**Equation:** `{reg.get('equation', 'N/A')}`")

            # Plot
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if len(numeric_cols) >= 2:
                fig = viz.regression_plot(reg, numeric_cols[0], numeric_cols[1])
                st.plotly_chart(fig, use_container_width=True)

    # Anomalies
    if 'anomalies' in results and results['anomalies']:
        with st.expander("⚠️ Anomaly Detection", expanded=True):
            viz = Visualization(st.session_state.theme, st.session_state.color_palette)

            for col, info in list(results['anomalies'].items())[:3]:
                st.markdown(f"**{col}**: {info['count']} anomalies ({info['percentage']:.2f}%)")

                if info.get('anomalies'):
                    anom_df = pd.DataFrame(info['anomalies'][:20])
                    st.dataframe(anom_df, use_container_width=True)

    # Forecasts
    if 'forecasts' in results:
        with st.expander("🔮 Forecasts", expanded=True):
            viz = Visualization(st.session_state.theme, st.session_state.color_palette)
            forecasts = results['forecasts']

            for col, forecast in forecasts.items():
                if isinstance(forecast, dict) and 'error' not in forecast:
                    st.markdown(f"**{col}** - Method: {forecast.get('method', 'N/A')}")
                    fig = viz.forecast_plot(forecast)
                    st.plotly_chart(fig, use_container_width=True)
                elif 'error' in forecast:
                    st.warning(f"Forecast error: {forecast['error']}")


# ============================================================
# TAB 4: VISUALIZE
# ============================================================
def render_visualize_tab():
    """Render visualization tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar")
        return

    st.markdown(f'<h2 class="section-header">🎨 Visualize: {file_name}</h2>', unsafe_allow_html=True)

    viz = Visualization(st.session_state.theme, st.session_state.color_palette)

    # Chart configuration
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("### 📊 Chart Type")

        # Categorize charts
        chart_type = st.selectbox(
            "Select chart type",
            [
                "Histogram", "Box Plot", "Violin Plot", "Scatter Plot",
                "Q-Q Plot", "Distribution Plot",
                "Bar Chart", "Pie Chart", "Treemap", "Sunburst",
                "Line Chart", "Area Chart",
                "Correlation Heatmap", "Pair Plot", "Bubble Chart",
                "3D Scatter", "Parallel Coordinates", "Missing Values Heatmap"
            ]
        )

        palette = st.selectbox("Color Palette", list(COLOR_PALETTES.keys()),
                              index=list(COLOR_PALETTES.keys()).index(st.session_state.color_palette))
        st.session_state.color_palette = palette

        chart_height = st.slider("Chart Height", 300, 1000, st.session_state.chart_height, 50)

    with col2:
        st.markdown("### 📋 Data Selection")

        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Smart column selection based on chart type
        col_selections = {}

        if chart_type in ["Histogram", "Box Plot", "Violin Plot", "Q-Q Plot", "Distribution Plot"]:
            if numeric_cols:
                col_selections['column'] = st.selectbox("Column", numeric_cols)

        elif chart_type == "Scatter Plot":
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    col_selections['x'] = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                with col2:
                    default_idx = min(1, len(numeric_cols)-1)
                    col_selections['y'] = st.selectbox("Y-axis", numeric_cols, index=default_idx, key="scatter_y")
                if cat_cols:
                    col_selections['color'] = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="scatter_color")

        elif chart_type in ["Bar Chart", "Pie Chart"]:
            target_cols = cat_cols if cat_cols else df.columns.tolist()
            col_selections['column'] = st.selectbox("Column", target_cols)

        elif chart_type in ["Treemap", "Sunburst"]:
            target_cols = cat_cols if cat_cols else df.columns.tolist()
            if target_cols:
                col_selections['path'] = st.multiselect("Hierarchy (path)", target_cols, default=target_cols[:2] if len(target_cols) >= 2 else target_cols[:1])

        elif chart_type in ["Line Chart", "Area Chart"]:
            x_options = date_cols + numeric_cols
            if not x_options:
                x_options = df.columns.tolist()
            if x_options:
                col_selections['x'] = st.selectbox("X-axis (time)", x_options)
                if numeric_cols:
                    col_selections['y'] = st.multiselect("Y-axis values", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols[:1])

        elif chart_type == "Correlation Heatmap":
            if len(numeric_cols) >= 2:
                col_selections['columns'] = st.multiselect("Columns", numeric_cols, default=numeric_cols[:min(8, len(numeric_cols))])

        elif chart_type == "Pair Plot":
            if len(numeric_cols) >= 2:
                col_selections['columns'] = st.multiselect("Columns", numeric_cols, default=numeric_cols[:min(4, len(numeric_cols))])
                if cat_cols:
                    col_selections['color'] = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="pair_color")

        elif chart_type == "Bubble Chart":
            if len(numeric_cols) >= 3:
                col1, col2, col3 = st.columns(3)
                with col1:
                    col_selections['x'] = st.selectbox("X-axis", numeric_cols, key="bubble_x")
                with col2:
                    col_selections['y'] = st.selectbox("Y-axis", numeric_cols, index=1, key="bubble_y")
                with col3:
                    col_selections['size'] = st.selectbox("Size", numeric_cols, index=2, key="bubble_size")

        elif chart_type == "3D Scatter":
            if len(numeric_cols) >= 3:
                col1, col2, col3 = st.columns(3)
                with col1:
                    col_selections['x'] = st.selectbox("X", numeric_cols, key="3d_x")
                with col2:
                    col_selections['y'] = st.selectbox("Y", numeric_cols, index=1, key="3d_y")
                with col3:
                    col_selections['z'] = st.selectbox("Z", numeric_cols, index=2, key="3d_z")
                if cat_cols:
                    col_selections['color'] = st.selectbox("Color (optional)", ["None"] + cat_cols, key="3d_color")

    with col3:
        st.markdown("### 💾 Export")

        if st.button("📥 Download as PNG", use_container_width=True):
            st.info("Use the camera/download icon on the chart")

    st.markdown("---")

    # Generate and display chart
    try:
        fig = None

        if chart_type == "Histogram" and 'column' in col_selections:
            fig = viz.histogram(df, col_selections['column'], show_kde=True)

        elif chart_type == "Box Plot" and 'column' in col_selections:
            fig = viz.box_plot(df, [col_selections['column']])

        elif chart_type == "Violin Plot" and 'column' in col_selections:
            fig = viz.violin_plot(df, [col_selections['column']])

        elif chart_type == "Scatter Plot" and 'x' in col_selections:
            color = col_selections.get('color')
            if color == "None":
                color = None
            fig = viz.scatter_plot(df, col_selections['x'], col_selections['y'], color)

        elif chart_type == "Q-Q Plot" and 'column' in col_selections:
            fig = viz.qq_plot(df, col_selections['column'])

        elif chart_type == "Distribution Plot" and 'column' in col_selections:
            fig = viz.distribution_plot(df, col_selections['column'])

        elif chart_type == "Bar Chart" and 'column' in col_selections:
            fig = viz.bar_chart(df, col_selections['column'])

        elif chart_type == "Pie Chart" and 'column' in col_selections:
            fig = viz.pie_chart(df, col_selections['column'])

        elif chart_type in ["Treemap", "Sunburst"] and 'path' in col_selections and col_selections['path']:
            if chart_type == "Treemap":
                fig = viz.treemap(df, col_selections['path'])
            else:
                fig = viz.sunburst(df, col_selections['path'])

        elif chart_type == "Line Chart" and 'x' in col_selections and col_selections.get('y'):
            fig = viz.line_chart(df, col_selections['x'], col_selections['y'])

        elif chart_type == "Area Chart" and 'x' in col_selections and col_selections.get('y'):
            fig = viz.area_chart(df, col_selections['x'], col_selections['y'])

        elif chart_type == "Correlation Heatmap" and col_selections.get('columns') and len(col_selections['columns']) >= 2:
            fig = viz.correlation_heatmap(df, col_selections['columns'])

        elif chart_type == "Pair Plot" and col_selections.get('columns') and len(col_selections['columns']) >= 2:
            color = col_selections.get('color')
            if color == "None":
                color = None
            fig = viz.pair_plot(df, col_selections['columns'], color)

        elif chart_type == "Bubble Chart" and all(k in col_selections for k in ['x', 'y', 'size']):
            fig = viz.bubble_chart(df, col_selections['x'], col_selections['y'], col_selections['size'])

        elif chart_type == "3D Scatter" and all(k in col_selections for k in ['x', 'y', 'z']):
            color = col_selections.get('color')
            if color == "None":
                color = None
            fig = viz.scatter_3d(df, col_selections['x'], col_selections['y'], col_selections['z'], color)

        elif chart_type == "Missing Values Heatmap":
            fig = viz.missing_values_heatmap(df)

        if fig:
            st.plotly_chart(fig, use_container_width=True, height=chart_height)
        else:
            show_warning("Please select valid columns for this chart type")

    except Exception as e:
        show_error(f"Chart generation failed: {str(e)}")


# ============================================================
# TAB 5: REPORT
# ============================================================
def render_report_tab():
    """Render report generation tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar")
        return

    st.markdown(f'<h2 class="section-header">📄 Report: {file_name}</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ⚙️ Report Configuration")

        report_title = st.text_input("Report Title", value=f"Analysis Report - {file_name}")

        report_template = st.selectbox(
            "Template",
            list(REPORT_TEMPLATES.keys()),
            format_func=lambda x: REPORT_TEMPLATES[x]['name'],
            index=list(REPORT_TEMPLATES.keys()).index(st.session_state.report_template)
        )

        st.markdown("### 📑 Sections to Include")
        include_cover = st.checkbox("📄 Cover Page", value=True)
        include_exec = st.checkbox("📊 Executive Summary", value=True)
        include_overview = st.checkbox("🔍 Data Overview", value=True)
        include_quality = st.checkbox("✅ Data Quality", value=True)
        include_stats = st.checkbox("📈 Summary Statistics", value=True)
        include_corr = st.checkbox("🔗 Correlation Analysis", value=True)
        include_anom = st.checkbox("⚠️ Anomalies", value=True)
        include_forecast = st.checkbox("🔮 Forecasts", value=True)
        include_concl = st.checkbox("💡 Conclusions", value=True)

        report_notes = st.text_area("Notes / Annotations", placeholder="Add any notes for the report...")

        watermark = st.text_input("Watermark (optional)", placeholder="e.g., CONFIDENTIAL, DRAFT")

    with col2:
        st.markdown("### 👁️ Preview & Generate")

        if st.button("🎨 Generate Report", type="primary", use_container_width=True):
            generate_report(file_name, df, {
                'title': report_title,
                'template': report_template,
                'notes': report_notes,
                'watermark': watermark,
                'sections': {
                    'cover_page': include_cover,
                    'executive_summary': include_exec,
                    'data_overview': include_overview,
                    'data_quality': include_quality,
                    'summary_statistics': include_stats,
                    'correlation_analysis': include_corr,
                    'anomalies': include_anom,
                    'forecasts': include_forecast,
                    'conclusions': include_concl
                }
            })


def generate_report(file_name, df, config):
    """Generate and offer report downloads"""
    with st.spinner("Generating report..."):
        try:
            # Gather all analysis data
            handler = FileHandler()
            analyzer = DataAnalyzer()

            # Get quality score
            quality = handler.get_quality_score(df)

            # Get statistics
            stats = analyzer.basic_statistics(df)

            # Get correlations
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            correlations = {}
            if len(numeric_cols) >= 2:
                correlations = analyzer.correlation_analysis(df, numeric_cols)

            # Get anomalies
            anomalies = analyzer.detect_anomalies(df, numeric_cols, method='iqr')

            # Get forecasts
            forecasts = {}
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            if not date_cols:
                for col in df.columns:
                    try:
                        pd.to_datetime(df[col], errors='raise')
                        date_cols = [col]
                        break
                    except:
                        pass

            if date_cols and numeric_cols:
                df_temp = df.copy()
                df_temp[date_cols[0]] = pd.to_datetime(df_temp[date_cols[0]], errors='coerce')
                df_temp = df_temp.dropna(subset=[date_cols[0]])
                if not df_temp.empty:
                    forecasts[numeric_cols[0]] = analyzer.time_series_forecast(
                        df_temp, date_cols[0], numeric_cols[0], periods=30, method='linear'
                    )

            # Data types
            data_types = handler.get_data_types_summary(df)

            # Build analysis data
            analysis_data = {
                'file_name': file_name,
                'file_size': f"{st.session_state.uploaded_files[file_name]['metadata']['size_mb']} MB",
                'file_format': st.session_state.uploaded_files[file_name]['metadata']['format'],
                'overview': {
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'quality_score': quality,
                'statistics': stats,
                'correlations': correlations,
                'anomalies': anomalies,
                'forecasts': forecasts,
                'data_types': data_types,
                'key_findings': [
                    f"Analyzed {len(df):,} rows across {len(df.columns)} columns",
                    f"Data quality score: {quality['overall']:.1f}%",
                    f"Found {sum(v.get('count', 0) for v in anomalies.values())} total anomalies",
                    f"Identified {len(correlations.get('pearson', {}).get('strong_pairs', []))} strong correlations"
                ]
            }

            # Generate report
            report_gen = ReportGenerator(
                template=config['template'],
                customizations=config
            )

            st.success("✅ Report generated successfully!")

            st.markdown("### 📥 Download Options")

            col1, col2, col3 = st.columns(3)

            # HTML Report
            with col1:
                html_content = report_gen.generate_html_report(analysis_data)
                st.download_button(
                    "📄 Download HTML",
                    data=html_content.encode('utf-8'),
                    file_name=f"report_{file_name}_{get_current_timestamp()}.html",
                    mime="text/html",
                    use_container_width=True
                )

            # PDF Report
            with col2:
                pdf_content = report_gen.generate_pdf_report(analysis_data)
                if pdf_content:
                    st.download_button(
                        "📕 Download PDF",
                        data=pdf_content,
                        file_name=f"report_{file_name}_{get_current_timestamp()}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("PDF not available")

            # DOCX Report
            with col3:
                docx_content = report_gen.generate_docx_report(analysis_data)
                if docx_content:
                    st.download_button(
                        "📘 Download DOCX",
                        data=docx_content,
                        file_name=f"report_{file_name}_{get_current_timestamp()}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                else:
                    st.info("DOCX not available")

            # JSON Report
            json_content = report_gen.generate_json_report(analysis_data)
            st.download_button(
                "📋 Download JSON (Full Analysis Data)",
                data=json_content.encode('utf-8'),
                file_name=f"report_{file_name}_{get_current_timestamp()}.json",
                mime="application/json",
                use_container_width=True
            )

        except Exception as e:
            show_error(f"Report generation failed: {str(e)}")


# ============================================================
# TAB 6: EXPORT
# ============================================================
def render_export_tab():
    """Render export tab"""
    df, file_name, file_data = get_selected_data()

    if df is None:
        show_info("👈 Please upload and select a file from the sidebar")
        return

    st.markdown(f'<h2 class="section-header">⬇️ Export: {file_name}</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Export data
    with col1:
        st.markdown("### 📊 Data Export")
        st.markdown("Export the raw data in various formats.")

        csv_data = export_dataframe_to_csv(df)
        st.download_button(
            "📄 Download CSV",
            data=csv_data,
            file_name=f"{file_name}_{get_current_timestamp()}.csv",
            mime="text/csv",
            use_container_width=True
        )

        json_data = export_dataframe_to_json(df)
        st.download_button(
            "📋 Download JSON",
            data=json_data,
            file_name=f"{file_name}_{get_current_timestamp()}.json",
            mime="application/json",
            use_container_width=True
        )

        try:
            excel_data = export_dataframe_to_excel(df)
            st.download_button(
                "📊 Download Excel",
                data=excel_data,
                file_name=f"{file_name}_{get_current_timestamp()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except:
            pass

    # Export statistics
    with col2:
        st.markdown("### 📈 Statistics Export")
        st.markdown("Export computed statistics.")

        if st.button("📊 Generate Statistics Export", use_container_width=True):
            analyzer = DataAnalyzer()
            stats = analyzer.basic_statistics(df)
            stats_df = pd.DataFrame(stats).T
            csv_stats = stats_df.to_csv().encode('utf-8')

            st.download_button(
                "📥 Download Statistics (CSV)",
                data=csv_stats,
                file_name=f"statistics_{file_name}_{get_current_timestamp()}.csv",
                mime="text/csv",
                key="stats_csv"
            )

            try:
                excel_stats = io.BytesIO()
                with pd.ExcelWriter(excel_stats, engine='openpyxl') as writer:
                    stats_df.to_excel(writer, sheet_name='Statistics')
                excel_stats.seek(0)

                st.download_button(
                    "📥 Download Statistics (Excel)",
                    data=excel_stats.getvalue(),
                    file_name=f"statistics_{file_name}_{get_current_timestamp()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="stats_excel"
                )
            except:
                pass

    # Batch export
    with col3:
        st.markdown("### 📦 Batch Export")
        st.markdown("Export everything as ZIP.")

        if st.button("📦 Generate Complete Package", use_container_width=True):
            try:
                with st.spinner("Creating ZIP package..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                        # Add CSV
                        zf.writestr(f"{file_name}.csv", export_dataframe_to_csv(df))
                        # Add JSON
                        zf.writestr(f"{file_name}.json", export_dataframe_to_json(df))
                        # Add metadata
                        metadata = {
                            'file_name': file_name,
                            'export_date': datetime.now().isoformat(),
                            'rows': len(df),
                            'columns': len(df.columns),
                            'version': '1.1.0'
                        }
                        zf.writestr("metadata.json", json.dumps(metadata, indent=2))

                        # Add statistics if available
                        if file_name in st.session_state.analysis_results:
                            stats = st.session_state.analysis_results[file_name].get('statistics', {})
                            if stats:
                                stats_df = pd.DataFrame(stats).T
                                zf.writestr("statistics.csv", stats_df.to_csv())

                zip_buffer.seek(0)
                st.download_button(
                    "📥 Download ZIP Package",
                    data=zip_buffer.getvalue(),
                    file_name=f"analysis_package_{file_name}_{get_current_timestamp()}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                show_success("Package created!")
            except Exception as e:
                show_error(f"Package creation failed: {str(e)}")


# ============================================================
# MAIN APP
# ============================================================
def main():
    """Main application function"""

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Process any uploaded files from session
    if 'pending_uploads' not in st.session_state:
        st.session_state.pending_uploads = None

    # Get files from file uploader (handled in sidebar)

    # Main content area
    if not st.session_state.uploaded_files:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📊</div>
            <h1 style="background: linear-gradient(90deg, #0072B2 0%, #009E73 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2.5rem; margin-bottom: 1rem;">
                Welcome to DataInsight Pro
            </h1>
            <p style="font-size: 1.2rem; color: #888; margin-bottom: 2rem;">
                Enterprise Analytics Platform v1.1.0
            </p>
            <p style="font-size: 1rem; color: #666; max-width: 600px; margin: 0 auto 2rem auto;">
                Transform your data into insights with professional analytics.
                Upload CSV or Excel files to get started, or try our sample datasets.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        st.markdown("### ✨ Key Features")

        col1, col2, col3 = st.columns(3)

        features = [
            ("📁", "Multi-File Upload", "Upload multiple files at once. Support for CSV and Excel formats up to 75MB each."),
            ("🎨", "Beautiful Visualizations", "20+ chart types including histograms, scatter plots, 3D visualizations, and more."),
            ("📊", "Advanced Statistics", "Normality tests, correlations, regression, hypothesis testing, and forecasting."),
            ("🧹", "Data Cleaning", "Handle missing values, remove duplicates, filter, and transform your data with ease."),
            ("📄", "Custom Reports", "Generate professional PDF, HTML, and DOCX reports with custom branding."),
            ("📱", "Mobile Responsive", "Works perfectly on desktop, tablet, and mobile devices.")
        ]

        for idx, (icon, title, desc) in enumerate(features):
            with [col1, col2, col3][idx % 3]:
                st.markdown(f"""
                <div class="info-card fade-in" style="margin-bottom: 1rem;">
                    <div class="card-icon" style="font-size: 2.5rem;">{icon}</div>
                    <div class="card-title" style="margin-top: 0.5rem;">{title}</div>
                    <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Quick start
        st.markdown("### 🚀 Quick Start")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **1️⃣ Upload Data**
            - Click "Upload CSV or Excel files" in the sidebar
            - Select one or multiple files
            - Or try a sample dataset
            """)

        with col2:
            st.markdown("""
            **2️⃣ Analyze**
            - Go to "Analysis" tab
            - Select statistics to run
            - View comprehensive results
            """)

        with col3:
            st.markdown("""
            **3️⃣ Visualize & Export**
            - Create beautiful charts
            - Generate custom reports
            - Download in multiple formats
            """)

    else:
        # Show tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview", "🔍 Inspect", "📈 Analysis",
            "🎨 Visualize", "📄 Report", "⬇️ Export"
        ])

        with tab1:
            render_overview_tab()

        with tab2:
            render_inspect_tab()

        with tab3:
            render_analysis_tab()

        with tab4:
            render_visualize_tab()

        with tab5:
            render_report_tab()

        with tab6:
            render_export_tab()

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #888; font-size: 0.85rem; padding: 1rem;">
        <strong>{APP_NAME}</strong> v{APP_VERSION} • {APP_TAGLINE}<br>
        Built with ❤️ using Streamlit • Enterprise Analytics Platform
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
