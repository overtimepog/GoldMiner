# GoldMiner Demo Guide 🚀

## Quick Start

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Start the Application**
   ```bash
   python start_demo.py
   ```

3. **Access the Application**
   - 🌐 Web UI: http://localhost:8501
   - 📡 API: http://localhost:8000
   - 📚 API Docs: http://localhost:8000/docs

## Using the Application

### Generate Ideas
1. Open the Web UI at http://localhost:8501
2. Select your market focus (e.g., Healthcare, Technology)
3. Choose innovation type (Product, Service, Business Model)
4. Click "🚀 Generate New Idea"
5. The AI will create a unique startup concept using OpenRouter's free models

### Validate Ideas
1. After generating an idea, click "Validate" 
2. Choose validation depth (standard, deep, comprehensive)
3. Click "🔍 Run Validation"
4. View detailed scores across 4 dimensions:
   - Problem Validation (25%)
   - Solution Validation (25%)
   - Market Validation (30%)
   - Execution Validation (20%)

### Market Research
1. Navigate to the "Market Research" tab
2. Select research depth
3. Click "🔍 Conduct Research"
4. View competitive analysis, market size, and trends

## API Testing

Test the API directly:

```bash
# Test root endpoint
curl http://localhost:8000/

# Generate an idea via API
curl -X POST http://localhost:8000/api/ideas/generate \
  -H "Content-Type: application/json" \
  -d '{
    "market_focus": "Healthcare",
    "innovation_type": "Service",
    "target_demographic": "Seniors",
    "problem_area": "Remote health monitoring"
  }'
```

## Troubleshooting

1. **Port Already in Use**
   ```bash
   # Kill existing processes
   pkill -f uvicorn
   pkill -f streamlit
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key Issues**
   - Ensure your OpenRouter API key is in the `.env` file
   - Get a free key at: https://openrouter.ai/

## Features Demonstrated

✅ **Multi-Agent AI System**
- Idea Generator Agent (Creative AI)
- Market Researcher Agent (Analysis AI)
- Validator Agent (Evaluation AI)

✅ **Free AI Models**
- Google Gemini 2.0 Flash (Reasoning)
- Meta LLaMA 4 Maverick (Creativity)
- Google Gemini Flash 1.5 (Processing)

✅ **Full Stack Application**
- FastAPI Backend with REST APIs
- Streamlit Frontend with Interactive UI
- SQLite Database for Persistence
- Real-time Validation Scoring

✅ **Professional Features**
- Comprehensive API Documentation
- Error Handling & Logging
- Docker Ready Architecture
- Export Capabilities (PDF/CSV ready)

## Next Steps

1. **Test Different Markets**: Try generating ideas for various industries
2. **Compare Validations**: Generate multiple ideas and compare scores
3. **API Integration**: Use the REST API to integrate with other tools
4. **Customize Prompts**: Modify prompts in `app/core/prompts.py`

Enjoy exploring AI-powered startup validation! 🎉