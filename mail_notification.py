from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import smtplib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_monitor.log"),
        logging.StreamHandler()
    ]
)

def send_email_notification(change_info, config):
    email_config = config["email"]
    recipient = email_config["recipient"]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    site_name = change_info["site_name"]
    url = change_info["url"]
    
    display_url = url
    if len(url) > 40:
        display_url = url[:37] + "..."
    
    subject = f"🔔 Change Detected: {site_name}"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Website Change Alert</title>
        <style>
            :root {{
                color-scheme: dark;
            }}
            body {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #e1e1e1;
                background-color: #121212;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #1e1e1e;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            }}
            .header {{
                background-color: #2d2d2d;
                padding: 20px;
                border-bottom: 1px solid #333;
                text-align: center;
            }}
            .header h2 {{
                margin: 0;
                color: #ffffff;
                font-size: 24px;
                font-weight: 600;
            }}
            .header p {{
                margin: 10px 0 0;
                color: #bbb;
                font-size: 14px;
            }}
            .alert-badge {{
                background-color: #ff3e3e;
                color: white;
                font-size: 14px;
                font-weight: bold;
                display: inline-block;
                padding: 5px 15px;
                border-radius: 30px;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .content {{
                padding: 25px;
            }}
            .website-info {{
                background-color: #252525;
                padding: 20px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
            .website-info-grid {{
                display: block;
            }}
            .info-item {{
                margin-bottom: 12px;
            }}
            .info-label {{
                color: #999;
                font-weight: 500;
                margin-bottom: 4px;
            }}
            .info-value {{
                color: #fff;
                font-weight: 600;
                word-break: break-all;
            }}
            .change-panel {{
                background-color: #252525;
                border-radius: 6px;
                margin-bottom: 15px;
                overflow: hidden;
            }}
            .change-header {{
                background-color: #2d2d2d;
                padding: 12px 15px;
                font-weight: 600;
                display: flex;
                align-items: center;
            }}
            .change-header.new {{
                background-color: #0a4b23;
                color: #5cff9d;
            }}
            .change-header.old {{
                background-color: #3a3a3a;
                color: #aaa;
            }}
            .change-content {{
                padding: 15px;
                color: #ddd;
                word-break: break-word;
            }}
            .change-content.new {{
                background-color: rgba(10, 75, 35, 0.2);
            }}
            .change-content.old {{
                color: #bbb;
            }}
            .button {{
                display: inline-block;
                background-color: #2c84fc;
                color: #ffffff !important;
                text-decoration: none;
                padding: 12px 25px;
                border-radius: 4px;
                font-weight: 600;
                margin-top: 10px;
                transition: background-color 0.2s;
                text-align: center;
                width: 100%;
                box-sizing: border-box;
            }}
            .button:hover {{
                background-color: #2275e5;
            }}
            a {{
                color: #5caaff;
                text-decoration: none;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 20px;
                background-color: #1a1a1a;
                border-top: 1px solid #333;
            }}
            .icon {{
                display: inline-block;
                width: 18px;
                height: 18px;
                margin-right: 8px;
                vertical-align: middle;
            }}
            @media only screen and (min-width: 481px) {{
                .website-info-grid {{
                    display: grid;
                    grid-template-columns: auto 1fr;
                    grid-gap: 10px;
                    align-items: start;
                }}
                .info-item {{
                    margin-bottom: 0;
                }}
                .button {{
                    width: auto;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="alert-badge">Alert</div>
                <h2>Website Change Detected</h2>
                <p>{timestamp}</p>
            </div>
            <div class="content">
                <div class="website-info">
                    <div class="website-info-grid">
                        <div class="info-item">
                            <div class="info-label">Website:</div>
                            <div class="info-value">{site_name}</div>
                        </div>
                        
                        <div class="info-item">
                            <div class="info-label">URL:</div>
                            <div class="info-value">
                                <a href="{url}" title="{url}">{display_url}</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="change-panel">
                    <div class="change-header new">
                        <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM11 11H7V13H11V17H13V13H17V11H13V7H11V11Z"/>
                        </svg>
                        New Content
                    </div>
                    <div class="change-content new">{change_info['new']}</div>
                </div>
                
                <div class="change-panel">
                    <div class="change-header old">
                        <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM7 11H17V13H7V11Z"/>
                        </svg>
                        Previous Content
                    </div>
                    <div class="change-content old">{change_info['old']}</div>
                </div>
                
                <a href="{url}" class="button">Visit Website</a>
            </div>
            <div class="footer">
                <p>This is an automated notification from your Website Monitor.</p>
                <p style="margin-top: 5px; color: #666;">© {datetime.now().year} Website Monitor</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    WEBSITE CHANGE DETECTED
    Time: {timestamp}
    
    A change has been detected on the website you're monitoring:
    
    Website: {site_name}
    URL: {url}
    
    NEW CONTENT:
    {change_info['new']}
    
    PREVIOUS CONTENT:
    {change_info['old']}
    
    This is an automated notification from your Website Monitor.
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email_config["sender"]
    msg['To'] = recipient
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    _send_email(msg, config)
    logging.info(f"Email notification sent to {recipient}")

def _send_email(msg, config):
    email_config = config["email"]
    
    if email_config["use_ssl"]:
        server = smtplib.SMTP_SSL(email_config["smtp_server"], email_config["smtp_port"])
    else:
        server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
        if email_config["use_tls"]:
            server.starttls()
    
    if email_config["smtp_username"] and email_config["smtp_password"]:
        server.login(email_config["smtp_username"], email_config["smtp_password"])
    
    server.send_message(msg)
    server.quit()