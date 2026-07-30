"""
DataInsight Pro v1.1.0 - Configuration
Enterprise-ready analytics platform configuration
"""

# ============================================================
# APP METADATA
# ============================================================
APP_NAME = "DataInsight Pro"
APP_VERSION = "1.1.0"
APP_TAGLINE = "Enterprise Analytics Platform"
APP_DESCRIPTION = "Transform your data into insights with professional analytics"

# ============================================================
# FILE HANDLING
# ============================================================
MAX_FILE_SIZE_MB = 75  # Updated from 50
SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
MAX_ROWS = 500000
MAX_FILES_UPLOAD = 20
ENCODING_OPTIONS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

# ============================================================
# CHARTS & VISUALIZATION
# ============================================================
CHART_HEIGHT = 600
CHART_WIDTH = 1000
CHART_MIN_HEIGHT = 300
CHART_MAX_HEIGHT = 1000
CHART_MIN_WIDTH = 400
CHART_MAX_WIDTH = 1400

COLOR_PALETTES = {
    'Viridis': ['#440154', '#3B528B', '#21908C', '#5DC863', '#FDE725'],
    'Plasma': ['#0D0887', '#6A00A8', '#B12A90', '#E16462', '#FCA636'],
    'Cool': ['#00BFFF', '#1E90FF', '#4169E1', '#0000CD', '#00008B'],
    'Warm': ['#FF6B6B', '#FF8E53', '#FFA500', '#FF6347', '#DC143C'],
    'Blues': ['#08306B', '#08519C', '#2171B5', '#4292C6', '#6BAED6'],
    'Greens': ['#00441B', '#006D2C', '#238B45', '#41AB5D', '#74C476'],
    'Reds': ['#67000D', '#A50F15', '#CB181D', '#EF3B2C', '#FB6A4A'],
    'Custom': ['#0072B2', '#009E73', '#D55E00', '#F0E442', '#56B4E9']
}

# ============================================================
# FEATURE TOGGLES
# ============================================================
ENABLE_ADVANCED_STATS = True
ENABLE_FORECASTING = True
ENABLE_ANOMALY_DETECTION = True
ENABLE_TEMPLATES = True
ENABLE_DATA_CLEANING = True
ENABLE_PROFILE_MANAGER = True
ENABLE_COMPARISON_MODE = True
ENABLE_BOOKMARKING = False  # Future feature

# ============================================================
# THEME COLORS
# ============================================================
THEME_COLORS = {
    'light': {
        'primary': '#0072B2',
        'secondary': '#009E73',
        'accent': '#D55E00',
        'background': '#FFFFFF',
        'text': '#1F1F1F',
        'cards': '#F5F5F5',
        'border': '#E0E0E0',
        'success': '#52C41A',
        'warning': '#FAAD14',
        'error': '#FF4D4F',
        'info': '#1890FF'
    },
    'dark': {
        'primary': '#56B4E9',
        'secondary': '#52C41A',
        'accent': '#FF7A45',
        'background': '#1E1E1E',
        'text': '#E8E8E8',
        'cards': '#2D2D2D',
        'border': '#404040',
        'success': '#73D13D',
        'warning': '#FFC53D',
        'error': '#FF7875',
        'info': '#40A9FF'
    }
}

# ============================================================
# TYPOGRAPHY
# ============================================================
FONTS = {
    'header': 'Segoe UI, Roboto, sans-serif',
    'body': 'Segoe UI, Roboto, sans-serif',
    'monospace': 'JetBrains Mono, Consolas, monospace'
}

FONT_SIZES = {
    'h1': 24,
    'h2': 18,
    'h3': 16,
    'body': 14,
    'small': 12,
    'tiny': 10
}

# ============================================================
# SPACING
# ============================================================
SPACING = {
    'card_padding': 16,
    'section_margin': 24,
    'chart_margin': 20,
    'button_padding': 8
}

# ============================================================
# STATISTICS OPTIONS
# ============================================================
BASIC_STATS = [
    'count', 'mean', 'median', 'mode', 'std',
    'min', 'max', 'range', 'q1', 'q3', 'iqr',
    'skewness', 'kurtosis', 'missing_pct'
]

