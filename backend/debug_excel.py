#!/usr/bin/env python3
"""
Debug script to test Excel generation functionality
"""

import os
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from excel_export import ExcelReportGenerator, MarkdownTableParser
    print("✅ Successfully imported ExcelReportGenerator and MarkdownTableParser")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

def test_openpyxl():
    """Test if openpyxl is available"""
    try:
        import openpyxl
        print(f"✅ openpyxl is available: version {openpyxl.__version__}")
        return True
    except ImportError:
        print("❌ openpyxl is not available")
        return False

def test_pandas():
    """Test if pandas is available"""
    try:
        import pandas as pd
        print(f"✅ pandas is available: version {pd.__version__}")
        return True
    except ImportError:
        print("❌ pandas is not available")
        return False

def test_excel_generation():
    """Test Excel generation with sample data"""
    print("\n🧪 Testing Excel generation...")
    
    # Sample analysis result that mimics what comes from LLM
    sample_analysis = {
        "analysis": {
            "raw_markdown": """
# Grafana Dashboard Analysis Report

## Widget Analysis Table

| Widget Name | Category | Current Value | Min Value | Max Value | Trend | Status | Key Observations |
|-------------|----------|---------------|-----------|-----------|-------|--------|------------------|
| CPU Usage | System | 75% | 0% | 100% | Increasing | Warning | High CPU usage detected |
| Memory Usage | System | 60% | 0% | 100% | Stable | Normal | Memory usage within limits |
| Disk Space | Infrastructure | 85% | 0% | 100% | Increasing | Critical | Disk space running low |

## Summary Metrics

- **Total Widgets Analyzed**: 3
- **Critical Issues**: 1
- **Warnings**: 1
- **Normal Status**: 1
- **Overall Health Score**: 70%
"""
        }
    }
    
    # Sample widget data
    sample_widget_data = [
        {"widget_name": "CPU Usage", "category": "System", "status": "Warning"},
        {"widget_name": "Memory Usage", "category": "System", "status": "Normal"},
        {"widget_name": "Disk Space", "category": "Infrastructure", "status": "Critical"}
    ]
    
    try:
        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        print(f"📁 Reports directory: {reports_dir.absolute()}")
        
        # Initialize Excel generator
        excel_generator = ExcelReportGenerator(output_dir=str(reports_dir))
        print("✅ ExcelReportGenerator initialized")
        
        # Generate Excel report
        excel_file = excel_generator.generate_excel_report(sample_analysis, sample_widget_data)
        print(f"✅ Excel report generated: {excel_file}")
        
        # Check if file exists
        if os.path.exists(excel_file):
            file_size = os.path.getsize(excel_file)
            print(f"✅ Excel file exists with size: {file_size} bytes")
            
            # List all files in reports directory
            print(f"\n📋 Files in reports directory:")
            for file in reports_dir.iterdir():
                if file.is_file():
                    print(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            print(f"❌ Excel file not found at: {excel_file}")
            
    except Exception as e:
        print(f"❌ Excel generation failed: {e}")
        traceback.print_exc()

def test_markdown_parser():
    """Test markdown table parser"""
    print("\n🧪 Testing MarkdownTableParser...")
    
    sample_markdown = """
# Test Report

## Widget Analysis Table

| Widget Name | Category | Current Value | Min Value | Max Value | Trend | Status | Key Observations |
|-------------|----------|---------------|-----------|-----------|-------|--------|------------------|
| CPU Usage | System | 75% | 0% | 100% | Increasing | Warning | High CPU usage detected |
| Memory Usage | System | 60% | 0% | 100% | Stable | Normal | Memory usage within limits |

## Summary Metrics

- **Total Widgets**: 2
- **Critical Issues**: 0
- **Warnings**: 1
"""
    
    try:
        widget_rows = MarkdownTableParser.parse_widget_table(sample_markdown)
        print(f"✅ Parsed {len(widget_rows)} widget rows")
        for row in widget_rows:
            print(f"  - {row.widget_name}: {row.status}")
            
        summary_metrics = MarkdownTableParser.parse_summary_metrics(sample_markdown)
        print(f"✅ Parsed {len(summary_metrics)} summary metrics")
        for metric in summary_metrics:
            print(f"  - {metric['metric']}: {metric['value']}")
            
    except Exception as e:
        print(f"❌ Markdown parsing failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Excel Generation Debug Script")
    print("=" * 50)
    
    # Test dependencies
    openpyxl_ok = test_openpyxl()
    pandas_ok = test_pandas()
    
    if not (openpyxl_ok and pandas_ok):
        print("\n❌ Missing required dependencies. Please install them first.")
        sys.exit(1)
    
    # Test markdown parser
    test_markdown_parser()
    
    # Test Excel generation
    test_excel_generation()
    
    print("\n✅ Debug script completed!")
