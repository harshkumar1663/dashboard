#!/usr/bin/env python3
"""
Quick GitHub Connection Test
Tests if your GitHub token and repo are configured correctly
Run this: python test_github.py
"""

import sys
import os

print("🔍 Testing GitHub Connection...")
print()

# Check for secrets file
try:
    with open(".streamlit/secrets.toml") as f:
        content = f.read()
        if "GITHUB_TOKEN" not in content:
            print("❌ GITHUB_TOKEN not in .streamlit/secrets.toml")
        else:
            print("✓ GITHUB_TOKEN found in secrets file")
        
        if "GITHUB_REPO" not in content:
            print("❌ GITHUB_REPO not in .streamlit/secrets.toml")
        else:
            print("✓ GITHUB_REPO found in secrets file")
except FileNotFoundError:
    print("⚠️  No .streamlit/secrets.toml file (using Streamlit UI secrets)")

print()

# Check for streamlit installed
try:
    import streamlit as st
    print("✓ Streamlit is installed")
except:
    print("❌ Streamlit not installed")
    print("   Run: pip install streamlit requests")
    sys.exit(1)

# Try to read secrets
print()
print("🔐 Reading secrets from Streamlit...")

try:
    token = st.secrets.get("GITHUB_TOKEN")
    repo = st.secrets.get("GITHUB_REPO")
    
    if not token:
        print("❌ GITHUB_TOKEN not found in Streamlit secrets!")
        print("\n   How to add:")
        print("   1. Run: streamlit run ssc_weekly_planner.py")
        print("   2. Click ⚙️ (top-right) → Secrets")
        print("   3. Add: GITHUB_TOKEN = \"ghp_xxxx\"")
        sys.exit(1)
    
    if not repo:
        print("❌ GITHUB_REPO not found in Streamlit secrets!")
        print("\n   How to add:")
        print("   1. Run: streamlit run ssc_weekly_planner.py")
        print("   2. Click ⚙️ (top-right) → Secrets")
        print("   3. Add: GITHUB_REPO = \"owner/repo\"")
        sys.exit(1)
    
    print(f"✓ Token: {token[:10]}..." if len(token) > 10 else f"✓ Token: {token}")
    print(f"✓ Repo: {repo}")
    
except Exception as e:
    print(f"❌ Could not read secrets: {e}")
    sys.exit(1)

# Test GitHub API
print()
print("🌐 Testing GitHub API...")

import requests
import json
import base64

headers = {"Authorization": f"token {token}"}

# Test repo access
url = f"https://api.github.com/repos/{repo}"
print(f"\n  Testing: {url}")

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 401:
        print("  ❌ Token is INVALID or EXPIRED!")
        print("\n  Solution:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Create a new token (classic)")
        print("  3. Select 'repo' scope")
        print("  4. Copy the token")
        print("  5. Update Streamlit Secrets with new token")
        sys.exit(1)
    
    if response.status_code == 403:
        print("  ❌ Access DENIED!")
        print("     Token may not have 'repo' scope")
        sys.exit(1)
    
    if response.status_code == 404:
        print(f"  ❌ Repository NOT FOUND: {repo}")
        print("\n  Check:")
        print("  1. Repo exists and is accessible")
        print("  2. GITHUB_REPO format is: owner/repo")
        print("  3. You have access to the repo")
        sys.exit(1)
    
    if response.status_code == 200:
        print("  ✓ Repository found!")
        repo_data = response.json()
        print(f"    → Full name: {repo_data['full_name']}")
        print(f"    → Default branch: {repo_data['default_branch']}")
    else:
        print(f"  ❌ Unexpected error: {response.status_code}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print("  ❌ Connection TIMEOUT!")
    print("     Check your internet connection")
    sys.exit(1)

except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    sys.exit(1)

# Test data files
print()
print("📄 Testing data files...")

for file_name in ["gk_data.json", "maths_data.json"]:
    url = f"https://api.github.com/repos/{repo}/contents/{file_name}?ref=main"
    print(f"\n  Testing: {file_name}")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✓ Found {file_name}")
            
            # Decode and validate JSON
            try:
                content = response.json()["content"]
                decoded = base64.b64decode(content).decode('utf-8')
                data = json.loads(decoded)
                
                if file_name == "gk_data.json":
                    if "revisions" in data:
                        print(f"    ✓ Valid JSON with 'revisions'")
                        print(f"    ✓ Topics: {list(data['revisions'].keys())[:3]}...")
                    else:
                        print(f"    ⚠️  Valid JSON but missing 'revisions' key")
                
                elif file_name == "maths_data.json":
                    sections = []
                    if "chapters" in data:
                        sections.append("chapters")
                    if "reasoning" in data:
                        sections.append("reasoning")
                    print(f"    ✓ Valid JSON with: {', '.join(sections)}")
            
            except json.JSONDecodeError as e:
                print(f"  ❌ INVALID JSON: {str(e)}")
                sys.exit(1)
        
        elif response.status_code == 404:
            print(f"  ❌ NOT FOUND: {file_name}")
            print(f"\n  Solutions:")
            print(f"  1. Add {file_name} to {repo}")
            print(f"  2. Make sure file is at root level")
            print(f"  3. Commit and push to GitHub")
            print(f"\n  Example:")
            print(f"  $ git add {file_name}")
            print(f"  $ git commit -m 'Add {file_name}'")
            print(f"  $ git push")
            sys.exit(1)
        
        else:
            print(f"  ❌ Error: {response.status_code}")
            if response.status_code == 403:
                print("     Access denied (token scope issue?)")
            sys.exit(1)
    
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout")
        sys.exit(1)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print()
print("Your setup is correct. Run the app:")
print("  streamlit run ssc_weekly_planner.py")
print()