ADVANCED_STATS_OPTIONS = {
    'regression': ['linear', 'polynomial'],
    'hypothesis_tests': ['t_test', 'anova', 'chi_square'],
    'anomaly_methods': ['isolation_forest', 'z_score', 'iqr'],
    'forecasting': ['arima', 'exponential_smoothing'],
    'correlations': ['pearson', 'spearman', 'kendall']
}

# ============================================================
# EXPORT OPTIONS
# ============================================================
EXPORT_FORMATS = {
    'chart': ['PNG', 'SVG'],
    'data': ['CSV', 'JSON', 'Excel'],
    'report': ['PDF', 'HTML', 'DOCX'],
    'batch': ['ZIP'],
    'statistics': ['CSV', 'Excel', 'JSON']
}

EXPORT_RESOLUTIONS = [72, 150, 300, 600]  # DPI options
DEFAULT_EXPORT_DPI = 300

# ============================================================
# ANIMATION TIMINGS
# ============================================================
ANIMATIONS = {
    'transition': 0.4,  # seconds
    'hover': 0.2,
    'fade': 0.3
}

# ============================================================
# REPORT TEMPLATES
# ============================================================
REPORT_TEMPLATES = {
    'professional': {
        'name': 'Professional',
        'description': 'Corporate style with formal layout',
        'color_scheme': 'light',
        'style': 'corporate'
    },
    'academic': {
        'name': 'Academic',
        'description': 'Research style with detailed methodology',
        'color_scheme': 'light',
        'style': 'research'
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Clean and simple design',
        'color_scheme': 'light',
        'style': 'minimal'
    },
    'detailed': {
        'name': 'Detailed',
        'description': 'Comprehensive with all details',
        'color_scheme': 'light',
        'style': 'comprehensive'
    }
}

# ============================================================
# ANALYSIS TEMPLATES
# ============================================================
ANALYSIS_TEMPLATES = {
    'sales': {
        'name': 'Sales Analysis',
        'description': 'Revenue, regional, and category analysis',
        'icon': '💰',
        'keywords': ['sales', 'revenue', 'amount', 'price', 'order'],
        'required_columns': ['date', 'amount'],
        'charts': ['time_series', 'bar', 'pie', 'treemap'],
        'stats': ['basic', 'trends', 'forecasting']
    },
    'research': {
        'name': 'Research Data',
        'description': 'Statistical analysis for research',
        'icon': '🔬',
        'keywords': ['subject', 'group', 'treatment', 'outcome'],
        'required_columns': ['variable'],
        'charts': ['distribution', 'box', 'violin', 'pair'],
        'stats': ['basic', 'hypothesis', 'correlation']
    },
    'operations': {
        'name': 'Operational Metrics',
        'description': 'KPIs, trends, and anomaly detection',
        'icon': '📊',
        'keywords': ['metric', 'kpi', 'department', 'performance'],
        'required_columns': ['date', 'metric'],
        'charts': ['time_series', 'anomaly', 'bar'],
        'stats': ['basic', 'anomaly', 'forecasting']
    },
    'survey': {
        'name': 'Customer/Survey Data',
        'description': 'Response analysis and demographics',
        'icon': '📋',
        'keywords': ['response', 'rating', 'satisfaction', 'feedback'],
        'required_columns': ['response'],
        'charts': ['bar', 'pie', 'cross_tab'],
        'stats': ['basic', 'correlation', 'categorical']
    },
    'timeseries': {
        'name': 'Time-Series (IoT/Sensors)',
        'description': 'Sensor data and forecasting',
        'icon': '📡',
        'keywords': ['sensor', 'temperature', 'reading', 'timestamp'],
        'required_columns': ['timestamp', 'value'],
        'charts': ['time_series', 'seasonal', 'forecast'],
        'stats': ['basic', 'forecasting', 'anomaly']
    }
}

# ============================================================
# DATA QUALITY THRESHOLDS
# ============================================================
QUALITY_THRESHOLDS = {
    'excellent': 90,
    'good': 75,
    'fair': 60,
    'poor': 0
}

# ============================================================
# PERFORMANCE SETTINGS
# ============================================================
CHUNK_SIZE = 10000
CACHE_TTL = 3600  # seconds
MAX_CACHED_ITEMS = 10
