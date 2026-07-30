"""
Utilities Module
Helper functions used across the application
"""

import streamlit as st
import pandas as pd
import plotly.io as pio
from typing import Dict, Any
from datetime import datetime
import base64
import io


def get_theme_css(theme: str) -> str:
    """Get theme CSS based on selection"""
    if theme == 'dark':
        try:
            with open('styles/theme_dark.css', 'r') as f:
                return f.read()
        except:
            return ""
    else:
        try:
            with open('styles/theme_light.css', 'r') as f:
                return f.read()
        except:
            return ""


def get_animations_css() -> str:
    """Get animations CSS"""
    try:
        with open('styles/animations.css', 'r') as f:
            return f.read()
    except:
        return ""


def apply_theme(theme: str):
    """Apply theme to Streamlit app"""
    css = get_theme_css(theme) + get_animations_css()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


def create_metric_card(label: str, value: Any, icon: str = "📊", help_text: str = "") -> str:
    """Create a metric card HTML"""
    return f"""
    <div class="info-card fade-in">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{label}</div>
        <div class="card-value">{value}</div>
        {f'<div class="card-label">{help_text}</div>' if help_text else ''}
    </div>
    """


def create_file_item(file_meta: Dict) -> str:
    """Create a file list item HTML"""
    return f"""
    <div class="file-item">
        <div class="file-info">
            <span class="file-icon">{file_meta['icon']}</span>
            <div>
                <div class="file-name">{file_meta['name']}</div>
                <div class="file-meta">
                    {file_meta['size_mb']} MB • {file_meta['rows']:,} rows • {file_meta['columns']} columns
                </div>
            </div>
        </div>
    </div>
    """


def create_status_badge(status: str) -> str:
    """Create status badge HTML"""
    status_class = f"status-{status}"
    status_text = status.capitalize()
    return f'<span class="{status_class}">{status_text}</span>'


def create_data_type_badge(dtype: str) -> str:
    """Create data type badge HTML"""
    if pd.api.types.is_numeric_dtype(pd.Series([1])):
        if 'int' in str(dtype) or 'float' in str(dtype):
            return f'<span class="badge badge-numeric">{dtype}</span>'

    if pd.api.types.is_datetime64_any_dtype(pd.Series([pd.Timestamp.now()])):
        if 'datetime' in str(dtype):
            return f'<span class="badge badge-datetime">{dtype}</span>'

    dtype_str = str(dtype).lower()
    if 'datetime' in dtype_str or 'date' in dtype_str:
        return f'<span class="badge badge-datetime">{dtype}</span>'
    elif 'int' in dtype_str or 'float' in dtype_str:
        return f'<span class="badge badge-numeric">{dtype}</span>'
    elif 'bool' in dtype_str:
        return f'<span class="badge badge-boolean">{dtype}</span>'
    else:
        return f'<span class="badge badge-categorical">{dtype}</span>'


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"


def download_button(data: Any, filename: str, mime: str, label: str, key: str = None):
    """Create a download button"""
    if isinstance(data, str):
        data = data.encode()
    elif isinstance(data, bytes):
        pass
    else:
        data = str(data).encode()

    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        key=key
    )


def show_error(message: str, suggestion: str = ""):
    """Show user-friendly error"""
    st.error(f"❌ {message}")
    if suggestion:
        st.info(f"💡 **Suggestion:** {suggestion}")


def show_success(message: str):
    """Show success message"""
    st.success(f"✅ {message}")


def show_info(message: str):
    """Show info message"""
    st.info(f"ℹ️ {message}")


def show_warning(message: str):
    """Show warning message"""
    st.warning(f"⚠️ {message}")


def get_sample_data_files() -> Dict[str, str]:
    """Get list of sample data files"""
    return {
        'Sales Data': 'sample_data/sample_sales.csv',
        'Research Data': 'sample_data/sample_research.csv',
        'Temperature Data': 'sample_data/sample_temperature.csv'
    }


def export_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """Export DataFrame to CSV bytes"""
    return df.to_csv(index=False).encode('utf-8')


def export_dataframe_to_json(df: pd.DataFrame) -> bytes:
    """Export DataFrame to JSON bytes"""
    return df.to_json(orient='records', indent=2).encode('utf-8')


def export_dataframe_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel bytes"""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return buffer.getvalue()


def get_current_timestamp() -> str:
    """Get current timestamp string"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def safe_division(a: float, b: float, default: float = 0) -> float:
    """Safe division with default"""
    try:
        if b == 0:
            return default
        return a / b
    except:
        return default


def truncate_string(s: str, max_length: int = 50) -> str:
    """Truncate string with ellipsis"""
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."


def get_dataframe_info(df: pd.DataFrame) -> Dict:
    """Get comprehensive DataFrame info"""
    if df is None or df.empty:
        return {}

    return {
        'shape': df.shape,
        'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        'dtypes': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'numeric_cols': df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_cols': df.select_dtypes(include=['datetime64']).columns.tolist()
    }
