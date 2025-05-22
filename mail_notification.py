from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import smtplib

def send_email_notification(change_info, config):
    email_config = config["email"]
    
    site_recipients = change_info.get("recipients", [])
    global_recipients = email_config.get("recipients", email_config.get("recipient", []))
    
    if isinstance(site_recipients, str):
        site_recipients = [site_recipients]
    elif site_recipients is None:
        site_recipients = []
    
    if isinstance(global_recipients, str):
        global_recipients = [global_recipients]
    elif global_recipients is None:
        global_recipients = []
    
    recipients = site_recipients if site_recipients else global_recipients
    
    if not recipients:
        logging.warning("No email recipients configured")
        return
    
    recipients = list(dict.fromkeys(recipients))
    
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
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                line-height: 1.5;
                color: #e2e8f0;
                background-color: #0f172a;
                margin: 0;
                padding: 16px;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #1e293b;
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #334155;
            }}
            
            .header {{
                background-color: #1e293b;
                padding: 24px;
                border-bottom: 1px solid #334155;
            }}
            
            .header h1 {{
                color: #f1f5f9;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 4px;
            }}
            
            .timestamp {{
                color: #94a3b8;
                font-size: 14px;
            }}
            
            .content {{
                padding: 24px;
            }}
            
            .site-info {{
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 16px;
                margin-bottom: 24px;
            }}
            
            .site-name {{
                color: #f1f5f9;
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 8px;
            }}
            
            .site-url {{
                color: #60a5fa;
                font-size: 14px;
                text-decoration: none;
                word-break: break-all;
            }}
            
            .changes {{
                margin-bottom: 24px;
            }}
            
            .change-block {{
                border: 1px solid #334155;
                border-radius: 6px;
                margin-bottom: 16px;
                overflow: hidden;
            }}
            
            .change-header {{
                padding: 12px 16px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .change-header.new {{
                background-color: #166534;
                color: #dcfce7;
            }}
            
            .change-header.old {{
                background-color: #991b1b;
                color: #fecaca;
            }}
            
            .change-content {{
                padding: 16px;
                font-size: 14px;
                line-height: 1.6;
                word-break: break-word;
            }}
            
            .change-content.new {{
                background-color: #0f172a;
                color: #dcfce7;
                border-left: 3px solid #22c55e;
            }}
            
            .change-content.old {{
                background-color: #0f172a;
                color: #fecaca;
                border-left: 3px solid #ef4444;
            }}
            
            .visit-button {{
                display: block;
                background-color: #3b82f6;
                color: #ffffff;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 500;
                text-align: center;
                margin-bottom: 24px;
            }}
            
            .footer {{
                padding: 16px 24px;
                background-color: #0f172a;
                border-top: 1px solid #334155;
                text-align: center;
            }}
            
            .footer p {{
                color: #64748b;
                font-size: 12px;
                margin-bottom: 4px;
            }}
            
            .footer p:last-child {{
                margin-bottom: 0;
                color: #475569;
            }}
            
            /* Mobile adjustments */
            @media (max-width: 600px) {{
                body {{
                    padding: 8px;
                }}
                
                .container {{
                    border-radius: 6px;
                }}
                
                .header {{
                    padding: 20px;
                }}
                
                .content {{
                    padding: 20px;
                }}
                
                .site-info {{
                    padding: 14px;
                }}
                
                .change-content {{
                    padding: 14px;
                    font-size: 13px;
                }}
                
                .visit-button {{
                    padding: 14px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{site_name}</h1>
                <p class="timestamp">{timestamp}</p>
            </div>
            
            <div class="content">
                <div class="site-info">
                    <div class="site-name">{site_name}</div>
                    <a href="{url}" class="site-url">{display_url}</a>
                </div>
                
                <div class="changes">
                    <div class="change-block">
                        <div class="change-header new">+ Added</div>
                        <div class="change-content new">{change_info['new']}</div>
                    </div>
                    
                    <div class="change-block">
                        <div class="change-header old">- Removed</div>
                        <div class="change-content old">{change_info['old']}</div>
                    </div>
                </div>
                
                <a href="{url}" class="visit-button">Visit Website</a>
            </div>
            
            <div class="footer">
                <p>Website Monitor © {datetime.now().year}</p>
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
    msg['To'] = ', '.join(recipients)
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    _send_email(msg, config)
    logging.info(f"Email notification sent to {len(recipients)} recipient(s): {', '.join(recipients)}")

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