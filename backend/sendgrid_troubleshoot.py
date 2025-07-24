#!/usr/bin/env python3
"""
SendGrid Email Delivery Troubleshooting Script

This script helps identify why SendGrid emails return 202 but don't arrive in inbox.
Common causes:
1. Sender authentication not set up
2. Email going to spam/junk folder
3. Domain reputation issues
4. ISP filtering
5. SendGrid account limitations
"""

import os
import sys
import time
from datetime import datetime, timezone
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from email_notification import EmailNotificationService, EmailRecipient

def check_sendgrid_delivery():
    """Comprehensive SendGrid delivery troubleshooting"""
    print("🔍 SendGrid Email Delivery Troubleshooting")
    print("=" * 60)
    
    # Get configuration
    service = EmailNotificationService()
    config = service.config
    
    print("📧 Current SendGrid Configuration:")
    print(f"   API Key: {config.sendgrid_api_key[:20]}...{config.sendgrid_api_key[-10:]}")
    print(f"   From Email: {config.from_email}")
    print(f"   Delivery Method: {config.delivery_method}")
    
    print("\n👥 Target Recipients:")
    for recipient in service.recipients:
        print(f"   {recipient.type.upper()}: {recipient.email}")
    
    print("\n🚨 Common SendGrid Delivery Issues:")
    print("-" * 40)
    
    # Issue 1: Sender Authentication
    print("1. ⚠️ SENDER AUTHENTICATION (Most Common Issue)")
    print("   Problem: SendGrid requires domain authentication for good delivery")
    print("   Your from_email:", config.from_email)
    print("   Status: Likely NOT authenticated (cause of your delivery issue)")
    print("   Solution: Set up Single Sender Verification in SendGrid")
    print("   URL: https://app.sendgrid.com/settings/sender_auth/senders")
    
    # Issue 2: Spam Folder
    print("\n2. 📁 SPAM/JUNK FOLDER")
    print("   Problem: Emails often go to spam without authentication")
    print("   Action: Check your spam/junk folders for test emails")
    print("   Gmail: Check 'Spam' folder")
    print("   Outlook: Check 'Junk Email' folder")
    
    # Issue 3: Domain Reputation
    print("\n3. 🏷️ DOMAIN REPUTATION")
    print("   Problem: Using personal email (iswarya.kolimalla@amzur.com) without auth")
    print("   Issue: ISPs may filter emails from unauthenticated domains")
    print("   Solution: Use SendGrid verified sender or domain authentication")
    
    # Issue 4: Content Filtering
    print("\n4. 🔍 CONTENT FILTERING")
    print("   Problem: Email content triggers spam filters")
    print("   Your subject: Contains 'CRITICAL ALERT' - might trigger filters")
    print("   Solution: Use more neutral subjects for testing")
    
    # Issue 5: Rate Limiting
    print("\n5. ⏱️ RATE LIMITING")
    print("   Problem: SendGrid free tier has daily limits")
    print("   Limit: 100 emails/day for free accounts")
    print("   Solution: Check SendGrid dashboard for delivery stats")
    
    return True

def test_sendgrid_with_debugging():
    """Send test email with detailed logging"""
    print("\n🧪 Sending Test Email with Debug Info...")
    print("-" * 40)
    
    service = EmailNotificationService()
    
    # Create a simple test recipient
    test_recipient = EmailRecipient(
        email="kiswarya74@gmail.com",
        name="Iswarya Test",
        type="to"
    )
    
    print(f"Sending to: {test_recipient.email}")
    print(f"From: {service.config.from_email}")
    print(f"Time: {datetime.now()}")
    
    # Send the email
    success = service.send_critical_alert(
        critical_issues=["SendGrid Delivery Test - Please check all folders"],
        immediate_actions=[
            "Check your INBOX",
            "Check your SPAM/JUNK folder",
            "Check your PROMOTIONS tab (Gmail)",
            "Reply to confirm receipt"
        ],
        recipients=[test_recipient]
    )
    
    if success:
        print("✅ SendGrid accepted email (Status 202)")
        print("\n📱 NEXT STEPS - Check These Locations:")
        print("   1. Gmail Inbox")
        print("   2. Gmail Spam folder")
        print("   3. Gmail Promotions tab")
        print("   4. Gmail Social tab")
        print("   5. Wait 2-5 minutes for delivery")
    else:
        print("❌ SendGrid rejected email")
    
    return success

