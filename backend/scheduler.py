#!/usr/bin/env python3
"""
Automated Scheduler for Grafana Analysis Reports

This module provides automated scheduling capabilities for:
- Daily analysis reports
- Weekly summaries
- Critical alert monitoring
- Automatic email delivery to stakeholders

Usage:
    python scheduler.py --start-scheduler
"""

import schedule
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import argparse
import logging

# Add the backend directory to the path
sys.path.append('.')

from email_notification import EmailNotificationService, EmailRecipient
from llm_analysis import GrafanaAnalysisLLM, MarkdownReportGenerator, WidgetData
from excel_export import ExcelReportGenerator
from demo_llm_analysis import generate_sample_widgets

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GrafanaAnalysisScheduler:
    """
    Automated scheduler for Grafana analysis and email reports
    """
    
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.llm_analyzer = GrafanaAnalysisLLM()
        self.report_generator = MarkdownReportGenerator()
        self.excel_generator = ExcelReportGenerator()
        
        # Create reports directory
        self.reports_dir = Path("./scheduled_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        logger.info("Grafana Analysis Scheduler initialized")
    
    def daily_analysis_report(self):
        """
        Generate and send daily analysis report
        """
        try:
            logger.info("Starting daily analysis report generation...")
            
            # Generate sample widget data (in production, this would come from actual screenshots)
            widgets = generate_sample_widgets(count=25)
            
            # Perform LLM analysis
            analysis_result = self.llm_analyzer.analyze_widgets(widgets)
            
            if not analysis_result["success"]:
                logger.error(f"LLM analysis failed: {analysis_result['error']}")
                return False
            
            # Generate reports
            report_data = self.report_generator.generate_report(analysis_result, widgets)
            
            # Save markdown report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            markdown_file = self.reports_dir / f"daily_analysis_{timestamp}.md"
            
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(report_data["markdown"])
            
            # Generate Excel report
            excel_file = self.excel_generator.generate_excel_report(analysis_result, widgets)
            
            # Send email to stakeholders
            success = self.email_service.send_analysis_report(
                analysis_result=analysis_result,
                widgets_data=widgets,
                excel_file=excel_file,
                markdown_file=str(markdown_file)
            )
            
            if success:
                logger.info("Daily analysis report sent successfully")
            else:
                logger.error("Failed to send daily analysis report")
            
            return success
            
        except Exception as e:
            logger.error(f"Daily analysis report failed: {str(e)}")
            return False
    
    def weekly_summary_report(self):
        """
        Generate and send weekly summary report
        """
        try:
            logger.info("Starting weekly summary report generation...")
            
            # Generate comprehensive widget data for weekly review
            widgets = generate_sample_widgets(count=50)
            
            # Perform analysis with focus on trends
            analysis_result = self.llm_analyzer.analyze_widgets(widgets)
            
            if not analysis_result["success"]:
                logger.error(f"Weekly analysis failed: {analysis_result['error']}")
                return False
            
            # Generate reports
            report_data = self.report_generator.generate_report(analysis_result, widgets)
            
            # Save reports with weekly prefix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            markdown_file = self.reports_dir / f"weekly_summary_{timestamp}.md"
            
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(report_data["markdown"])
            
            excel_file = self.excel_generator.generate_excel_report(analysis_result, widgets)
            
            # Send to all stakeholders (including management)
            success = self.email_service.send_analysis_report(
                analysis_result=analysis_result,
                widgets_data=widgets,
                excel_file=excel_file,
                markdown_file=str(markdown_file)
            )
            
            logger.info("Weekly summary report completed")
            return success
            
        except Exception as e:
            logger.error(f"Weekly summary report failed: {str(e)}")
            return False
    
    def check_critical_alerts(self):
        """
        Monitor for critical alerts and send immediate notifications
        """
        try:
            logger.info("Checking for critical alerts...")
            
            # Generate current system state
            widgets = generate_sample_widgets(count=20)
            
            # Quick analysis focused on critical issues
            analysis_result = self.llm_analyzer.analyze_widgets(widgets)
            
            if analysis_result["success"]:
                structured_data = analysis_result["analysis"]["structured_data"]
                critical_issues = structured_data.get("issues", [])
                
                # Check if performance score is below threshold
                performance_score = structured_data.get("performance_score", 10)
                
                if critical_issues or performance_score < 5:
                    logger.warning(f"Critical issues detected: {len(critical_issues)} issues, score: {performance_score}")
                    
                    # Send critical alert
                    immediate_actions = structured_data.get("recommendations", {}).get("immediate", [])
                    
                    success = self.email_service.send_critical_alert(
                        critical_issues=critical_issues,
                        immediate_actions=immediate_actions
                    )
                    
                    if success:
                        logger.warning("Critical alert sent successfully")
                    else:
                        logger.error("Failed to send critical alert")
                    
                    return success
                else:
                    logger.info("No critical issues detected")
                    return True
            else:
                logger.error("Failed to check critical alerts")
                return False
                
        except Exception as e:
            logger.error(f"Critical alert check failed: {str(e)}")
            return False
    
    def health_check(self):
        """
        Perform system health check
        """
        try:
            logger.info("Performing system health check...")
            
            health_status = {
                "email_service": False,
                "llm_service": False,
                "reports_directory": False,
                "timestamp": datetime.now().isoformat()
            }
            
            # Check email service
            try:
                # Try to initialize email service
                if hasattr(self.email_service, 'recipients') and self.email_service.recipients:
                    health_status["email_service"] = True
            except Exception:
                pass
            
            # Check LLM service
            try:
                if os.getenv("OPENAI_API_KEY"):
                    health_status["llm_service"] = True
            except Exception:
                pass
            
            # Check reports directory
            health_status["reports_directory"] = self.reports_dir.exists()
            
            # Log health status
            all_healthy = all(health_status.values())
            if all_healthy:
                logger.info("System health check passed")
            else:
                logger.warning(f"System health issues detected: {health_status}")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def start_scheduler(self):
        """
        Start the automated scheduler
        """
        logger.info("Starting Grafana Analysis Scheduler...")
        
        # Schedule daily reports (every day at 8:00 AM)
        schedule.every().day.at("08:00").do(self.daily_analysis_report)
        
        # Schedule weekly reports (every Monday at 9:00 AM)
        schedule.every().monday.at("09:00").do(self.weekly_summary_report)
        
        # Schedule critical alert checks (every 30 minutes)
        schedule.every(30).minutes.do(self.check_critical_alerts)
        
        # Schedule health checks (every hour)
        schedule.every().hour.do(self.health_check)
        
        logger.info("Scheduler configured with the following jobs:")
        logger.info("- Daily reports: 08:00 AM")
        logger.info("- Weekly reports: Monday 09:00 AM")
        logger.info("- Critical alerts: Every 30 minutes")
        logger.info("- Health checks: Every hour")
        
        # Run scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Grafana Analysis Scheduler")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the automated scheduler")
    parser.add_argument("--test-daily", action="store_true", help="Test daily report generation")
    parser.add_argument("--test-weekly", action="store_true", help="Test weekly report generation")
    parser.add_argument("--test-critical", action="store_true", help="Test critical alert check")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    
    args = parser.parse_args()
    
    scheduler = GrafanaAnalysisScheduler()
    
    if args.start_scheduler:
        scheduler.start_scheduler()
    elif args.test_daily:
        print("🧪 Testing daily report generation...")
        success = scheduler.daily_analysis_report()
        print(f"✅ Daily report test: {'SUCCESS' if success else 'FAILED'}")
    elif args.test_weekly:
        print("🧪 Testing weekly report generation...")
        success = scheduler.weekly_summary_report()
        print(f"✅ Weekly report test: {'SUCCESS' if success else 'FAILED'}")
    elif args.test_critical:
        print("🧪 Testing critical alert check...")
        success = scheduler.check_critical_alerts()
        print(f"✅ Critical alert test: {'SUCCESS' if success else 'FAILED'}")
    elif args.health_check:
        print("🧪 Performing health check...")
        health = scheduler.health_check()
        print(f"📊 Health status: {health}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
