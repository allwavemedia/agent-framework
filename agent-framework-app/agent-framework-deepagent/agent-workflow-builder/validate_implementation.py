#!/usr/bin/env python3
"""
Validation script for Tasks 4-6 implementation.
Checks that all required components are in place.
"""
import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file_exists(file_path, description):
    """Check if a file exists."""
    if os.path.exists(file_path):
        print(f"{GREEN}✓{RESET} {description}: {file_path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {file_path} (NOT FOUND)")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists."""
    if os.path.isdir(dir_path):
        print(f"{GREEN}✓{RESET} {description}: {dir_path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {dir_path} (NOT FOUND)")
        return False

def count_test_functions(test_file):
    """Count test functions in a test file."""
    if not os.path.exists(test_file):
        return 0
    
    with open(test_file, 'r') as f:
        content = f.read()
        return content.count('def test_') + content.count('async def test_')

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Tasks 4-6 Implementation Validation{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    base_path = Path("/home/runner/work/agent-framework/agent-framework/agent-framework-app/agent-framework-deepagent/agent-workflow-builder")
    backend_path = base_path / "backend"
    
    all_checks_passed = True
    
    # Task 4: Context Providers & Memory
    print(f"\n{BLUE}Task 4: Context Providers & Memory{RESET}")
    print(f"{'-'*70}")
    
    task4_files = [
        (backend_path / "app/services/context_service.py", "Context Service"),
        (backend_path / "app/api/routes/context.py", "Context API Routes"),
        (backend_path / "tests/unit/test_context_provider.py", "Context Provider Tests"),
        (backend_path / "migrations/add_context_provider_models.sql", "Database Migration"),
    ]
    
    for file_path, description in task4_files:
        if not check_file_exists(str(file_path), description):
            all_checks_passed = False
    
    # Check test count
    test_file = backend_path / "tests/unit/test_context_provider.py"
    test_count = count_test_functions(str(test_file))
    if test_count >= 10:
        print(f"{GREEN}✓{RESET} Context Provider Tests: {test_count} test functions")
    else:
        print(f"{YELLOW}!{RESET} Context Provider Tests: Only {test_count} test functions (expected 10+)")
    
    # Task 5: Observability Integration
    print(f"\n{BLUE}Task 5: Observability Integration{RESET}")
    print(f"{'-'*70}")
    
    task5_files = [
        (backend_path / "app/services/observability_service.py", "Observability Service"),
        (backend_path / "app/api/routes/observability.py", "Observability API Routes"),
        (backend_path / "tests/unit/test_observability.py", "Observability Tests"),
    ]
    
    for file_path, description in task5_files:
        if not check_file_exists(str(file_path), description):
            all_checks_passed = False
    
    # Check test count
    test_file = backend_path / "tests/unit/test_observability.py"
    test_count = count_test_functions(str(test_file))
    if test_count >= 10:
        print(f"{GREEN}✓{RESET} Observability Tests: {test_count} test functions")
    else:
        print(f"{YELLOW}!{RESET} Observability Tests: Only {test_count} test functions (expected 10+)")
    
    # Task 6: WorkflowViz Integration
    print(f"\n{BLUE}Task 6: WorkflowViz Integration{RESET}")
    print(f"{'-'*70}")
    
    task6_files = [
        (backend_path / "app/workflows/workflow_visualizer.py", "Enhanced Workflow Visualizer"),
        (backend_path / "tests/unit/test_workflow_viz.py", "WorkflowViz Tests"),
    ]
    
    for file_path, description in task6_files:
        if not check_file_exists(str(file_path), description):
            all_checks_passed = False
    
    # Check test count
    test_file = backend_path / "tests/unit/test_workflow_viz.py"
    test_count = count_test_functions(str(test_file))
    if test_count >= 10:
        print(f"{GREEN}✓{RESET} WorkflowViz Tests: {test_count} test functions")
    else:
        print(f"{YELLOW}!{RESET} WorkflowViz Tests: Only {test_count} test functions (expected 10+)")
    
    # Check API Registration
    print(f"\n{BLUE}API Integration{RESET}")
    print(f"{'-'*70}")
    
    api_main = backend_path / "app/api/main.py"
    if os.path.exists(str(api_main)):
        with open(str(api_main), 'r') as f:
            content = f.read()
            
        if 'context' in content and 'observability' in content:
            print(f"{GREEN}✓{RESET} Routes registered in API: context, observability")
        else:
            print(f"{RED}✗{RESET} Routes not properly registered in API main")
            all_checks_passed = False
    else:
        print(f"{RED}✗{RESET} API main file not found")
        all_checks_passed = False
    
    # Documentation
    print(f"\n{BLUE}Documentation{RESET}")
    print(f"{'-'*70}")
    
    doc_files = [
        (base_path / "TASKS_4_6_IMPLEMENTATION.md", "Implementation Guide"),
        (backend_path / "migrations/README.md", "Migration Guide"),
    ]
    
    for file_path, description in doc_files:
        if not check_file_exists(str(file_path), description):
            all_checks_passed = False
    
    # Database Models
    print(f"\n{BLUE}Database Models{RESET}")
    print(f"{'-'*70}")
    
    models_file = backend_path / "app/models/models.py"
    if os.path.exists(str(models_file)):
        with open(str(models_file), 'r') as f:
            content = f.read()
        
        required_models = [
            'ConversationMemory',
            'ContextProviderConfig',
        ]
        
        for model in required_models:
            if model in content:
                print(f"{GREEN}✓{RESET} Model found: {model}")
            else:
                print(f"{RED}✗{RESET} Model not found: {model}")
                all_checks_passed = False
    else:
        print(f"{RED}✗{RESET} Models file not found")
        all_checks_passed = False
    
    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    if all_checks_passed:
        print(f"{GREEN}✓ All validation checks passed!{RESET}")
        print(f"\n{GREEN}Implementation Complete:{RESET}")
        print(f"  • Task 4: Context Providers & Memory ✓")
        print(f"  • Task 5: Observability Integration ✓")
        print(f"  • Task 6: WorkflowViz Integration ✓")
        return 0
    else:
        print(f"{YELLOW}⚠ Some checks failed. Please review the output above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