def fix_sender_authentication():
    """Provide step-by-step authentication setup"""
    print("\n🔧 FIXING SENDER AUTHENTICATION (Required!)")
    print("=" * 50)
    
    print("Step 1: Go to SendGrid Single Sender Verification")
    print("URL: https://app.sendgrid.com/settings/sender_auth/senders")
    
    print("\nStep 2: Click 'Create New Sender'")
    
    print("\nStep 3: Fill in these details:")
    print("   From Name: Grafana Analysis System")
    print("   From Email Address: iswarya.kolimalla@amzur.com")
    print("   Reply To: iswarya.kolimalla@amzur.com")
    print("   Company Address: (your company details)")
    
    print("\nStep 4: Check your email for verification")
    print("   - SendGrid will send verification email to iswarya.kolimalla@amzur.com")
    print("   - Click the verification link")
    
    print("\nStep 5: Test again after verification")
    print("   - Run this script again")
    print("   - Emails should now reach inbox instead of spam")
    
    print("\n⚡ ALTERNATIVE: Use SendGrid's from email")
    print("   Update your .env file:")
    print("   EMAIL_FROM=noreply@sendgrid.net  # SendGrid verified domain")

def check_email_logs():
    """Guide to check SendGrid delivery logs"""
    print("\n📊 CHECKING SENDGRID DELIVERY LOGS")
    print("=" * 40)
    
    print("1. Go to SendGrid Activity Feed:")
    print("   URL: https://app.sendgrid.com/email_activity")
    
    print("\n2. Look for your test emails")
    print("   - Should show 'Delivered' or 'Processed' status")
    print("   - If showing 'Dropped' or 'Bounce' - there's an issue")
    
    print("\n3. Check Email Statistics:")
    print("   URL: https://app.sendgrid.com/statistics")
    
    print("\n4. Common Status Meanings:")
    print("   - Processed: SendGrid accepted, sending to ISP")
    print("   - Delivered: ISP accepted (but might go to spam)")
    print("   - Dropped: SendGrid rejected (auth issue)")
    print("   - Bounce: Recipient server rejected")
    print("   - Spam Report: Marked as spam by recipient")

def main():
    """Main troubleshooting workflow"""
    print("🚀 SendGrid Email Delivery Diagnosis")
    print("=" * 60)
    
    # Step 1: Check configuration
    check_sendgrid_delivery()
    
    # Step 2: Send test email
    success = test_sendgrid_with_debugging()
    
    if success:
        print("\n⏰ WAIT 2-5 MINUTES then check these locations:")
        print("   📧 Gmail: Inbox, Spam, Promotions, Social tabs")
        print("   📧 Other: Inbox, Junk/Spam folders")
        
        input("\nPress Enter after checking your email folders...")
        
        received = input("Did you receive the test email? (y/n): ").lower()
        
        if received == 'y':
            print("🎉 SUCCESS! Your email system is working!")
        elif received == 'n':
            print("\n🔧 EMAIL NOT RECEIVED - Root Cause Analysis:")
            print("   Most likely cause: Sender Authentication NOT set up")
            print("   Status 202 = SendGrid accepted, but ISPs filtered it")
            
            fix_sender_authentication()
            check_email_logs()
        else:
            print("Please answer 'y' or 'n'")
    else:
        print("\n❌ SendGrid API Error - Check API key and configuration")

if __name__ == "__main__":
    main()
