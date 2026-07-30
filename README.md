# DataInsight Pro v1.1.0

**Enterprise Analytics Platform** - Transform your data into insights with professional analytics.

## 🚀 Features

### Core Capabilities
- 📁 **Multi-File Upload**: Upload multiple CSV/Excel files simultaneously (up to 75MB each)
- 🎨 **20+ Chart Types**: Histograms, scatter plots, 3D visualizations, time-series, and more
- 📊 **Advanced Statistics**: Normality tests, correlations, regression, hypothesis testing
- 🧹 **Data Cleaning**: Handle missing values, duplicates, outliers with visual tools
- 📄 **Custom Reports**: Generate PDF, HTML, and DOCX reports with custom branding
- 🌓 **Dark/Light Themes**: Auto-detect or manually switch themes
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🔮 **Forecasting**: Time-series predictions with confidence intervals
- ⚠️ **Anomaly Detection**: Multiple methods (IQR, Z-Score, Isolation Forest)
- 💾 **Profile Manager**: Save and load analysis settings
- 📋 **Pre-built Templates**: Sales, Research, Operations, Survey, IoT/Time-Series
- ⬇️ **Multiple Export Formats**: CSV, JSON, Excel, PDF, HTML, DOCX, ZIP

## 📦 Installation

### Local Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/data-analysis-tool.git
cd data-analysis-tool

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy with one click
5. Auto-deploys on every push to main branch

## 🎯 Usage

### Quick Start

1. **Upload Files**: Click "Upload CSV or Excel files" in the sidebar
2. **Select Files**: Choose which files to analyze from the list
3. **Explore Tabs**:
   - **Overview**: File info, data quality score, quick stats
   - **Inspect**: Data preview, quality report, cleaning options
   - **Analysis**: Choose and run statistical analyses
   - **Visualize**: Create interactive charts
   - **Report**: Generate custom PDF/HTML/DOCX reports
   - **Export**: Download data, statistics, and reports

### Sample Datasets

Try the app with built-in samples:
- 💰 **Sales Data**: Revenue, regional, category analysis
- 🔬 **Research Data**: Statistical analysis for research
- 📡 **IoT/Sensor Data**: Time-series and forecasting

## 📊 Analysis Templates

### 1. Sales Analysis
- Auto-detects: Date, Amount, Category, Region
- Charts: Time-series, regional breakdown, category analysis
- Stats: Revenue metrics, growth rates, forecasts

### 2. Research Data
- Auto-detects: Subject, Variables, Outcomes
- Charts: Distribution, correlations, group comparisons
- Stats: Hypothesis testing, effect sizes, ANOVA

### 3. Operational Metrics
- Auto-detects: Date, Metric, Department
- Charts: Trends, anomalies, KPIs
- Stats: Baselines, alerts, forecasts

### 4. Customer/Survey Data
- Auto-detects: Categorical responses, Ratings
- Charts: Response distribution, cross-tabulation
- Stats: Sentiment analysis, correlation with demographics

### 5. Time-Series (IoT/Sensors)
- Auto-detects: Timestamp, Sensor readings
- Charts: Time-series, patterns, anomalies
- Stats: Forecasting, seasonality, anomaly detection

## 🔧 Configuration

Edit `config.py` to customize:
- File size limits (default: 75MB)
- Supported formats
- Chart settings
- Color palettes
- Theme colors
- Feature toggles

## 📁 Project Structure

```
data-analysis-tool/
├── app.py                          # Main Streamlit app
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version
├── modules/
│   ├── file_handler.py            # Multi-file upload
│   ├── data_analyzer.py           # Statistics
│   ├── visualization.py           # Charts
│   ├── data_cleaner.py            # Data cleaning
│   ├── profile_manager.py         # User profiles
│   ├── template_manager.py        # Analysis templates
│   ├── report_generator.py        # PDF/HTML/DOCX
│   └── utils.py                   # Helpers
├── styles/
│   ├── theme_light.css            # Light theme
│   ├── theme_dark.css             # Dark theme
│   └── animations.css             # Animations
├── templates/
│   ├── sales_template.json
│   ├── research_template.json
│   ├── operations_template.json
│   ├── survey_template.json
│   └── timeseries_template.json
├── sample_data/
│   ├── sample_sales.csv
│   ├── sample_research.csv
│   └── sample_temperature.csv
└── outputs/
    ├── reports/
    ├── charts/
    └── temp/
```

## 🎨 Customization

### Themes
- **Light Theme**: Default professional blue/green
- **Dark Theme**: Easy on the eyes for long analysis sessions
- Toggle via the header button

### Color Palettes
- Viridis, Plasma, Cool, Warm, Blues, Reds, Greens, Custom
- Set in sidebar settings

### Report Templates
- Professional (corporate)
- Academic (research)
- Minimal (clean)
- Detailed (comprehensive)

## 🔒 Privacy & Security

- All analysis happens in your browser/session
- No data is sent to external servers
- Files are processed locally
- Session-based storage (cleared on browser close)

## 📈 Performance

- Handles files up to 75MB
- Up to 500,000 rows
- Analysis completes in <10 seconds for typical datasets
- Charts render in <3 seconds
- PDF generation in <5 seconds

## 🐛 Troubleshooting

### Common Issues

**File upload fails**
- Check file size (max 75MB)
- Verify format (CSV, XLSX, XLS only)
- Try different encoding (UTF-8 recommended)

**Charts not displaying**
- Check column data types
- Ensure sufficient data points
- Try different chart types

**Analysis errors**
- Verify data has no critical missing values
- Check for sufficient numeric columns
- Use cleaned data for better results

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the documentation
- Review the sample datasets

## 🎉 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Scikit-learn](https://scikit-learn.org/) - Machine learning
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [python-docx](https://python-docx.readthedocs.io/) - DOCX generation

---

**DataInsight Pro v1.1.0** - Enterprise Analytics Platform
Made with ❤️ for data enthusiasts
