#!/usr/bin/env python3
"""
Test runner script for ollama_stat_model unit tests.
Usage: python run_tests.py
"""
import subprocess
import sys
import os

def main():
    """Run the test suite."""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("Running unit tests for ollama_stat_model...")
    print("=" * 50)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], check=True)
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements-test.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())