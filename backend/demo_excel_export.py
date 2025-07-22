#!/usr/bin/env python3
"""
Demo script for testing Excel export functionality

This script demonstrates:
1. Loading existing analysis results 
2. Converting markdown to Excel format
3. Generating structured Excel reports with multiple sheets

Usage:
    python demo_excel_export.py [--input-file analysis_file.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to the path
sys.path.append('.')

from excel_export import ExcelReportGenerator, MarkdownTableParser
from llm_analysis import WidgetData


def load_sample_analysis():
    """Load sample analysis data for testing"""
    sample_files = [
        "./demo_reports/analysis_metadata_20250722_162828.json",
        "./reports/grafana_analysis_20250722_163053.md"
    ]
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"📁 Loading sample data from: {file_path}")
            
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get("analysis_result", {})
            
    print("❌ No sample analysis files found")
    return None


def create_sample_analysis():
    """Create sample analysis result for testing"""
    sample_markdown = """
## 📊 Widget Analysis Summary

### Per-Widget Analysis Table
| Widget Name           | Category      | Current Value | Min/Max       | Trend   | Status   | Key Observations                          |
|-----------------------|---------------|---------------|---------------|---------|----------|-------------------------------------------|
| CPU Usage             | Infrastructure| 38.9%         | 10.0%/95.0%   | Rising  | Warning  | Rising trend, but within acceptable range |
| Memory Usage          | Infrastructure| 50.6%         | 15.0%/90.0%   | Rising  | Info     | Usage increasing, but within limits       |
| Disk I/O Read         | Storage       | 91.6 MB/s     | 5.0 MB/s/150.0 MB/s | Spiking | Critical | High I/O read, requires attention         |
| Network In            | Network       | 78.4 Mbps     | 1.0 Mbps/100.0 Mbps | Stable | Info     | High but stable network input             |
| Response Time         | Performance   | 538.5 ms      | 50.0 ms/2000.0 ms | Stable | Info     | Response time is stable                   |
| Error Rate            | Reliability   | 3.1%          | 0.0%/5.0%     | Spiking | Critical | Spiking error rate, requires attention    |
| DB Connections        | Database      | 35            | 5/100         | Stable  | Info     | Stable DB connections                     |
| Active Users          | Application   | 420           | 50/1000       | Rising  | Info     | Rising trend, monitor for capacity        |
| Pod CPU Usage         | Container     | 57.9%         | 10.0%/90.0%   | Spiking | Warning  | Spiking usage, monitor for resource limits|
| API Latency           | API           | 498.4 ms      | 25.0 ms/800.0 ms | Spiking | Critical | High latency, requires immediate attention|
| Log Errors/min        | Observability | 65            | 0/100         | Stable  | Warning  | High error rate, investigate causes       |
| SSL Cert Expiry       | Security      | 38            | 1/90          | Falling | Info     | SSL certificate expiry within safe range  |

## 🔍 Detailed Analysis

### Infrastructure Widgets
CPU usage is trending upward at 38.9%, which requires monitoring but is still within acceptable limits.

### System Widgets  
Response times are stable, but error rates are spiking which needs immediate attention.

## ⚠️ Critical Issues & Alerts
- Disk I/O read performance is critically high at 91.6 MB/s
- Error rate spiking to 3.1% above normal thresholds  
- API latency is critically high at 498.4ms

## 🛠️ Recommendations

### Immediate Actions (< 1 hour)
- Investigate high disk I/O causing performance bottleneck
- Review error logs for error rate spike causes
- Monitor API latency for service degradation

### Short-term Actions (< 24 hours)
- Scale CPU resources if usage continues rising
- Optimize database queries affecting response times
- Review network capacity planning

### Long-term Optimizations (< 1 week)
- Implement auto-scaling for CPU and memory
- Set up proactive alerting for performance metrics
- Conduct capacity planning review

## 📈 Performance Insights
Overall system health is at 7/10 with several areas requiring attention to prevent performance degradation.

