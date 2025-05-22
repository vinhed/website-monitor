# Website Monitor

A simple tool that checks websites for content changes and sends notifications.

## Features

- Monitor multiple websites
- Email notifications to different emails
- Random check intervals
- Persistent monitoring state

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage
1. Configure your sites in `config.json`
2. Run `python website_monitor.py`

## Configuration Example
```bash
{
  "sites": [
    {
      "id": "example-site",
      "name": "Example Site",
      "url": "https://example.com/page",
      "min_check_interval_minutes": 5,
      "max_check_interval_minutes": 15,
      "css_selector": ".content-to-watch"
    }
  ],
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "sender": "your-email@gmail.com",
    "recipient": "your-email@gmail.com",
    "use_tls": true
  },
  "logging": {
    "console_enabled": false,
    "level": "INFO",
    "max_file_size_mb": 5,
    "backup_count": 3,
    "quiet_mode": true
  }
}
```