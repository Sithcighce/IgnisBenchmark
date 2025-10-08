#!/usr/bin/env python3
"""
Clean Output Files Script
Removes temporary and output files from the root directory
"""

import os
import sys
from pathlib import Path

def clean_root_directory():
    """Clean temporary and output files from root directory"""
    project_root = Path(__file__).parent.parent
    
    # Files to clean from root directory
    files_to_clean = [
        'question_browser.html',
        'complete_question_browser.html', 
        'visualization_dashboard.png',
        'data_analysis_report.md',
        '*.png',
        '*.html',
        '*.log'
    ]
    
    print("🧹 Cleaning root directory...")
    print("=" * 50)
    
    cleaned_count = 0
    
    for pattern in files_to_clean:
        if '*' in pattern:
            # Handle wildcard patterns
            extension = pattern.split('*')[1]
            for file_path in project_root.glob(f"*{extension}"):
                if file_path.is_file() and file_path.name not in ['README.md', 'README_ZH.md']:
                    try:
                        file_path.unlink()
                        print(f"✅ Removed: {file_path.name}")
                        cleaned_count += 1
                    except Exception as e:
                        print(f"❌ Failed to remove {file_path.name}: {e}")
        else:
            # Handle specific files
            file_path = project_root / pattern
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"✅ Removed: {pattern}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {pattern}: {e}")
    
    print("=" * 50)
    print(f"🎉 Cleanup complete! Removed {cleaned_count} files.")
    print("📁 Root directory is now clean.")

def main():
    clean_root_directory()

if __name__ == "__main__":
    main()