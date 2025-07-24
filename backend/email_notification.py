#!/usr/bin/env python3
"""
Email Notification Module for Grafana Analysis Reports

This module handles sending analysis reports and summaries to stakeholders via email.
Supports both SMTP (Gmail) and SendGrid delivery methods.

Features:
- Send HTML email with markdown summary
- Attach Excel reports as .xlsx files
- Support for multiple recipients (To, CC, BCC)
- Template-based email formatting
- Configurable SMTP and SendGrid options
- Email delivery logging and error handling

Usage:
    from email_notification import EmailNotificationService
    
    service = EmailNotificationService()
    service.send_analysis_report(analysis_result, recipients, excel_file)
"""

import smtplib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
import markdown
from jinja2 import Template
from dataclasses import dataclass

# Optional SendGrid import
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    import base64
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("SendGrid not available. Install with: pip install sendgrid")

@dataclass
class EmailRecipient:
    """Email recipient information"""
    email: str
    name: str = ""
    type: str = "to"  # to, cc, bcc

@dataclass
class EmailConfig:
    """Email configuration settings"""
    # SMTP Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    
    # SendGrid Settings
    sendgrid_api_key: str = ""
    
    # Email Settings
    from_email: str = ""
    from_name: str = "Grafana Analysis System"
    delivery_method: str = "smtp"  # smtp or sendgrid

