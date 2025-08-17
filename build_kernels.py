#!/usr/bin/env python3
"""
Build script for the kernels React app for production deployment.
This script should be run before deploying to production.
"""

import os
import subprocess
import shutil
import json
import re
from pathlib import Path

def main():
    # Paths
    project_root = Path(__file__).parent
    frontend_dir = project_root.parent / "cube-kernels-2" / "frontend"
    build_dir = frontend_dir / "build"
    static_dir = project_root / "staticfiles" / "kernels"
    template_file = project_root / "cards" / "templates" / "cards" / "kernels.html"
    
    print("🚀 Building kernels React app for production...")
    
    # Step 1: Build the React app
    print("📦 Building React app...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        print("✅ React app built successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to build React app")
        return False
    
    # Step 2: Copy build files to Django static directory
    print("📁 Copying build files to Django static directory...")
    if static_dir.exists():
        shutil.rmtree(static_dir)
    static_dir.mkdir(parents=True)
    
    # Copy static files (CSS and JS) to the root of kernels directory
    build_static_dir = build_dir / "static"
    if build_static_dir.exists():
        shutil.copytree(build_static_dir, static_dir, dirs_exist_ok=True)
    
    # Copy other build files (index.html, manifest.json, etc.)
    for item in build_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, static_dir)
    
    print("✅ Files copied successfully")
    
    # Step 3: Update template with correct file names
    print("📝 Updating template with correct file names...")
    
    # Find the main JS file
    js_files = list((static_dir / "js").glob("main.*.js"))
    chunk_files = list((static_dir / "js").glob("*.chunk.js"))
    css_files = list((static_dir / "css").glob("main.*.css"))
    
    if not js_files:
        print("❌ Could not find main JS file")
        return False
    
    main_js = js_files[0].name
    chunk_js = chunk_files[0].name if chunk_files else None
    main_css = css_files[0].name if css_files else None
    
    print(f"Found files: {main_js}, {chunk_js}, {main_css}")
    
    # Read template
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Update JS file references
    template_content = re.sub(
        r'main\.[a-f0-9]+\.js',
        main_js,
        template_content
    )
    
    if chunk_js:
        template_content = re.sub(
            r'[0-9]+\.[a-f0-9]+\.chunk\.js',
            chunk_js,
            template_content
        )
    
    if main_css:
        template_content = re.sub(
            r'main\.[a-f0-9]+\.css',
            main_css,
            template_content
        )
    
    # Write updated template
    with open(template_file, 'w') as f:
        f.write(template_content)
    
    print("✅ Template updated successfully")
    
    # Step 4: Create a build info file
    build_info = {
        "main_js": main_js,
        "chunk_js": chunk_js,
        "main_css": main_css,
        "build_time": subprocess.check_output(["date"], text=True).strip()
    }
    
    with open(static_dir / "build_info.json", 'w') as f:
        json.dump(build_info, f, indent=2)
    
    print("🎉 Build complete! The kernels app is ready for production deployment.")
    print(f"📊 Build info: {build_info}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)