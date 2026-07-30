"""
File Handler Module
Multi-file upload, validation, and management
"""

import os
import io
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
from config import MAX_FILE_SIZE_MB, SUPPORTED_FORMATS, MAX_ROWS, ENCODING_OPTIONS


class FileHandler:
    """Handles file uploads, validation, and DataFrame management"""

    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS
        self.max_size_mb = MAX_FILE_SIZE_MB
        self.max_rows = MAX_ROWS

    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file size and format
        Returns: (is_valid, message)
        """
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > self.max_size_mb:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum ({self.max_size_mb}MB)"

        # Check file format
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in self.supported_formats:
            return False, f"Unsupported format. Use: {', '.join(self.supported_formats)}"

        return True, "File is valid"

    def read_file(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Read file with multiple encoding attempts for CSV
        Returns: (dataframe, error_message)
        """
        try:
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            file_name = uploaded_file.name

            if file_ext == '.csv':
                # Try multiple encodings
                for encoding in ENCODING_OPTIONS:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding=encoding, low_memory=False)
                        if len(df) > self.max_rows:
                            return None, f"File has {len(df):,} rows. Maximum allowed: {self.max_rows:,}"
                        return df, ""
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                    except Exception as e:
                        continue

                # If all encodings fail, try with error handling
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='utf-8', encoding_errors='ignore', low_memory=False)
                    return df, ""
                except Exception as e:
                    return None, f"Failed to read CSV: {str(e)}"

            elif file_ext in ['.xlsx', '.xls']:
                try:
                    df = pd.read_excel(uploaded_file, engine='openpyxl' if file_ext == '.xlsx' else None)
                    if len(df) > self.max_rows:
                        return None, f"File has {len(df):,} rows. Maximum allowed: {self.max_rows:,}"
                    return df, ""
                except Exception as e:
                    return None, f"Failed to read Excel: {str(e)}"

            else:
                return None, f"Unsupported file format: {file_ext}"

        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

    def get_file_metadata(self, uploaded_file, df: Optional[pd.DataFrame] = None) -> Dict:
        """Extract metadata from uploaded file"""
        file_size_mb = uploaded_file.size / (1024 * 1024)
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()

        metadata = {
            'name': uploaded_file.name,
            'size_bytes': uploaded_file.size,
            'size_mb': round(file_size_mb, 2),
            'format': file_ext,
            'icon': self._get_file_icon(file_ext),
            'rows': len(df) if df is not None else 0,
            'columns': len(df.columns) if df is not None else 0,
            'column_names': list(df.columns) if df is not None else [],
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB" if df is not None else "0 MB"
        }

        return metadata

    def _get_file_icon(self, file_ext: str) -> str:
        """Get emoji icon for file type"""
        icons = {
            '.csv': '📄',
            '.xlsx': '📊',
            '.xls': '📊'
        }
        return icons.get(file_ext, '📁')

    def process_multiple_uploads(self, uploaded_files) -> Dict:
        """
        Process multiple uploaded files
        Returns dict of {filename: {dataframe, metadata, status}}
        """
        results = {}

        for uploaded_file in uploaded_files:
            # Validate
            is_valid, message = self.validate_file(uploaded_file)

            if not is_valid:
                results[uploaded_file.name] = {
                    'dataframe': None,
                    'metadata': self.get_file_metadata(uploaded_file),
                    'status': 'error',
                    'error': message
                }
                continue

            # Read file
            df, error = self.read_file(uploaded_file)

            if df is None:
                results[uploaded_file.name] = {
                    'dataframe': None,
                    'metadata': self.get_file_metadata(uploaded_file),
                    'status': 'error',
                    'error': error
                }
            else:
                results[uploaded_file.name] = {
                    'dataframe': df,
                    'metadata': self.get_file_metadata(uploaded_file, df),
                    'status': 'success',
                    'error': None
                }

        return results

    def get_data_types_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of data types in DataFrame"""
        if df is None or df.empty:
            return {}

        summary = {
            'numeric': df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist(),
            'categorical': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime': df.select_dtypes(include=['datetime64']).columns.tolist(),
            'boolean': df.select_dtypes(include=['bool']).columns.tolist()
        }

        # Try to detect datetime columns in object type
        for col in df.select_dtypes(include=['object']).columns:
            try:
                pd.to_datetime(df[col], errors='raise')
                if col not in summary['datetime']:
                    summary['datetime'].append(col)
                    if col in summary['categorical']:
                        summary['categorical'].remove(col)
            except:
                pass

        return summary

    def remove_file(self, file_name: str):
        """Remove file from session state"""
        if 'uploaded_files' in st.session_state:
            if file_name in st.session_state.uploaded_files:
                del st.session_state.uploaded_files[file_name]

    def get_quality_score(self, df: pd.DataFrame) -> Dict:
        """
        Calculate data quality score
        Returns dict with scores for each dimension
        """
        if df is None or df.empty:
            return {
                'overall': 0,
                'completeness': 0,
                'uniqueness': 0,
                'consistency': 0,
                'validity': 0,
                'issues': []
            }

        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0

        # Uniqueness: based on duplicate rows
        duplicate_count = df.duplicated().sum()
        uniqueness = ((len(df) - duplicate_count) / len(df) * 100) if len(df) > 0 else 0

        # Consistency: % of columns with consistent types
        consistency_scores = []
        for col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            if pd.api.types.is_numeric_dtype(col_data):
                # Check if all values are numeric
                consistency_scores.append(100)
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                consistency_scores.append(100)
            else:
                # Check for mixed types in object columns
                try:
                    pd.to_numeric(col_data)
                    consistency_scores.append(50)  # Mixed
                except:
                    consistency_scores.append(100)

        consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0

        # Validity: check for outliers in numeric columns
        validity_scores = []
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((col_data < (Q1 - 1.5 * IQR)) | (col_data > (Q3 + 1.5 * IQR))).sum()
                outlier_pct = (outliers / len(col_data)) * 100
                # Lower outlier % = higher validity
                validity = max(0, 100 - outlier_pct)
                validity_scores.append(validity)

        validity = sum(validity_scores) / len(validity_scores) if validity_scores else 100

        # Overall score (weighted average)
        overall = (completeness * 0.4 + uniqueness * 0.2 + consistency * 0.2 + validity * 0.2)

        # Issues
        issues = []
        if completeness < 90:
            issues.append(f"{missing_cells:,} missing values ({100-completeness:.1f}%)")
        if duplicate_count > 0:
            issues.append(f"{duplicate_count} duplicate rows")
        if validity < 80:
            issues.append("Significant outliers detected")

        return {
            'overall': round(overall, 1),
            'completeness': round(completeness, 1),
            'uniqueness': round(uniqueness, 1),
            'consistency': round(consistency, 1),
            'validity': round(validity, 1),
            'issues': issues,
            'missing_cells': missing_cells,
            'duplicate_rows': duplicate_count
        }

    def detect_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> Dict:
        """
        Detect outliers in numeric columns
        Methods: 'iqr', 'z_score', 'isolation_forest'
        """
        results = {}
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower) | (df[col] > upper)].index.tolist()

            elif method == 'z_score':
                mean = col_data.mean()
                std = col_data.std()
                if std == 0:
                    outliers = []
                else:
                    z_scores = abs((df[col] - mean) / std)
                    outliers = df[z_scores > 3].index.tolist()

            elif method == 'isolation_forest':
                try:
                    from sklearn.ensemble import IsolationForest
                    X = col_data.values.reshape(-1, 1)
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    predictions = iso_forest.fit_predict(X)
                    outlier_mask = predictions == -1
                    outliers = col_data[outlier_mask].index.tolist()
                except:
                    outliers = []

            else:
                outliers = []

            results[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(df) * 100) if len(df) > 0 else 0,
                'indices': outliers[:100]  # Limit to first 100
            }

        return results
