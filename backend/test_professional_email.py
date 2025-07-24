# Create backend/test_professional_email.py
from email_notification import EmailNotificationService, EmailRecipient

def test_professional_email():
    """Test the professional email format"""
    
    # Sample analysis data (matching the expected structure)
    sample_analysis_result = {
        "analysis": {
            "structured_data": {
                "performance_score": 7.5,
                "issues": [
                    "amazon-ssm-agent showing memory leak patterns",
                    "process-exporter CPU spike detected", 
                    "portail IO wait spike around 02:00",
                    "uniskad high voluntary context switches",
                    "apt.systemd high disk write activity"
                ],
                "recommendations": {
                    "immediate": [
                        "Investigate amazon-ssm-agent memory leak",
                        "Review process-exporter configuration",
                        "Monitor portail IO patterns"
                    ],
                    "short_term": [
                        "Scale CPU resources if needed",
                        "Optimize disk write scheduling"
                    ],
                    "long_term": [
                        "Implement proactive monitoring",
                        "Set up automated scaling"
                    ]
                }
            },
            "model_used": "gpt-4o",
            "analyzed_at": "2025-07-23T12:00:00"
        }
    }
    
    # Sample widgets data
    sample_widgets = [
        type('Widget', (), {
            'widget_name': 'amazon-ssm-agent',
            'category': 'System',
            'trend': 'Critical',
            'current_value': '85%',
            'comments': 'Memory leak detected'
        })(),
        type('Widget', (), {
            'widget_name': 'process-exporter', 
            'category': 'Infrastructure',
            'trend': 'Spiking',
            'current_value': '92%',
            'comments': 'CPU spike observed'
        })(),
        type('Widget', (), {
            'widget_name': 'portail',
            'category': 'Storage', 
            'trend': 'Warning',
            'current_value': '15ms',
            'comments': 'IO wait spike at 02:00'
        })()
    ]
    
    # Create recipients (using your current recipients.json structure)
    recipients = [
        EmailRecipient("kiswarya74@gmail.com", "Iswarya", "to"),
        EmailRecipient("iswarya.kolimalla@amzur.com", "Iswarya Work", "cc"),
        EmailRecipient("vishnu.kanthamaraju@amzur.com", "Vishnu", "to")
    ]
    
    # Send professional email with CORRECT parameter names
    service = EmailNotificationService()
    success = service.send_analysis_report(
        analysis_result=sample_analysis_result,  # ← Fixed parameter name
        widgets_data=sample_widgets,             # ← Fixed parameter name
        excel_file="reports/Amzur_infra_status_report.xlsx",    # ← Fixed parameter name
        markdown_file="reports/grafana_analysis_report.md",     # ← Fixed parameter name
        recipients=recipients
    )
    
    print(f"✅ Professional email sent: {success}")
    
    # Also test critical alert
    success_critical = service.send_critical_alert(
        critical_issues=[
            "amazon-ssm-agent memory leak requires immediate attention",
            "process-exporter CPU usage critically high"
        ],
        immediate_actions=[
            "Restart amazon-ssm-agent service",
            "Scale process-exporter resources",
            "Monitor system performance closely"
        ],
        recipients=recipients
    )
    
    print(f"✅ Critical alert sent: {success_critical}")

if __name__ == "__main__":
    test_professional_email()