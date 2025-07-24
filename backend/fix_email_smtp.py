#!/usr/bin/env python3
"""
Alternative SMTP Configuration Script

This script helps test different SMTP configurations for Gmail.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_alternative_smtp_configs():
    """Test different SMTP configurations"""
    
    username = os.getenv("EMAIL_SMTP_USERNAME")
    password = os.getenv("EMAIL_SMTP_PASSWORD")
    
    # Configuration options to try
    configs = [
        {
            "name": "Gmail TLS (Port 587)",
            "server": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "use_ssl": False
        },
        {
            "name": "Gmail SSL (Port 465)",
            "server": "smtp.gmail.com", 
            "port": 465,
            "use_tls": False,
            "use_ssl": True
        },
        {
            "name": "Gmail Legacy (Port 25)",
            "server": "smtp.gmail.com",
            "port": 25,
            "use_tls": True,
            "use_ssl": False
        }
    ]
    
    print("🧪 Testing Alternative SMTP Configurations")
    print("=" * 50)
    
    for config in configs:
        print(f"\n📧 Testing: {config['name']}")
        print(f"   Server: {config['server']}:{config['port']}")
        
        try:
            if config['use_ssl']:
                # Use SSL connection
                server = smtplib.SMTP_SSL(config['server'], config['port'])
            else:
                # Use regular connection
                server = smtplib.SMTP(config['server'], config['port'])
                
            if config['use_tls'] and not config['use_ssl']:
                server.starttls()
                
            print("   ✅ Connection successful")
            
            # Test authentication
            try:
                server.login(username, password)
                print("   ✅ Authentication successful")
                server.quit()
                
                print(f"   🎉 SUCCESS! Use this configuration:")
                print(f"      SMTP_SERVER: {config['server']}")
                print(f"      SMTP_PORT: {config['port']}")
                print(f"      USE_TLS: {config['use_tls']}")
                print(f"      USE_SSL: {config['use_ssl']}")
                return config
                
            except Exception as auth_error:
                print(f"   ❌ Authentication failed: {auth_error}")
                server.quit()
                
        except Exception as conn_error:
            print(f"   ❌ Connection failed: {conn_error}")
    
    print("\n❌ All SMTP configurations failed.")
    print("   You need to use Gmail App Passwords or switch to SendGrid.")
    return None

if __name__ == "__main__":
    test_alternative_smtp_configs()
