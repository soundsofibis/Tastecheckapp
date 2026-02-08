"""
TasteCheck Backend Server
Handles image analysis using Claude's vision API
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import anthropic
import os
import base64
from urllib.parse import urlparse

# Configuration
PORT = 8000
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=API_KEY)


class TasteCheckHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for TasteCheck"""
    
    def do_GET(self):
        """Serve static files"""
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests for image analysis"""
        if self.path == '/analyze':
            self.handle_analyze()
        else:
            self.send_error(404)
    
    def handle_analyze(self):
        """Process image analysis request"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            # Extract data
            images = data.get('images', [])
            style = data.get('style', 'analytical')
            mode = data.get('mode', 'single')
            
            # Backward compatibility: handle single image format
            if not images and data.get('image'):
                images = [data.get('image')]
            
            # Analyze based on mode
            if mode == 'manual':
                # Manual input mode - no images required
                answers = data.get('answers', {})
                userName = data.get('userName', '')
                if not answers:
                    self.send_error(400, "No answers provided")
                    return
                result = analyze_manual_input(answers, style, userName)
            elif mode == 'single':
                if not images:
                    self.send_error(400, "No images provided")
                    return
                userName = data.get('userName', '')
                result = analyze_music_taste(images[0], style, userName=userName)
            elif mode == 'evolution':
                if not images:
                    self.send_error(400, "No images provided")
                    return
                userName = data.get('userName', '')
                result = analyze_evolution(images, style, userName=userName)
            elif mode == 'battle':
                if not images:
                    self.send_error(400, "No images provided")
                    return
                nameA = data.get('nameA', 'Person 1')
                nameB = data.get('nameB', 'Person 2')
                result = analyze_battle(images, style, nameA, nameB)
            else:
                self.send_error(400, "Invalid mode")
                return
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def detect_image_type(image_base64):
    """
    Detect image type from base64 data by checking file signature
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        media_type string like 'image/png' or 'image/jpeg'
    """
    try:
        # Decode first few bytes to check file signature
        image_bytes = base64.b64decode(image_base64[:100])
        
        # PNG signature: 89 50 4E 47
        if image_bytes[:4] == b'\x89PNG':
            return 'image/png'
        
        # JPEG signature: FF D8 FF
        elif image_bytes[:3] == b'\xff\xd8\xff':
            return 'image/jpeg'
        
        # WebP signature: RIFF...WEBP
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return 'image/webp'
        
        # GIF signature: GIF89a or GIF87a
        elif image_bytes[:4] in (b'GIF8', b'GIF9'):
            return 'image/gif'
        
        # Default to JPEG if can't detect
        else:
            return 'image/jpeg'
            
    except Exception:
        # If anything goes wrong, default to JPEG
        return 'image/jpeg'


def analyze_music_taste(image_base64, style, userName=''):
    """
    Use Claude's vision API to analyze music taste from screenshot
    
    Args:
        image_base64: Base64 encoded image
        style: Feedback style (roasting, encouraging, sarcastic, analytical)
    
    Returns:
        dict with 'score' and 'analysis'
    """
    
    # Create style-specific prompts
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
    
    # Create the prompt for Claude
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
        # Detect the actual image type
        media_type = detect_image_type(image_base64)
        
        # Call Claude API with vision
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
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
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        
        # Extract score and analysis
        score = 75  # Default
        analysis = response_text
        
        # Try to parse the structured response
        if "SCORE:" in response_text and "ANALYSIS:" in response_text:
            parts = response_text.split("ANALYSIS:")
            score_part = parts[0].replace("SCORE:", "").strip()
            analysis = parts[1].strip()
            
            # Extract numeric score
            try:
                score = int(''.join(filter(str.isdigit, score_part[:3])))
                score = max(0, min(100, score))  # Clamp between 0-100
            except:
                score = 75
        
        return {
            "score": score,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "score": 0,
            "analysis": f"Sorry, something went wrong analyzing your image. Error: {str(e)}"
        }


def analyze_evolution(images, style, userName=''):
    """
    Analyze musical evolution across multiple years
    
    Args:
        images: List of 2-3 base64 encoded images
        style: Feedback style
    
    Returns:
        dict with 'score' and 'analysis'
    """
    
    style_prompts = {
        'roasting': "Be brutally honest about their musical journey. Point out if they're getting more basic or if they've actually evolved.",
        'encouraging': "Celebrate their growth! Highlight positive changes and interesting developments in their taste.",
        'sarcastic': "Use wit and irony to comment on their musical evolution (or lack thereof).",
        'analytical': "Provide deep insights about the trends, patterns, and trajectory of their musical taste over time."
    }
    
    style_instruction = style_prompts.get(style, style_prompts['analytical'])
    
    prompt = f"""Analyze these music streaming recaps from different years (oldest to newest) and provide:

1. An OVERALL EVOLUTION SCORE from 0-100 based on:
   - Whether their taste is improving or getting worse
   - Discovery of better/more sophisticated artists
   - Consistency vs. volatility in taste
   - Overall trajectory (leveling up, stagnating, or regressing)

2. A detailed analysis in this style: {style_instruction}

The analysis should cover:
- How their taste has changed over time (better? worse? different?)
- Patterns you notice (getting more adventurous, more basic, etc.)
- Whether they're developing good taste or regressing
- Specific observations about each year
- Overall verdict on their musical journey

Format your response EXACTLY like this:
SCORE: [number 0-100]
ANALYSIS: [your detailed analysis]

Remember: {style_instruction}"""

    try:
        # Build content with all images
        content = []
        for i, img_base64 in enumerate(images):
            media_type = detect_image_type(img_base64)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": img_base64,
                },
            })
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        
        response_text = message.content[0].text
        
        # Parse response
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
        
        return {
            "score": score,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "score": 0,
            "analysis": f"Sorry, something went wrong. Error: {str(e)}"
        }


