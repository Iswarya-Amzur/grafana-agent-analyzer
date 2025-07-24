#!/usr/bin/env python3
"""
Email Configuration Debug Script

This script helps diagnose why emails are not being sent by checking:
1. Configuration settings
2. Environment variables
3. SMTP/SendGrid connectivity
4. Authentication issues
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from email_notification import EmailNotificationService, EmailRecipient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_email_config():
    """Check email configuration and debug issues"""
    print("🔍 Email Configuration Debug Report")
    print("=" * 50)
    
    # Create service
    try:
        service = EmailNotificationService()
        config = service.config
        
        print("📧 Email Configuration:")
        print(f"   SMTP Server: {config.smtp_server}:{config.smtp_port}")
        print(f"   SMTP Username: {config.smtp_username}")
        # Fix the f-string syntax error
        password_display = '*' * len(config.smtp_password) if config.smtp_password else 'NOT SET'
        print(f"   SMTP Password: {password_display}")
        print(f"   From Email: {config.from_email}")
        print(f"   Delivery Method: {config.delivery_method}")
        print(f"   TLS Enabled: {config.use_tls}")
        
        print("\n🌐 Environment Variables:")
        print(f"   EMAIL_SMTP_USERNAME: {os.getenv('EMAIL_SMTP_USERNAME', 'NOT SET')}")
        env_password = os.getenv('EMAIL_SMTP_PASSWORD')
        password_env_display = '*' * len(env_password) if env_password else 'NOT SET'
        print(f"   EMAIL_SMTP_PASSWORD: {password_env_display}")
        print(f"   EMAIL_FROM: {os.getenv('EMAIL_FROM', 'NOT SET')}")
        print(f"   EMAIL_DELIVERY_METHOD: {os.getenv('EMAIL_DELIVERY_METHOD', 'NOT SET')}")
        
        print("\n👥 Recipients:")
        if service.recipients:
            for recipient in service.recipients:
                print(f"   {recipient.type.upper()}: {recipient.email} ({recipient.name})")
        else:
            print("   ⚠️ No recipients configured!")
            
        # Check environment fallback
        env_recipients = os.getenv('EMAIL_RECIPIENTS', '')
        if env_recipients:
            print(f"   ENV_RECIPIENTS: {env_recipients}")
        
        print("\n🧪 Configuration Tests:")
        
        # Test 1: Basic configuration check
        missing_configs = []
        if not config.smtp_username:
            missing_configs.append("SMTP Username")
        if not config.smtp_password:
            missing_configs.append("SMTP Password")
        if not config.from_email:
            missing_configs.append("From Email")
        if not service.recipients and not env_recipients:
            missing_configs.append("Recipients")
            
        if missing_configs:
            print(f"   ❌ Missing configuration: {', '.join(missing_configs)}")
            return False
        else:
            print("   ✅ Basic configuration complete")
        
        # Test 2: Email Provider Connection Test
        if config.delivery_method.lower() == "sendgrid":
            print("\n🔗 SendGrid API Test:")
            try:
                if not config.sendgrid_api_key:
                    print("   ❌ SendGrid API key not configured")
                    return False
                
                # Test SendGrid API key format
                if config.sendgrid_api_key.startswith("SG."):
                    print("   ✅ SendGrid API key format valid")
                else:
                    print("   ⚠️ SendGrid API key format might be invalid")
                
                print("   ✅ SendGrid configured - will test actual sending below")
                
            except Exception as sg_error:
                print(f"   ❌ SendGrid configuration error: {sg_error}")
                return False
        else:
            print("\n🔗 SMTP Connection Test:")
            try:
                server = smtplib.SMTP(config.smtp_server, config.smtp_port)
                if config.use_tls:
                    server.starttls()
                print("   ✅ SMTP connection successful")
                
                # Test authentication
                try:
                    server.login(config.smtp_username, config.smtp_password)
                    print("   ✅ SMTP authentication successful")
                    server.quit()
                except Exception as auth_error:
                    print(f"   ❌ SMTP authentication failed: {auth_error}")
                    server.quit()
                    return False
                    
            except Exception as conn_error:
                print(f"   ❌ SMTP connection failed: {conn_error}")
                return False
        
        # Test 3: Send test email
        print("\n📧 Sending test email...")
        try:
            test_recipients = []
            if service.recipients:
                test_recipients = [service.recipients[0]]  # Use first recipient
            elif env_recipients:
                first_email = env_recipients.split(',')[0].strip()
                test_recipients = [EmailRecipient(email=first_email, type="to")]
            
            if test_recipients:
                success = service.send_critical_alert(
                    critical_issues=["This is a test email from the debug script"],
                    immediate_actions=["No action required - this is a configuration test"],
                    recipients=test_recipients
                )
                
                if success:
                    print(f"   ✅ Test email sent successfully to {test_recipients[0].email}")
                    return True
                else:
                    print("   ❌ Test email failed to send")
                    return False
            else:
                print("   ❌ No recipients available for test")
                return False
                
        except Exception as email_error:
            print(f"   ❌ Test email error: {email_error}")
            return False
            
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common email issues"""
    print("\n🔧 Common Email Issues & Fixes:")
    print("-" * 30)
    
    print("1. Gmail SMTP Authentication:")
    print("   - Use App Passwords instead of regular password")
    print("   - Enable 2FA and generate app-specific password")
    print("   - https://support.google.com/accounts/answer/185833")
    
    print("\n2. Configuration Issues:")
    print("   - Check .env file for correct EMAIL_SMTP_USERNAME")
    print("   - Verify EMAIL_SMTP_PASSWORD is set")
    print("   - Ensure EMAIL_FROM matches your SMTP username")
    
    print("\n3. Recipients Configuration:")
    print("   - Update recipients.json with valid email addresses")
    print("   - Or set EMAIL_RECIPIENTS in .env file")
    
    print("\n4. Network/Firewall Issues:")
    print("   - Check if port 587 is blocked")
    print("   - Try port 465 with SSL instead of TLS")
    
    print("\n5. Alternative: Use SendGrid")
    print("   - Set SENDGRID_API_KEY in .env")
    print("   - Set EMAIL_DELIVERY_METHOD=sendgrid")

if __name__ == "__main__":
    print("🚀 Starting Email Debug Session...\n")
    
    success = check_email_config()
    
    if not success:
        suggest_fixes()
    
    print(f"\n📊 Debug Result: {'✅ EMAIL SYSTEM WORKING' if success else '❌ EMAIL ISSUES DETECTED'}")
