import openai
import json
import os
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv
import markdown
from jinja2 import Template

# Load environment variables
load_dotenv()

@dataclass
class WidgetData:
    widget_name: str
    category: str
    min_value: str
    max_value: str
    current_value: str
    trend: str
    spike_time: str
    comments: str
    raw_ocr_text: str = ""
    extracted_at: str = ""

class GrafanaAnalysisLLM:
    """
    LLM-powered analysis engine for Grafana widget data
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o"  # Using GPT-4o for better analysis
        
    def create_analysis_prompt(self, widgets_data: List[WidgetData]) -> str:
        """
        Create a comprehensive analysis prompt for LLM
        """
        
        # Convert widget data to JSON for the prompt
        widgets_json = []
        for widget in widgets_data:
            widgets_json.append({
                "widget_name": widget.widget_name,
                "category": widget.category,
                "min": widget.min_value,
                "max": widget.max_value,
                "current": widget.current_value,
                "trend": widget.trend,
                "spike_time": widget.spike_time,
                "comments": widget.comments,
                "raw_text": widget.raw_ocr_text
            })
        
        system_prompt = """
You are an expert DevOps and Infrastructure Monitoring Analyst with deep expertise in Grafana, system performance monitoring, and incident analysis. You have been asked to analyze monitoring widget data extracted from Grafana screenshots.

Your task is to:
1. Analyze each widget's performance metrics and trends
2. Identify potential issues, anomalies, and patterns
3. Provide actionable recommendations
4. Generate a comprehensive markdown report

Please provide analysis in the following format:

## 📊 Widget Analysis Summary

### Per-Widget Analysis Table
| Widget Name | Category | Current Value | Min/Max | Trend | Status | Key Observations |
|-------------|----------|---------------|---------|-------|--------|------------------|
| [Fill for each widget] | | | | | | |

## 🔍 Detailed Analysis

### Infrastructure Widgets
[Analyze infrastructure-related widgets]

### System Widgets  
[Analyze system-related widgets]

## ⚠️ Critical Issues & Alerts
[List any critical issues that need immediate attention]

## 🛠️ Recommendations

### Immediate Actions (< 1 hour)
- [List urgent actions]

### Short-term Actions (< 24 hours)
- [List short-term improvements]

### Long-term Optimizations (< 1 week)
- [List strategic improvements]

## 📈 Performance Insights
[Provide insights about overall system health and performance patterns]

## 🎯 Key Metrics Summary
- **Total Widgets Analyzed**: X
- **Widgets with Issues**: X
- **Critical Alerts**: X
- **Performance Score**: X/10

Analysis Guidelines:
- Focus on actionable insights
- Identify correlations between metrics
- Consider normal vs abnormal ranges for each metric type
- Provide context-aware recommendations
- Use appropriate monitoring terminology
- Include severity levels (Critical, Warning, Info)
"""

        user_prompt = f"""
Please analyze the following Grafana monitoring data:

```json
{json.dumps(widgets_json, indent=2)}
```

Consider:
- CPU usage patterns and thresholds
- Memory utilization and trends  
- Disk I/O performance
- Network traffic patterns
- Response time analysis
- Error rates and anomalies
- Time correlations between metrics
- Resource bottlenecks
- Capacity planning implications

Generate a comprehensive markdown report following the specified format.
"""

        return system_prompt, user_prompt
    
    def analyze_widgets(self, widgets_data: List[WidgetData]) -> Dict[str, Any]:
        """
        Analyze widgets using LLM and return structured results
        """
        try:
            # Create the analysis prompt
            system_prompt, user_prompt = self.create_analysis_prompt(widgets_data)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=4000,
                timeout=60
            )
            
            # Extract the markdown response
            analysis_markdown = response.choices[0].message.content
            
            # Parse the response to extract structured data
            structured_analysis = self._parse_analysis_response(analysis_markdown)
            
            return {
                "success": True,
                "analysis": {
                    "raw_markdown": analysis_markdown,
                    "structured_data": structured_analysis,
                    "model_used": self.model,
                    "analyzed_at": datetime.now().isoformat(),
                    "widget_count": len(widgets_data),
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def _parse_analysis_response(self, markdown_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract structured data
        """
        try:
            structured = {
                "summary": {},
                "issues": [],
                "recommendations": {
                    "immediate": [],
                    "short_term": [],
                    "long_term": []
                },
                "performance_score": None,
                "key_metrics": {}
            }
            
            lines = markdown_text.split('\n')
            current_section = None
            current_list = None
            
            for line in lines:
                line = line.strip()
                
                # Extract performance score
                if "Performance Score" in line and "/10" in line:
                    import re
                    score_match = re.search(r'(\d+(?:\.\d+)?)/10', line)
                    if score_match:
                        structured["performance_score"] = float(score_match.group(1))
                
                # Extract sections
                if line.startswith("## ⚠️ Critical Issues"):
                    current_section = "issues"
                elif line.startswith("### Immediate Actions"):
                    current_section = "immediate"
                elif line.startswith("### Short-term Actions"):
                    current_section = "short_term"
                elif line.startswith("### Long-term Optimizations"):
                    current_section = "long_term"
                elif line.startswith("- ") and current_section:
                    item = line[2:].strip()
                    if current_section == "issues":
                        structured["issues"].append(item)
                    elif current_section in ["immediate", "short_term", "long_term"]:
                        structured["recommendations"][current_section].append(item)
            
            return structured
            
        except Exception as e:
            return {"parse_error": str(e)}

