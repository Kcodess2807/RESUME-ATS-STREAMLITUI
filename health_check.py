"""
Health check script to verify deployment readiness
Run this before deploying to catch common issues
"""

import sys
from pathlib import Path

def check_files():
    """Check that all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'packages.txt',
        'runtime.txt',
        'assets/styles.css',
        '.streamlit/config.toml',
        'app/__init__.py',
        'app/views/__init__.py',
        'app/views/landing.py',
        'app/views/scorer.py',
        'app/views/history.py',
        'app/views/resources.py',
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    return len(missing) == 0

def check_imports():
    """Check that imports work"""
    print("\n🔍 Checking imports...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Check core imports
        print("  Checking app.views...")
        from app.views import landing, scorer, history, resources
        print("  ✅ app.views imports successful")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def check_requirements():
    """Check requirements.txt format"""
    print("\n🔍 Checking requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # Check for common issues
                if ' ' in line and '==' not in line and '>=' not in line:
                    issues.append(f"Line {i}: Possible space in package name: {line}")
        
        if issues:
            for issue in issues:
                print(f"  ⚠️  {issue}")
            return False
        else:
            print("  ✅ requirements.txt looks good")
            return True
    except Exception as e:
        print(f"  ❌ Error reading requirements.txt: {e}")
        return False

def check_runtime():
    """Check runtime.txt"""
    print("\n🔍 Checking runtime.txt...")
    
    try:
        with open('runtime.txt', 'r') as f:
            version = f.read().strip()
        
        print(f"  Python version: {version}")
        
        if version.startswith('python-3.'):
            print("  ✅ Valid Python version")
            return True
        else:
            print("  ⚠️  Unusual Python version format")
            return False
    except Exception as e:
        print(f"  ❌ Error reading runtime.txt: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🏥 ATS Resume Scorer - Deployment Health Check")
    print("=" * 60)
    
    checks = [
        ("Files", check_files()),
        ("Imports", check_imports()),
        ("Requirements", check_requirements()),
        ("Runtime", check_runtime()),
    ]
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All checks passed! Ready to deploy.")
        return 0
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
