#!/usr/bin/env python3
"""
SSC Weekly Planner - Setup Verification Script

Run this script to verify your configuration is correct before running the dashboard.
"""

import sys
import os
import json
from pathlib import Path
from typing import Tuple, Dict
import requests
import base64

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    print_header("1. Checking Python Version")
    
    version = sys.version_info
    min_version = (3, 8)
    
    if version >= min_version:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (required: >= 3.8)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} is too old (required: >= 3.8)")
        return False

def check_dependencies() -> bool:
    """Check if required packages are installed"""
    print_header("2. Checking Required Packages")
    
    required = ['streamlit', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            missing.append(package)
    
    if missing:
        print_warning(f"\nInstall missing packages with:")
        print_info(f"pip install {' '.join(missing)}")
        return False
    return True

def check_secrets_file() -> Tuple[bool, Dict]:
    """Check if secrets are properly configured"""
    print_header("3. Checking Secrets Configuration")
    
    secrets = {}
    secrets_path = Path(".streamlit/secrets.toml")
    
    if secrets_path.exists():
        print_info(f"Local secrets file found: {secrets_path}")
        
        # Parse TOML manually (simple parsing)
        try:
            with open(secrets_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if value and not value.startswith('your_'):
                            secrets[key] = value
        except Exception as e:
            print_warning(f"Could not parse secrets.toml: {e}")
    else:
        print_info("No local secrets file (will use Streamlit UI)")
    
    required_keys = ['GITHUB_TOKEN', 'GITHUB_REPO']
    missing_keys = [k for k in required_keys if k not in secrets]
    
    if missing_keys:
        print_warning(f"Missing: {', '.join(missing_keys)}")
        print_info("""
You can configure secrets two ways:
1. Via Streamlit UI: Click ⚙️ → Secrets (recommended)
2. Via .streamlit/secrets.toml file (local only)

To add via UI:
1. Run: streamlit run ssc_weekly_planner.py
2. Click ⚙️ (settings) → Secrets
3. Add GITHUB_TOKEN and GITHUB_REPO
4. Refresh the page
        """)
        
        if secrets:
            print_success(f"Found {len(secrets)} secret(s) in local file")
        
        return len(secrets) >= 2, secrets
    
    # Validate token format
    if 'GITHUB_TOKEN' in secrets and not secrets['GITHUB_TOKEN'].startswith('ghp_'):
        print_warning("GITHUB_TOKEN doesn't start with 'ghp_' (may be invalid)")
    
    if 'GITHUB_TOKEN' in secrets:
        print_success("GitHub token format looks valid")
    
    # Validate repo format
    if 'GITHUB_REPO' in secrets:
        if '/' not in secrets['GITHUB_REPO']:
            print_error("GITHUB_REPO must be in format: 'owner/repo'")
            return False, secrets
        print_success("GitHub repo format is valid")
        print_info(f"Repository: {secrets['GITHUB_REPO']}")
    
    return True, secrets

def test_github_connection(secrets: Dict) -> bool:
    """Test connection to GitHub API"""
    print_header("4. Testing GitHub API Connection")
    
    if not secrets:
        print_warning("Skipping GitHub test (no secrets loaded)")
        return False
    
    token = secrets.get('GITHUB_TOKEN')
    repo = secrets.get('GITHUB_REPO')
    branch = secrets.get('GITHUB_BRANCH', 'main')
    
    if not token or not repo:
        print_error("Missing GitHub credentials")
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {"Authorization": f"token {token}"}
        
        print_info(f"Testing connection to: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print_success("Successfully connected to GitHub API")
            repo_data = response.json()
            print_info(f"Repository: {repo_data['full_name']}")
            print_info(f"Default branch: {repo_data['default_branch']}")
            return True
        
        elif response.status_code == 401:
            print_error("GitHub token is invalid or expired")
            return False
        
        elif response.status_code == 404:
            print_error(f"Repository not found: {repo}")
            print_warning("Verify: 1) Repository exists 2) You have access 3) GITHUB_REPO is correct")
            return False
        
        else:
            print_error(f"GitHub API error: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print_error("Connection timeout - check your internet connection")
        return False
    
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def test_data_files(secrets: Dict) -> bool:
    """Test if data files can be fetched from GitHub"""
    print_header("5. Testing Data File Access")
    
    if not secrets:
        print_warning("Skipping data file test (no secrets loaded)")
        return False
    
    token = secrets.get('GITHUB_TOKEN')
    repo = secrets.get('GITHUB_REPO')
    branch = secrets.get('GITHUB_BRANCH', 'main')
    files = ['gk_data.json', 'maths_data.json']
    
    all_found = True
    headers = {"Authorization": f"token {token}"}
    
    for file in files:
        try:
            url = f"https://api.github.com/repos/{repo}/contents/{file}?ref={branch}"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print_success(f"Found {file}")
                
                # Try to decode and parse
                try:
                    content = response.json()["content"]
                    decoded = base64.b64decode(content).decode('utf-8')
                    json.loads(decoded)
                    print_info(f"  ✓ File is valid JSON")
                except json.JSONDecodeError as e:
                    print_error(f"  ✗ Invalid JSON in {file}: {e}")
                    all_found = False
                except Exception as e:
                    print_error(f"  ✗ Error parsing {file}: {e}")
                    all_found = False
            
            elif response.status_code == 404:
                print_error(f"Not found: {file}")
                print_warning(f"  Make sure '{file}' exists in {repo} at branch '{branch}'")
                all_found = False
            
            else:
                print_error(f"Error accessing {file}: {response.status_code}")
                all_found = False
        
        except Exception as e:
            print_error(f"Failed to fetch {file}: {e}")
            all_found = False
    
    return all_found

def check_data_files_exist() -> bool:
    """Check if example data files exist locally"""
    print_header("6. Checking Example Data Files")
    
    files = ['example_gk_data.json', 'example_maths_data.json']
    all_exist = True
    
    for file in files:
        path = Path(file)
        if path.exists():
            print_success(f"Found {file}")
            try:
                with open(path) as f:
                    json.load(f)
                print_info(f"  ✓ Valid JSON")
            except json.JSONDecodeError as e:
                print_error(f"  ✗ Invalid JSON: {e}")
                all_exist = False
        else:
            print_warning(f"Not found locally: {file} (optional)")
    
    return all_exist

def print_summary(results: Dict[str, bool]):
    """Print summary of all checks"""
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    checks = [
        ("Python Version", "python"),
        ("Required Packages", "packages"),
        ("Secrets Configuration", "secrets"),
        ("GitHub Connection", "github"),
        ("Data Files", "data"),
        ("Example Files", "examples"),
    ]
    
    for name, key in checks:
        if key in results:
            status = "✓ PASS" if results[key] else "✗ FAIL"
            color = Colors.GREEN if results[key] else Colors.RED
            print(f"{color}{status}{Colors.RESET}  {name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.RESET}")
    
    if passed == total:
        print_success("All checks passed! You're ready to run the dashboard.")
        print_info("Run: streamlit run ssc_weekly_planner.py")
        return True
    else:
        print_warning("Please fix the failed checks before running the dashboard.")
        return False

def main():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   SSC Weekly Planner - Setup Verification Tool            ║")
    print("║   This tool will verify your configuration is correct      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    results = {}
    
    # Run checks
    results['python'] = check_python_version()
    results['packages'] = check_dependencies()
    
    secrets_ok, secrets = check_secrets_file()
    results['secrets'] = secrets_ok
    
    results['github'] = test_github_connection(secrets) if secrets_ok else False
    results['data'] = test_data_files(secrets) if secrets_ok else False
    results['examples'] = check_data_files_exist()
    
    # Print summary
    success = print_summary(results)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