class MarkdownReportGenerator:
    """
    Generate formatted markdown reports from analysis results
    """
    
    def __init__(self):
        self.report_template = """
# 📊 Grafana Monitoring Analysis Report

**Generated:** {{ timestamp }}  
**Widgets Analyzed:** {{ widget_count }}  
**Analysis Model:** {{ model_used }}  

---

{{ analysis_content }}

---

## 📋 Technical Details

**Analysis Parameters:**
- OCR Confidence Threshold: > 30%
- Model Used: {{ model_used }}
- Tokens Consumed: {{ tokens_used }}
- Processing Time: {{ processing_time }}

**Data Sources:**
- Infrastructure Screenshots: ✅
- System Screenshots: ✅  
- Date Range: {{ date_range }}

## 🔗 Next Steps

1. **Review Critical Issues** - Address any items marked as urgent
2. **Implement Recommendations** - Follow the prioritized action plan
3. **Monitor Progress** - Track metrics improvement over time
4. **Schedule Follow-up** - Plan next analysis cycle

---
*Report generated by Grafana Screenshot Analysis System*
"""
    
    def generate_report(self, analysis_result: Dict[str, Any], widgets_data: List[WidgetData]) -> Dict[str, str]:
        """
        Generate formatted markdown report
        """
        try:
            # Calculate processing metrics
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            widget_count = len(widgets_data)
            
            # Extract date range from widgets
            dates = [w.extracted_at for w in widgets_data if w.extracted_at]
            date_range = f"{min(dates) if dates else 'N/A'} to {max(dates) if dates else 'N/A'}"
            
            # Prepare template variables
            template_vars = {
                "timestamp": timestamp,
                "widget_count": widget_count,
                "model_used": analysis_result.get("analysis", {}).get("model_used", "GPT-4o"),
                "tokens_used": analysis_result.get("analysis", {}).get("tokens_used", 0),
                "processing_time": "< 60s",
                "date_range": date_range,
                "analysis_content": analysis_result.get("analysis", {}).get("raw_markdown", "No analysis available")
            }
            
            # Render the template
            template = Template(self.report_template)
            full_report = template.render(**template_vars)
            
            # Generate HTML version
            html_report = markdown.markdown(full_report, extensions=['tables', 'fenced_code'])
            
            return {
                "markdown": full_report,
                "html": html_report,
                "summary": self._extract_summary(analysis_result),
                "metadata": {
                    "generated_at": timestamp,
                    "widget_count": widget_count,
                    "model_used": template_vars["model_used"],
                    "tokens_used": template_vars["tokens_used"]
                }
            }
            
        except Exception as e:
            return {
                "markdown": f"# Error Generating Report\n\nError: {str(e)}",
                "html": f"<h1>Error Generating Report</h1><p>Error: {str(e)}</p>",
                "summary": f"Report generation failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _extract_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        Extract a brief summary from the analysis
        """
        try:
            structured = analysis_result.get("analysis", {}).get("structured_data", {})
            
            summary_parts = []
            
            # Performance score
            score = structured.get("performance_score")
            if score:
                summary_parts.append(f"Performance Score: {score}/10")
            
            # Issues count
            issues = structured.get("issues", [])
            if issues:
                summary_parts.append(f"Critical Issues: {len(issues)}")
            
            # Recommendations count
            recommendations = structured.get("recommendations", {})
            total_recs = sum(len(recs) for recs in recommendations.values())
            if total_recs:
                summary_parts.append(f"Recommendations: {total_recs}")
            
            return " | ".join(summary_parts) if summary_parts else "Analysis completed"
            
        except Exception:
            return "Summary extraction failed"

# Test function
def test_llm_analysis():
    """
    Test function for LLM analysis
    """
    # Sample widget data for testing
    test_widgets = [
        WidgetData(
            widget_name="CPU Usage",
            category="Infrastructure", 
            min_value="12%",
            max_value="98%",
            current_value="75%",
            trend="Spiking",
            spike_time="11:05 AM",
            comments="",
            raw_ocr_text="CPU Usage 75% spike detected at 11:05 AM"
        ),
        WidgetData(
            widget_name="Memory Usage",
            category="System",
            min_value="2.1 GB", 
            max_value="7.8 GB",
            current_value="6.2 GB",
            trend="Rising",
            spike_time="",
            comments="",
            raw_ocr_text="Memory Usage 6.2 GB rising trend"
        )
    ]
    
    try:
        # Test without API key (will fail gracefully)
        analyzer = GrafanaAnalysisLLM()
        print("LLM Analyzer initialized")
        
        # Test prompt generation
        system_prompt, user_prompt = analyzer.create_analysis_prompt(test_widgets)
        print(f"Generated prompts - System: {len(system_prompt)} chars, User: {len(user_prompt)} chars")
        
        # Test report generator
        report_gen = MarkdownReportGenerator()
        print("Report generator initialized")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_llm_analysis()
