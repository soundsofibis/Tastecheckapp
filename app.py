"""
TasteCheck Backend Server - Flask Version
Handles image analysis using Claude's vision API
"""

from flask import Flask, request, jsonify, send_from_directory
import anthropic
import os
import base64

# Configuration
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Initialize Flask app
app = Flask(__name__, static_folder='.')

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=API_KEY)


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)


@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle POST requests for image analysis"""
    try:
        data = request.get_json()
        
        # Extract data
        images = data.get('images', [])
        style = data.get('style', 'analytical')
        mode = data.get('mode', 'single')
        
        # Backward compatibility: handle single image format
        if not images and data.get('image'):
            images = [data.get('image')]
        
        # Analyze based on mode
        if mode == 'manual':
            answers = data.get('answers', {})
            userName = data.get('userName', '')
            if not answers:
                return jsonify({"error": "No answers provided"}), 400
            result = analyze_manual_input(answers, style, userName)
        elif mode == 'single':
            if not images:
                return jsonify({"error": "No images provided"}), 400
            userName = data.get('userName', '')
            result = analyze_music_taste(images[0], style, userName=userName)
        elif mode == 'evolution':
            if not images:
                return jsonify({"error": "No images provided"}), 400
            userName = data.get('userName', '')
            result = analyze_evolution(images, style, userName=userName)
        elif mode == 'battle':
            if not images:
                return jsonify({"error": "No images provided"}), 400
            nameA = data.get('nameA', 'Person 1')
            nameB = data.get('nameB', 'Person 2')
            result = analyze_battle(images, style, nameA, nameB)
        else:
            return jsonify({"error": "Invalid mode"}), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


def detect_image_type(image_base64):
    """Detect image type from base64 data"""
    try:
        image_bytes = base64.b64decode(image_base64[:100])
        
        if image_bytes[:4] == b'\x89PNG':
            return 'image/png'
        elif image_bytes[:3] == b'\xff\xd8\xff':
            return 'image/jpeg'
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return 'image/webp'
        elif image_bytes[:4] in (b'GIF8', b'GIF9'):
            return 'image/gif'
        else:
            return 'image/jpeg'
    except Exception:
        return 'image/jpeg'


def analyze_music_taste(image_base64, style, userName=''):
    """Analyze music taste from screenshot"""
    style_prompts = {
        'roasting': """You're a brutally honest music critic. Roast their taste while being funny. 
        Point out basic choices, questionable artists, or lack of diversity. Be savage but entertaining.""",
        'encouraging': """You're a supportive music enthusiast. Celebrate their taste! 
        Highlight the good choices, interesting discoveries, and unique aspects. Be genuinely positive.""",
        'sarcastic': """You're a playfully sarcastic music snob. Use wit and irony. 
        Make cheeky observations about their choices. Be funny without being mean.""",
        'analytical': """You're a music data analyst. Provide deep insights about their listening patterns. 
        Discuss genre diversity, era spread, mainstream vs. indie balance. Be thorough and academic."""
    }
    
    style_instruction = style_prompts.get(style, style_prompts['analytical'])
    
    prompt = f"""Analyze this music streaming recap/wrapped screenshot and provide:

1. A TASTE QUALITY SCORE from 0-100 based on:
   - Musical sophistication and depth
   - Balance of discovery vs. accessibility  
   - Genre diversity and interesting combinations
   - Mix of classic/timeless artists with quality current music
   - Overall cultural awareness and taste
   
2. A fun, detailed analysis in this style: {style_instruction}

The analysis should be 3-4 paragraphs covering:
- Overall impression of their taste (is it good, basic, adventurous?)
- Specific observations about artists/genres shown
- What this says about them as a music listener
- Surprising patterns or standout choices

Format your response EXACTLY like this:
SCORE: [number 0-100]
ANALYSIS: [your detailed analysis]

Remember: {style_instruction}"""

    try:
        media_type = detect_image_type(image_base64)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {"type": "text", "text": prompt}
                ],
            }],
        )
        
        response_text = message.content[0].text
        score = 75
        analysis = response_text
        
        if "SCORE:" in response_text and "ANALYSIS:" in response_text:
            parts = response_text.split("ANALYSIS:")
            score_part = parts[0].replace("SCORE:", "").strip()
            analysis = parts[1].strip()
            
            try:
                score = int(''.join(filter(str.isdigit, score_part[:3])))
                score = max(0, min(100, score))
            except:
                score = 75
        
        return {"score": score, "analysis": analysis}
        
    except Exception as e:
        print(f"API Error: {e}")
        return {"score": 0, "analysis": f"Sorry, something went wrong. Error: {str(e)}"}


def analyze_evolution(images, style, userName=''):
    """Analyze musical evolution across multiple years"""
    style_prompts = {
        'roasting': "Be brutally honest about their musical journey.",
        'encouraging': "Celebrate their growth!",
        'sarcastic': "Use wit and irony to comment on their musical evolution.",
        'analytical': "Provide deep insights about trends and patterns."
    }
    
    style_instruction = style_prompts.get(style, style_prompts['analytical'])
    
    prompt = f"""Analyze these music streaming recaps from different years and provide:

