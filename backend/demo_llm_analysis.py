#!/usr/bin/env python3
"""
Demo script for testing LLM analysis with custom Grafana widget data

This script demonstrates how to:
1. Create sample widget data (simulating 37 widgets)
2. Use custom prompts for LLM analysis
3. Generate markdown reports
4. Export analysis results

Usage:
    python demo_llm_analysis.py [--api-key YOUR_API_KEY]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
import random
from typing import List
sys.path.append('.')

from llm_analysis import GrafanaAnalysisLLM, MarkdownReportGenerator, WidgetData

def generate_sample_widgets(count: int = 37) -> List[WidgetData]:
    """
    Generate sample widget data representing a typical Grafana dashboard
    """
    widgets = []
    
    # Define widget templates
    widget_templates = [
        # Infrastructure widgets
        ("CPU Usage", "Infrastructure", "%", (10, 95), ("stable", "rising", "spiking")),
        ("CPU Load Average", "Infrastructure", "", (0.5, 8.0), ("stable", "rising")),
        ("Memory Usage", "Infrastructure", "%", (15, 90), ("stable", "rising")),
        ("Memory Available", "Infrastructure", "GB", (0.5, 16.0), ("stable", "falling")),
        ("Disk Usage /", "Storage", "%", (20, 95), ("stable", "rising")),
        ("Disk Usage /var", "Storage", "%", (10, 85), ("stable", "rising")),
        ("Disk I/O Read", "Storage", "MB/s", (5, 150), ("stable", "spiking")),
        ("Disk I/O Write", "Storage", "MB/s", (2, 80), ("stable", "spiking")),
        
        # Network widgets
        ("Network In", "Network", "Mbps", (1, 100), ("stable", "rising")),
        ("Network Out", "Network", "Mbps", (0.5, 50), ("stable", "rising")),
        ("Network Errors", "Network", "count", (0, 25), ("stable", "spiking")),
        ("TCP Connections", "Network", "count", (50, 1000), ("stable", "rising")),
        
        # Application Performance
        ("Response Time", "Performance", "ms", (50, 2000), ("stable", "rising", "spiking")),
        ("Throughput", "Performance", "req/s", (100, 5000), ("stable", "rising", "falling")),
        ("Error Rate", "Reliability", "%", (0, 5), ("stable", "spiking")),
        ("Success Rate", "Reliability", "%", (95, 100), ("stable", "falling")),
        
        # Database metrics
        ("DB Connections", "Database", "count", (5, 100), ("stable", "rising")),
        ("DB Query Time", "Database", "ms", (10, 500), ("stable", "rising", "spiking")),
        ("DB Lock Waits", "Database", "count", (0, 50), ("stable", "spiking")),
        ("DB Cache Hit Rate", "Database", "%", (85, 99), ("stable", "falling")),
        
        # Application specific
        ("Active Users", "Application", "count", (50, 1000), ("stable", "rising", "falling")),
        ("Session Count", "Application", "count", (20, 500), ("stable", "rising")),
        ("Queue Length", "Application", "count", (0, 100), ("stable", "rising", "spiking")),
        ("Cache Hit Rate", "Performance", "%", (80, 98), ("stable", "falling")),
        
        # Container/K8s metrics
        ("Pod CPU Usage", "Container", "%", (10, 90), ("stable", "rising", "spiking")),
        ("Pod Memory Usage", "Container", "%", (20, 85), ("stable", "rising")),
        ("Container Restarts", "Container", "count", (0, 10), ("stable", "spiking")),
        ("Node Count", "Container", "count", (3, 20), ("stable", "rising", "falling")),
        
        # Custom application metrics
        ("API Latency", "API", "ms", (25, 800), ("stable", "rising", "spiking")),
        ("Upload Rate", "Application", "files/min", (10, 200), ("stable", "rising")),
        ("Processing Queue", "Application", "items", (0, 500), ("stable", "rising", "spiking")),
        ("Concurrent Tasks", "Application", "count", (5, 50), ("stable", "rising")),
        ("Worker Threads", "Application", "count", (2, 20), ("stable", "rising")),
        
        # Additional monitoring
        ("Log Errors/min", "Observability", "count", (0, 100), ("stable", "spiking")),
        ("Alert Count", "Observability", "count", (0, 15), ("stable", "spiking")),
        ("Backup Status", "Reliability", "hours", (0, 48), ("stable", "rising")),
        ("SSL Cert Expiry", "Security", "days", (1, 90), ("stable", "falling")),
    ]
    
    # Generate widgets with realistic data
    for i in range(min(count, len(widget_templates))):
        template = widget_templates[i]
        name, category, unit, value_range, trends = template
        
        # Generate realistic values
        min_val = value_range[0]
        max_val = value_range[1]
        current_val = random.uniform(min_val + (max_val - min_val) * 0.2, 
                                   min_val + (max_val - min_val) * 0.8)
        
        # Format values based on unit
        if unit == "%":
            min_str = f"{min_val:.1f}%"
            max_str = f"{max_val:.1f}%"
            current_str = f"{current_val:.1f}%"
        elif unit in ["GB", "MB/s", "Mbps", "ms"]:
            min_str = f"{min_val:.1f} {unit}"
            max_str = f"{max_val:.1f} {unit}"
            current_str = f"{current_val:.1f} {unit}"
        else:
            min_str = f"{int(min_val)}"
            max_str = f"{int(max_val)}"
            current_str = f"{int(current_val)}"
        
        # Select trend
        trend = random.choice(trends).title()
        
        # Generate spike time for spiking trends
        spike_time = ""
        if trend == "Spiking":
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            spike_time = f"{hour:02d}:{minute:02d}"
        
        # Generate comments for problematic metrics
        comments = ""
        if trend == "Spiking" or (unit == "%" and current_val > max_val * 0.8):
            comments = "Requires attention"
        elif category == "Reliability" and current_val < min_val + (max_val - min_val) * 0.3:
            comments = "Below threshold"
        
        widget = WidgetData(
            widget_name=name,
            category=category,
            min_value=min_str,
            max_value=max_str,
            current_value=current_str,
            trend=trend,
            spike_time=spike_time,
            comments=comments,
            raw_ocr_text=f"{name} {current_str} {trend}",
            extracted_at=(datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
        )
        
        widgets.append(widget)
    
    return widgets

def create_custom_analysis_prompt() -> str:
    """
    Create a custom prompt tailored for comprehensive Grafana analysis
    """
    return """
