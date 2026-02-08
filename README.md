# 🎵 TasteCheck

Analyze your music streaming recap and get an eclecticism score with fun AI-powered feedback!

## What This Does

1. Upload a screenshot of your Spotify Wrapped, Apple Music Replay, or any streaming service recap
2. Choose your feedback style (Roasting, Encouraging, Sarcastic, or Analytical)
3. Get an eclecticism score (0-100) based on genre diversity, artist variety, and more
4. Receive personalized analysis from Claude AI

## Setup Instructions

### Step 1: Install Python Dependencies

You already have Python 3.9.6, so just install the Anthropic library:

```bash
pip install anthropic
```

Or if that doesn't work:

```bash
pip3 install anthropic
```

### Step 2: Set Your API Key

You need to tell the server your Anthropic API key.

**On Mac/Linux (Terminal):**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**On Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**On Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

Replace `your-api-key-here` with your actual API key from console.anthropic.com

### Step 3: Run the Server

Navigate to the tastecheck folder and run:

```bash
python server.py
```

Or:

```bash
python3 server.py
```

You should see:
```
🎵 TasteCheck Server Running!
✅ Open your browser to: http://localhost:8000
```

### Step 4: Use the App

1. Open your web browser
2. Go to `http://localhost:8000`
3. Upload a music recap screenshot
4. Choose your feedback style
5. Get your results!

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- You need to set the environment variable before running the server
- The command only works in the current terminal session
- Run the export/set command, then run server.py in the SAME terminal window

**"Module 'anthropic' not found"**
- Run: `pip install anthropic` or `pip3 install anthropic`

**"Port already in use"**
- Something else is using port 8000
- Edit server.py and change `PORT = 8000` to `PORT = 8001` or another number
- Then visit `http://localhost:8001` instead

**Image not uploading**
- Make sure your image is a PNG, JPG, or HEIC file
- Try a smaller image if it's very large (under 5MB works best)

## How It Works

**Frontend (HTML/CSS/JS):**
- `index.html` - The webpage structure
- `style.css` - All the styling and colors
- `script.js` - Handles file uploads and user interactions

**Backend (Python):**
- `server.py` - Web server that serves files and processes API requests
- Uses Claude's vision API to "read" the screenshot
- Analyzes artists, genres, and patterns
- Generates a score and personalized feedback

## Cost

Each analysis costs about $0.01-0.03 depending on the image size and response length. Your $5 credit should give you 150-500+ analyses.

## Privacy

- Your images are sent to Anthropic's API for analysis
- Nothing is stored on a server - it's all processed in real-time
- Once you close the app, your data is gone

## Next Steps

Ideas for extending this app:
- Add more feedback styles
- Show detailed breakdowns (genres, decades, etc.)
- Compare multiple screenshots
- Save and share results
- Add music recommendations based on taste

Have fun! 🎵
