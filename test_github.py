#!/usr/bin/env python3
"""
Quick GitHub Connection Test
Tests if your GitHub token and repo are configured correctly
"""

import sys
import os

# Check for streamlit installed
try:
    import streamlit as st
    secrets = dict(st.secrets)
except:
    print("❌ Streamlit not installed. Run: pip install streamlit requests")
    sys.exit(1)

# Quick test
print("🔍 Testing GitHub Connection...")
print()

# Check secrets
if "GITHUB_TOKEN" not in secrets:
    print("❌ GITHUB_TOKEN not found in secrets")
    print("   → Click ⚙️ → Secrets in Streamlit UI to add it")
    sys.exit(1)

if "GITHUB_REPO" not in secrets:
    print("❌ GITHUB_REPO not found in secrets")
    print("   → Click ⚙️ → Secrets in Streamlit UI to add it")
    sys.exit(1)

print("✓ Secrets loaded")

# Test GitHub API
import requests
import json
import base64

token = secrets["GITHUB_TOKEN"]
repo = secrets["GITHUB_REPO"]

print(f"✓ Testing repo: {repo}")

url = f"https://api.github.com/repos/{repo}"
headers = {"Authorization": f"token {token}"}

try:
    print("  → Connecting to GitHub API...")
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 401:
        print("❌ Token is invalid or expired")
        sys.exit(1)
    
    if response.status_code == 404:
        print(f"❌ Repository not found: {repo}")
        sys.exit(1)
    
    if response.status_code == 200:
        print("✓ Repository found")
        repo_data = response.json()
        print(f"  → Name: {repo_data['full_name']}")
        print(f"  → Branch: {repo_data['default_branch']}")
    else:
        print(f"❌ Error: {response.status_code}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print("❌ Connection timeout (check internet)")
    sys.exit(1)

except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Test data files
print()
print("✓ Testing data files...")

for file_name in ["gk_data.json", "maths_data.json"]:
    url = f"https://api.github.com/repos/{repo}/contents/{file_name}?ref=main"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✓ Found {file_name}")
            
            # Decode and validate JSON
            try:
                content = response.json()["content"]
                decoded = base64.b64decode(content).decode('utf-8')
                json.loads(decoded)
                print(f"    ✓ Valid JSON")
            except json.JSONDecodeError:
                print(f"    ❌ Invalid JSON in {file_name}")
                sys.exit(1)
        
        elif response.status_code == 404:
            print(f"  ❌ Not found: {file_name}")
            print(f"     → Add {file_name} to {repo}")
            sys.exit(1)
        
        else:
            print(f"  ❌ Error: {response.status_code}")
            sys.exit(1)
    
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout fetching {file_name}")
        sys.exit(1)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)

print()
print("✅ All checks passed!")
print("   → Run: streamlit run ssc_weekly_planner.py")
