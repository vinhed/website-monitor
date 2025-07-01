# Website Monitor

A Python-based tool that monitors websites for content changes and sends email notifications. Perfect for tracking product availability, price changes, or any website content updates.

## ✨ Features

- **Multi-site monitoring** - Track unlimited websites simultaneously
- **Smart email notifications** - HTML emails
- **Multiple email recipients** - Send notifications to multiple email addresses per site or globally
- **Per-site email recipients** - Send different notifications to different email addresses
- **Intelligent intervals** - Random check intervals to avoid detection
- **Persistent state** - Remembers previous content across restarts
- **Advanced logging** - Configurable logging with file rotation and UTF-8 support
- **Quiet mode** - Reduce console spam for long-running monitoring

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 📖 Usage

1. Configure your sites and email settings in `config.json`
2. Run the monitor:
   ```bash
   python website_listener.py
   ```
3. The tool will continuously monitor your sites and send notifications when changes are detected

## ⚙️ Configuration

### Complete Configuration Example

```json
{
  "sites": [
    {
      "id": "example-tickets",
      "name": "Example Tickets",
      "url": "https://www.example.se/ticket",
      "min_check_interval_minutes": 15,
      "max_check_interval_minutes": 30,
      "css_selector": ".ticket-availability",
      "recipients": [
        "fan1@example.com",
        "fan2@example.com",
        "group-notifications@example.com"
      ],
      "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
      }
    },
    {
      "id": "product-stock",
      "name": "Product Stock Check",
      "url": "https://shop.example.com/product",
      "min_check_interval_minutes": 2,
      "max_check_interval_minutes": 5,
      "css_selector": ".stock-indicator",
      "recipients": [
        "stock-alerts@example.com"
      ]
    },
    {
      "id": "site-using-global-recipients",
      "name": "Site Using Global Recipients",
      "url": "https://example.com/another-product",
      "min_check_interval_minutes": 10,
      "max_check_interval_minutes": 20,
      "css_selector": ".product-status"
    }
  ],
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "sender": "your-email@gmail.com",
    "recipients": [
      "default@example.com",
      "backup@example.com",
      "admin@example.com"
    ],
    "use_tls": true,
    "use_ssl": false
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

## 📧 Email Configuration

### Gmail Setup
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password in `smtp_password` field

### Multiple Recipients
- **Global Recipients**: Set `recipients` (array) in the `email` section for default notifications
- **Site-Specific Recipients**: Set `recipients` (array) per site for targeted notifications
- **Priority**: Site-specific recipients take precedence over global recipients
- **Duplicate Removal**: Automatically removes duplicate email addresses while preserving order

## 🎯 CSS Selector Support

### Regular CSS Selectors
Use standard CSS selectors to target specific elements:
```json
"css_selector": ".product-status"
"css_selector": "#availability-info"
```

### Regex CSS Selectors
Use regex patterns to match CSS classes dynamically by prefixing with `regex:`:
```json
"css_selector": "regex:InfoBlock_info-text.*"
"css_selector": "regex:product-\\d+-status"
```

This is useful when websites use dynamic CSS class names or when you want to match multiple similar classes.

## 🔧 Configuration Options

### Site Settings
- **`id`** - Unique identifier for the site
- **`name`** - Display name for notifications
- **`url`** - Website URL to monitor
- **`css_selector`** - CSS selector for the content to watch (supports regex with `regex:` prefix)
- **`min_check_interval_minutes`** - Minimum time between checks
- **`max_check_interval_minutes`** - Maximum time between checks
- **`recipients`** - (Optional) array of site-specific email addresses
- **`headers`** - (Optional) HTTP headers (useful for User-Agent)

### Email Settings
- **`enabled`** - Enable/disable email notifications
- **`smtp_server`** - SMTP server address
- **`smtp_port`** - SMTP port (587 for TLS, 465 for SSL)
- **`smtp_username`** - SMTP login username
- **`smtp_password`** - SMTP password or app password
- **`sender`** - From email address
- **`recipients`** - Array of default recipient email addresses
- **`use_tls`** - Use TLS encryption
- **`use_ssl`** - Use SSL encryption

### Logging Settings
- **`console_enabled`** - Show logs in console (false for quiet operation)
- **`level`** - Log level (DEBUG, INFO, WARNING, ERROR)
- **`max_file_size_mb`** - Max log file size before rotation
- **`backup_count`** - Number of backup log files to keep
- **`quiet_mode`** - Reduce routine log messages

## 📧 Email Notification Behavior

- **Single Email to Multiple Recipients**: Sends one email with all recipients in the "To" field
- **Duplicate Prevention**: Automatically removes duplicate email addresses
- **Fallback Logic**: If no site-specific recipients are configured, uses global recipients
- **Logging**: Logs successful delivery with recipient count and addresses

## 📄 License

This project is open source and available under the MIT License.