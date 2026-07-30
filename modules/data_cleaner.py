"""
Data Cleaner Module
Data cleaning, transformation, and preprocessing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class DataCleaner:
    """Provides data cleaning operations"""

    def __init__(self):
        self.cleaning_log = []

    def remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Remove duplicate rows"""
        before = len(df)
        df_clean = df.drop_duplicates()
        after = len(df_clean)
        removed = before - after

        result = {
            'operation': 'remove_duplicates',
            'rows_before': before,
            'rows_after': after,
            'rows_removed': removed,
            'success': True
        }

        self.cleaning_log.append(result)
        return df_clean, result

    def handle_missing_values(self, df: pd.DataFrame, strategy: str,
                            columns: Optional[List[str]] = None,
                            custom_value: Optional[any] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Handle missing values
        strategy: 'drop_rows', 'drop_cols', 'mean', 'median', 'mode', 'ffill', 'bfill', 'custom'
        """
        df_clean = df.copy()

        if columns is None:
            columns = df.columns[df.isnull().any()].tolist()

        if not columns:
            return df_clean, {'operation': 'handle_missing', 'action': 'no_missing_values'}

        before_missing = df[columns].isnull().sum().sum()

        if strategy == 'drop_rows':
            df_clean = df_clean.dropna(subset=columns)
        elif strategy == 'drop_cols':
            df_clean = df_clean.drop(columns=columns)
        elif strategy in ['mean', 'median']:
            for col in columns:
                if pd.api.types.is_numeric_dtype(df_clean[col]):
                    fill_value = df_clean[col].mean() if strategy == 'mean' else df_clean[col].median()
                    df_clean[col] = df_clean[col].fillna(fill_value)
        elif strategy == 'mode':
            for col in columns:
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col] = df_clean[col].fillna(mode_val.iloc[0])
        elif strategy == 'ffill':
            df_clean[columns] = df_clean[columns].fillna(method='ffill')
        elif strategy == 'bfill':
            df_clean[columns] = df_clean[columns].fillna(method='bfill')
        elif strategy == 'custom' and custom_value is not None:
            df_clean[columns] = df_clean[columns].fillna(custom_value)

        after_missing = df_clean[columns].isnull().sum().sum() if columns and all(c in df_clean.columns for c in columns) else 0

        result = {
            'operation': 'handle_missing',
            'strategy': strategy,
            'columns': columns,
            'values_filled': int(before_missing - after_missing),
            'rows_after': len(df_clean),
            'success': True
        }

        self.cleaning_log.append(result)
        return df_clean, result

    def filter_rows(self, df: pd.DataFrame, column: str, operator: str,
                   value: any) -> Tuple[pd.DataFrame, Dict]:
        """
        Filter rows by condition
        operators: '==', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains'
        """
        before = len(df)

        try:
            if operator == '==':
                df_filtered = df[df[column] == value]
            elif operator == '!=':
                df_filtered = df[df[column] != value]
            elif operator == '>':
                df_filtered = df[df[column] > value]
            elif operator == '<':
                df_filtered = df[df[column] < value]
            elif operator == '>=':
                df_filtered = df[df[column] >= value]
            elif operator == '<=':
                df_filtered = df[df[column] <= value]
            elif operator == 'contains':
                df_filtered = df[df[column].astype(str).str.contains(str(value), na=False)]
            elif operator == 'not_contains':
                df_filtered = df[~df[column].astype(str).str.contains(str(value), na=False)]
            else:
                return df, {'error': f'Unknown operator: {operator}'}

            after = len(df_filtered)

            result = {
                'operation': 'filter_rows',
                'column': column,
                'operator': operator,
                'value': str(value),
                'rows_before': before,
                'rows_after': after,
                'rows_removed': before - after,
                'success': True
            }

            self.cleaning_log.append(result)
            return df_filtered, result

        except Exception as e:
            return df, {'error': str(e)}

    def change_data_type(self, df: pd.DataFrame, column: str, new_type: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Change column data type
        new_type: 'int', 'float', 'str', 'datetime', 'category', 'bool'
        """
        df_clean = df.copy()

        try:
            if new_type == 'int':
                df_clean[column] = pd.to_numeric(df_clean[column], errors='coerce').astype('Int64')
            elif new_type == 'float':
                df_clean[column] = pd.to_numeric(df_clean[column], errors='coerce')
            elif new_type == 'str':
                df_clean[column] = df_clean[column].astype(str)
            elif new_type == 'datetime':
                df_clean[column] = pd.to_datetime(df_clean[column], errors='coerce')
            elif new_type == 'category':
                df_clean[column] = df_clean[column].astype('category')
            elif new_type == 'bool':
                df_clean[column] = df_clean[column].astype(bool)

            result = {
                'operation': 'change_dtype',
                'column': column,
                'new_type': new_type,
                'success': True
            }

            self.cleaning_log.append(result)
            return df_clean, result

        except Exception as e:
            return df, {'error': str(e), 'column': column}

    def rename_columns(self, df: pd.DataFrame, rename_map: Dict[str, str]) -> Tuple[pd.DataFrame, Dict]:
        """Rename columns"""
        df_clean = df.copy()
        df_clean = df_clean.rename(columns=rename_map)

        result = {
            'operation': 'rename_columns',
            'renamed': rename_map,
            'success': True
        }

        self.cleaning_log.append(result)
        return df_clean, result

    def remove_outliers(self, df: pd.DataFrame, columns: List[str],
                        method: str = 'iqr', action: str = 'remove') -> Tuple[pd.DataFrame, Dict]:
        """
        Remove or flag outliers
        action: 'remove', 'flag', 'cap'
        """
        df_clean = df.copy()
        before = len(df)
        outlier_mask = pd.Series([False] * len(df), index=df.index)

        for col in columns:
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue

            col_data = df_clean[col].dropna()

            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                mask = (df_clean[col] < lower) | (df_clean[col] > upper)

            elif method == 'z_score':
                mean = col_data.mean()
                std = col_data.std()
                if std == 0:
                    continue
                z_scores = abs((df_clean[col] - mean) / std)
                mask = z_scores > 3
            else:
                continue

            outlier_mask = outlier_mask | mask

        if action == 'remove':
            df_clean = df_clean[~outlier_mask]
        elif action == 'flag':
            df_clean['_outlier'] = outlier_mask
        elif action == 'cap':
            for col in columns:
                if not pd.api.types.is_numeric_dtype(df_clean[col]):
                    continue
                col_data = df_clean[col].dropna()
                if method == 'iqr':
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                else:
                    mean = col_data.mean()
                    std = col_data.std()
                    lower = mean - 3 * std
                    upper = mean + 3 * std

                df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)

        after = len(df_clean) if action != 'flag' else before
        removed = before - after

        result = {
            'operation': 'remove_outliers',
            'method': method,
            'action': action,
            'columns': columns,
            'outliers_found': int(outlier_mask.sum()),
            'rows_removed': removed,
            'success': True
        }

        self.cleaning_log.append(result)
        return df_clean, result

    def get_cleaning_log(self) -> List[Dict]:
        """Get cleaning operation log"""
        return self.cleaning_log

    def clear_log(self):
        """Clear cleaning log"""
        self.cleaning_log = []
