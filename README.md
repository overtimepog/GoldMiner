# GoldMiner 2.0 💡

AI-Powered Startup Idea Generation and Validation System with Enhanced UI

## Overview

GoldMiner is an autonomous AI system that generates novel startup ideas and validates them through comprehensive market research, competitive analysis, and validation frameworks. Built entirely on free AI models accessible through OpenRouter.

**Version 2.0 Features a completely redesigned UI with full idea management capabilities!**

## Features

### Core Features
- 🚀 **Autonomous Idea Generation**: AI-powered startup concept creation
- 📊 **Market Research Automation**: Real-time competitive analysis
- ✅ **Validation Framework**: Comprehensive scoring and validation
- 💰 **Cost-Effective**: Built on free AI models
- 🔄 **Multi-Agent Architecture**: Specialized agents for different tasks

### 🆕 New in Version 2.0
- ⏱️ **Real-Time Progress**: Live updates during goldmining with stop/pause controls
- ✏️ **Full Idea Management**: Edit, delete, and manually validate any idea
- 📋 **Kanban Board View**: Visual organization by status (Pending/Validated/Rejected)
- 🔍 **Advanced Filtering**: Filter by status, score, and sort by multiple criteria
- 📤 **Export Options**: Download ideas as CSV, JSON, or Markdown
- 🎨 **Modern UI**: Clean, responsive design with intuitive navigation
- 🔌 **WebSocket Support**: Real-time updates without page refresh

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key (get free at https://openrouter.ai)

### One-Command Setup & Run

```bash
# Clone the repository
git clone https://github.com/yourusername/GoldMiner.git
cd GoldMiner

# Run everything with one command
./run.sh
```

That's it! The `run.sh` script will:
- ✅ Check Docker installation
- ✅ Create .env file if needed
- ✅ Build Docker container
- ✅ Start both backend and frontend
- ✅ Display live logs

### Access the Application

Once running, access:
- 🌐 **Enhanced Web UI**: http://localhost:8501
- 📡 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🔌 **WebSocket**: ws://localhost:8000/ws

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed directory layout.

### Docker Commands

```bash
# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

## Development

### Project Structure

```
GoldMiner/
├── app/
│   ├── api/          # FastAPI backend
│   ├── agents/       # AI agents
│   ├── db/          # Database models
│   ├── ui/          # Streamlit interface
│   └── utils/       # Utilities
├── tests/           # Test suite
├── docs/            # Documentation
└── .taskmaster/     # Task management
```

### Task Management

This project uses Task Master AI for development workflow:

```bash
# View current tasks
task-master list

# Get next task
task-master next

# Mark task complete
task-master set-status --id=<id> --status=done
```

## License

MIT License - see LICENSE file for details