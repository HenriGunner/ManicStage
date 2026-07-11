#!/usr/bin/env python3
"""
Sony NW-S715F Database Repair Tool
Safely repairs corrupted database files without touching your music

HOW IT WORKS:
1. Checks each database file's "header" (like an ID card)
2. If corrupted, replaces ONLY that file with a clean template
3. Your music files (MP3/ATRAC) are NEVER touched
4. Creates backups before any changes

SAFETY FEATURES:
- Backs up all files before changes
- Only replaces files with invalid headers
- Won't run if device isn't properly connected
- Preserves all your music data
"""

import os
import sys
import shutil
from datetime import datetime

# Expected file signatures (first 4 bytes in hex as ASCII)
EXPECTED_SIGNATURES = {
    '00GTRLST.DAT': b'GTLT',  # Main track list
    '01TREE01.DAT': b'TREE',  # Tree structure
    '01TREE02.DAT': b'TREE',
    '01TREE03.DAT': b'TREE',
    '01TREE04.DAT': b'TREE',
    '01TREE22.DAT': b'TREE',
    '01TREE2D.DAT': b'TREE',
    '02TREINF.DAT': b'GTIF',  # Tree info
    '03GINF01.DAT': b'GPIF',  # Group info
    '03GINF02.DAT': b'GPIF',
    '03GINF03.DAT': b'GPIF',
    '03GINF04.DAT': b'GPIF',
    '03GINF22.DAT': b'GPIF',
    '03GINF2D.DAT': b'GPIF',
    '04CNTINF.DAT': b'CNIF',  # Content info
    '05CIDLST.DAT': b'CIDL',  # CID list
}

# Files that should exist but we don't check signature (like RESERVED.DAT)
REQUIRED_FILES = [
    '00GTRLST.DAT', '00010021.DAT',
    '01TREE01.DAT', '01TREE02.DAT', '01TREE03.DAT', 
    '01TREE04.DAT', '01TREE22.DAT', '01TREE2D.DAT',
    '02TREINF.DAT',
    '03GINF01.DAT', '03GINF02.DAT', '03GINF03.DAT',
    '03GINF04.DAT', '03GINF22.DAT', '03GINF2D.DAT',
    '04CNTINF.DAT', '05CIDLST.DAT', 'RESERVED.DAT'
]

def get_script_dir():
    """Get the directory where this script is located"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def find_walkman_drive():
    """Find the connected Sony Walkman drive"""
    # Common mount points for Sony Walkman
    possible_paths = []
    
    # Windows
    for drive in 'DEFGHIJKLMNOPQRSTUVWXYZ':
        path = f'{drive}:/'
        if os.path.exists(path):
            possible_paths.append((path, 'OMGAUDIO', 'NWWM'))
    
    # macOS
    macos_paths = ['/Volumes']
    for base in macos_paths:
        if os.path.exists(base):
            for item in os.listdir(base):
                item_path = os.path.join(base, item)
                if os.path.isdir(item_path):
                    possible_paths.append((item_path, 'OMGAUDIO', 'NWWM'))
    
    # Linux
    linux_paths = ['/media', '/mnt']
    for base in linux_paths:
        if os.path.exists(base):
            for user in os.listdir(base):
                user_path = os.path.join(base, user)
                if os.path.isdir(user_path):
                    possible_paths.append((user_path, 'OMGAUDIO', 'NWWM'))
    
    # Check which path has the OMGAUDIO folder
    for base, omg, nwwm in possible_paths:
        omg_path = os.path.join(base, omg)
        if os.path.exists(omg_path) and os.path.isdir(omg_path):
            # Verify it's a Sony device by checking for expected files
            test_file = os.path.join(omg_path, '00GTRLST.DAT')
            if os.path.exists(test_file) or len(os.listdir(omg_path)) > 0:
                return base
    
    return None

def check_file_signature(filepath, expected_sig):
    """Check if file has the correct signature"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)
            return header == expected_sig
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return False