## 🎯 Key Metrics Summary
- **Total Widgets Analyzed**: 12
- **Widgets with Issues**: 6
- **Critical Alerts**: 3
- **Performance Score**: 7/10
"""

    return {
        "success": True,
        "analysis": {
            "raw_markdown": sample_markdown,
            "structured_data": {
                "performance_score": 7.0,
                "issues": [
                    "Disk I/O read performance critically high",
                    "Error rate spiking above thresholds",
                    "API latency critically high"
                ],
                "recommendations": {
                    "immediate": [
                        "Investigate high disk I/O",
                        "Review error logs",
                        "Monitor API latency"
                    ],
                    "short_term": [
                        "Scale CPU resources",
                        "Optimize database queries",
                        "Review network capacity"
                    ],
                    "long_term": [
                        "Implement auto-scaling",
                        "Set up proactive alerting",
                        "Conduct capacity planning"
                    ]
                }
            },
            "model_used": "gpt-4o",
            "analyzed_at": datetime.now().isoformat(),
            "widget_count": 12,
            "tokens_used": 2500
        }
    }


def create_sample_widgets():
    """Create sample widget data for testing"""
    widgets = [
        WidgetData("CPU Usage", "Infrastructure", "10.0%", "95.0%", "38.9%", "Rising", "", "", "", ""),
        WidgetData("Memory Usage", "Infrastructure", "15.0%", "90.0%", "50.6%", "Rising", "", "", "", ""),
        WidgetData("Disk I/O Read", "Storage", "5.0 MB/s", "150.0 MB/s", "91.6 MB/s", "Spiking", "", "", "", ""),
        WidgetData("Network In", "Network", "1.0 Mbps", "100.0 Mbps", "78.4 Mbps", "Stable", "", "", "", ""),
        WidgetData("Response Time", "Performance", "50.0 ms", "2000.0 ms", "538.5 ms", "Stable", "", "", "", ""),
        WidgetData("Error Rate", "Reliability", "0.0%", "5.0%", "3.1%", "Spiking", "", "", "", ""),
    ]
    return widgets


def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Demo Excel export for Grafana analysis")
    parser.add_argument("--input-file", help="Input analysis JSON file")
    parser.add_argument("--output-dir", default="./reports", help="Output directory for Excel files")
    args = parser.parse_args()
    
    print("🚀 Starting Excel Export Demo")
    
    # Load or create analysis data
    if args.input_file and os.path.exists(args.input_file):
        print(f"📁 Loading analysis from: {args.input_file}")
        with open(args.input_file, 'r') as f:
            data = json.load(f)
            analysis_result = data.get("analysis_result", {})
    else:
        print("📝 Creating sample analysis data...")
        analysis_result = create_sample_analysis()
    
    # Create sample widgets
    widgets_data = create_sample_widgets()
    
    print(f"✅ Analysis loaded with {len(widgets_data)} widgets")
    
    # Test markdown parsing
    print("\n🔍 Testing markdown table parsing...")
    markdown_text = analysis_result.get("analysis", {}).get("raw_markdown", "")
    
    if markdown_text:
        widget_rows = MarkdownTableParser.parse_widget_table(markdown_text)
        print(f"📊 Parsed {len(widget_rows)} widget rows from markdown")
        
        summary_metrics = MarkdownTableParser.parse_summary_metrics(markdown_text)
        print(f"📈 Extracted summary metrics: {summary_metrics}")
    else:
        print("⚠️ No markdown content found")
    
    # Generate Excel report
    print("\n📊 Generating Excel report...")
    try:
        generator = ExcelReportGenerator(output_dir=args.output_dir)
        excel_file = generator.generate_excel_report(analysis_result, widgets_data)
        
        print(f"✅ Excel report generated successfully!")
        print(f"📁 File location: {excel_file}")
        
        # Display file info
        if os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            print(f"📏 File size: {file_size:,} bytes")
            print(f"🕒 Created: {datetime.fromtimestamp(os.path.getctime(excel_file))}")
            
            print("\n📋 Excel file contains 3 sheets:")
            print("  📊 Summary - Key metrics and overview")
            print("  🏗️ Infrastructure Widgets - CPU, Memory, Storage, Network, Database")
            print("  ⚙️ System Widgets - Performance, Application, Container, API, etc.")
            
        return True
        
    except Exception as e:
        print(f"❌ Excel generation failed: {e}")
        print("💡 Make sure openpyxl is installed: pip install openpyxl")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
