#!/usr/bin/env python3
"""
🔧 Quick Setup Diagnostic
Helps you debug GitHub configuration issues
Run: python diagnose.py
"""

import sys
import requests
import json
import base64

def test_setup():
    """Test if GitHub is accessible with CLI args"""
    
    print("\n" + "="*60)
    print("  🔧 SSC Weekly Planner - Setup Diagnostic")
    print("="*60 + "\n")
    
    if len(sys.argv) < 3:
        print("Usage: python diagnose.py <github-token> <repo>\n")
        print("Example: python diagnose.py ghp_xxxx owner/repo\n")
        print("Arguments:")
        print("  <github-token>  - Your GitHub personal access token")
        print("  <repo>          - Repository in format: owner/repo\n")
        
        print("How to get a GitHub token:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Select ONLY 'repo' checkbox")
        print("  4. Copy the token\n")
        
        print("Example of running diagnostic:")
        print("  python diagnose.py ghp_abc123def456 myusername/mycodebase\n")
        sys.exit(1)
    
    token = sys.argv[1]
    repo = sys.argv[2]
    
    if not token.startswith("ghp_"):
        print("❌ Token doesn't start with 'ghp_'")
        print("   Make sure you copied the whole token\n")
        sys.exit(1)
    
    if "/" not in repo:
        print("❌ Repository must be in format: owner/repo")
        print("   Example: myusername/my-ssc-tracker\n")
        sys.exit(1)
    
    print(f"Token:      {token[:10]}...{token[-4:]}")
    print(f"Repository: {repo}\n")
    print("-" * 60)
    
    # Step 1: Test repo access
    print("\n1️⃣  Testing repository access...")
    
    url = f"https://api.github.com/repos/{repo}"
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 401:
            print("   ❌ Token is INVALID or EXPIRED")
            print("      Generate a new token and try again")
            sys.exit(1)
        
        if response.status_code == 404:
            print(f"   ❌ Repository NOT FOUND: {repo}")
            print("      Check:")
            print("      • Repo exists on GitHub")
            print("      • Repository name is correct")
            print("      • You have access to it")
            sys.exit(1)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Repository found")
            print(f"     • Name: {data['full_name']}")
            print(f"     • Branch: {data['default_branch']}")
            print(f"     • Private: {'Yes' if data['private'] else 'No'}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            sys.exit(1)
    
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        sys.exit(1)
    
    # Step 2: Test data files
    print("\n2️⃣  Testing data files...")
    
    files_ok = True
    
    for file_name in ["gk_data.json", "maths_data.json"]:
        url = f"https://api.github.com/repos/{repo}/contents/{file_name}?ref=main"
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                try:
                    content = response.json()["content"]
                    decoded = base64.b64decode(content).decode('utf-8')
                    data = json.loads(decoded)
                    
                    print(f"\n   ✓ {file_name}")
                    print(f"     • Status: Found")
                    print(f"     • Valid JSON: Yes")
                    
                    # Show sample keys
                    if isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        print(f"     • Keys: {', '.join(keys)}")
                
                except json.JSONDecodeError as e:
                    print(f"\n   ❌ {file_name}")
                    print(f"     • Status: Found")
                    print(f"     • Valid JSON: NO ❌")
                    print(f"     • Error: {str(e)}")
                    files_ok = False
                
                except Exception as e:
                    print(f"\n   ❌ {file_name}")
                    print(f"     • Error: {str(e)}")
                    files_ok = False
            
            elif response.status_code == 404:
                print(f"\n   ❌ {file_name}")
                print(f"     • Status: NOT FOUND")
                print(f"     • Action: Add file to repo root")
                files_ok = False
            
            else:
                print(f"\n   ❌ {file_name}")
                print(f"     • Error: {response.status_code}")
                files_ok = False
        
        except Exception as e:
            print(f"\n   ❌ {file_name}")
            print(f"     • Error: {str(e)}")
            files_ok = False
    
    # Summary
    print("\n" + "-" * 60)
    
    if files_ok:
        print("\n✅ Setup is CORRECT!")
        print("\nNext steps:")
        print("  1. Run: streamlit run ssc_weekly_planner.py")
        print("  2. Click ⚙️ → Secrets")
        print(f"  3. Add:")
        print(f"     GITHUB_TOKEN = \"{token}\"")
        print(f"     GITHUB_REPO = \"{repo}\"")
        print("  4. Refresh page\n")
    else:
        print("\n❌ Setup has issues")
        print("\nCheck:")
        print("  • Both files exist in repo at root level")
        print("  • Files are committed to git")
        print("  • Files are valid JSON")
        print("  • Token has 'repo' scope\n")
    
    sys.exit(0 if files_ok else 1)

if __name__ == "__main__":
    test_setup()
