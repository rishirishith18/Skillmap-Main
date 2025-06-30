#!/usr/bin/env python3
"""
Fix navigation paths to use relative paths that work with any web server
"""

import os
import re
from pathlib import Path

def fix_html_file(file_path, depth=0):
    """Fix paths in a single HTML file based on its depth in the directory structure"""
    print(f"Fixing {file_path} (depth: {depth})...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Calculate relative path prefixes based on depth
    if depth == 0:  # frontend/index.html
        prefix = ""
    elif depth == 1:  # frontend/pages/api-test.html
        prefix = "../"
    elif depth == 2:  # frontend/pages/candidate/*, frontend/pages/recruiter/*, frontend/pages/voice/*
        prefix = "../../"
    
    # Fix navigation links
    replacements = {
        # Home page links
        'href="/index.html"': f'href="{prefix}index.html"',
        
        # Candidate page links
        'href="/pages/candidate/signup.html"': f'href="{prefix}pages/candidate/signup.html"',
        'href="/pages/candidate/register.html"': f'href="{prefix}pages/candidate/register.html"',
        'href="/pages/candidate/login.html"': f'href="{prefix}pages/candidate/login.html"',
        'href="/pages/candidate/dashboard.html"': f'href="{prefix}pages/candidate/dashboard.html"',
        
        # Recruiter page links
        'href="/pages/recruiter/login.html"': f'href="{prefix}pages/recruiter/login.html"',
        'href="/pages/recruiter/register.html"': f'href="{prefix}pages/recruiter/register.html"',
        'href="/pages/recruiter/dashboard.html"': f'href="{prefix}pages/recruiter/dashboard.html"',
        
        # Voice page links
        'href="/pages/voice/challenge.html"': f'href="{prefix}pages/voice/challenge.html"',
        'href="/pages/voice/results.html"': f'href="{prefix}pages/voice/results.html"',
        
        # JavaScript redirects
        "window.location.href='/pages/candidate/register.html'": f"window.location.href='{prefix}pages/candidate/register.html'",
        "window.location.href='/pages/candidate/login.html'": f"window.location.href='{prefix}pages/candidate/login.html'",
        "window.location.href='/pages/candidate/dashboard.html'": f"window.location.href='{prefix}pages/candidate/dashboard.html'",
        "window.location.href='/pages/recruiter/login.html'": f"window.location.href='{prefix}pages/recruiter/login.html'",
        "window.location.href='/pages/recruiter/register.html'": f"window.location.href='{prefix}pages/recruiter/register.html'",
        "window.location.href='/pages/recruiter/dashboard.html'": f"window.location.href='{prefix}pages/recruiter/dashboard.html'",
        "window.location.href='/pages/voice/challenge.html'": f"window.location.href='{prefix}pages/voice/challenge.html'",
        "window.location.href='/pages/voice/results.html'": f"window.location.href='{prefix}pages/voice/results.html'",
    }
    
    # Apply replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {file_path}")

def main():
    """Main function to fix all HTML files"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return
    
    print("🔧 Fixing navigation paths to use relative paths...")
    print("=" * 50)
    
    # Define files and their depths
    files_to_fix = [
        ("frontend/index.html", 0),
        ("frontend/pages/api-test.html", 1),
        ("frontend/pages/candidate/signup.html", 2),
        ("frontend/pages/candidate/register.html", 2),
        ("frontend/pages/candidate/login.html", 2),
        ("frontend/pages/candidate/dashboard.html", 2),
        ("frontend/pages/recruiter/login.html", 2),
        ("frontend/pages/recruiter/register.html", 2),
        ("frontend/pages/recruiter/dashboard.html", 2),
        ("frontend/pages/voice/challenge.html", 2),
        ("frontend/pages/voice/results.html", 2),
    ]
    
    for file_path, depth in files_to_fix:
        if os.path.exists(file_path):
            fix_html_file(file_path, depth)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 50)
    print("🎉 All navigation paths fixed!")
    print("✅ Now using relative paths that work with any web server")
    print(f"🌐 Try: http://localhost:3000/index.html")
    print(f"🌐  Or: http://localhost:8080/index.html")

if __name__ == "__main__":
    main() 