1. An OVERALL EVOLUTION SCORE from 0-100
2. A detailed analysis in this style: {style_instruction}

Format: SCORE: [0-100]
ANALYSIS: [your analysis]"""

    try:
        content = []
        for img_base64 in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": detect_image_type(img_base64),
                    "data": img_base64,
                },
            })
        content.append({"type": "text", "text": prompt})
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        
        response_text = message.content[0].text
        score = 75
        analysis = response_text
        
        if "SCORE:" in response_text and "ANALYSIS:" in response_text:
            parts = response_text.split("ANALYSIS:")
            score_part = parts[0].replace("SCORE:", "").strip()
            analysis = parts[1].strip()
            try:
                score = int(''.join(filter(str.isdigit, score_part[:3])))
                score = max(0, min(100, score))
            except:
                pass
        
        return {"score": score, "analysis": analysis}
    except Exception as e:
        return {"score": 0, "analysis": f"Error: {str(e)}"}


def analyze_battle(images, style, nameA='Person 1', nameB='Person 2'):
    """Compare two people's music taste"""
    prompt = f"""Compare these two music recaps. First is {nameA}, second is {nameB}.

Give scores 0-100 for each and detailed comparison.

Format:
SCORE_A: [0-100 for {nameA}]
SCORE_B: [0-100 for {nameB}]
ANALYSIS: [comparison using {nameA} and {nameB}]"""

    try:
        content = [
            {"type": "image", "source": {"type": "base64", "media_type": detect_image_type(images[0]), "data": images[0]}},
            {"type": "image", "source": {"type": "base64", "media_type": detect_image_type(images[1]), "data": images[1]}},
            {"type": "text", "text": prompt}
        ]
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        
        response_text = message.content[0].text
        scoreA = scoreB = 75
        analysis = response_text
        
        if "SCORE_A:" in response_text and "SCORE_B:" in response_text:
            try:
                score_a_match = response_text.split("SCORE_A:")[1].split("SCORE_B:")[0]
                scoreA = int(''.join(filter(str.isdigit, score_a_match[:3])))
                scoreA = max(0, min(100, scoreA))
                
                score_b_match = response_text.split("SCORE_B:")[1].split("ANALYSIS:")[0]
                scoreB = int(''.join(filter(str.isdigit, score_b_match[:3])))
                scoreB = max(0, min(100, scoreB))
                
                analysis = response_text.split("ANALYSIS:")[1].strip()
            except:
                pass
        
        return {"scoreA": scoreA, "scoreB": scoreB, "analysis": analysis}
    except Exception as e:
        return {"scoreA": 0, "scoreB": 0, "analysis": f"Error: {str(e)}"}


def analyze_manual_input(answers, style, userName=''):
    """Analyze music taste from text answers"""
    answers_text = f"""
Favorite artist: {answers.get('favoriteArtist', 'N/A')}
Favorite album: {answers.get('favoriteAlbum', 'N/A')}
Current song: {answers.get('currentSong', 'N/A')}
Current artist: {answers.get('currentArtist', 'N/A')}
Guilty pleasure: {answers.get('guiltyPleasure', 'N/A')}
Genres: {answers.get('genres', 'N/A')}
"""
    
    prompt = f"""Analyze this music taste:
{answers_text}

Provide SCORE (0-100) and detailed ANALYSIS.
Format: SCORE: [number]
ANALYSIS: [analysis]"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        
        response_text = message.content[0].text
        score = 75
        analysis = response_text
        
        if "SCORE:" in response_text and "ANALYSIS:" in response_text:
            parts = response_text.split("ANALYSIS:")
            score_part = parts[0].replace("SCORE:", "").strip()
            analysis = parts[1].strip()
            try:
                score = int(''.join(filter(str.isdigit, score_part[:3])))
                score = max(0, min(100, score))
            except:
                pass
        
        return {"score": score, "analysis": analysis}
    except Exception as e:
        return {"score": 0, "analysis": f"Error: {str(e)}"}


if __name__ == '__main__':
    if not API_KEY:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set!")
    app.run(host='0.0.0.0', port=8000, debug=True)
