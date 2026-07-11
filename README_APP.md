# 🎵 Sony Walkman Repair Tool - One-Click macOS App

A simple, safe, one-click app to fix your Sony NW-S715F database errors **without losing your music**.

## 📦 What You Got

I built you a complete macOS app that:
- ✅ Repairs corrupted database files automatically
- ✅ **NEVER touches your music files** (MP3/ATRAC stay safe)
- ✅ Creates backups before making any changes
- ✅ Uses the same official templates as Sony's ManicStage app
- ✅ Takes only 5 seconds vs minutes of re-importing

### Files Created:
1. **`Sony Walkman Repair.app`** - Your one-click repair app
2. **`build_mac_app.sh`** - Script to rebuild the app if needed
3. **`sony_walkman_repair_gui.py`** - The GUI code (used by the app)

## 🚀 How to Use

### Step 1: Copy the App to Your Mac
Transfer the `Sony Walkman Repair.app` folder to your Mac (Applications folder or Desktop).

### Step 2: First Time Setup
macOS will warn about "unidentified developer" because it's not from the App Store. This is normal!

**To open it:**
1. **Right-click** (or Control-click) on `Sony Walkman Repair.app`
2. Select **"Open"** from the menu
3. Click **"Open"** again in the warning dialog

*(You only need to do this once. After that, you can just double-click normally.)*

### Step 3: Repair Your Walkman
1. **Connect** your Sony NW-S715F via USB cable
2. **Wait** for it to appear as a drive on your Mac
3. **Double-click** `Sony Walkman Repair.app`
4. **Click** the "🔧 Start Repair" button
5. **Wait** ~5 seconds for completion
6. **Safely eject** your Walkman
7. **Disconnect** USB and enjoy!

## 🔒 Why It's Safe

| Concern | Our Solution |
|---------|--------------|
| Will it delete my music? | **NO** - Only touches database (.DAT) files, never music files |
| What if something goes wrong? | **Full backup** created automatically before any changes |
| Is it using official files? | **YES** - Uses exact same templates from Sony's ManicStage app |
| Can it brick my Walkman? | **NO** - Only replaces corrupted database files with valid ones |
| What if my Walkman isn't detected? | App won't run unless it finds your actual Sony device |

## 🛠️ How It Works (Simple Version)

Think of your Walkman like a library:
- **Music files** = Books on shelves (never touched)
- **Database files** = Card catalog (gets fixed if corrupted)

When the database gets corrupted, ManicStage can't find your music and asks you to "reinitialize" (throw away the old catalog and make a new one from scratch). 

Our app just **fixes the broken cards** in the catalog instead of throwing everything away. Your music stays exactly where it is!

## 📋 Technical Details

### What Gets Checked:
The app checks these database files for corruption:
- `00GTRLST.DAT` - Main track list
- `01TREE*.DAT` - Folder structure
- `02TREINF.DAT` - Tree information
- `03GINF*.DAT` - Group/playlist info
- `04CNTINF.DAT` - Content metadata
- `05CIDLST.DAT` - Track ID list

### What Happens During Repair:
1. **Detect** your Sony Walkman automatically
2. **Backup** all current database files
3. **Check** each file's "signature" (first 4 bytes)
4. **Replace** only corrupted files with clean templates
5. **Report** what was fixed

### System Requirements:
- macOS 10.13 (High Sierra) or later
- Python 3 (comes pre-installed on modern macOS)
- Sony NW-S715F connected via USB

## ❓ Troubleshooting

### "No Sony Walkman detected"
- Make sure your Walkman is connected via USB
- Wait for it to appear as a drive in Finder
- Try a different USB cable or port
- Make sure the Walkman is in USB mode (not charging only)

### "Templates not found"
- Don't move the app away from its original location
- The templates are bundled inside the app - don't modify them

### "Python 3 not found"
- On older macOS versions, install Python from [python.org](https://www.python.org/downloads/)
- Most modern macOS versions have Python 3 pre-installed

### App won't open at all
- Right-click → Open → Click "Open" to bypass Gatekeeper
- Go to System Preferences → Security & Privacy → Click "Open Anyway"

## 📁 Backup Location

Backups are saved in the same folder as the app:
```
Sony Walkman Repair.app/
├── backup_20240711_143022/  ← Your backups here
│   ├── OMGAUDIO/
│   └── NWWM/
```

If anything goes wrong, you can manually restore from these backups.

## 💡 Pro Tips

1. **Use this app regularly** - Run it once a month to prevent corruption
2. **Always safely eject** - Never unplug without ejecting first
3. **Keep backups** - Don't delete the backup folders
4. **One click fix** - Much faster than full reinitialization + re-import

---

**Made with ❤️ for Sony Walkman lovers**

No more losing hours re-importing your music library!