def create_backup(walkman_base, timestamp):
    """Create backup of current database files"""
    backup_dir = os.path.join(get_script_dir(), f'backup_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    
    omg_src = os.path.join(walkman_base, 'OMGAUDIO')
    omg_backup = os.path.join(backup_dir, 'OMGAUDIO')
    os.makedirs(omg_backup, exist_ok=True)
    
    nwwm_src = os.path.join(walkman_base, 'NWWM')
    if os.path.exists(nwwm_src):
        nwwm_backup = os.path.join(backup_dir, 'NWWM')
        os.makedirs(nwwm_backup, exist_ok=True)
        shutil.copytree(nwwm_src, nwwm_backup, dirs_exist_ok=True)
    
    # Copy all DAT files
    for filename in os.listdir(omg_src):
        if filename.endswith('.DAT'):
            src = os.path.join(omg_src, filename)
            dst = os.path.join(omg_backup, filename)
            shutil.copy2(src, dst)
    
    return backup_dir

def get_template_files():
    """Get path to template files from the app bundle"""
    script_dir = get_script_dir()
    
    # Try common locations for templates
    template_locations = [
        os.path.join(script_dir, 'dmg_contents', 'ManicStage.app', 
                    'Contents', 'Resources', 'templates', 'empty_library'),
        os.path.join(script_dir, 'templates', 'empty_library'),
        os.path.join(script_dir, '..', 'dmg_contents', 'ManicStage.app',
                    'Contents', 'Resources', 'templates', 'empty_library'),
    ]
    
    for template_path in template_locations:
        omg_path = os.path.join(template_path, 'OMGAUDIO')
        if os.path.exists(omg_path):
            return template_path
    
    # If not found, try to extract from DMG or use embedded templates
    print("\n⚠️  Template files not found in expected location.")
    print("   Please ensure this script is in the same directory as the ManicStage extraction.")
    return None

def repair_database(walkman_base, template_path):
    """Repair corrupted database files"""
    omg_path = os.path.join(walkman_base, 'OMGAUDIO')
    template_omg = os.path.join(template_path, 'OMGAUDIO')
    
    repaired = []
    replaced = []
    errors = []
    
    print(f"\n📁 Checking database files in: {omg_path}")
    print("-" * 60)
    
    # Check each file with known signature
    for filename, expected_sig in EXPECTED_SIGNATURES.items():
        filepath = os.path.join(omg_path, filename)
        template_file = os.path.join(template_omg, filename)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  Missing: {filename}")
            if os.path.exists(template_file):
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                print(f"      ✓ Restored from template")
            else:
                errors.append(f"{filename} (missing, no template)")
            continue
        
        if check_file_signature(filepath, expected_sig):
            print(f"  ✓ OK: {filename}")
            repaired.append(f"{filename} (valid)")
        else:
            print(f"  ✗ CORRUPTED: {filename}")
            if os.path.exists(template_file):
                # Create individual backup before replacing
                backup_file = os.path.join(get_script_dir(), f'{filename}.corrupted')
                shutil.copy2(filepath, backup_file)
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                print(f"      ✓ Replaced (original saved as {filename}.corrupted)")
            else:
                errors.append(f"{filename} (corrupted, no template)")
    
    # Check for required files without signature validation
    for filename in REQUIRED_FILES:
        if filename in EXPECTED_SIGNATURES:
            continue
        
        filepath = os.path.join(omg_path, filename)
        template_file = os.path.join(template_omg, filename)
        
        if not os.path.exists(filepath):
            print(f"  ⚠️  Missing: {filename}")
            if os.path.exists(template_file):
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                print(f"      ✓ Restored from template")
            else:
                errors.append(f"{filename} (missing, no template)")
        else:
            print(f"  ✓ Present: {filename}")
    
    return repaired, replaced, errors

def main():
    print("=" * 60)
    print("  Sony NW-S715F Database Repair Tool")
    print("  Safe repair - your music files are NEVER modified")
    print("=" * 60)
    
    # Find the Walkman
    print("\n🔍 Searching for Sony Walkman...")
    walkman_base = find_walkman_drive()
    
    if not walkman_base:
        print("\n❌ No Sony Walkman detected!")
        print("\nPlease:")
        print("  1. Connect your NW-S715F via USB")
        print("  2. Wait for it to appear as a drive")
        print("  3. Run this script again")
        return 1
    
    print(f"✓ Found Walkman at: {walkman_base}")
    
    # Verify OMGAUDIO folder exists
    omg_path = os.path.join(walkman_base, 'OMGAUDIO')
    if not os.path.exists(omg_path):
        print(f"\n❌ OMGAUDIO folder not found at {omg_path}")
        print("This might not be a Sony device or it's not properly connected.")
        return 1
    
    # Get template files
    template_path = get_template_files()
    if not template_path:
        print("\n❌ Cannot find template files needed for repair.")
        print("\nPlease download the full package from the repository.")
        return 1
    
    print(f"✓ Using templates from: {template_path}")
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n💾 Creating backup...")
    try:
        backup_dir = create_backup(walkman_base, timestamp)
        print(f"✓ Backup created: {backup_dir}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        print("Aborting for safety.")
        return 1
    
    # Perform repair
    print(f"\n🔧 Starting repair...")
    repaired, replaced, errors = repair_database(walkman_base, template_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("  REPAIR SUMMARY")
    print("=" * 60)
    print(f"✓ Valid files: {len([r for r in repaired if 'valid' in r])}")
    print(f"🔄 Replaced files: {len(replaced)}")
    if replaced:
        for f in replaced:
            print(f"    - {f}")
    if errors:
        print(f"\n⚠️  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e}")
    
    if replaced or errors:
        print(f"\n💾 Full backup saved to: {backup_dir}")
        print(f"   Corrupted individual files saved as *.corrupted")
    
    if not errors and len(replaced) == 0:
        print("\n✅ All database files are healthy! No repair needed.")
    elif not errors:
        print("\n✅ Repair completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Safely eject your Walkman")
        print("   2. Disconnect USB")
        print("   3. Turn on your Walkman")
        print("   4. Open ManicStage - it should work now!")
    else:
        print("\n⚠️  Repair completed with some errors.")
        print("   You may need to reinitialize if problems persist.")
    
    print("\n" + "=" * 60)
    return 0 if not errors else 1

if __name__ == '__main__':
    sys.exit(main())
