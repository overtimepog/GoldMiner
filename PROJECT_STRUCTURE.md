# GoldMiner Project Structure

## Directory Layout

```
GoldMiner/
├── app/                    # Main application code
│   ├── agents/            # AI agent implementations
│   │   ├── browser_pain_point_agent.py
│   │   ├── idea_generator.py
│   │   ├── market_researcher.py
│   │   ├── pain_point_researcher.py
│   │   └── validator.py
│   ├── api/               # FastAPI backend
│   │   ├── main.py       # API entry point
│   │   ├── websocket.py  # WebSocket support
│   │   └── routers/      # API route handlers
│   │       ├── ideas.py
│   │       ├── pain_points.py
│   │       ├── research.py
│   │       └── validation.py
│   ├── core/             # Core utilities
│   │   ├── config.py     # Configuration management
│   │   ├── openrouter.py # OpenRouter client
│   │   ├── perplexity_client.py
│   │   └── prompts.py    # AI prompts
│   ├── db/               # Database layer
│   │   ├── crud.py       # CRUD operations
│   │   ├── database.py   # Database connection
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── migrate.py    # Migration utilities
│   └── ui/               # Streamlit frontend
│       └── main.py       # Enhanced UI v2
│
├── data/                  # Data storage (auto-created)
├── logs/                  # Application logs (auto-created)
├── docs/                  # Documentation
│   ├── AGENTS.md         # Agent architecture
│   ├── DEMO.md           # Demo instructions
│   ├── UI_V2_FEATURES.md # UI features guide
│   └── UPGRADE_TO_V2.md  # Upgrade guide
├── scripts/              # Utility scripts
│   ├── check_deps.py     # Dependency checker
│   ├── setup.sh          # Local setup script
│   └── start_local.py    # Local startup script
│
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── .taskmaster/         # Task management
├── .vscode/             # VSCode settings
│   └── mcp.json        # MCP configuration
├── CLAUDE.md            # AI assistant instructions
├── docker-compose.yml   # Docker composition
├── Dockerfile          # Docker image definition
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
└── run.sh             # Main startup script
```

## Key Files

### Entry Points
- `run.sh` - Main Docker-based startup script
- `app/api/main.py` - FastAPI backend entry
- `app/ui/main.py` - Streamlit frontend entry

### Configuration
- `.env` - Environment variables (API keys)
- `app/core/config.py` - Application settings

### Database
- `data/goldminer.db` - SQLite database (auto-created)
- `app/db/models.py` - Data models

### Docker
- `Dockerfile` - Container definition
- `docker-compose.yml` - Service orchestration

## Removed/Cleaned
- Test files (`test_*.py`)
- Duplicate editor configs (`.cursor/`, `.roo/`, etc.)
- Alembic migrations (using custom migration)
- Unused dependencies
- `__pycache__` directories
- Old UI version