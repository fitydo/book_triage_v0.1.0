# 📚 Book Triage App - Setup Instructions

## 🚀 Quick Start (5 minutes)

### Step 1: Install Python
1. Go to [python.org](https://python.org/downloads/)
2. Download **Python 3.12** or newer
3. **Important:** Check "Add Python to PATH" during installation

### Step 2: Get OpenAI API Key
1. Go to [openai.com](https://openai.com)
2. Create account and get API key
3. Copy the key (starts with `sk-...`)

### Step 3: Setup Environment
1. In the app folder, find `.env.example`
2. Copy it and rename to `.env`
3. Open `.env` in notepad
4. Replace `your_openai_api_key_here` with your actual API key
5. Save the file

### Step 4: Start the App
1. **Double-click** `start_book_triage.bat`
2. Wait for "Starting web server..." message
3. Open browser and go to `http://localhost:8000`

## 🎉 You're Ready!

- Upload book photos or enter titles manually
- Fill in the scoring fields (F, R, A, V, S, P)
- Click "Save & Rescan" for AI enrichment
- Review decisions and citations

## 🔧 Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or try `start_simple.bat` instead

### "OpenAI API error"
- Check your `.env` file has correct API key
- Verify you have OpenAI credits/billing setup

### "Permission denied"
- Right-click batch file → "Run as administrator"
- Or use PowerShell: `start_book_triage.ps1`

### Web page won't load
- Wait 30 seconds after "Starting web server..."
- Try `http://127.0.0.1:8000` instead
- Check Windows Firewall isn't blocking

## 📞 Need Help?

Contact the person who shared this app with you!

## 🎯 What Each File Does

- `start_book_triage.bat` - Main launcher (double-click this)
- `start_simple.bat` - Backup launcher if main doesn't work
- `sample_books.csv` - Your book data (automatically created)
- `.env` - Your API key configuration
- `book_triage/` - The app code (don't modify)

## 💡 Tips

- Keep the app folder in a permanent location
- Back up your `sample_books.csv` file regularly
- You can rename `sample_books.csv` to anything you want
- Press `Ctrl+C` in the terminal window to stop the app 