import requests
import json
import time
import os
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from mail_notification import send_email_notification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_monitor.log"),
        logging.StreamHandler()
    ]
)

class WebsiteMonitor:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data_dir = "monitor_data"
        self.ensure_data_dir_exists()
        self.load_config()
        self.site_states = {}
        self.load_previous_states()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logging.info(f"Configuration loaded from {self.config_path}")
            else:
                self.config = {
                    "sites": [
                        {
                            "id": "example-product",
                            "name": "Example Product Page",
                            "url": "https://example.com/product",
                            "check_interval_minutes": 5,
                            "css_selector": ".product-availability",
                            "headers": {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                            }
                        }
                    ],
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "smtp_username": "your-email@gmail.com",
                        "smtp_password": "your-password-or-app-password",
                        "sender": "your-email@gmail.com",
                        "recipient": "your-email@gmail.com",
                        "use_tls": True,
                        "use_ssl": False
                    }
                }
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
                logging.info(f"Default configuration created at {self.config_path}")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise
        
    def ensure_data_dir_exists(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logging.info(f"Created data directory: {self.data_dir}")
    
    def get_site_state_path(self, site_id):
        return os.path.join(self.data_dir, f"{site_id}.json")
    

    def load_previous_states(self):
        for site_config in self.config["sites"]:
            site_id = site_config["id"]
            state_path = self.get_site_state_path(site_id)
            
            if os.path.exists(state_path):
                try:
                    with open(state_path, 'r') as f:
                        site_state = json.load(f)
                        self.site_states[site_id] = site_state
                        logging.info(f"Loaded previous state for site: {site_id}")
                except Exception as e:
                    logging.error(f"Failed to load previous state for site {site_id}: {e}")
                    self.site_states[site_id] = {"content": None, "last_check": None}
            else:
                self.site_states[site_id] = {"content": None, "last_check": None}
                logging.info(f"No previous state found for site: {site_id}")
    
    def save_site_state(self, site_id, content):
        state_path = self.get_site_state_path(site_id)
        
        state = {
            "content": content,
            "last_check": datetime.now().isoformat()
        }
        
        try:
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=4)
            
            self.site_states[site_id] = state
            logging.info(f"Saved state for site: {site_id}")
        except Exception as e:
            logging.error(f"Failed to save state for site {site_id}: {e}")
    
    def check_website(self, site_config):
        site_id = site_config["id"]
        site_name = site_config.get("name", site_id)
        
        try:
            url = site_config["url"]
            headers = site_config.get("headers", {})
            css_selector = site_config["css_selector"]
            
            logging.info(f"Checking site: {site_name} ({url})")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.select_one(css_selector)
            
            if element is None:
                logging.warning(f"Element with selector '{css_selector}' not found on {site_name}")
                current_content = "<Element not found>"
            else:
                current_content = element.get_text().strip()
            
            previous_content = None if site_id not in self.site_states else self.site_states[site_id]["content"]
            
            if previous_content is None:
                self.save_site_state(site_id, current_content)
                logging.info(f"Initial content for {site_name}: '{current_content}'")
                return False, None
            
            if current_content != previous_content:
                old_content = previous_content
                self.save_site_state(site_id, current_content)
                logging.info(f"Content changed on {site_name} from '{old_content}' to '{current_content}'")
                return True, {
                    "site_id": site_id, 
                    "site_name": site_name,
                    "url": url,
                    "old": old_content, 
                    "new": current_content
                }
            
            logging.info(f"No changes detected for {site_name}")
            return False, None
            
        except Exception as e:
            logging.error(f"Error checking website {site_name}: {e}")
            return False, None
    
    def send_notification(self, change_info):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        site_name = change_info["site_name"]
        url = change_info["url"]
        
        notification_message = f"[{timestamp}] Change detected on {site_name}!\n"
        notification_message += f"URL: {url}\n"
        notification_message += f"{change_info['new']}"
        
        print("\n" + "!" * 50)
        print(notification_message)
        print("!" * 50 + "\n")
        
        if "email" in self.config and self.config["email"]["enabled"]:
            try:
                send_email_notification(change_info, self.config)
            except Exception as e:
                logging.error(f"Failed to send email notification: {e}")
        
        logging.info(f"Notification sent for {site_name}")
    
    def run(self):
        try:
            site_count = len(self.config["sites"])
            logging.info(f"Starting to monitor {site_count} website{'s' if site_count > 1 else ''}")
            
            next_checks = {}
            last_intervals = {}
            
            for site in self.config["sites"]:
                next_checks[site["id"]] = 0
                last_intervals[site["id"]] = None
            
            while True:
                current_time = time.time()
                
                for site_config in self.config["sites"]:
                    site_id = site_config["id"]
                    site_name = site_config.get("name", site_id)
                    
                    if current_time >= next_checks[site_id]:
                        changed, change_info = self.check_website(site_config)
                        if changed:
                            self.send_notification(change_info)
                        
                        min_interval = site_config.get("min_check_interval_minutes", 5)
                        max_interval = site_config.get("max_check_interval_minutes", min_interval * 2)
                        
                        if max_interval < min_interval:
                            max_interval = min_interval
                        
                        import random
                        interval_minutes = random.uniform(min_interval, max_interval)
                        check_interval = interval_minutes * 60
                        
                        next_checks[site_id] = current_time + check_interval
                        
                        if last_intervals[site_id] != interval_minutes:
                            last_intervals[site_id] = interval_minutes
                            logging.info(f"Next check for {site_name} in {interval_minutes:.2f} minutes")
                
                min_next_check = min(next_checks.values())
                wait_time = max(1, min_next_check - time.time())
                
                next_site_id = min(next_checks, key=next_checks.get)
                next_site_name = next((site.get("name", site["id"]) for site in self.config["sites"] if site["id"] == next_site_id), next_site_id)
                logging.info(f"Sleeping for {wait_time:.2f} seconds until next check ({next_site_name})")
                
                time.sleep(wait_time)
            
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        except Exception as e:
            logging.error(f"Error in monitor: {e}")
            raise

if __name__ == "__main__":
    monitor = WebsiteMonitor()
    monitor.run()