You are a Senior DevOps Engineer and Infrastructure Monitoring Expert with 10+ years of experience in:
- Large-scale system monitoring and observability
- Grafana dashboard analysis and optimization
- Performance troubleshooting and capacity planning
- Incident response and root cause analysis

Your task is to analyze monitoring data from a production Grafana dashboard and provide expert-level insights.

ANALYSIS REQUIREMENTS:
1. **Critical Issue Detection**: Identify any metrics that indicate immediate problems
2. **Pattern Recognition**: Look for correlations between different metrics
3. **Capacity Planning**: Assess resource utilization trends
4. **Performance Optimization**: Suggest improvements based on current patterns
5. **Alert Strategy**: Recommend alerting thresholds and policies

OUTPUT FORMAT:
```markdown
# 🚨 Executive Summary
**Overall System Health**: [Excellent/Good/Fair/Poor/Critical]
**Priority Issues**: [Count]
**Immediate Actions Required**: [Yes/No]

# 📊 Metric Analysis Dashboard

## Infrastructure Health Matrix
| Component | Status | Current Load | Trend | Risk Level | Action Needed |
|-----------|--------|--------------|-------|------------|---------------|
| CPU | 🟢/🟡/🔴 | XX% | ↗️↘️➡️ | Low/Med/High | Details |
| Memory | 🟢/🟡/🔴 | XX% | ↗️↘️➡️ | Low/Med/High | Details |
| Storage | 🟢/🟡/🔴 | XX% | ↗️↘️➡️ | Low/Med/High | Details |
| Network | 🟢/🟡/🔴 | XX% | ↗️↘️➡️ | Low/Med/High | Details |

## Application Performance Analysis
### Response Time Breakdown
- **API Latency**: [Analysis]
- **Database Performance**: [Analysis]
- **Cache Efficiency**: [Analysis]

### Throughput & Reliability
- **Request Handling**: [Analysis]
- **Error Rates**: [Analysis]
- **Success Patterns**: [Analysis]

# ⚠️ Critical Issues Requiring Immediate Attention

## 🔴 Severity 1 (Fix within 1 hour)
- [List critical issues]

## 🟡 Severity 2 (Fix within 24 hours)
- [List warning issues]

## 🔵 Severity 3 (Plan for next week)
- [List optimization opportunities]

# 🔍 Deep Dive Analysis

## Resource Utilization Patterns
[Detailed analysis of resource usage patterns]

## Performance Bottlenecks
[Identification of performance constraints]

## Scalability Assessment
[Analysis of system's ability to handle growth]

# 🛠️ Recommended Actions

## Immediate (Next 1-4 hours)
1. [Urgent actions with specific commands/steps]
2. [Include monitoring commands to run]

## Short-term (Next 1-3 days)
1. [Preventive measures]
2. [Configuration optimizations]

## Medium-term (Next 1-2 weeks)
1. [Capacity planning actions]
2. [Infrastructure improvements]

## Long-term (Next 1-3 months)
1. [Strategic improvements]
2. [Architecture recommendations]

# 📈 Monitoring & Alerting Recommendations

## Suggested Alert Thresholds
```yaml
alerts:
  cpu_usage:
    warning: 70%
    critical: 85%
  memory_usage:
    warning: 80%
    critical: 90%
  response_time:
    warning: 500ms
    critical: 1000ms