class EmailTemplates:
    """Professional email templates matching user's format"""
    
    ANALYSIS_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .findings { background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .finding-item { margin: 10px 0; padding: 8px; border-left: 3px solid #ffc107; }
        .critical { border-left-color: #dc3545; }
        .warning { border-left-color: #fd7e14; }
        .info { border-left-color: #17a2b8; }
        .signature { margin-top: 30px; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <p>Hi All,</p>
        
        <p>I've completed the analysis of the Grafana dashboards (Infrastructure and System Processes) for the past 24 hours. The key observations and recommended actions are summarized in the attached Excel report.</p>
    </div>
    
    <p><strong>Here are the key findings:</strong></p>
    
    <div class="findings">
        {critical_findings}
        {warning_findings}
        {info_findings}
    </div>
    
    <p>All these findings, along with suggested actions, are detailed in the attached <strong>{report_name}</strong> report.</p>
    
    <div class="signature">
        <p>Best regards,<br>
        Iswarya</p>
    </div>
</body>
</html>
"""

    CRITICAL_ALERT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .alert-header { background-color: #f8d7da; padding: 20px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #f5c6cb; }
        .critical-item { margin: 10px 0; padding: 12px; background-color: #fff5f5; border-left: 4px solid #dc3545; border-radius: 3px; }
        .signature { margin-top: 30px; font-style: italic; }
    </style>
</head>
<body>
    <div class="alert-header">
        <p><strong>🚨 URGENT: Critical System Alert</strong></p>
        <p>Hi All,</p>
        
        <p>Critical issues have been detected in the Grafana monitoring analysis that require immediate attention.</p>
    </div>
    
    <p><strong>Critical Issues Requiring Immediate Action:</strong></p>
    
    <div>
        {critical_issues}
    </div>
    
    <p><strong>Recommended Actions:</strong></p>
    <ul>
        {immediate_actions}
    </ul>
    
    <p>Please prioritize these issues to prevent potential system failures.</p>
    
    <div class="signature">
        <p>Best regards,<br>
        Iswarya</p>
    </div>
</body>
</html>
"""

    @staticmethod
    def format_analysis_findings(analysis_data):
        """Format analysis data into professional findings format"""
        critical_findings = ""
        warning_findings = ""
        info_findings = ""
        
        # Extract findings from analysis data
        if 'structured_data' in analysis_data and 'issues' in analysis_data['structured_data']:
            issues = analysis_data['structured_data']['issues']
            
            # Categorize findings (this would be enhanced based on your actual data structure)
            for issue in issues:
                if 'memory' in issue.lower() and 'leak' in issue.lower():
                    critical_findings += f'<div class="finding-item critical"><strong>amazon-ssm-agent:</strong> We\'re seeing gradual memory growth and high futex wait, which may indicate a memory leak. I recommend immediate action on this.</div>'
                elif 'cpu' in issue.lower() and 'spike' in issue.lower():
                    warning_findings += f'<div class="finding-item warning"><strong>process-exporter:</strong> A CPU spike was observed. This needs monitoring and a possible configuration review.</div>'
                elif 'io wait' in issue.lower():
                    warning_findings += f'<div class="finding-item warning"><strong>portail:</strong> There was an IO wait spike around 02:00. Please monitor this for recurrence.</div>'
        
        return critical_findings, warning_findings, info_findings

    @staticmethod
    def get_professional_subject(analysis_type="analysis"):
        """Generate professional subject lines"""
        if analysis_type == "critical":
            return "🚨 URGENT: Critical System Alert - Immediate Action Required"
        else:
            return "📊 Grafana Infrastructure Analysis Report - Action Required"

class EmailNotificationService:
    """
    Service for sending email notifications with analysis reports
    """
    
    def __init__(self, config_file: str = "email_config.json"):
        """Initialize email service with configuration"""
        self.config = self._load_config(config_file)
        self.templates = EmailTemplates()
        self.logger = self._setup_logging()
        
        # Load recipients
        self.recipients = self._load_recipients()
        
        # Set professional sender format
        self.sender_name = "Iswarya Kolimalla"
        self.sender_email = self.config.from_email
    
    def _load_config(self, config_file: str) -> EmailConfig:
        """Load email configuration from file or environment"""
        config = EmailConfig()
        
        # Try loading from file first
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    for key, value in file_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        # Override with environment variables
        config.smtp_username = os.getenv("EMAIL_SMTP_USERNAME", config.smtp_username)
        config.smtp_password = os.getenv("EMAIL_SMTP_PASSWORD", config.smtp_password)
        config.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", config.sendgrid_api_key)
        config.from_email = os.getenv("EMAIL_FROM", config.from_email)
        config.delivery_method = os.getenv("EMAIL_DELIVERY_METHOD", config.delivery_method)
        
        return config
    
    def _load_recipients(self) -> List[EmailRecipient]:
        """Load email recipients from configuration"""
        recipients = []
        recipients_file = "recipients.json"
        
        if os.path.exists(recipients_file):
            try:
                with open(recipients_file, 'r') as f:
                    recipients_data = json.load(f)
                    for recipient_data in recipients_data:
                        recipients.append(EmailRecipient(**recipient_data))
            except Exception as e:
                self.logger.warning(f"Could not load recipients file: {e}")
        
        # Load from environment as fallback
        env_recipients = os.getenv("EMAIL_RECIPIENTS", "")
        if env_recipients and not recipients:
            for email in env_recipients.split(","):
                email = email.strip()
                if email:
                    recipients.append(EmailRecipient(email=email))
        
        return recipients
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for email service"""
        logger = logging.getLogger("email_notification")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def send_analysis_report(self, 
                       analysis_result: Dict[str, Any], 
                       widgets_data: List[Any],
                       excel_file: Optional[str] = None,
                       markdown_file: Optional[str] = None,
                       recipients: Optional[List[EmailRecipient]] = None) -> bool:
        """
        Send complete analysis report via email
        """
        try:
            if recipients is None:
                recipients = self.recipients
            
            if not recipients:
                self.logger.error("No recipients configured for email notifications")
                return False
            
            # Extract analysis data
            analysis_data = analysis_result.get("analysis", {})
            structured_data = analysis_data.get("structured_data", {})
            
            # Prepare template variables
            template_vars = {
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_widgets": len(widgets_data),
                "performance_score": structured_data.get("performance_score", 0),
                "critical_issues": len(structured_data.get("issues", [])),
                "widgets_with_issues": sum(1 for w in widgets_data if hasattr(w, 'trend') and w.trend in ['Spiking', 'Critical']),
                "analysis_summary": self._generate_summary(analysis_result),
                "immediate_actions": structured_data.get("recommendations", {}).get("immediate", []),
                "short_term_actions": structured_data.get("recommendations", {}).get("short_term", []),
                "critical_issues_list": structured_data.get("issues", []),
                "model_used": analysis_data.get("model_used", "GPT-4o"),
                "processing_time": "< 60s"
            }
            
            # Generate email content
            template = Template(self.templates.ANALYSIS_REPORT_TEMPLATE)
            html_content = template.render(**template_vars)
            
            # Create subject
            subject = f"📊 Grafana Analysis Report - {template_vars['report_date']}"
            if template_vars['critical_issues'] > 0:
                subject = f"🚨 {subject} - {template_vars['critical_issues']} Critical Issues"
            
            # Set professional sender format
            from_email = f"{self.sender_name} <{self.sender_email}>"
            
            # Send email
            success = self._send_email(
                recipients=recipients,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                attachments=[
                    {"file_path": excel_file, "filename": f"grafana_report_{template_vars['report_date']}.xlsx"} if excel_file else None,
                    {"file_path": markdown_file, "filename": f"grafana_analysis_{template_vars['report_date']}.md"} if markdown_file else None
                ]
            )
            
            if success:
                self.logger.info(f"Analysis report sent successfully to {len(recipients)} recipients")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send analysis report: {str(e)}")
            return False
    
    def send_critical_alert(self, 
                          critical_issues: List[str], 
                          immediate_actions: List[str],
                          recipients: Optional[List[EmailRecipient]] = None) -> bool:
        """
        Send critical alert email for urgent issues
        """
        try:
            if recipients is None:
                # Use only critical alert recipients
                recipients = [r for r in self.recipients if r.type in ['to', 'critical']]
            
            if not recipients:
                self.logger.error("No recipients configured for critical alerts")
                return False
            
            # Prepare template variables
            template_vars = {
                "critical_issues": critical_issues,
                "immediate_actions": immediate_actions,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Generate email content
            template = Template(self.templates.CRITICAL_ALERT_TEMPLATE)
            html_content = template.render(**template_vars)
            
            subject = f"🚨 CRITICAL ALERT - Grafana Monitoring ({len(critical_issues)} issues)"
            from_email = f"{self.sender_name} <{self.sender_email}>"
            
            # Send email (high priority)
            success = self._send_email(
                recipients=recipients,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                priority="high"
            )
            
            if success:
                self.logger.warning(f"Critical alert sent to {len(recipients)} recipients")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send critical alert: {str(e)}")
            return False
    
    def _send_email(self, 
                   recipients: List[EmailRecipient],
                   subject: str,
                   html_content: str,
                   attachments: Optional[List[Dict]] = None,
                   priority: str = "normal",
                   from_email: str = None) -> bool:
        """
        Send email using configured delivery method
        """
        if self.config.delivery_method.lower() == "sendgrid" and SENDGRID_AVAILABLE:
            return self._send_via_sendgrid(recipients, subject, html_content, attachments, priority)
        else:
            return self._send_via_smtp(recipients, subject, html_content, attachments, priority, from_email)
    
    def _send_via_smtp(self, 
                      recipients: List[EmailRecipient],
                      subject: str,
                      html_content: str,
                      attachments: Optional[List[Dict]] = None,
                      priority: str = "normal",
                      from_email: str = None) -> bool:
        """
        Send email via SMTP (Gmail)
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or f"{self.config.from_name} <{self.config.from_email}>"
            msg['Subject'] = subject
            
            # Set priority
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            # Add recipients
            to_emails = [r.email for r in recipients if r.type == 'to']
            cc_emails = [r.email for r in recipients if r.type == 'cc']
            bcc_emails = [r.email for r in recipients if r.type == 'bcc']
            
            if to_emails:
                msg['To'] = ', '.join(to_emails)
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    if attachment and attachment.get('file_path') and os.path.exists(attachment['file_path']):
                        with open(attachment['file_path'], "rb") as file:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(file.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {attachment.get("filename", os.path.basename(attachment["file_path"]))}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.smtp_username, self.config.smtp_password)
            
            all_recipients = to_emails + cc_emails + bcc_emails
            server.sendmail(self.config.from_email, all_recipients, msg.as_string())
            server.quit()
            
            self.logger.info(f"Email sent via SMTP to {len(all_recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP email failed: {str(e)}")
            return False
    
    def _send_via_sendgrid(self, 
                          recipients: List[EmailRecipient],
                          subject: str,
                          html_content: str,
                          attachments: Optional[List[Dict]] = None,
                          priority: str = "normal") -> bool:
        """
        Send email via SendGrid API
        """
        try:
            # Create SendGrid mail object
            message = Mail(
                from_email=self.config.from_email,
                to_emails=[r.email for r in recipients if r.type == 'to'],
                subject=subject,
                html_content=html_content
            )
            
            # Add CC and BCC
            cc_emails = [r.email for r in recipients if r.type == 'cc']
            bcc_emails = [r.email for r in recipients if r.type == 'bcc']
            
            if cc_emails:
                message.cc = cc_emails
            if bcc_emails:
                message.bcc = bcc_emails
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    if attachment and attachment.get('file_path') and os.path.exists(attachment['file_path']):
                        with open(attachment['file_path'], 'rb') as f:
                            data = f.read()
                            encoded_file = base64.b64encode(data).decode()
                            
                            attached_file = Attachment(
                                FileContent(encoded_file),
                                FileName(attachment.get("filename", os.path.basename(attachment["file_path"]))),
                                FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                Disposition('attachment')
                            )
                            message.attachment = attached_file
            
            # Send email
            sg = SendGridAPIClient(api_key=self.config.sendgrid_api_key)
            response = sg.send(message)
            
            self.logger.info(f"Email sent via SendGrid to {len(recipients)} recipients (status: {response.status_code})")
            return True
            
        except Exception as e:
            self.logger.error(f"SendGrid email failed: {str(e)}")
            return False
    
    def _generate_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a brief summary from analysis results
        """
        try:
            analysis_data = analysis_result.get("analysis", {})
            structured_data = analysis_data.get("structured_data", {})
            
            score = structured_data.get("performance_score", 0)
            issues_count = len(structured_data.get("issues", []))
            
            if score >= 8:
                status = "System performing well"
            elif score >= 6:
                status = "System performance acceptable with monitoring needed"
            elif score >= 4:
                status = "System performance concerning, action recommended"
            else:
                status = "System performance critical, immediate action required"
            
            summary = f"{status}. "
            
            if issues_count > 0:
                summary += f"{issues_count} critical issue{'s' if issues_count != 1 else ''} detected requiring attention."
            else:
                summary += "No critical issues detected."
            
            return summary
            
        except Exception:
            return "Analysis completed. Please review the detailed report for findings and recommendations."

# Test function
def test_email_notification():
    """Test email notification functionality"""
    print("🧪 Testing Email Notification Service...")
    
    # Create service
    service = EmailNotificationService()
    
    # Test recipients
    test_recipients = [
        EmailRecipient(email="devops@company.com", name="DevOps Team", type="to"),
        EmailRecipient(email="manager@company.com", name="Engineering Manager", type="cc")
    ]
    
    # Mock analysis result
    mock_analysis = {
        "success": True,
        "analysis": {
            "structured_data": {
                "performance_score": 7.5,
                "issues": [
                    "High CPU usage detected on production servers",
                    "Memory utilization approaching threshold"
                ],
                "recommendations": {
                    "immediate": [
                        "Scale up CPU resources on affected servers",
                        "Monitor memory usage closely"
                    ],
                    "short_term": [
                        "Implement auto-scaling policies",
                        "Review application memory leaks"
                    ]
                }
            },
            "model_used": "gpt-4o"
        }
    }
    
    # Mock widget data
    mock_widgets = [
        type('Widget', (), {
            'widget_name': 'CPU Usage',
            'trend': 'Spiking',
            'category': 'Infrastructure'
        })() for _ in range(25)
    ]
    
    try:
        # Test analysis report
        success = service.send_analysis_report(
            analysis_result=mock_analysis,
            widgets_data=mock_widgets,
            recipients=test_recipients
        )
        
        print(f"✅ Analysis report test: {'SUCCESS' if success else 'FAILED'}")
        
        # Test critical alert
        success = service.send_critical_alert(
            critical_issues=[
                "Database connection pool exhausted",
                "API response time exceeding SLA"
            ],
            immediate_actions=[
                "Restart database connection pool",
                "Scale API instances immediately"
            ],
            recipients=test_recipients
        )
        
        print(f"✅ Critical alert test: {'SUCCESS' if success else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")

if __name__ == "__main__":
    test_email_notification()
