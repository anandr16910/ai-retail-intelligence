# AI Retail Intelligence Web Dashboard

A comprehensive web dashboard built with Streamlit for the AI Retail Intelligence platform. This dashboard provides an intuitive interface for all platform capabilities including price forecasting, competitive pricing, market copilot, and document analysis.

## 🚀 Features

### Dashboard Pages

#### 🏠 Dashboard Overview
- **Key Metrics**: Real-time display of tracked products, current gold/silver prices, and best deal savings
- **Price Trends Chart**: Interactive visualization of precious metals price movements
- **Platform Comparison**: Bar chart showing average prices across e-commerce platforms
- **Recent Activity**: Best deals and platform status updates
- **Quick Stats**: Product count, latest prices, and system status indicators

#### 📈 Price Forecasting
- **Asset Selection**: Choose between Gold, Silver, or ETF forecasting
- **Configurable Parameters**: Adjust forecast horizon (1-90 days) and model type
- **Interactive Charts**: Historical data with forecast overlay and confidence intervals
- **Forecast Metrics**: Model performance indicators and accuracy scores
- **Trend Analysis**: Upward/downward trend identification with percentage changes

#### 💰 Competitive Pricing Intelligence
- **Product Search**: Search and filter products across the catalog
- **Price Comparison**: Side-by-side comparison across 6 major Indian platforms
- **Savings Calculator**: Automatic calculation of potential savings and percentages
- **Visual Analytics**: Color-coded bar charts highlighting best and worst prices
- **Price Trends**: 7-day trend analysis with directional indicators
- **Best Deals**: Ranked list of products with highest savings potential

#### 🤖 Market Copilot
- **Chat Interface**: Natural language conversation with AI assistant
- **Quick Actions**: Pre-defined buttons for common queries
- **Context Awareness**: Maintains conversation history and context
- **Multi-domain Support**: Handles pricing, forecasting, and market analysis queries
- **Real-time Responses**: Integration with all platform capabilities

#### 📄 Document Analysis
- **File Upload**: Support for TXT, PDF, and DOCX files (TXT implemented)
- **Text Input**: Direct paste functionality for document content
- **Entity Extraction**: Automatic identification of financial entities and metrics
- **Market Insights**: Categorized insights extraction from documents
- **Confidence Scoring**: Analysis confidence indicators
- **Sample Documents**: Pre-loaded examples for testing

#### ⚙️ Platform Status
- **System Monitoring**: Real-time status of all core services
- **Data Status**: Availability and record counts for all datasets
- **Integration Status**: Amazon Bedrock and Amazon Q framework status
- **Performance Metrics**: Response times, cache hit rates, and error rates
- **Configuration**: API settings and model parameters
- **Logs Viewer**: Recent system activity and events

#### 🔧 Amazon Q Integration
- **Status Dashboard**: Integration availability and requirements
- **Capabilities Overview**: Detailed breakdown of Amazon Q features
- **Demo Mode**: Mock responses demonstrating business reasoning and PDF analysis
- **Business Intelligence**: Sample queries and strategic analysis
- **Configuration Guide**: Future setup instructions and API endpoints

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- AI Retail Intelligence platform (main project)
- Streamlit and dashboard dependencies

### Step 1: Install Dashboard Dependencies
```bash
# From the project root directory
cd dashboard
pip install -r requirements.txt
```

### Step 2: Start the Main Platform API (Required)
```bash
# From the project root directory
python main.py --mode server
```

### Step 3: Launch Dashboard
```bash
# From the dashboard directory
streamlit run app.py
```

### Step 4: Access Dashboard
Open your browser and navigate to:
- **Dashboard URL**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs (main platform)

## 📊 Dashboard Screenshots & Features

### Dashboard Overview
- **Metrics Cards**: Key performance indicators with delta changes
- **Interactive Charts**: Plotly-powered visualizations with zoom and pan
- **Real-time Data**: Live updates from the platform API
- **Responsive Design**: Optimized for desktop and tablet viewing

### Price Forecasting Interface
- **Model Selection**: Choose between moving average and random forest models
- **Horizon Slider**: Adjust forecast period from 1 to 90 days
- **Confidence Intervals**: Visual representation of prediction uncertainty
- **Historical Context**: Last 60 days of price data for context

### Competitive Pricing Dashboard
- **Search Functionality**: Real-time product search with autocomplete
- **Comparison Matrix**: Detailed price breakdown by platform
- **Savings Highlights**: Color-coded indicators for best deals
- **Trend Indicators**: 📈📉➡️ icons showing price movement direction

### Market Copilot Chat
- **Conversational UI**: WhatsApp-style chat interface
- **Message History**: Persistent conversation tracking
- **Quick Actions**: One-click buttons for common queries
- **Rich Responses**: Formatted text with tables and lists

