import requests
import json
import time
import os
import logging
import re
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from datetime import datetime
from mail_notification import send_email_notification

class WebsiteMonitor:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data_dir = "monitor_data"
        self.ensure_data_dir_exists()
        self.load_config()
        self.setup_logging()
        self.site_states = {}
        self.load_previous_states()

    def setup_logging(self):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        log_config = self.config.get("logging", {})
        max_file_size = log_config.get("max_file_size_mb", 5) * 1024 * 1024
        backup_count = log_config.get("backup_count", 3)
        
        file_handler = RotatingFileHandler(
            "website_monitor.log", 
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        if log_config.get("console_enabled", True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        log_level = log_config.get("level", "INFO").upper()
        if hasattr(logging, log_level):
            logger.setLevel(getattr(logging, log_level))

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                print(f"Configuration loaded from {self.config_path}")
            else:
                print(f"Please configure a conifg file at {self.config_path}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
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
            logging.debug(f"Saved state for site: {site_id}")
        except Exception as e:
            logging.error(f"Failed to save state for site {site_id}: {e}")
    
    def find_element_by_selector(self, soup, css_selector):
        try:
            element = soup.select_one(css_selector)
            if element:
                return element
        except Exception:
            pass
        
        is_regex = css_selector.startswith('regex:')
        if is_regex:
            regex_pattern = css_selector[6:]
            try:
                compiled_regex = re.compile(regex_pattern)
                for element in soup.find_all():
                    if element.get('class'):
                        class_str = ' '.join(element.get('class'))
                        if compiled_regex.search(class_str):
                            return element
            except re.error as e:
                logging.error(f"Invalid regex pattern '{regex_pattern}': {e}")
        
        return None

    def check_website(self, site_config):
        site_id = site_config["id"]
        site_name = site_config.get("name", site_id)
        quiet_mode = self.config.get("logging", {}).get("quiet_mode", False)
        
        try:
            url = site_config["url"]
            headers = site_config.get("headers", {})
            css_selector = site_config["css_selector"]
            
            if not quiet_mode:
                logging.info(f"Checking site: {site_name} ({url})")
            else:
                logging.debug(f"Checking site: {site_name} ({url})")
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                element = self.find_element_by_selector(soup, css_selector)
                
                if element is None:
                    logging.warning(f"Element with selector '{css_selector}' not found on {site_name}")
                    current_content = "<Element not found>"
                else:
                    current_content = element.get_text().strip()
            else:
                current_content = f"Status Code: {response.status_code}"
            
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
                    "new": current_content,
                    "recipients": site_config.get("recipients", site_config.get("recipients"))
                }
            
            if not quiet_mode:
                logging.debug(f"No changes detected for {site_name}")
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
            
            quiet_mode = self.config.get("logging", {}).get("quiet_mode", False)
            if quiet_mode:
                logging.info("Running in quiet mode - reduced console output")
            
            logging.info("Performing initial startup checks...")
            for site_config in self.config["sites"]:
                site_name = site_config.get("name", site_config["id"])
                logging.info(f"Startup check for {site_name}")
                changed, change_info = self.check_website(site_config)
                if changed:
                    self.send_notification(change_info)
            
            logging.info("Startup checks complete. Beginning regular monitoring...")
            
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
                            if not quiet_mode:
                                logging.info(f"Next check for {site_name} in {interval_minutes:.2f} minutes")
                            else:
                                logging.debug(f"Next check for {site_name} in {interval_minutes:.2f} minutes")
                
                min_next_check = min(next_checks.values())
                wait_time = max(1, min_next_check - time.time())
                
                if not quiet_mode:
                    next_site_id = min(next_checks, key=next_checks.get)
                    next_site_name = next((site.get("name", site["id"]) for site in self.config["sites"] if site["id"] == next_site_id), next_site_id)
                    logging.debug(f"Sleeping for {wait_time:.2f} seconds until next check ({next_site_name})")
                
                time.sleep(wait_time)
            
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        except Exception as e:
            logging.error(f"Error in monitor: {e}")
            raise

if __name__ == "__main__":
    monitor = WebsiteMonitor()
    monitor.run()