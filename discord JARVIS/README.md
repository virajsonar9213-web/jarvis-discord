# JARVIS - Your Personal AI Assistant Inside Discord

Private AI Discord bot. Python, discord.py, Google Gemini, SQLite. Exactly two
authorized users (Owner + Friend).

## Tech Stack

- Python 3.11+
- discord.py 2.x (slash commands via `app_commands`)
- Google Gemini (`google-genai`)
- SQLite (`aiosqlite`)
- python-dotenv
- edge-tts (TTS, Phase 5)
- FFmpeg (audio playback, Phase 5)

## Project Structure

```
.
├── main.py                  # Entry point: validates env, starts the bot
├── bot.py                   # JARVISBot class, component wiring, lifecycle
├── config/
│   ├── settings.py          # Environment-backed settings + validation
│   ├── permissions.py       # Owner/Friend authorization rules
│   └── channels.py          # Server/channel configuration objects
├── database/
│   ├── database.py          # aiosqlite wrapper, schema bootstrap
│   ├── schema.sql           # Tables: users, memories, reminders, ...
│   └── migrations/          # Future schema migrations
├── utils/
│   ├── logger.py            # Console + file logging
│   ├── error_handler.py     # Centralized error handling
│   └── helpers.py           # Small formatting/parsing utilities
├── ai/
│   ├── gemini.py            # Gemini client (text, context, images)
│   ├── personality.py       # JARVIS system instructions/tone
│   ├── memory.py            # Memory manager
│   ├── context.py           # Per-user/channel conversation context
│   └── tools.py             # Gemini tool/function-calling registry
├── commands/
│   ├── register.py          # Registers all slash commands on the tree
│   ├── ask.py  help.py  status.py  summarize.py
│   ├── read.py  remind.py  memory.py  settings.py  voice.py
├── events/
│   ├── on_ready.py          # Connection/guild logging
│   ├── on_message.py        # Message pipeline (authorization, routing)
│   └── on_interaction.py    # Component interactions (approval buttons)
└── services/
    ├── message_reader.py  message_sender.py
    ├── summarizer.py       notifications.py
    ├── approval.py         voice.py
    ├── reminder.py         image_analyzer.py
```

## Slash Commands

| Command | Purpose |
|---|---|
| `/ask question:` | Ask JARVIS a question (AI answer lands in Phase 2) |
| `/help` | In-Discord command reference |
| `/status` | Bot, AI, database and memory status |
| `/summarize [channel] [limit]` | Summarize recent channel messages |
| `/read action:` | start / stop / pause / resume / change channel |
| `/remind action:` | add / list / complete / delete |
| `/memory action:` | list / add / delete / forget |
| `/settings action:` | view / set / reset (owner only) |
| `/voice action:` | join / leave / speak / stop (Phase 5) |

Slash commands do not require the privileged Message Content Intent. `!help`,
`!status`, `!ping` and `@JARVIS` mentions only work if that intent is enabled
in the Discord Developer Portal.

## Setup

1. Copy `.env.example` to `.env`
2. Fill in `DISCORD_TOKEN`, `OWNER_USER_ID`, `FRIEND_USER_ID`, `GEMINI_API_KEY`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

The database is created automatically at `data/jarvis.db` on first run.

## Security

- Only the two configured Discord user IDs can use JARVIS
- Credentials live in `.env` only and are never committed
- Authorization is checked before every command
- Consequential actions require explicit approval (Phase 4)

## Development Phases

1. **Foundation** - project setup, Discord connection, authorization, logging,
   database schema, command skeleton
2. **AI Brain** - Gemini responses, personality, `/ask`, conversation context,
   persistent memory
3. **Discord Awareness** - server/channel config, message reading, mentions,
   summarization
4. **Communication** - message drafting, approval UI, sending, notifications
5. **Voice** - TTS, voice channels, message announcements
6. **Advanced Intelligence** - images, documents, tasks, tool calling
7. **Polish** - settings UI, hardening, performance, docs

## License

Private project.
