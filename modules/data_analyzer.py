"""
Data Analyzer Module
Advanced statistics, hypothesis testing, regression, forecasting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.stats import shapiro, normaltest, kstest
import warnings
warnings.filterwarnings('ignore')


class DataAnalyzer:
    """Performs comprehensive statistical analysis on DataFrames"""

    def __init__(self):
        self.results = {}

    def basic_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate basic statistics for all columns
        """
        if df is None or df.empty:
            return {}

        results = {}

        for col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            col_stats = {
                'count': int(len(col_data)),
                'missing': int(df[col].isnull().sum()),
                'missing_pct': round(df[col].isnull().sum() / len(df) * 100, 2),
                'unique': int(col_data.nunique()),
                'dtype': str(df[col].dtype)
            }

            # Numeric statistics
            if pd.api.types.is_numeric_dtype(col_data):
                col_stats.update({
                    'mean': round(float(col_data.mean()), 4),
                    'median': round(float(col_data.median()), 4),
                    'std': round(float(col_data.std()), 4),
                    'min': round(float(col_data.min()), 4),
                    'max': round(float(col_data.max()), 4),
                    'range': round(float(col_data.max() - col_data.min()), 4),
                    'q1': round(float(col_data.quantile(0.25)), 4),
                    'q3': round(float(col_data.quantile(0.75)), 4),
                    'iqr': round(float(col_data.quantile(0.75) - col_data.quantile(0.25)), 4),
                    'skewness': round(float(col_data.skew()), 4),
                    'kurtosis': round(float(col_data.kurtosis()), 4),
                    'variance': round(float(col_data.var()), 4),
                    'cv': round(float(col_data.std() / col_data.mean() * 100), 2) if col_data.mean() != 0 else 0
                })

                # Mode for numeric
                try:
                    mode_vals = col_data.mode()
                    if len(mode_vals) > 0:
                        col_stats['mode'] = round(float(mode_vals.iloc[0]), 4)
                except:
                    pass

                # Sum
                col_stats['sum'] = round(float(col_data.sum()), 4)

            # Categorical statistics
            elif pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
                try:
                    mode_vals = col_data.mode()
                    if len(mode_vals) > 0:
                        col_stats['mode'] = str(mode_vals.iloc[0])
                        col_stats['mode_count'] = int((col_data == mode_vals.iloc[0]).sum())
                        col_stats['mode_pct'] = round((col_data == mode_vals.iloc[0]).sum() / len(col_data) * 100, 2)
                except:
                    pass

                col_stats['top_values'] = col_data.value_counts().head(5).to_dict()

            # Datetime statistics
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_stats['min_date'] = str(col_data.min())
                col_stats['max_date'] = str(col_data.max())
                col_stats['date_range_days'] = (col_data.max() - col_data.min()).days

            results[col] = col_stats

        return results

    def advanced_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Advanced statistical tests
        """
        if df is None or df.empty:
            return {}

        results = {}

        # Normality tests for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        normality_results = {}

        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) < 3:
                continue

            tests = {}

            # Shapiro-Wilk (if sample size <= 5000)
            if 3 <= len(col_data) <= 5000:
                try:
                    stat, p_value = shapiro(col_data)
                    tests['shapiro'] = {
                        'statistic': round(float(stat), 4),
                        'p_value': round(float(p_value), 4),
                        'is_normal': p_value > 0.05
                    }
                except:
                    pass

            # D'Agostino-Pearson
            if len(col_data) >= 20:
                try:
                    stat, p_value = normaltest(col_data)
                    tests['dagostino'] = {
                        'statistic': round(float(stat), 4),
                        'p_value': round(float(p_value), 4),
                        'is_normal': p_value > 0.05
                    }
                except:
                    pass

            # Kolmogorov-Smirnov
            try:
                standardized = (col_data - col_data.mean()) / col_data.std()
                stat, p_value = kstest(standardized, 'norm')
                tests['kolmogorov_smirnov'] = {
                    'statistic': round(float(stat), 4),
                    'p_value': round(float(p_value), 4),
                    'is_normal': p_value > 0.05
                }
            except:
                pass

            if tests:
                normality_results[col] = tests

        if normality_results:
            results['normality_tests'] = normality_results

        # Correlation analysis
        if len(numeric_cols) >= 2:
            correlation_results = self.correlation_analysis(df, numeric_cols)
            if correlation_results:
                results['correlations'] = correlation_results

        return results

    def correlation_analysis(self, df: pd.DataFrame, columns: List[str]) -> Dict:
        """
        Calculate multiple correlation types
        """
        if len(columns) < 2:
            return {}

        results = {}

        # Pearson
        try:
            pearson = df[columns].corr(method='pearson')
            results['pearson'] = {
                'matrix': pearson.round(4).to_dict(),
                'strong_pairs': self._find_strong_correlations(pearson)
            }
        except:
            pass

        # Spearman
        try:
            spearman = df[columns].corr(method='spearman')
            results['spearman'] = {
                'matrix': spearman.round(4).to_dict(),
                'strong_pairs': self._find_strong_correlations(spearman)
            }
        except:
            pass

        # Kendall
        try:
            kendall = df[columns].corr(method='kendall')
            results['kendall'] = {
                'matrix': kendall.round(4).to_dict(),
                'strong_pairs': self._find_strong_correlations(kendall)
            }
        except:
            pass

        return results

    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """Find pairs with strong correlation"""
        strong_pairs = []
        cols = corr_matrix.columns

        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    strong_pairs.append({
                        'var1': cols[i],
                        'var2': cols[j],
                        'correlation': round(float(corr_val), 4),
                        'strength': 'very strong' if abs(corr_val) >= 0.9 else 'strong'
                    })

        return sorted(strong_pairs, key=lambda x: abs(x['correlation']), reverse=True)

    def regression_analysis(self, df: pd.DataFrame, x_col: str, y_col: str,
                          degree: int = 1) -> Dict:
        """
        Perform regression analysis
        """
        try:
            # Remove missing values
            data = df[[x_col, y_col]].dropna()
            if len(data) < degree + 2:
                return {'error': 'Insufficient data'}

            X = data[x_col].values
            y = data[y_col].values

            # Linear/Polynomial regression
            coefficients = np.polyfit(X, y, degree)
            predictions = np.polyval(coefficients, X)

            # Calculate metrics
            ss_res = np.sum((y - predictions) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            mse = ss_res / len(y)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(y - predictions))

            # Predictions at new points
            x_min, x_max = X.min(), X.max()
            x_pred = np.linspace(x_min, x_max, 100)
            y_pred = np.polyval(coefficients, x_pred)

            # Residuals
            residuals = y - predictions

            return {
                'degree': degree,
                'coefficients': [round(float(c), 4) for c in coefficients],
                'r_squared': round(float(r_squared), 4),
                'mse': round(float(mse), 4),
                'rmse': round(float(rmse), 4),
                'mae': round(float(mae), 4),
                'x_pred': x_pred.tolist(),
                'y_pred': y_pred.tolist(),
                'x_data': X.tolist(),
                'y_data': y.tolist(),
                'predictions': predictions.tolist(),
                'residuals': residuals.tolist(),
                'equation': self._format_equation(coefficients, degree, x_col, y_col)
            }
        except Exception as e:
            return {'error': str(e)}

    def _format_equation(self, coeffs: List[float], degree: int, x_col: str, y_col: str) -> str:
        """Format polynomial equation as string"""
        terms = []
        for i, c in enumerate(coeffs):
            power = degree - i
            if power == 0:
                terms.append(f"{c:.4f}")
            elif power == 1:
                terms.append(f"{c:.4f}*x")
            else:
                terms.append(f"{c:.4f}*x^{power}")

        return f"{y_col} = {' + '.join(terms)}"

    def hypothesis_test(self, df: pd.DataFrame, test_type: str, **kwargs) -> Dict:
        """
        Perform hypothesis tests
        test_type: 't_test_one', 't_test_two', 'anova', 'chi_square'
        """
        try:
            if test_type == 't_test_one':
                col = kwargs.get('column')
                popmean = kwargs.get('popmean', 0)
                col_data = df[col].dropna()

                stat, p_value = stats.ttest_1samp(col_data, popmean)

                return {
                    'test': 'One-Sample T-Test',
                    'statistic': round(float(stat), 4),
                    'p_value': round(float(p_value), 4),
                    'significant': p_value < 0.05,
                    'mean': round(float(col_data.mean()), 4),
                    'popmean': popmean
                }

            elif test_type == 't_test_two':
                col1 = kwargs.get('col1')
                col2 = kwargs.get('col2')
                data1 = df[col1].dropna()
                data2 = df[col2].dropna()

                # Independent t-test
                stat, p_value = stats.ttest_ind(data1, data2)

                return {
                    'test': 'Independent T-Test',
                    'statistic': round(float(stat), 4),
                    'p_value': round(float(p_value), 4),
                    'significant': p_value < 0.05,
                    'mean1': round(float(data1.mean()), 4),
                    'mean2': round(float(data2.mean()), 4)
                }

            elif test_type == 'anova':
                group_col = kwargs.get('group_col')
                value_col = kwargs.get('value_col')

                groups = []
                for group in df[group_col].unique():
                    group_data = df[df[group_col] == group][value_col].dropna()
                    if len(group_data) > 0:
                        groups.append(group_data.values)

                if len(groups) < 2:
                    return {'error': 'Need at least 2 groups'}

                stat, p_value = stats.f_oneway(*groups)

                return {
                    'test': 'One-Way ANOVA',
                    'statistic': round(float(stat), 4),
                    'p_value': round(float(p_value), 4),
                    'significant': p_value < 0.05,
                    'n_groups': len(groups)
                }

            elif test_type == 'chi_square':
                col1 = kwargs.get('col1')
                col2 = kwargs.get('col2')

                contingency = pd.crosstab(df[col1], df[col2])
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

                return {
                    'test': 'Chi-Square Test',
                    'statistic': round(float(chi2), 4),
                    'p_value': round(float(p_value), 4),
                    'degrees_of_freedom': int(dof),
                    'significant': p_value < 0.05
                }

            else:
                return {'error': f'Unknown test type: {test_type}'}

        except Exception as e:
            return {'error': str(e)}

    def time_series_forecast(self, df: pd.DataFrame, date_col: str, value_col: str,
                            periods: int = 30, method: str = 'linear') -> Dict:
        """
        Simple forecasting methods
        Methods: 'linear', 'polynomial', 'exponential_smoothing', 'moving_average'
        """
        try:
            # Prepare data
            data = df[[date_col, value_col]].dropna().copy()
            data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
            data = data.dropna().sort_values(date_col)

            if len(data) < 10:
                return {'error': 'Insufficient data for forecasting (need at least 10 points)'}

            # Create numeric x (days from start)
            data['x'] = (data[date_col] - data[date_col].min()).dt.days
            y = data[value_col].values
            x = data['x'].values

            results = {
                'date_col': date_col,
                'value_col': value_col,
                'periods': periods,
                'method': method
            }

            if method == 'linear':
                # Linear trend
                coeffs = np.polyfit(x, y, 1)
                future_x = np.arange(x.max() + 1, x.max() + 1 + periods)
                future_dates = pd.date_range(start=data[date_col].max() + pd.Timedelta(days=1), periods=periods)
                forecast = np.polyval(coeffs, future_x)

                # Confidence intervals (approximate)
                predictions = np.polyval(coeffs, x)
                residuals = y - predictions
                std_error = np.std(residuals)
                ci_lower = forecast - 1.96 * std_error
                ci_upper = forecast + 1.96 * std_error

                results.update({
                    'historical_dates': data[date_col].dt.strftime('%Y-%m-%d').tolist(),
                    'historical_values': y.tolist(),
                    'forecast_dates': future_dates.strftime('%Y-%m-%d').tolist(),
                    'forecast_values': forecast.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'slope': round(float(coeffs[0]), 4),
                    'intercept': round(float(coeffs[1]), 4)
                })

            elif method == 'polynomial':
                degree = min(3, len(x) // 10)
                degree = max(1, degree)
                coeffs = np.polyfit(x, y, degree)
                future_x = np.arange(x.max() + 1, x.max() + 1 + periods)
                future_dates = pd.date_range(start=data[date_col].max() + pd.Timedelta(days=1), periods=periods)
                forecast = np.polyval(coeffs, future_x)

                predictions = np.polyval(coeffs, x)
                residuals = y - predictions
                std_error = np.std(residuals)
                ci_lower = forecast - 1.96 * std_error
                ci_upper = forecast + 1.96 * std_error

                results.update({
                    'historical_dates': data[date_col].dt.strftime('%Y-%m-%d').tolist(),
                    'historical_values': y.tolist(),
                    'forecast_dates': future_dates.strftime('%Y-%m-%d').tolist(),
                    'forecast_values': forecast.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'degree': degree
                })

            elif method == 'exponential_smoothing':
                try:
                    from statsmodels.tsa.holtwinters import ExponentialSmoothing

                    ts = pd.Series(y, index=pd.to_datetime(data[date_col]))
                    ts = ts.sort_index()

                    # Remove duplicates
                    ts = ts[~ts.index.duplicated(keep='first')]

                    # Simple exponential smoothing
                    model = ExponentialSmoothing(ts, trend='add', seasonal=None, initialization_method='estimated')
                    fitted = model.fit()

                    forecast = fitted.forecast(periods)

                    # Future dates
                    future_dates = pd.date_range(start=data[date_col].max() + pd.Timedelta(days=1), periods=periods)

                    # Confidence intervals from residual std
                    residuals = fitted.resid
                    std_error = np.std(residuals.dropna())
                    ci_lower = forecast.values - 1.96 * std_error
                    ci_upper = forecast.values + 1.96 * std_error

                    results.update({
                        'historical_dates': ts.index.strftime('%Y-%m-%d').tolist(),
                        'historical_values': ts.values.tolist(),
                        'forecast_dates': future_dates.strftime('%Y-%m-%d').tolist(),
                        'forecast_values': forecast.values.tolist(),
                        'ci_lower': ci_lower.tolist(),
                        'ci_upper': ci_upper.tolist()
                    })
                except Exception as e:
                    # Fallback to linear
                    return self.time_series_forecast(df, date_col, value_col, periods, 'linear')

            elif method == 'moving_average':
                window = min(7, len(x) // 3)
                window = max(2, window)
                moving_avg = pd.Series(y).rolling(window=window).mean()

                # Last value + average change
                last_value = y[-1]
                recent_values = y[-window:]
                trend = (recent_values[-1] - recent_values[0]) / window

                future_dates = pd.date_range(start=data[date_col].max() + pd.Timedelta(days=1), periods=periods)
                forecast = [last_value + trend * (i + 1) for i in range(periods)]
                forecast = np.array(forecast)

                std_error = np.std(y[-window:])
                ci_lower = forecast - 1.96 * std_error
                ci_upper = forecast + 1.96 * std_error

                results.update({
                    'historical_dates': data[date_col].dt.strftime('%Y-%m-%d').tolist(),
                    'historical_values': y.tolist(),
                    'forecast_dates': future_dates.strftime('%Y-%m-%d').tolist(),
                    'forecast_values': forecast.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'window': window
                })

            return results

        except Exception as e:
            return {'error': str(e)}

    def detect_anomalies(self, df: pd.DataFrame, columns: List[str], method: str = 'iqr') -> Dict:
        """
        Detect anomalies in specified columns
        Methods: 'iqr', 'z_score', 'isolation_forest'
        """
        results = {}

        for col in columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue

            col_data = df[col].dropna()
            if len(col_data) < 10:
                continue

            anomalies = []

            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR

                mask = (df[col] < lower) | (df[col] > upper)
                anomaly_indices = df[mask].index.tolist()
                anomaly_values = df.loc[mask, col].tolist()

                for idx, val in zip(anomaly_indices, anomaly_values):
                    if pd.isna(val):
                        continue
                    severity = 'high' if (val < Q1 - 3*IQR or val > Q3 + 3*IQR) else 'medium'
                    anomalies.append({
                        'index': int(idx),
                        'value': round(float(val), 4),
                        'severity': severity,
                        'method': 'IQR'
                    })

            elif method == 'z_score':
                mean = col_data.mean()
                std = col_data.std()

                if std == 0:
                    continue

                z_scores = abs((df[col] - mean) / std)
                mask = z_scores > 3
                anomaly_indices = df[mask].index.tolist()
                anomaly_values = df.loc[mask, col].tolist()
                z_vals = z_scores[mask].tolist()

                for idx, val, z in zip(anomaly_indices, anomaly_values, z_vals):
                    if pd.isna(val):
                        continue
                    severity = 'high' if z > 5 else 'medium'
                    anomalies.append({
                        'index': int(idx),
                        'value': round(float(val), 4),
                        'z_score': round(float(z), 4),
                        'severity': severity,
                        'method': 'Z-Score'
                    })

            elif method == 'isolation_forest':
                try:
                    from sklearn.ensemble import IsolationForest

                    X = col_data.values.reshape(-1, 1)
                    iso = IsolationForest(contamination=0.05, random_state=42)
                    predictions = iso.fit_predict(X)

                    anomaly_mask = predictions == -1
                    anomaly_indices = col_data[anomaly_mask].index.tolist()
                    anomaly_values = col_data[anomaly_mask].tolist()

                    for idx, val in zip(anomaly_indices, anomaly_values):
                        if pd.isna(val):
                            continue
                        anomalies.append({
                            'index': int(idx),
                            'value': round(float(val), 4),
                            'severity': 'high',
                            'method': 'Isolation Forest'
                        })
                except:
                    continue

            if anomalies:
                results[col] = {
                    'count': len(anomalies),
                    'percentage': round(len(anomalies) / len(df) * 100, 2),
                    'anomalies': anomalies[:100]  # Limit display
                }

        return results

    def cross_tabulation(self, df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
        """Create cross-tabulation"""
        return pd.crosstab(df[col1], df[col2], margins=True, margins_name='Total')

    def value_counts_with_pct(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Get value counts with percentages"""
        counts = df[column].value_counts()
        pct = df[column].value_counts(normalize=True) * 100

        result = pd.DataFrame({
            'Count': counts,
            'Percentage': pct.round(2)
        })
        result['Cumulative %'] = result['Percentage'].cumsum().round(2)

        return result
