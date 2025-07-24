#!/usr/bin/env python3
"""
Debug script to test the full upload and email process
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_email_delivery():
    """Test email delivery with different methods"""
    print("\n📧 Email Delivery Debug")
    print("=" * 40)
    
    # Test 1: Check if emails are in spam folder
    print("✉️ Email Delivery Checklist:")
    print("1. Check your SPAM/JUNK folder for emails from SendGrid")
    print("2. Check kiswarya74@gmail.com inbox")
    print("3. Check iswarya.kolimalla@amzur.com inbox")
    
    # Test 2: Check SendGrid API directly
    try:
        from email_notification import EmailNotificationService, EmailRecipient
        from dotenv import load_dotenv
        load_dotenv()
        
        service = EmailNotificationService()
        
        print(f"\n🔧 SendGrid Configuration:")
        print(f"   API Key: {'*' * 20}...{service.config.sendgrid_api_key[-4:] if service.config.sendgrid_api_key else 'NOT SET'}")
        print(f"   From Email: {service.config.from_email}")
        print(f"   Delivery Method: {service.config.delivery_method}")
        
        # Test sending email to specific address
        test_recipient = EmailRecipient(email="kiswarya74@gmail.com", name="Test User", type="to")
        
        print("\n📨 Sending test email to kiswarya74@gmail.com...")
        success = service.send_critical_alert(
            critical_issues=["TEST EMAIL - Please confirm you received this"],
            immediate_actions=["Reply to this email to confirm receipt"],
            recipients=[test_recipient]
        )
        
        if success:
            print("✅ Email sent successfully via SendGrid")
            print("📋 Next Steps:")
            print("   1. Check kiswarya74@gmail.com inbox (including spam)")
            print("   2. If no email, check SendGrid dashboard for delivery logs")
            print("   3. Verify kiswarya74@gmail.com is a valid email address")
        else:
            print("❌ Email sending failed")
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")

def test_upload_process():
    """Test the full upload process"""
    print("\n📤 Upload Process Debug")
    print("=" * 40)
    
    # Check if FastAPI server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ FastAPI server is running")
        else:
            print("❌ FastAPI server responded with error")
            return False
    except Exception as e:
        print("❌ FastAPI server is not running. Start it with: uvicorn main:app --reload")
        return False
    
    # Check reports directory
    reports_dir = Path("reports")
    if reports_dir.exists():
        print(f"✅ Reports directory exists: {reports_dir.absolute()}")
        files = list(reports_dir.glob("*"))
        print(f"📁 Found {len(files)} files in reports directory:")
        for file in files:
            print(f"   - {file.name} ({file.stat().st_size} bytes)")
    else:
        print("❌ Reports directory not found")
        return False
    
    return True

def test_excel_with_real_data():
    """Test Excel generation with real markdown data"""
    print("\n📊 Excel Generation with Real Data")
    print("=" * 40)
    
    try:
        from excel_export import ExcelReportGenerator
        
        # Find the most recent markdown file
        reports_dir = Path("reports")
        md_files = list(reports_dir.glob("*.md"))
        
        if not md_files:
            print("❌ No markdown files found in reports directory")
            return
        
        latest_md = max(md_files, key=lambda f: f.stat().st_mtime)
        print(f"📄 Using markdown file: {latest_md.name}")
        
        # Read the markdown content
        with open(latest_md, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Create mock analysis result with real markdown
        analysis_result = {
            "analysis": {
                "raw_markdown": markdown_content,
                "structured_data": {
                    "performance_score": 7.5,
                    "issues": ["Sample issue from real data"],
                    "recommendations": {
                        "immediate": ["Test immediate action"],
                        "short_term": ["Test short-term action"]
                    }
                }
            }
        }
        
        # Generate Excel report
        excel_generator = ExcelReportGenerator(output_dir="reports")
        excel_file = excel_generator.generate_excel_report(analysis_result, [])
        
        if excel_file and os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            print(f"✅ Excel file generated successfully: {os.path.basename(excel_file)} ({file_size} bytes)")
        else:
            print("❌ Excel file generation failed")
            
    except Exception as e:
        print(f"❌ Excel test failed: {e}")
        import traceback
        traceback.print_exc()

def check_sendgrid_status():
    """Check SendGrid API status"""
    print("\n🌐 SendGrid API Status Check")
    print("=" * 40)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            print("❌ SENDGRID_API_KEY not found in environment")
            return
        
        # Test SendGrid API connection
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Check API key validity
        response = requests.get("https://api.sendgrid.com/v3/user/profile", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ SendGrid API key is valid")
            print(f"   Account: {user_data.get('username', 'Unknown')}")
        elif response.status_code == 401:
            print("❌ SendGrid API key is invalid or expired")
        else:
            print(f"❌ SendGrid API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ SendGrid check failed: {e}")

if __name__ == "__main__":
    print("🔍 Full System Debug Script")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    upload_ok = test_upload_process()
    
    if upload_ok:
        test_excel_with_real_data()
    
    check_sendgrid_status()
    test_email_delivery()
    
    print(f"\n📋 Debug Summary:")
    print("1. Check your email inbox AND spam folder")
    print("2. Look for Excel files in the reports directory")
    print("3. If emails still not arriving, check SendGrid dashboard")
    print("4. Verify email addresses are correct in recipients.json")
    
    print(f"\n✅ Debug script completed at {datetime.now().strftime('%H:%M:%S')}")
