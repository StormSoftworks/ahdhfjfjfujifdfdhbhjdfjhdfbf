# Overview

FC8 Moderation is a Discord bot designed to provide comprehensive moderation tools for Discord servers. The bot implements essential moderation features including user kicks, bans, warnings, timeouts, and leave of absence (LOA) management. It uses SQLite databases for persistent data storage and Discord's modern slash command system for user interactions.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Discord.py**: Uses the discord.py library with command extensions for bot functionality
- **Slash Commands**: Implements modern Discord slash commands instead of traditional prefix commands
- **Intents**: Configured with all Discord intents to access necessary guild and member data
- **Permissions System**: Role-based permissions using Discord's permission decorators

## Data Storage
- **SQLite Databases**: Two separate SQLite databases for different data types:
  - `warnings.db`: Stores user warning records and moderation history
  - `loadb.db`: Manages leave of absence requests and approvals
- **Database Design**: Simple relational structure suitable for Discord server moderation needs

## Command Structure
- **Async Operations**: All commands are asynchronous to handle Discord API calls efficiently
- **Error Handling**: Implements try-catch blocks for graceful error management
- **User Input Validation**: Includes time parsing utilities for duration-based commands
- **Interactive Elements**: Uses Discord UI components like buttons, modals, and text inputs

## Moderation Features
- **User Management**: Kick, ban, timeout, and warning systems
- **Time Parsing**: Flexible time duration parsing (seconds, minutes, hours, days, weeks, months)
- **Logging System**: Dedicated moderation logs channel for audit trails
- **Role-based Access**: Moderator role requirements for sensitive commands

## Configuration Management
- **Hard-coded Constants**: Bot token, channel IDs, and role IDs are defined as constants
- **Guild-specific Settings**: Moderator role and logging channel are server-specific configurations

# External Dependencies

## Core Libraries
- **discord.py**: Primary Discord API wrapper for bot functionality
- **asyncio**: Asynchronous programming support for concurrent operations
- **sqlite3**: Built-in Python SQLite database interface
- **colorama**: Terminal color formatting for enhanced console output

## Discord API Integration
- **Discord Gateway**: Real-time event handling and bot presence management
- **Discord Slash Commands**: Modern command interface with parameter validation
- **Discord UI Components**: Interactive buttons, modals, and forms for enhanced user experience
- **Discord Permissions**: Guild permission system integration for access control

## Database Technology
- **SQLite**: Lightweight, file-based database for persistent data storage
- **Local File Storage**: Database files stored locally for simple deployment and backup