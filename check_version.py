#!/usr/bin/env python3
"""
Version checker - Check what methods are being called in install_manager.py
"""
import os
import sys

def check_install_manager():
    """Check the install_manager.py file for method calls"""
    install_manager_path = os.path.join(os.path.dirname(__file__), "install_manager.py")
    
    if not os.path.exists(install_manager_path):
        print("❌ install_manager.py not found!")
        return
    
    print(f"📁 Checking: {install_manager_path}")
    print("=" * 50)
    
    with open(install_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for old method calls
    old_methods = [
        "mark_step_failed",
        "mark_step_completed", 
        "mark_installation_completed"
    ]
    
    new_methods = [
        "fail_step",
        "complete_step",
        "complete_installation"
    ]
    
    print("🔍 Checking for old method calls:")
    found_old = False
    for method in old_methods:
        if method in content:
            print(f"❌ Found old method: {method}")
            found_old = True
    
    if not found_old:
        print("✅ No old method calls found")
    
    print("\n🔍 Checking for new method calls:")
    found_new = False
    for method in new_methods:
        if method in content:
            print(f"✅ Found new method: {method}")
            found_new = True
    
    if not found_new:
        print("❌ No new method calls found")
    
    print("\n📊 Summary:")
    if found_old and not found_new:
        print("❌ File contains OLD method calls - needs update!")
    elif not found_old and found_new:
        print("✅ File contains NEW method calls - should work!")
    elif found_old and found_new:
        print("⚠️ File contains MIXED method calls - needs cleanup!")
    else:
        print("❓ File contains NO step tracker calls - check manually")

if __name__ == "__main__":
    check_install_manager()