```

## Dashboard Improvements
- [Specific suggestions for dashboard enhancements]

# 🎯 Key Performance Indicators

## Current Metrics Summary
- **System Availability**: XX.XX%
- **Average Response Time**: XXXms
- **Error Rate**: X.XX%
- **Resource Efficiency Score**: XX/100

## Trending Analysis
- **Performance Trend**: [Improving/Stable/Degrading]
- **Capacity Trend**: [Sufficient/Approaching Limits/Over Capacity]
- **Reliability Trend**: [Stable/Concerning/Critical]

# 💡 Expert Insights & Best Practices
[Professional recommendations based on industry experience]
```

ANALYSIS GUIDELINES:
- Use actual numbers from the provided metrics
- Consider normal operating ranges for each metric type
- Identify unusual patterns or correlations
- Provide specific, actionable recommendations
- Use appropriate urgency levels
- Consider business impact in your analysis
- Suggest monitoring improvements
"""

def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Demo LLM analysis for Grafana widgets")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--widget-count", type=int, default=37, help="Number of widgets to generate")
    parser.add_argument("--output-dir", default="./demo_reports", help="Output directory for reports")
    args = parser.parse_args()
    
    # Set up API key
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    # Create output directory
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🚀 Starting Grafana LLM Analysis Demo")
    print(f"📊 Generating {args.widget_count} sample widgets...")
    
    # Generate sample widgets
    widgets = generate_sample_widgets(args.widget_count)
    
    print(f"✅ Generated {len(widgets)} widgets")
    print("\n📋 Sample widgets:")
    for i, widget in enumerate(widgets[:5]):
        print(f"  {i+1}. {widget.widget_name}: {widget.current_value} ({widget.trend})")
    if len(widgets) > 5:
        print(f"  ... and {len(widgets) - 5} more")
    
    # Save widget data to JSON
    widget_data_file = os.path.join(output_dir, f"widget_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(widget_data_file, "w") as f:
        widget_dicts = []
        for widget in widgets:
            widget_dict = {
                "widget_name": widget.widget_name,
                "category": widget.category,
                "min_value": widget.min_value,
                "max_value": widget.max_value,
                "current_value": widget.current_value,
                "trend": widget.trend,
                "spike_time": widget.spike_time,
                "comments": widget.comments,
                "raw_ocr_text": widget.raw_ocr_text,
                "extracted_at": widget.extracted_at
            }
            widget_dicts.append(widget_dict)
        json.dump(widget_dicts, f, indent=2)
    
    print(f"💾 Saved widget data to: {widget_data_file}")
    
    # Test LLM analysis if API key is available
    if os.getenv("OPENAI_API_KEY"):
        print("\n🤖 Starting LLM analysis...")
        
        try:
            # Initialize LLM analyzer
            analyzer = GrafanaAnalysisLLM()
            
            # Perform analysis
            print("⏳ Analyzing widgets with GPT-4o...")
            analysis_result = analyzer.analyze_widgets(widgets)
            
            if analysis_result["success"]:
                print("✅ LLM analysis completed successfully!")
                
                # Generate report
                print("📝 Generating markdown report...")
                report_generator = MarkdownReportGenerator()
                report_data = report_generator.generate_report(analysis_result, widgets)
                
                # Save reports
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save markdown report
                md_file = os.path.join(output_dir, f"analysis_report_{timestamp}.md")
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(report_data["markdown"])
                
                # Save HTML report
                html_file = os.path.join(output_dir, f"analysis_report_{timestamp}.html")
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(report_data["html"])
                
                # Save analysis metadata
                meta_file = os.path.join(output_dir, f"analysis_metadata_{timestamp}.json")
                with open(meta_file, "w") as f:
                    json.dump({
                        "analysis_result": analysis_result,
                        "report_metadata": report_data["metadata"],
                        "widget_count": len(widgets),
                        "generated_at": timestamp
                    }, f, indent=2)
                
                print(f"📄 Reports saved:")
                print(f"  - Markdown: {md_file}")
                print(f"  - HTML: {html_file}")
                print(f"  - Metadata: {meta_file}")
                
                # Print summary
                print(f"\n📊 Analysis Summary:")
                print(f"  - Model Used: {analysis_result['analysis']['model_used']}")
                print(f"  - Tokens Used: {analysis_result['analysis']['tokens_used']}")
                print(f"  - Widgets Analyzed: {len(widgets)}")
                print(f"  - Report Summary: {report_data['summary']}")
                
            else:
                print(f"❌ LLM analysis failed: {analysis_result['error']}")
                
        except Exception as e:
            print(f"❌ Error during LLM analysis: {e}")
    
    else:
        print("\n⚠️ No OpenAI API key provided. Skipping LLM analysis.")
        print("   Use --api-key to enable LLM analysis")
    
    print("\n🏁 Demo completed!")
    print(f"📁 All files saved to: {output_dir}")

if __name__ == "__main__":
    main()
