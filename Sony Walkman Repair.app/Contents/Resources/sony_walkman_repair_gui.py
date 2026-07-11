#!/usr/bin/env python3
"""
Sony NW-S715F Database Repair Tool - GUI Version
A simple one-click app to fix your Walkman without losing music
"""

import os
import sys
import shutil
import threading
from datetime import datetime
from pathlib import Path

# Try to import tkinter for GUI
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

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

# Files that should exist but we don't check signature
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
    """Get the directory where this script/app is located"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def find_walkman_drive():
    """Find the connected Sony Walkman drive"""
    possible_paths = []
    
    # macOS - check /Volumes
    volumes_path = '/Volumes'
    if os.path.exists(volumes_path):
        for item in os.listdir(volumes_path):
            item_path = os.path.join(volumes_path, item)
            if os.path.isdir(item_path):
                omg_path = os.path.join(item_path, 'OMGAUDIO')
                if os.path.exists(omg_path) and os.path.isdir(omg_path):
                    # Verify it's a Sony device
                    test_file = os.path.join(omg_path, '00GTRLST.DAT')
                    if os.path.exists(test_file) or len(os.listdir(omg_path)) > 0:
                        return item_path
    
    # Windows
    for drive in 'DEFGHIJKLMNOPQRSTUVWXYZ':
        path = f'{drive}:/'
        if os.path.exists(path):
            omg_path = os.path.join(path, 'OMGAUDIO')
            if os.path.exists(omg_path):
                return path
    
    # Linux
    linux_paths = ['/media', '/mnt']
    for base in linux_paths:
        if os.path.exists(base):
            for user in os.listdir(base):
                user_path = os.path.join(base, user)
                if os.path.isdir(user_path):
                    omg_path = os.path.join(user_path, 'OMGAUDIO')
                    if os.path.exists(omg_path):
                        return user_path
    
    return None

def check_file_signature(filepath, expected_sig):
    """Check if file has the correct signature"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)
            return header == expected_sig
    except Exception:
        return False

def create_backup(walkman_base, timestamp, script_dir):
    """Create backup of current database files"""
    backup_dir = os.path.join(script_dir, f'backup_{timestamp}')
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
    """Get path to template files"""
    script_dir = get_script_dir()
    
    # Try common locations for templates
    template_locations = [
        os.path.join(script_dir, 'dmg_contents', 'ManicStage.app', 
                    'Contents', 'Resources', 'templates', 'empty_library'),
        os.path.join(script_dir, 'templates', 'empty_library'),
        os.path.join(script_dir, '..', 'dmg_contents', 'ManicStage.app',
                    'Contents', 'Resources', 'templates', 'empty_library'),
        # When running as .app bundle on macOS
        os.path.join(script_dir, '..', 'Resources', 'templates', 'empty_library'),
    ]
    
    for template_path in template_locations:
        omg_path = os.path.join(template_path, 'OMGAUDIO')
        if os.path.exists(omg_path):
            return template_path
    
    return None

def repair_database(walkman_base, template_path, script_dir, log_callback=None):
    """Repair corrupted database files"""
    omg_path = os.path.join(walkman_base, 'OMGAUDIO')
    template_omg = os.path.join(template_path, 'OMGAUDIO')
    
    repaired = []
    replaced = []
    errors = []
    
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)
    
    log(f"Checking database files in: {omg_path}")
    log("-" * 60)
    
    # Check each file with known signature
    for filename, expected_sig in EXPECTED_SIGNATURES.items():
        filepath = os.path.join(omg_path, filename)
        template_file = os.path.join(template_omg, filename)
        
        if not os.path.exists(filepath):
            log(f"  ⚠️  Missing: {filename}")
            if os.path.exists(template_file):
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                log(f"      ✓ Restored from template")
            else:
                errors.append(f"{filename} (missing, no template)")
            continue
        
        if check_file_signature(filepath, expected_sig):
            log(f"  ✓ OK: {filename}")
            repaired.append(f"{filename} (valid)")
        else:
            log(f"  ✗ CORRUPTED: {filename}")
            if os.path.exists(template_file):
                # Create individual backup before replacing
                backup_file = os.path.join(script_dir, f'{filename}.corrupted')
                shutil.copy2(filepath, backup_file)
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                log(f"      ✓ Replaced (original saved as {filename}.corrupted)")
            else:
                errors.append(f"{filename} (corrupted, no template)")
    
    # Check for required files without signature validation
    for filename in REQUIRED_FILES:
        if filename in EXPECTED_SIGNATURES:
            continue
        
        filepath = os.path.join(omg_path, filename)
        template_file = os.path.join(template_omg, filename)
        
        if not os.path.exists(filepath):
            log(f"  ⚠️  Missing: {filename}")
            if os.path.exists(template_file):
                shutil.copy2(template_file, filepath)
                replaced.append(filename)
                log(f"      ✓ Restored from template")
            else:
                errors.append(f"{filename} (missing, no template)")
        else:
            log(f"  ✓ Present: {filename}")
    
    return repaired, replaced, errors


class RepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sony Walkman Repair Tool")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Set macOS style
        try:
            self.root.tk.call('tk', 'scaling', 2.0)
        except:
            pass
        
        self.is_repairing = False
        self.script_dir = get_script_dir()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Sony NW-S715F Repair Tool", 
                               font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Fix database errors without losing your music",
                                  font=('Helvetica', 12))
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Click 'Start Repair' to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                font=('Helvetica', 11))
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD,
                                                  font=('Courier', 10))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(10, 0))
        
        self.repair_button = ttk.Button(button_frame, text="🔧 Start Repair",
                                       command=self.start_repair,
                                       style='Accent.TButton')
        self.repair_button.grid(row=0, column=0, padx=5)
        
        self.close_button = ttk.Button(button_frame, text="Close",
                                      command=self.root.quit)
        self.close_button.grid(row=0, column=1, padx=5)
        
        # Info label
        info_label = ttk.Label(main_frame,
                              text="⚠️ Keep your Walkman connected during repair",
                              font=('Helvetica', 9), foreground='orange')
        info_label.grid(row=5, column=0, pady=(10, 0))
        
        # Style configuration
        style = ttk.Style()
        try:
            style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'))
        except:
            pass
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status label"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def start_repair(self):
        """Start the repair process in a thread"""
        if self.is_repairing:
            return
        
        self.is_repairing = True
        self.repair_button.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        
        # Start repair in background thread
        thread = threading.Thread(target=self.run_repair)
        thread.daemon = True
        thread.start()
    
    def run_repair(self):
        """Run the repair process"""
        try:
            self.update_status("🔍 Searching for Sony Walkman...")
            self.log_message("=" * 60)
            self.log_message("  Sony NW-S715F Database Repair Tool")
            self.log_message("  Safe repair - your music files are NEVER modified")
            self.log_message("=" * 60)
            self.log_message("")
            
            # Find the Walkman
            walkman_base = find_walkman_drive()
            
            if not walkman_base:
                self.update_status("❌ No Walkman detected!")
                self.log_message("\n❌ No Sony Walkman detected!")
                self.log_message("\nPlease:")
                self.log_message("  1. Connect your NW-S715F via USB")
                self.log_message("  2. Wait for it to appear as a drive")
                self.log_message("  3. Click 'Start Repair' again")
                self.root.after(0, lambda: messagebox.showerror(
                    "No Device Found",
                    "No Sony Walkman detected!\n\n"
                    "Please:\n"
                    "1. Connect your NW-S715F via USB\n"
                    "2. Wait for it to appear as a drive\n"
                    "3. Click 'Start Repair' again"
                ))
                self.is_repairing = False
                self.root.after(0, lambda: self.repair_button.config(state='normal'))
                return
            
            self.update_status(f"✓ Found at: {walkman_base}")
            self.log_message(f"\n✓ Found Walkman at: {walkman_base}")
            
            # Verify OMGAUDIO folder exists
            omg_path = os.path.join(walkman_base, 'OMGAUDIO')
            if not os.path.exists(omg_path):
                self.update_status("❌ Not a Sony device")
                self.log_message(f"\n❌ OMGAUDIO folder not found")
                self.root.after(0, lambda: messagebox.showerror(
                    "Invalid Device",
                    "OMGAUDIO folder not found.\n"
                    "This might not be a Sony device."
                ))
                self.is_repairing = False
                self.root.after(0, lambda: self.repair_button.config(state='normal'))
                return
            
            # Get template files
            self.update_status("📦 Loading templates...")
            template_path = get_template_files()
            if not template_path:
                self.update_status("❌ Templates not found")
                self.log_message("\n❌ Cannot find template files needed for repair.")
                self.root.after(0, lambda: messagebox.showerror(
                    "Missing Templates",
                    "Cannot find template files needed for repair.\n\n"
                    "Please ensure the app is properly installed."
                ))
                self.is_repairing = False
                self.root.after(0, lambda: self.repair_button.config(state='normal'))
                return
            
            self.log_message(f"✓ Using templates from: {template_path}")
            
            # Create timestamp for backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create backup
            self.update_status("💾 Creating backup...")
            self.log_message(f"\n💾 Creating backup...")
            try:
                backup_dir = create_backup(walkman_base, timestamp, self.script_dir)
                self.log_message(f"✓ Backup created: {backup_dir}")
            except Exception as e:
                self.update_status("❌ Backup failed")
                self.log_message(f"❌ Failed to create backup: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Backup Failed",
                    f"Failed to create backup:\n{e}\n\nAborting for safety."
                ))
                self.is_repairing = False
                self.root.after(0, lambda: self.repair_button.config(state='normal'))
                return
            
            # Perform repair
            self.update_status("🔧 Repairing database...")
            self.log_message(f"\n🔧 Starting repair...")
            repaired, replaced, errors = repair_database(
                walkman_base, template_path, self.script_dir, self.log_message
            )
            
            # Summary
            self.log_message("\n" + "=" * 60)
            self.log_message("  REPAIR SUMMARY")
            self.log_message("=" * 60)
            valid_count = len([r for r in repaired if 'valid' in r])
            self.log_message(f"✓ Valid files: {valid_count}")
            self.log_message(f"🔄 Replaced files: {len(replaced)}")
            if replaced:
                for f in replaced:
                    self.log_message(f"    - {f}")
            if errors:
                self.log_message(f"\n⚠️  Errors: {len(errors)}")
                for e in errors:
                    self.log_message(f"    - {e}")
            
            if replaced or errors:
                self.log_message(f"\n💾 Full backup saved to: {backup_dir}")
            
            # Final status
            if not errors and len(replaced) == 0:
                self.update_status("✅ All healthy!")
                self.log_message("\n✅ All database files are healthy! No repair needed.")
                self.root.after(0, lambda: messagebox.showinfo(
                    "All Good!",
                    "All database files are healthy!\nNo repair needed."
                ))
            elif not errors:
                self.update_status("✅ Repair successful!")
                self.log_message("\n✅ Repair completed successfully!")
                self.log_message("\n📝 Next steps:")
                self.log_message("   1. Safely eject your Walkman")
                self.log_message("   2. Disconnect USB")
                self.log_message("   3. Turn on your Walkman")
                self.log_message("   4. Open ManicStage - it should work now!")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    "Repair completed successfully!\n\n"
                    "Next steps:\n"
                    "1. Safely eject your Walkman\n"
                    "2. Disconnect USB\n"
                    "3. Turn on your Walkman\n"
                    "4. Open ManicStage - it should work now!"
                ))
            else:
                self.update_status("⚠️ Completed with errors")
                self.log_message("\n⚠️  Repair completed with some errors.")
                self.log_message("   You may need to reinitialize if problems persist.")
                self.root.after(0, lambda: messagebox.showwarning(
                    "Completed with Warnings",
                    "Repair completed with some errors.\n\n"
                    "You may need to reinitialize if problems persist."
                ))
            
            self.log_message("\n" + "=" * 60)
            
        except Exception as e:
            self.update_status("❌ Error occurred")
            self.log_message(f"\n❌ Unexpected error: {e}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n{e}"
            ))
        finally:
            self.is_repairing = False
            self.root.after(0, lambda: self.repair_button.config(state='normal'))


def main():
    if not GUI_AVAILABLE:
        print("GUI not available (tkinter not installed).")
        print("Running in command-line mode...")
        # Fall back to CLI version
        import sony_walkman_repair
        sony_walkman_repair.main()
        return
    
    root = tk.Tk()
    app = RepairApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
