# Teachers Bot v2.0

Modern Telegram bot for teacher management with integrated lesson monitoring.

## Features

- 🏠 **Modern Menu UI**: Intuitive navigation with inline keyboards
- 📝 **Self-Registration**: Teachers can register themselves
- 📚 **Lesson Management**: Create, view, edit, and manage lessons
- 💰 **Financial Dashboard**: Track invoices and earnings
- 🔔 **Smart Notifications**: Integrated lesson confirmation system
- ⚡ **Real-time Updates**: Live updates from lesson-checker service

## Architecture

This bot integrates with:
- **teachers-api**: All database operations via REST API
- **lesson-checker**: Receives notifications for lesson confirmations
- **Redis**: State management and caching
- **RabbitMQ**: Message queue for notifications

## Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the bot:**
   ```bash
   poetry run python main.py
   ```

## Configuration

Key environment variables:

- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
- `TEACHERS_API_URL`: URL of the teachers-api service
- `REDIS_HOST`: Redis server for state management
- `RABBIT_HOST`: RabbitMQ server for notifications

## Project Structure

```
teachers-bot-v2/
├── core/              # Core bot components
│   ├── bot.py         # Bot initialization
│   └── config.py      # Configuration management
├── handlers/          # Message and callback handlers
│   ├── main_menu.py   # Main navigation
│   ├── registration.py # Teacher registration
│   └── lessons.py     # Lesson management
├── keyboards/         # Inline keyboard layouts
├── services/          # External service integrations
├── models/           # Data models and FSM states
└── utils/            # Utility functions
```

## Key Improvements over v1

- **Modern UX**: Replace commands with visual menus
- **Self-Service**: Complete registration flow
- **API Integration**: No direct database access
- **Real-time**: Integrated notification handling
- **Scalable**: Clean architecture for future features

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
```

### Adding New Features

1. Create handler in `handlers/`
2. Add keyboards in `keyboards/`
3. Register handler in `main.py`
4. Add API calls in `services/api_client.py`

## Deployment

The bot can be deployed using:
- Docker container
- Kubernetes deployment
- Systemd service
- PM2 process manager

See deployment guide in docs/ for details.

## Integration with Existing Services

### teachers-api
All database operations go through the REST API:
- Teacher CRUD operations
- Lesson management
- Invoice tracking

### lesson-checker
Receives RabbitMQ messages for:
- Lesson confirmation requests
- Automatic reminder notifications

### Notification Flow
```
lesson-checker → RabbitMQ → bot → Telegram user
```

## Support

For issues and feature requests, contact the development team.