## 🎨 UI/UX Features

### Design Elements
- **Modern Styling**: Clean, professional interface with custom CSS
- **Color Coding**: Intuitive color schemes (green=good, red=expensive, blue=neutral)
- **Interactive Elements**: Hover effects, clickable charts, and responsive buttons
- **Loading States**: Spinners and progress indicators for better UX

### Navigation
- **Sidebar Menu**: Easy navigation between dashboard sections
- **Breadcrumbs**: Clear indication of current page location
- **Quick Stats**: Always-visible key metrics in sidebar
- **Status Indicators**: Real-time system health monitoring

### Data Visualization
- **Plotly Charts**: Interactive, zoomable, and exportable visualizations
- **Responsive Tables**: Sortable and filterable data displays
- **Progress Bars**: Visual confidence score indicators
- **Metric Cards**: Highlighted KPIs with trend indicators

## 🔧 Configuration

### Dashboard Settings
```python
# Page configuration
st.set_page_config(
    page_title="AI Retail Intelligence Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### API Integration
```python
# API base URL configuration
api_base_url = "http://localhost:8000/api/v1"

# Timeout settings
request_timeout = 5  # seconds
```

### Chart Configuration
```python
# Default chart settings
chart_height = 400
chart_colors = {
    'gold': 'gold',
    'silver': 'silver',
    'best_price': 'green',
    'worst_price': 'red'
}
```

## 🚀 Usage Examples

### Starting the Dashboard
```bash
# Terminal 1: Start main platform
python main.py --mode server

# Terminal 2: Start dashboard
cd dashboard
streamlit run app.py
```

### Accessing Features
1. **Overview**: Navigate to dashboard for system summary
2. **Forecasting**: Select asset → Set parameters → Generate forecast
3. **Pricing**: Search product → Compare prices → View savings
4. **Chat**: Type query → Get AI response → Continue conversation
5. **Documents**: Upload file → Select analysis type → View insights

### Sample Queries for Market Copilot
- "Compare prices for Godrej Single Door Fridge"
- "What are the current gold price trends?"
- "Show me the best deals available"
- "Give me a market summary"
- "What's the forecast for silver prices?"

## 🔍 Troubleshooting

### Common Issues

#### Dashboard Won't Start
```bash
# Check Streamlit installation
pip install streamlit

# Verify Python path
python --version

# Check port availability
netstat -an | grep 8501
```

#### API Connection Errors
```bash
# Verify main platform is running
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/api/v1/data/status
```

#### Import Errors
```bash
# Ensure running from correct directory
cd dashboard
python -c "import sys; print(sys.path)"

# Verify parent directory access
ls ../src/
```

#### Data Loading Issues
```bash
# Check data files exist
ls ../data/

# Verify CSV format
head ../data/competitive_pricing_sample.csv
```

### Performance Optimization

#### Caching
```python
# Use Streamlit caching for expensive operations
@st.cache_data
def load_data():
    return data_loader.load_all_data()
```

#### Memory Management
```python
# Clear large objects when not needed
del large_dataframe
gc.collect()
```

## 🎯 Future Enhancements

### Phase 1 (Immediate)
- [ ] Real-time data refresh
- [ ] Export functionality for charts and reports
- [ ] User authentication and sessions
- [ ] Mobile-responsive design improvements

### Phase 2 (Short-term)
- [ ] Advanced filtering and search
- [ ] Custom dashboard layouts
- [ ] Email/SMS alerts for price changes
- [ ] Integration with external data sources

### Phase 3 (Long-term)
- [ ] Multi-user support with role-based access
- [ ] Advanced analytics and machine learning insights
- [ ] API rate limiting and usage analytics
- [ ] White-label customization options

## 📱 Mobile Compatibility

The dashboard is designed to be responsive and works on:
- **Desktop**: Full feature set with optimal layout
- **Tablet**: Adapted layout with touch-friendly controls
- **Mobile**: Core functionality with simplified interface

## 🔒 Security Considerations

### Data Protection
- No sensitive data stored in browser
- API calls use secure HTTP methods
- Input validation for all user inputs
- Error handling prevents information leakage

### Access Control
- Local deployment by default
- No external API keys required
- Optional authentication can be added
- Audit logging for user actions

## 📄 License

This dashboard is part of the AI Retail Intelligence platform developed for the AI for Bharat Hackathon. Please refer to the main project license for usage terms.

## 🆘 Support

For dashboard-specific issues:

1. **Check Logs**: Streamlit logs appear in terminal
2. **Verify Setup**: Ensure main platform API is running
3. **Test Components**: Use individual page functions
4. **Browser Console**: Check for JavaScript errors

For platform issues, refer to the main project documentation.

---

**Built with ❤️ using Streamlit**

*Interactive web interface for AI-powered retail intelligence*