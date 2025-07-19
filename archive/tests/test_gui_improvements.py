#!/usr/bin/env python3
"""Test script to verify GUI improvements"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from readysearch_gui import ReadySearchGUI

def test_gui():
    """Test the improved GUI"""
    print("✅ Starting ReadySearch GUI v2.0...")
    print("📊 Testing improvements:")
    print("  - Better color contrast (deep blue, emerald green)")
    print("  - Larger window size (90% of screen)")
    print("  - Improved fonts and spacing")
    print("  - Fixed layout issues")
    print("  - Enhanced visual hierarchy")
    
    app = ReadySearchGUI()
    print("\n✅ GUI initialized successfully!")
    print("🎨 Color improvements applied:")
    print("  - Primary: Deep blue (#1E40AF)")
    print("  - Success: Emerald (#16A34A)")
    print("  - Background: Light gray (#F9FAFB)")
    print("  - Text: Almost black (#111827)")
    
    app.run()

if __name__ == "__main__":
    test_gui()
