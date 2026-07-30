"""
Visualization Module
All chart types: basic, advanced, 3D, time-series
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import COLOR_PALETTES, CHART_HEIGHT, CHART_WIDTH


class Visualization:
    """Creates all chart types for data analysis"""

    def __init__(self, theme: str = 'light', palette: str = 'Viridis'):
        self.theme = theme
        self.palette = palette
        self.colors = COLOR_PALETTES.get(palette, COLOR_PALETTES['Viridis'])
        self.template = 'plotly_white' if theme == 'light' else 'plotly_dark'

    def get_color_sequence(self, n: int = 1) -> List[str]:
        """Get n colors from current palette"""
        if n <= len(self.colors):
            return self.colors[:n]
        # Repeat colors if more needed
        return [self.colors[i % len(self.colors)] for i in range(n)]

    def get_continuous_colorscale(self) -> List:
        """Get continuous colorscale for heatmaps"""
        if self.palette in ['Blues', 'Reds', 'Greens']:
            return self.palette.lower()
        return self.palette

    # ==================== NUMERICAL CHARTS ====================

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30,
                  show_kde: bool = True) -> go.Figure:
        """Histogram with optional KDE curve"""
        data = df[column].dropna()

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=data,
            nbinsx=bins,
            name='Frequency',
            marker_color=self.colors[0],
            opacity=0.75,
            histnorm='probability density' if show_kde else None
        ))

        # KDE curve
        if show_kde and len(data) > 1:
            try:
                from scipy import stats
                kde = stats.gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 200)
                y_kde = kde(x_range)

                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_kde,
                    mode='lines',
                    name='Density',
                    line=dict(color=self.colors[1], width=3)
                ))
            except:
                pass

        fig.update_layout(
            title=f'Distribution of {column}',
            xaxis_title=column,
            yaxis_title='Frequency' if not show_kde else 'Density',
            template=self.template,
            height=CHART_HEIGHT,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def box_plot(self, df: pd.DataFrame, columns: List[str],
                 group_by: Optional[str] = None) -> go.Figure:
        """Box plot for one or multiple columns"""
        fig = go.Figure()

        if group_by:
            groups = df[group_by].unique()
            colors = self.get_color_sequence(len(groups))

            for i, group in enumerate(groups):
                group_data = df[df[group_by] == group]
                for col in columns:
                    fig.add_trace(go.Box(
                        y=group_data[col].dropna(),
                        name=f'{col}<br>({group})',
                        marker_color=colors[i],
                        boxmean='sd'
                    ))
        else:
            colors = self.get_color_sequence(len(columns))
            for i, col in enumerate(columns):
                fig.add_trace(go.Box(
                    y=df[col].dropna(),
                    name=col,
                    marker_color=colors[i],
                    boxmean='sd'
                ))

        fig.update_layout(
            title='Box Plot',
            yaxis_title='Value',
            template=self.template,
            height=CHART_HEIGHT,
            showlegend=True
        )

        return fig

    def violin_plot(self, df: pd.DataFrame, columns: List[str],
                    group_by: Optional[str] = None) -> go.Figure:
        """Violin plot"""
        fig = go.Figure()

        if group_by:
            groups = df[group_by].unique()
            colors = self.get_color_sequence(len(groups))

            for i, group in enumerate(groups):
                group_data = df[df[group_by] == group]
                for col in columns:
                    fig.add_trace(go.Violin(
                        y=group_data[col].dropna(),
                        name=f'{col}<br>({group})',
                        marker_color=colors[i],
                        box_visible=True,
                        meanline_visible=True
                    ))
        else:
            colors = self.get_color_sequence(len(columns))
            for i, col in enumerate(columns):
                fig.add_trace(go.Violin(
                    y=df[col].dropna(),
                    name=col,
                    marker_color=colors[i],
                    box_visible=True,
                    meanline_visible=True
                ))

        fig.update_layout(
            title='Violin Plot',
            yaxis_title='Value',
            template=self.template,
            height=CHART_HEIGHT,
            showlegend=True
        )

        return fig

    def scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str,
                    color_col: Optional[str] = None, size_col: Optional[str] = None,
                    trendline: bool = True) -> go.Figure:
        """Scatter plot with optional trendline"""
        data = df[[x_col, y_col]].dropna()

        if color_col:
            data[color_col] = df[color_col]

        if size_col:
            data[size_col] = df[size_col]

        if trendline and len(data) > 2:
            fig = px.scatter(
                data, x=x_col, y=y_col,
                color=color_col,
                size=size_col,
                trendline='ols',
                template=self.template,
                color_discrete_sequence=self.colors
            )
        else:
            fig = px.scatter(
                data, x=x_col, y=y_col,
                color=color_col,
                size=size_col,
                template=self.template,
                color_discrete_sequence=self.colors
            )

        fig.update_layout(
            title=f'{y_col} vs {x_col}',
            height=CHART_HEIGHT,
            hovermode='closest'
        )
        fig.update_traces(marker=dict(size=8, opacity=0.7))

        return fig

    def density_2d(self, df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """2D density plot"""
        data = df[[x_col, y_col]].dropna()

        fig = go.Figure()

        try:
            # Use histogram2dcontour
            fig = go.Figure(go.Histogram2dContour(
                x=data[x_col],
                y=data[y_col],
                colorscale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette,
                contours=dict(
                    showlabels=True,
                    labelfont=dict(size=12, color='white')
                )
            ))

            # Add scatter overlay
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode='markers',
                marker=dict(size=4, color='rgba(255,255,255,0.5)'),
                showlegend=False,
                hoverinfo='skip'
            ))
        except:
            # Fallback to scatter
            fig = px.scatter(data, x=x_col, y=y_col, template=self.template)

        fig.update_layout(
            title=f'2D Density: {x_col} vs {y_col}',
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=CHART_HEIGHT,
            template=self.template
        )

        return fig

    def qq_plot(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Q-Q plot for normality check"""
        data = df[column].dropna().values
        data_standardized = (data - np.mean(data)) / np.std(data)

        # Theoretical quantiles
        theoretical = np.random.normal(0, 1, len(data_standardized))
        theoretical.sort()

        data_sorted = np.sort(data_standardized)

        fig = go.Figure()

        # Q-Q points
        fig.add_trace(go.Scatter(
            x=theoretical,
            y=data_sorted,
            mode='markers',
            name='Q-Q Points',
            marker=dict(color=self.colors[0], size=6, opacity=0.7)
        ))

        # Reference line
        min_val = min(theoretical.min(), data_sorted.min())
        max_val = max(theoretical.max(), data_sorted.max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Normal Reference',
            line=dict(color=self.colors[1], width=2, dash='dash')
        ))

        fig.update_layout(
            title=f'Q-Q Plot: {column}',
            xaxis_title='Theoretical Quantiles',
            yaxis_title='Sample Quantiles',
            template=self.template,
            height=CHART_HEIGHT,
            showlegend=True
        )

        return fig

    # ==================== CATEGORICAL CHARTS ====================

    def bar_chart(self, df: pd.DataFrame, x_col: str, y_col: Optional[str] = None,
                 orientation: str = 'vertical', top_n: int = 20) -> go.Figure:
        """Bar chart (horizontal or vertical)"""
        if y_col is None:
            # Value counts
            data = df[x_col].value_counts().head(top_n)
            if orientation == 'vertical':
                fig = go.Figure(go.Bar(
                    x=data.index.astype(str),
                    y=data.values,
                    marker_color=self.colors[0],
                    text=data.values,
                    textposition='auto'
                ))
            else:
                fig = go.Figure(go.Bar(
                    y=data.index.astype(str),
                    x=data.values,
                    orientation='h',
                    marker_color=self.colors[0],
                    text=data.values,
                    textposition='auto'
                ))
        else:
            # Aggregated
            if orientation == 'vertical':
                fig = px.bar(df, x=x_col, y=y_col, template=self.template,
                           color_discrete_sequence=self.colors)
            else:
                fig = px.bar(df, x=y_col, y=x_col, orientation='h',
                           template=self.template,
                           color_discrete_sequence=self.colors)

        fig.update_layout(
            title=f'Bar Chart: {x_col}' + (f' by {y_col}' if y_col else ''),
            height=CHART_HEIGHT,
            template=self.template,
            showlegend=False
        )

        return fig

    def pie_chart(self, df: pd.DataFrame, column: str, top_n: int = 10) -> go.Figure:
        """Pie chart"""
        data = df[column].value_counts().head(top_n)

        fig = go.Figure(go.Pie(
            labels=data.index.astype(str),
            values=data.values,
            marker=dict(colors=self.get_color_sequence(len(data))),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
        ))

        fig.update_layout(
            title=f'Distribution of {column}',
            height=CHART_HEIGHT,
            template=self.template
        )

        return fig

    def treemap(self, df: pd.DataFrame, path_cols: List[str], value_col: Optional[str] = None) -> go.Figure:
        """Treemap"""
        if value_col is None:
            # Count occurrences
            grouped = df.groupby(path_cols).size().reset_index(name='count')
            value_col = 'count'

        try:
            fig = px.treemap(
                grouped,
                path=path_cols,
                values=value_col,
                template=self.template,
                color=value_col,
                color_continuous_scale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette
            )
        except:
            # Fallback
            fig = px.treemap(
                grouped,
                path=path_cols,
                values=value_col,
                template=self.template
            )

        fig.update_layout(
            title='Treemap',
            height=CHART_HEIGHT
        )

        return fig

    def sunburst(self, df: pd.DataFrame, path_cols: List[str], value_col: Optional[str] = None) -> go.Figure:
        """Sunburst chart"""
        if value_col is None:
            grouped = df.groupby(path_cols).size().reset_index(name='count')
            value_col = 'count'

        fig = px.sunburst(
            grouped,
            path=path_cols,
            values=value_col,
            template=self.template,
            color=value_col,
            color_continuous_scale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette
        )

        fig.update_layout(
            title='Sunburst Chart',
            height=CHART_HEIGHT
        )

        return fig

    # ==================== TIME-SERIES CHARTS ====================

    def line_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str],
                  show_trend: bool = True) -> go.Figure:
        """Line chart with trend"""
        fig = go.Figure()
        colors = self.get_color_sequence(len(y_cols))

        for i, y_col in enumerate(y_cols):
            data = df[[x_col, y_col]].dropna().sort_values(x_col)

            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode='lines+markers',
                name=y_col,
                line=dict(color=colors[i], width=2),
                marker=dict(size=6)
            ))

            # Add trend line
            if show_trend and len(data) > 2:
                try:
                    x_numeric = pd.to_numeric(pd.to_datetime(data[x_col]))
                    if pd.api.types.is_numeric_dtype(x_numeric):
                        z = np.polyfit(range(len(data)), data[y_col], 1)
                        p = np.poly1d(z)
                        trend_y = p(range(len(data)))

                        fig.add_trace(go.Scatter(
                            x=data[x_col],
                            y=trend_y,
                            mode='lines',
                            name=f'{y_col} (trend)',
                            line=dict(color=colors[i], width=1, dash='dash'),
                            opacity=0.5
                        ))
                except:
                    pass

        fig.update_layout(
            title='Time Series',
            xaxis_title=x_col,
            yaxis_title='Value',
            template=self.template,
            height=CHART_HEIGHT,
            hovermode='x unified'
        )

        return fig

    def area_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str]) -> go.Figure:
        """Area chart"""
        fig = go.Figure()
        colors = self.get_color_sequence(len(y_cols))

        for i, y_col in enumerate(y_cols):
            data = df[[x_col, y_col]].dropna().sort_values(x_col)

            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode='lines',
                name=y_col,
                fill='tozeroy',
                line=dict(color=colors[i], width=2),
                opacity=0.6
            ))

        fig.update_layout(
            title='Area Chart',
            xaxis_title=x_col,
            yaxis_title='Value',
            template=self.template,
            height=CHART_HEIGHT
        )

        return fig

    def candlestick(self, df: pd.DataFrame, date_col: str,
                   open_col: str, high_col: str, low_col: str, close_col: str) -> go.Figure:
        """Candlestick chart for OHLC data"""
        data = df[[date_col, open_col, high_col, low_col, close_col]].dropna().sort_values(date_col)

        fig = go.Figure(go.Candlestick(
            x=data[date_col],
            open=data[open_col],
            high=data[high_col],
            low=data[low_col],
            close=data[close_col],
            increasing_line_color=self.colors[2],
            decreasing_line_color=self.colors[3]
        ))

        fig.update_layout(
            title='Candlestick Chart',
            xaxis_title=date_col,
            yaxis_title='Price',
            template=self.template,
            height=CHART_HEIGHT
        )

        return fig

    # ==================== RELATIONSHIPS ====================

    def correlation_heatmap(self, df: pd.DataFrame, columns: List[str],
                          method: str = 'pearson') -> go.Figure:
        """Correlation heatmap"""
        corr = df[columns].corr(method=method)

        fig = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette,
            zmid=0,
            text=corr.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title=f'Correlation Heatmap ({method.capitalize()})',
            template=self.template,
            height=CHART_HEIGHT,
            width=CHART_HEIGHT
        )

        return fig

    def pair_plot(self, df: pd.DataFrame, columns: List[str],
                 color_col: Optional[str] = None) -> go.Figure:
        """Pair plot (scatter matrix)"""
        data = df[columns].dropna()

        if color_col and color_col in df.columns:
            data[color_col] = df[color_col]

        fig = px.scatter_matrix(
            data,
            dimensions=columns,
            color=color_col,
            template=self.template,
            color_discrete_sequence=self.colors
        )

        fig.update_layout(
            title='Pair Plot (Scatter Matrix)',
            height=CHART_HEIGHT + 200,
            showlegend=True
        )

        return fig

    def bubble_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                    size_col: str, color_col: Optional[str] = None) -> go.Figure:
        """Bubble chart"""
        data = df[[x_col, y_col, size_col]].dropna()

        if color_col:
            data[color_col] = df[color_col]

        fig = px.scatter(
            data, x=x_col, y=y_col, size=size_col, color=color_col,
            template=self.template,
            color_discrete_sequence=self.colors,
            size_max=60
        )

        fig.update_layout(
            title=f'Bubble Chart: {y_col} vs {x_col}',
            height=CHART_HEIGHT
        )

        return fig

    # ==================== ADVANCED CHARTS ====================

    def scatter_3d(self, df: pd.DataFrame, x_col: str, y_col: str, z_col: str,
                  color_col: Optional[str] = None) -> go.Figure:
        """3D scatter plot"""
        data = df[[x_col, y_col, z_col]].dropna()

        if color_col and color_col in df.columns:
            data[color_col] = df[color_col]

        fig = px.scatter_3d(
            data, x=x_col, y=y_col, z=z_col,
            color=color_col,
            template=self.template,
            color_discrete_sequence=self.colors
        )

        fig.update_layout(
            title=f'3D Scatter: {x_col}, {y_col}, {z_col}',
            height=CHART_HEIGHT
        )

        return fig

    def surface_3d(self, df: pd.DataFrame, x_col: str, y_col: str, z_col: str) -> go.Figure:
        """3D surface plot"""
        try:
            # Create pivot for surface
            pivot = df.pivot_table(values=z_col, index=y_col, columns=x_col, aggfunc='mean')

            fig = go.Figure(go.Surface(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette
            ))

            fig.update_layout(
                title='3D Surface Plot',
                height=CHART_HEIGHT,
                template=self.template
            )

            return fig
        except:
            # Fallback to 3D scatter
            return self.scatter_3d(df, x_col, y_col, z_col)

    def parallel_coordinates(self, df: pd.DataFrame, columns: List[str],
                           color_col: Optional[str] = None) -> go.Figure:
        """Parallel coordinates plot"""
        data = df[columns].dropna()

        if color_col and color_col in df.columns:
            data[color_col] = df[color_col]

        fig = px.parallel_coordinates(
            data,
            color=color_col,
            template=self.template,
            color_continuous_scale=self.palette.lower() if self.palette in ['Blues', 'Reds', 'Greens'] else self.palette
        )

        fig.update_layout(
            title='Parallel Coordinates',
            height=CHART_HEIGHT
        )

        return fig

    # ==================== SPECIAL CHARTS ====================

    def missing_values_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Heatmap showing missing value pattern"""
        missing = df.isnull().astype(int)

        fig = go.Figure(go.Heatmap(
            z=missing.values,
            x=missing.columns,
            y=[f'Row {i}' for i in range(len(missing))],
            colorscale=[[0, self.colors[0]], [1, self.colors[2] if len(self.colors) > 2 else '#FF4D4F']],
            showscale=False,
            hovertemplate='Column: %{x}<br>Row: %{y}<br>Missing: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title='Missing Values Pattern',
            xaxis_title='Columns',
            yaxis_title='Rows',
            template=self.template,
            height=CHART_HEIGHT
        )

        return fig

    def forecast_plot(self, forecast_data: Dict) -> go.Figure:
        """Plot forecast with confidence intervals"""
        fig = go.Figure()

        # Historical data
        fig.add_trace(go.Scatter(
            x=forecast_data['historical_dates'],
            y=forecast_data['historical_values'],
            mode='lines+markers',
            name='Historical',
            line=dict(color=self.colors[0], width=2),
            marker=dict(size=6)
        ))

        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_data['forecast_dates'],
            y=forecast_data['forecast_values'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color=self.colors[1], width=2, dash='dash'),
            marker=dict(size=6)
        ))

        # Confidence interval
        if 'ci_upper' in forecast_data and 'ci_lower' in forecast_data:
            fig.add_trace(go.Scatter(
                x=forecast_data['forecast_dates'] + forecast_data['forecast_dates'][::-1],
                y=forecast_data['ci_upper'] + forecast_data['ci_lower'][::-1],
                fill='toself',
                fillcolor='rgba(128,128,128,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% CI',
                showlegend=True
            ))

        fig.update_layout(
            title=f'Forecast ({forecast_data.get("method", "").replace("_", " ").title()})',
            xaxis_title='Date',
            yaxis_title='Value',
            template=self.template,
            height=CHART_HEIGHT,
            hovermode='x unified'
        )

        return fig

    def regression_plot(self, regression_data: Dict, x_col: str, y_col: str) -> go.Figure:
        """Plot regression results"""
        fig = go.Figure()

        # Data points
        fig.add_trace(go.Scatter(
            x=regression_data['x_data'],
            y=regression_data['y_data'],
            mode='markers',
            name='Data',
            marker=dict(color=self.colors[0], size=8, opacity=0.6)
        ))

        # Regression line
        fig.add_trace(go.Scatter(
            x=regression_data['x_pred'],
            y=regression_data['y_pred'],
            mode='lines',
            name=f"Fit (R²={regression_data['r_squared']:.4f})",
            line=dict(color=self.colors[1], width=3)
        ))

        fig.update_layout(
            title=f"Regression: {y_col} vs {x_col}<br><sub>{regression_data.get('equation', '')}</sub>",
            xaxis_title=x_col,
            yaxis_title=y_col,
            template=self.template,
            height=CHART_HEIGHT
        )

        return fig

    def distribution_plot(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Combined distribution plot"""
        data = df[column].dropna()

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Histogram', 'Box Plot'),
            column_widths=[0.7, 0.3]
        )

        # Histogram
        fig.add_trace(
            go.Histogram(
                x=data,
                nbinsx=30,
                marker_color=self.colors[0],
                name='Distribution',
                showlegend=False
            ),
            row=1, col=1
        )

        # Box plot
        fig.add_trace(
            go.Box(
                y=data,
                marker_color=self.colors[1],
                name='Box',
                showlegend=False
            ),
            row=1, col=2
        )

        fig.update_layout(
            title=f'Distribution Analysis: {column}',
            template=self.template,
            height=CHART_HEIGHT,
            showlegend=False
        )

        return fig