def analyze_battle(images, style, nameA='Person 1', nameB='Person 2'):
    """
    Compare two people's music taste head-to-head
    
    Args:
        images: List of 2 base64 encoded images [Person A, Person B]
        style: Feedback style
    
    Returns:
        dict with 'scoreA', 'scoreB', and 'analysis'
    """
    
    style_prompts = {
        'roasting': "Roast both of them! Be savage but funny about who has better (or worse) taste.",
        'encouraging': "Find positives in both tastes while gently declaring a winner.",
        'sarcastic': "Use playful sarcasm to compare their tastes and crown a winner.",
        'analytical': "Provide a thorough, data-driven comparison of their musical sophistication."
    }
    
    style_instruction = style_prompts.get(style, style_prompts['analytical'])
    
    prompt = f"""Compare these two people's music recaps and determine who has better taste.

The first image is {nameA}'s music recap.
The second image is {nameB}'s music recap.

Give BOTH people TASTE QUALITY SCORES from 0-100 based on:
- Musical sophistication
- Artist quality (good choices vs. basic/questionable)
- Balance and cultural awareness
- Overall impressiveness of their taste

Then provide a detailed comparison in this style: {style_instruction}

The analysis should cover:
- Each person's strengths and weaknesses
- Direct comparisons (who has better, more sophisticated taste?)
- Shared tastes vs. unique choices
- Clear declaration of who has "better" taste (even if close)
- Fun observations and zingers
- USE THEIR ACTUAL NAMES ({nameA} and {nameB}) throughout the analysis

Format your response EXACTLY like this:
SCORE_A: [number 0-100 for {nameA}]
SCORE_B: [number 0-100 for {nameB}]
ANALYSIS: [your detailed comparison using {nameA} and {nameB}]

Remember: {style_instruction}"""

    try:
        # Build content with both images
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": detect_image_type(images[0]),
                    "data": images[0],
                },
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": detect_image_type(images[1]),
                    "data": images[1],
                },
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        
        response_text = message.content[0].text
        
        # Parse response
        scoreA = 75
        scoreB = 75
        analysis = response_text
        
        if "SCORE_A:" in response_text and "SCORE_B:" in response_text and "ANALYSIS:" in response_text:
            # Extract scores
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
        
        return {
            "scoreA": scoreA,
            "scoreB": scoreB,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "scoreA": 0,
            "scoreB": 0,
            "analysis": f"Sorry, something went wrong. Error: {str(e)}"
        }


def analyze_manual_input(answers, style, userName=''):
    """
    Analyze music taste based on text answers
    
    Args:
        answers: Dict with favoriteArtist, favoriteAlbum, currentSong, etc.
        style: Feedback style
        userName: Optional user name
    
    Returns:
        dict with 'score' and 'analysis'
    """
    
    style_prompts = {
        'roasting': "Roast their taste! Be brutally honest and funny about their choices.",
        'encouraging': "Celebrate their taste! Find positives in their choices and be supportive.",
        'sarcastic': "Use playful sarcasm and wit to comment on their music choices.",
        'analytical': "Provide deep analytical insights about their musical preferences and what it reveals."
    }
    
    style_instruction = style_prompts.get(style, style_prompts['analytical'])
    
    # Build the prompt with answers
    answers_text = f"""
Favorite all-time artist: {answers.get('favoriteArtist', 'Not provided')}
Favorite album of all time: {answers.get('favoriteAlbum', 'Not provided')}
Current favorite song: {answers.get('currentSong', 'Not provided')}
Current favorite artist: {answers.get('currentArtist', 'Not provided')}
Guilty pleasure: {answers.get('guiltyPleasure', 'Not provided')}
Genres listened to most: {answers.get('genres', 'Not provided')}
"""
    
    name_str = f"{userName}'s" if userName else "This person's"
    
    prompt = f"""Analyze {name_str} music taste based on these answers:

{answers_text}

Provide:

1. A TASTE QUALITY SCORE from 0-100 based on:
   - Musical sophistication and depth of choices
   - Balance between accessible and adventurous
   - Era diversity (timeless classics vs. current favorites)
   - Artist choices (quality over popularity)
   - The guilty pleasure adds personality!
   - Overall cultural awareness

2. A detailed, fun analysis in this style: {style_instruction}

The analysis should cover:
- What their choices reveal about their personality and taste level
- Commentary on their favorite artists/albums (good choices or questionable?)
- Observations about genre preferences
- What the guilty pleasure says about them
- Overall verdict on how good their taste actually is

Format your response EXACTLY like this:
SCORE: [number 0-100]
ANALYSIS: [your detailed analysis{' using ' + userName if userName else ''}]

Remember: {style_instruction}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }],
        )
        
        response_text = message.content[0].text
        
        # Parse response
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
        
        return {
            "score": score,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "score": 0,
            "analysis": f"Sorry, something went wrong. Error: {str(e)}"
        }


def main():
    """Start the server"""
    
    # Check for API key
    if not API_KEY:
        print("\n" + "="*60)
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("="*60)
        print("\nYou need to set your API key as an environment variable.")
        print("\nOn Mac/Linux:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nOn Windows:")
        print("  set ANTHROPIC_API_KEY=your-key-here")
        print("\nThen run this script again.")
        print("="*60 + "\n")
        return
    
    # Start server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TasteCheckHandler)
    
    print("\n" + "="*60)
    print("🎵 TasteCheck Server Running!")
    print("="*60)
    print(f"\n✅ Open your browser to: http://localhost:{PORT}")
    print("\n💡 Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for using TasteCheck!\n")


if __name__ == '__main__':
    main()
