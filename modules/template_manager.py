"""
Template Manager Module
Pre-built analysis templates for common scenarios
"""

import json
import os
from typing import Dict, List, Optional
import pandas as pd


class TemplateManager:
    """Manages pre-built analysis templates"""

    def __init__(self):
        self.templates = {
            'sales': self._get_sales_template(),
            'research': self._get_research_template(),
            'operations': self._get_operations_template(),
            'survey': self._get_survey_template(),
            'timeseries': self._get_timeseries_template()
        }

    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a specific template"""
        return self.templates.get(template_name)

    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                'id': key,
                'name': template['name'],
                'description': template['description'],
                'icon': template['icon']
            }
            for key, template in self.templates.items()
        ]

    def detect_best_template(self, df: pd.DataFrame) -> Optional[str]:
        """
        Auto-detect best template based on column names
        """
        if df is None or df.empty:
            return None

        columns_lower = [str(col).lower() for col in df.columns]
        column_str = ' '.join(columns_lower)

        scores = {}

        # Sales template keywords
        sales_keywords = ['sales', 'revenue', 'amount', 'price', 'order', 'customer', 'product', 'region']
        scores['sales'] = sum(1 for kw in sales_keywords if kw in column_str)

        # Research template keywords
        research_keywords = ['subject', 'group', 'treatment', 'outcome', 'score', 'result', 'control', 'variable']
        scores['research'] = sum(1 for kw in research_keywords if kw in column_str)

        # Operations template keywords
        ops_keywords = ['metric', 'kpi', 'department', 'performance', 'target', 'baseline', 'alert']
        scores['operations'] = sum(1 for kw in ops_keywords if kw in column_str)

        # Survey template keywords
        survey_keywords = ['response', 'rating', 'satisfaction', 'feedback', 'question', 'answer', 'demographic']
        scores['survey'] = sum(1 for kw in survey_keywords if kw in column_str)

        # Time-series template keywords
        ts_keywords = ['sensor', 'temperature', 'reading', 'timestamp', 'time', 'date', 'hour', 'minute']
        scores['timeseries'] = sum(1 for kw in ts_keywords if kw in column_str)

        # Check for date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            scores['timeseries'] += 3

        if not scores or max(scores.values()) == 0:
            return None

        return max(scores, key=scores.get)

    def apply_template(self, template_name: str, df: pd.DataFrame) -> Dict:
        """Apply template configuration to analysis"""
        template = self.get_template(template_name)
        if not template:
            return {}

        # Auto-select columns based on template
        selected_columns = self._auto_select_columns(template, df)

        return {
            'template_name': template['name'],
            'selected_columns': selected_columns,
            'recommended_charts': template['charts'],
            'recommended_stats': template['stats'],
            'settings': template.get('settings', {})
        }

    def _auto_select_columns(self, template: Dict, df: pd.DataFrame) -> Dict:
        """Auto-select relevant columns based on template"""
        columns_lower = {str(col).lower(): col for col in df.columns}

        selected = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'date_col': None,
            'value_col': None,
            'group_col': None
        }

        # Identify column types
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Try to find date column
        for col in df.columns:
            col_lower = str(col).lower()
            if any(kw in col_lower for kw in ['date', 'time', 'timestamp']):
                selected['date_col'] = col
                if col in cat_cols:
                    cat_cols.remove(col)
                break

        # Try to find value column (numeric)
        for col in numeric_cols:
            col_lower = str(col).lower()
            if any(kw in col_lower for kw in ['amount', 'value', 'price', 'sales', 'revenue', 'metric', 'score']):
                selected['value_col'] = col
                break

        if not selected['value_col'] and numeric_cols:
            selected['value_col'] = numeric_cols[0]

        # Try to find group/category column
        for col in cat_cols:
            col_lower = str(col).lower()
            if any(kw in col_lower for kw in ['category', 'group', 'region', 'department', 'type', 'class']):
                selected['group_col'] = col
                break

        if not selected['group_col'] and cat_cols:
            selected['group_col'] = cat_cols[0]

        selected['numeric'] = numeric_cols
        selected['categorical'] = cat_cols
        selected['datetime'] = date_cols

        return selected

    # Template definitions
    def _get_sales_template(self) -> Dict:
        return {
            'name': 'Sales Analysis',
            'description': 'Revenue, regional, and category analysis',
            'icon': '💰',
            'keywords': ['sales', 'revenue', 'amount', 'price', 'order'],
            'required_columns': ['date', 'amount'],
            'charts': ['time_series', 'bar', 'pie', 'treemap', 'line', 'area'],
            'stats': ['basic', 'trends', 'forecasting', 'correlation'],
            'settings': {
                'value_col_priority': ['amount', 'revenue', 'sales', 'price'],
                'group_col_priority': ['region', 'category', 'product', 'customer'],
                'date_col_priority': ['date', 'order_date', 'timestamp']
            }
        }

    def _get_research_template(self) -> Dict:
        return {
            'name': 'Research Data',
            'description': 'Statistical analysis for research',
            'icon': '🔬',
            'keywords': ['subject', 'group', 'treatment', 'outcome'],
            'required_columns': ['variable'],
            'charts': ['distribution', 'box', 'violin', 'pair', 'scatter', 'bar'],
            'stats': ['basic', 'hypothesis', 'correlation', 'normality'],
            'settings': {
                'test_priority': ['t_test', 'anova', 'chi_square'],
                'group_col_priority': ['group', 'treatment', 'condition'],
                'value_col_priority': ['score', 'outcome', 'measurement', 'result']
            }
        }

    def _get_operations_template(self) -> Dict:
        return {
            'name': 'Operational Metrics',
            'description': 'KPIs, trends, and anomaly detection',
            'icon': '📊',
            'keywords': ['metric', 'kpi', 'department', 'performance'],
            'required_columns': ['date', 'metric'],
            'charts': ['time_series', 'anomaly', 'bar', 'line', 'area'],
            'stats': ['basic', 'anomaly', 'forecasting'],
            'settings': {
                'value_col_priority': ['metric', 'kpi', 'value', 'count'],
                'group_col_priority': ['department', 'team', 'category'],
                'anomaly_method': 'iqr'
            }
        }

    def _get_survey_template(self) -> Dict:
        return {
            'name': 'Customer/Survey Data',
            'description': 'Response analysis and demographics',
            'icon': '📋',
            'keywords': ['response', 'rating', 'satisfaction', 'feedback'],
            'required_columns': ['response'],
            'charts': ['bar', 'pie', 'cross_tab', 'treemap', 'sunburst'],
            'stats': ['basic', 'correlation', 'categorical'],
            'settings': {
                'group_col_priority': ['demographic', 'age_group', 'gender', 'region'],
                'value_col_priority': ['rating', 'score', 'satisfaction']
            }
        }

    def _get_timeseries_template(self) -> Dict:
        return {
            'name': 'Time-Series (IoT/Sensors)',
            'description': 'Sensor data and forecasting',
            'icon': '📡',
            'keywords': ['sensor', 'temperature', 'reading', 'timestamp'],
            'required_columns': ['timestamp', 'value'],
            'charts': ['time_series', 'seasonal', 'forecast', 'area', 'line'],
            'stats': ['basic', 'forecasting', 'anomaly'],
            'settings': {
                'value_col_priority': ['value', 'reading', 'temperature', 'sensor'],
                'date_col_priority': ['timestamp', 'datetime', 'time'],
                'forecast_method': 'exponential_smoothing'
            }
        }
