# Sony NW-S715F Database Repair Tool

A simple, safe tool to fix the "Sony database parse failed" error on your Sony NW-S715F Walkman **without losing your music**.

## 🎯 What This Does

When your Walkman shows "Sony database parse failed; initialization is recommended", this tool:

1. **Checks** each database file for corruption (like checking ID cards)
2. **Replaces ONLY corrupted files** with clean templates
3. **Keeps all your music** - MP3/ATRAC files are NEVER touched
4. **Creates backups** before making any changes

## 🔒 Safety Features

- ✅ **Your music is safe** - Only database files (.DAT) are modified
- ✅ **Automatic backups** - All original files are backed up before changes
- ✅ **Smart detection** - Only replaces files that are actually corrupted
- ✅ **Won't brick your device** - Uses the same template files as the official ManicStage app

## 📥 How to Use

### Option 1: Run with Python (Recommended)

1. **Connect your Walkman** via USB and wait for it to appear as a drive
2. **Download this script** (`sony_walkman_repair.py`)
3. **Run the script**:
   - **Windows**: Double-click `sony_walkman_repair.py` OR open Command Prompt and type:
     ```
     python sony_walkman_repair.py
     ```
   - **Mac/Linux**: Open Terminal and type:
     ```
     python3 sony_walkman_repair.py
     ```

4. **Follow the prompts** - The tool will:
   - Find your Walkman automatically
   - Check all database files
   - Replace any corrupted files
   - Show you a summary

5. **Safely eject** your Walkman and enjoy!

### Option 2: Make it a One-Click App (Windows)

If you don't have Python installed:

1. Download [PyInstaller](https://pyinstaller.org/) or ask someone to help you convert the script
2. Or just use Option 1 with Python (easiest!)

## 🤔 How It Works (Simple Explanation)

Your Walkman stores music information in special database files (like a library catalog). Sometimes these files get corrupted, but your actual music files are fine.

This tool:
```
1. Looks at each database file's "header" (first few bytes)
2. If the header is wrong → file is corrupted
3. Replaces ONLY that bad file with a clean copy
4. Your music stays untouched!
```

**Analogy**: Imagine your music is books in a library, and the database is the card catalog. If the catalog gets messed up, we replace just the catalog cards, not the books!

## 📊 What Gets Repaired

The tool checks these database files:
- `00GTRLST.DAT` - Main track list
- `01TREE*.DAT` - Folder structure
- `02TREINF.DAT` - Tree information
- `03GINF*.DAT` - Group information
- `04CNTINF.DAT` - Content information
- `05CIDLST.DAT` - Track ID list
- `RESERVED.DAT` - Reserved space
- And more...

## 🆚 vs "Initialize Empty Library"

| Feature | This Tool | ManicStage "Initialize" |
|---------|-----------|------------------------|
| Keeps your music | ✅ Yes | ❌ No (erases everything) |
| Quick | ✅ Seconds | ❌ Minutes (re-import needed) |
| Safe | ✅ Backups created | ⚠️ Full reset |
| Easy | ✅ One click | ✅ One click |

## ❓ Troubleshooting

### "No Sony Walkman detected!"
- Make sure your Walkman is connected via USB
- Wait for it to appear as a removable drive
- Try a different USB port or cable

### "Cannot find template files"
- Make sure the script is in the same folder as the `dmg_contents` folder
- Or download the full package from the repository

### "Repair completed with errors"
- Some files couldn't be repaired
- You may need to use "Initialize Empty Library" as a last resort
- Check the backup folder for details

## 📁 Backup Location

Backups are saved in a folder like:
- `backup_20240115_143022/` (next to the script)

Corrupted individual files are saved as:
- `00GTRLST.DAT.corrupted`
- etc.

## 🙏 Credits

Based on reverse-engineering of the ManicStage app for Sony NW-S715F.

Template files extracted from ManicStage-0.1.4.dmg

## 📝 License

Free to use. Share and improve!

---

**Made with ❤️ for Walkman users tired of re-initializing**
