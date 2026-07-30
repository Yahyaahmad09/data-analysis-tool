"""
Profile Manager Module
Save, load, and manage user analysis profiles using session storage
"""

import json
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime


class ProfileManager:
    """Manages user analysis profiles (session-based for v1.1.0)"""

    def __init__(self):
        if 'profiles' not in st.session_state:
            st.session_state.profiles = {}

    def save_profile(self, name: str, settings: Dict) -> Dict:
        """
        Save analysis profile
        settings: dict with selected stats, charts, colors, etc.
        """
        profile = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'settings': settings
        }

        st.session_state.profiles[name] = profile
        return {'success': True, 'message': f'Profile "{name}" saved successfully'}

    def load_profile(self, name: str) -> Optional[Dict]:
        """Load a saved profile"""
        return st.session_state.profiles.get(name)

    def list_profiles(self) -> List[str]:
        """List all saved profile names"""
        return list(st.session_state.profiles.keys())

    def delete_profile(self, name: str) -> Dict:
        """Delete a profile"""
        if name in st.session_state.profiles:
            del st.session_state.profiles[name]
            return {'success': True, 'message': f'Profile "{name}" deleted'}
        return {'success': False, 'message': 'Profile not found'}

    def export_profile(self, name: str) -> Optional[str]:
        """Export profile as JSON string"""
        profile = self.load_profile(name)
        if profile:
            return json.dumps(profile, indent=2)
        return None

    def import_profile(self, json_str: str) -> Dict:
        """Import profile from JSON string"""
        try:
            profile = json.loads(json_str)
            name = profile.get('name', 'Imported Profile')
            profile['imported_at'] = datetime.now().isoformat()
            st.session_state.profiles[name] = profile
            return {'success': True, 'message': f'Profile "{name}" imported successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Import failed: {str(e)}'}

    def get_default_settings(self) -> Dict:
        """Get default analysis settings"""
        return {
            'selected_statistics': ['basic'],
            'selected_charts': ['histogram', 'bar'],
            'color_palette': 'Viridis',
            'theme': 'light',
            'chart_height': 600,
            'chart_width': 1000,
            'show_trendlines': True,
            'show_kde': True,
            'confidence_level': 0.95,
            'anomaly_method': 'iqr',
            'forecast_method': 'linear',
            'forecast_periods': 30,
            'regression_degree': 1,
            'report_template': 'professional',
            'report_sections': {
                'cover_page': True,
                'executive_summary': True,
                'data_overview': True,
                'data_quality': True,
                'summary_statistics': True,
                'visualizations': True,
                'correlation_analysis': True,
                'anomalies': True,
                'forecasts': True,
                'conclusions': True
            }
        }
