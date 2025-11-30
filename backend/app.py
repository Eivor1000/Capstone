from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from groq import Groq
import requests
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from PIL import Image as PILImage
from dotenv import load_dotenv
import time
from qwen_grader import get_grader

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
# Note: Using local Qwen2-VL-2B-Instruct model for kids challenge image grading

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Image generation API - Using Pollinations.ai (free, no API key needed)
POLLINATIONS_API_URL = "https://image.pollinations.ai/prompt/"

# YouTube Data API v3 configuration
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"

# In-memory storage for Kids Challenge (replace with database in production)
assignments_db = [
    {
        "id": 1,
        "title": "Rainbow Coloring",
        "description": "Color a beautiful rainbow with all 7 colors! Be creative and use bright colors.",
        "type": "coloring",
        "points_possible": 100,
        "difficulty": "easy",
        "criteria": "Use all 7 rainbow colors (red, orange, yellow, green, blue, indigo, violet). Stay within the lines. Use bright, vibrant colors.",
        "image_url": "https://via.placeholder.com/400x300?text=Rainbow+Template",
        "active": True
    },
    {
        "id": 2,
        "title": "Paper Plate Fish",
        "description": "Create a colorful fish using a paper plate, colors, and decorations!",
        "type": "craft",
        "points_possible": 100,
        "difficulty": "medium",
        "criteria": "Use a paper plate as the fish body. Add fins and tail. Decorate with colors, patterns, or glitter. Be creative!",
        "image_url": "https://via.placeholder.com/400x300?text=Fish+Example",
        "active": True
    },
    {
        "id": 3,
        "title": "Draw Your Dream House",
        "description": "Draw the house of your dreams! What would it look like?",
        "type": "drawing",
        "points_possible": 100,
        "difficulty": "medium",
        "criteria": "Include doors, windows, and a roof. Add colors and details. Be imaginative!",
        "image_url": "https://via.placeholder.com/400x300?text=House+Example",
        "active": True
    }
]

submissions_db = []
leaderboard_db = {}


@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """
    Generate a creative story using Groq API with llama-3.3-70b-versatile model.
    Expects JSON: {"prompt": "story prompt"}
    Returns: {"story": "generated story text"}
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Create a detailed prompt for story generation
        story_prompt = f"""You are a creative storyteller. Write an engaging and imaginative story based on this prompt: "{prompt}"

The story should be:
- Between 500-1000 words
- Have a clear beginning, middle, and end
- Include vivid descriptions and engaging characters
- Be creative and captivating

Write the complete story now:"""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": story_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=2000,
        )

        story = chat_completion.choices[0].message.content

        return jsonify({
            "story": story,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    Generate a cover image using Pollinations.ai (free, no API key needed).
    Expects JSON: {"prompt": "image description"}
    Returns: {"image_url": "base64 encoded image"}
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Create a book cover-focused prompt (keep it shorter for faster generation)
        image_prompt = f"book cover art: {prompt}, artistic, high quality"

        # URL encode the prompt for Pollinations.ai
        from urllib.parse import quote
        encoded_prompt = quote(image_prompt)

        # Pollinations.ai API - GET request returns image directly
        # Using smaller size for faster generation
        image_url = f"{POLLINATIONS_API_URL}{encoded_prompt}?width=768&height=768&nologo=true&enhance=true"

        print(f"Requesting image from: {image_url[:100]}...")

        # Try multiple times with increasing timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Increase timeout progressively
                timeout = 60 + (attempt * 30)  # 60s, 90s, 120s
                print(f"Attempt {attempt + 1}/{max_retries} with {timeout}s timeout...")

                response = requests.get(image_url, timeout=timeout)

                if response.status_code == 200:
                    # Convert image to base64 for transmission
                    import base64
                    image_bytes = response.content

                    # Verify it's actually an image
                    if len(image_bytes) < 100:
                        raise Exception("Received invalid image data")

                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                    print("Image generated successfully!")
                    return jsonify({
                        "image_data": image_base64,
                        "success": True
                    })
                else:
                    print(f"Failed with status {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        return jsonify({
                            "error": f"Image generation failed with status {response.status_code}",
                            "success": False
                        }), response.status_code

            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    return jsonify({
                        "error": "Image generation timed out. The service might be busy. Please try again.",
                        "success": False
                    }), 504

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/create-pdf', methods=['POST'])
def create_pdf():
    """
    Create a PDF with cover image on page 1 and story text on subsequent pages.
    Expects JSON: {"story": "story text", "image_data": "base64 image", "title": "Story Title"}
    Returns: PDF file for download
    """
    try:
        data = request.get_json()
        story = data.get('story', '')
        image_data_base64 = data.get('image_data', '')
        title = data.get('title', 'My Story')

        if not story or not image_data_base64:
            return jsonify({"error": "Story and image data are required"}), 400

        # Decode base64 image
        import base64
        image_bytes = base64.b64decode(image_data_base64)

        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story_elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='darkblue',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=12,
            leading=18,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Times-Roman'
        )

        # PAGE 1: Cover Image (full page)
        # Save image temporarily to use with reportlab
        img_buffer = BytesIO(image_bytes)
        pil_image = PILImage.open(img_buffer)

        # Resize image to fit page while maintaining aspect ratio
        page_width, page_height = letter
        img_width, img_height = pil_image.size
        aspect = img_height / float(img_width)

        # Make image fill most of the page
        display_width = page_width - 1*inch
        display_height = display_width * aspect

        # If height is too large, scale by height instead
        if display_height > page_height - 2*inch:
            display_height = page_height - 2*inch
            display_width = display_height / aspect

        # Save PIL image to BytesIO for reportlab
        img_io = BytesIO()
        pil_image.save(img_io, format='PNG')
        img_io.seek(0)

        # Add cover image centered on page
        cover_image = Image(img_io, width=display_width, height=display_height)
        story_elements.append(Spacer(1, 1*inch))
        story_elements.append(cover_image)

        # Page break before story content
        story_elements.append(PageBreak())

        # PAGE 2+: Story Title and Text
        story_elements.append(Spacer(1, 0.5*inch))
        story_elements.append(Paragraph(title, title_style))
        story_elements.append(Spacer(1, 0.3*inch))

        # Add story paragraphs
        # Split story into paragraphs
        paragraphs = story.split('\n')
        for para in paragraphs:
            if para.strip():
                story_elements.append(Paragraph(para.strip(), body_style))
                story_elements.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story_elements)

        # Get PDF bytes
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='story_with_cover.pdf'
        )

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    """
    Summarize text for students using Groq API.
    Expects JSON: {"text": "paragraph to summarize"}
    Returns: {"summary": "summarized text"}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Create summarization prompt
        prompt = f"""Summarize the following text in 3-5 clear bullet points suitable for a student. Make it concise and easy to understand:

{text}

Provide the summary as bullet points."""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1000,
        )

        summary = chat_completion.choices[0].message.content

        return jsonify({
            "summary": summary,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/explain', methods=['POST'])
def explain_concept():
    """
    Provide detailed explanation with examples using Groq API.
    Expects JSON: {"text": "concept to explain"}
    Returns: {"explanation": "detailed explanation"}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Create explanation prompt
        prompt = f"""Explain the following concept in detail for a student. Your explanation should include:

1. A simple, clear definition
2. Key points to understand
3. Real-world examples
4. Analogies if helpful
5. Why this is important

Concept/Text:
{text}

Provide a comprehensive but easy-to-understand explanation."""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=2000,
        )

        explanation = chat_completion.choices[0].message.content

        return jsonify({
            "explanation": explanation,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/generate-revision', methods=['POST'])
def generate_revision():
    """
    Generate MCQs and Q&A pairs for revision using Groq API.
    Expects JSON: {"text": "content to create questions from"}
    Returns: {"mcqs": [...], "qas": [...]}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Create revision questions prompt
        prompt = f"""Based on the following text, generate revision materials for a student:

Text:
{text}

Generate:
1. 7-10 multiple choice questions (MCQs) with 4 options each
2. 5 short answer questions with detailed answers

Format your response EXACTLY as JSON (no markdown, no code blocks, just pure JSON):
{{
  "mcqs": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Why this answer is correct"
    }}
  ],
  "qas": [
    {{
      "question": "Question text here?",
      "answer": "Detailed answer here"
    }}
  ]
}}

Make sure the questions test understanding, not just memorization."""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=3000,
        )

        response_text = chat_completion.choices[0].message.content

        # Try to parse JSON from response
        import json
        import re

        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()

        try:
            revision_data = json.loads(response_text)

            # Validate structure
            if 'mcqs' not in revision_data or 'qas' not in revision_data:
                raise ValueError("Invalid JSON structure")

            # Limit to max 10 MCQs and 5 QAs
            revision_data['mcqs'] = revision_data['mcqs'][:10]
            revision_data['qas'] = revision_data['qas'][:5]

            return jsonify({
                "mcqs": revision_data['mcqs'],
                "qas": revision_data['qas'],
                "success": True
            })

        except json.JSONDecodeError as je:
            # Fallback: return text-based response
            print(f"JSON parse error: {je}")
            print(f"Response was: {response_text}")
            return jsonify({
                "error": "Failed to parse revision questions. Please try again.",
                "raw_response": response_text,
                "success": False
            }), 500

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/find-videos', methods=['POST'])
def find_educational_videos():
    """
    Find educational YouTube videos using YouTube Data API v3.
    EDUCATIONAL USE ONLY - includes safety filters and content restrictions.
    Expects JSON: {"text": "topic or paragraph to extract topic from"}
    Returns: {"topic": "extracted topic", "videos": [...]}
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        if not YOUTUBE_API_KEY:
            return jsonify({
                "error": "YouTube API not configured. Please add YOUTUBE_API_KEY to .env file.",
                "success": False
            }), 503

        # Step 1: Extract main topic using Groq
        topic_prompt = f"""Extract the main educational topic from this text. Return ONLY 2-4 words representing the core subject for searching educational videos.

Text: {text}

Topic:"""

        topic_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": topic_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=50,
        )

        topic = topic_completion.choices[0].message.content.strip()
        print(f"Extracted topic: {topic}")

        # Step 2: Search YouTube with educational filters
        # Educational channels whitelist for better quality
        educational_keywords = f"{topic} explained tutorial educational lesson"

        params = {
            'part': 'snippet',
            'q': educational_keywords,
            'type': 'video',
            'videoEmbeddable': 'true',  # Only embeddable videos
            'videoSyndicated': 'true',  # Only videos that can be played outside YouTube
            'safeSearch': 'strict',  # IMPORTANT: Strict safety filter
            'relevanceLanguage': 'en',  # English content
            'maxResults': 3,  # Only 3 videos as requested
            'order': 'relevance',  # Most relevant first
            'videoDuration': 'medium',  # 4-20 minutes (good for learning)
            'key': YOUTUBE_API_KEY
        }

        # Call YouTube Data API
        response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_message = error_data.get('error', {}).get('message', 'YouTube API error')

            # Handle quota exceeded
            if response.status_code == 403 and 'quota' in error_message.lower():
                return jsonify({
                    "error": "Daily YouTube search quota exceeded. Please try again tomorrow.",
                    "success": False,
                    "fallback_url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial"
                }), 429

            return jsonify({
                "error": f"YouTube API error: {error_message}",
                "success": False
            }), response.status_code

        youtube_data = response.json()
        videos = []

        # Parse YouTube response
        for item in youtube_data.get('items', []):
            video_id = item['id'].get('videoId')
            if not video_id:
                continue

            snippet = item['snippet']

            # Additional safety check: Skip if title/description contains inappropriate keywords
            title = snippet.get('title', '').lower()
            description = snippet.get('description', '').lower()

            # Skip non-educational content indicators
            skip_keywords = ['game', 'gaming', 'funny', 'prank', 'vlog', 'challenge', 'reaction']
            if any(keyword in title or keyword in description for keyword in skip_keywords):
                continue

            video_data = {
                'video_id': video_id,
                'title': snippet.get('title', 'Untitled'),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'description': snippet.get('description', '')[:200],  # First 200 chars
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'published_at': snippet.get('publishedAt', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }

            videos.append(video_data)

        # If no videos found after filtering, return error
        if not videos:
            return jsonify({
                "error": "No suitable educational videos found. Try a different topic.",
                "success": False,
                "topic": topic
            }), 404

        print(f"Found {len(videos)} educational videos for topic: {topic}")

        return jsonify({
            "topic": topic,
            "videos": videos[:3],  # Ensure max 3 videos
            "success": True,
            "educational_use_notice": "These videos are for educational purposes only."
        })

    except Exception as e:
        print(f"Error finding videos: {str(e)}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


# ========================================
# KIDS CREATIVE CHALLENGE ENDPOINTS
# ========================================

@app.route('/api/kids/assignments', methods=['GET'])
def get_assignments():
    """
    Get all active assignments for Kids Creative Challenge.
    Returns: {"assignments": [...]}
    """
    try:
        # Filter only active assignments
        active_assignments = [a for a in assignments_db if a.get('active', True)]

        return jsonify({
            "assignments": active_assignments,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """
    Get a specific assignment by ID.
    Returns: {"assignment": {...}}
    """
    try:
        assignment = next((a for a in assignments_db if a['id'] == assignment_id), None)

        if not assignment:
            return jsonify({
                "error": "Assignment not found",
                "success": False
            }), 404

        return jsonify({
            "assignment": assignment,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/submit', methods=['POST'])
def submit_assignment():
    """
    Submit an assignment for AI grading using local Qwen2-VL-2B-Instruct model.
    Expects JSON: {
        "assignment_id": 1,
        "child_name": "Emma",
        "image_data": "base64 encoded image"
    }
    Returns: {
        "score": 8.5,
        "points_earned": 85,
        "feedback": "Great job! ...",
        "improvements": "Try to...",
        "labels_detected": [...],
        "colors_detected": [...]
    }
    """
    try:
        data = request.get_json()
        assignment_id = data.get('assignment_id')
        child_name = data.get('child_name', 'Anonymous')
        image_data_base64 = data.get('image_data', '')

        if not assignment_id or not image_data_base64:
            return jsonify({
                "error": "Assignment ID and image data are required",
                "success": False
            }), 400

        # Get assignment details
        assignment = next((a for a in assignments_db if a['id'] == assignment_id), None)
        if not assignment:
            return jsonify({
                "error": "Assignment not found",
                "success": False
            }), 404

        # Decode base64 image
        import base64
        image_bytes = base64.b64decode(image_data_base64)

        print(f"Analyzing image with local Qwen2-VL-2B-Instruct model...")

        try:
            # Get Qwen grader instance
            grader = get_grader()

            # Analyze and grade using Qwen2-VL model (replaces both vision and grading models)
            grading_result = grader.analyze_image(
                image_bytes=image_bytes,
                assignment_title=assignment['title'],
                assignment_description=assignment['description'],
                assignment_criteria=assignment['criteria']
            )

            # Extract results
            image_description = grading_result.get('description', 'Creative work detected')
            score = grading_result.get('score', 7.5)
            feedback = grading_result.get('feedback', 'Great effort!')
            improvement = grading_result.get('improvement', 'Keep practicing and being creative!')

            print(f"Qwen2-VL grading complete: Score={score}/10")

            # Also do basic color analysis with Pillow as supplementary data
            from collections import Counter
            img_buffer = BytesIO(image_bytes)
            img = PILImage.open(img_buffer)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Quick color sampling
            colors_found = []
            width, height = img.size
            step = 20  # Sample fewer pixels for speed
            for x in range(0, width, step):
                for y in range(0, height, step):
                    r, g, b = img.getpixel((x, y))
                    colors_found.append((r, g, b))

            color_counter = Counter(colors_found)
            most_common_colors = color_counter.most_common(3)

            colors = []
            for (r, g, b), count in most_common_colors:
                colors.append({
                    "rgb": f"rgb({r}, {g}, {b})",
                    "percentage": round((count / len(colors_found)) * 100, 1)
                })

        except Exception as e:
            print(f"Error with Qwen2-VL analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"AI grading failed: {str(e)}",
                "success": False
            }), 500

        # Calculate points earned
        points_earned = int(score * 10)  # Score of 8.5 = 85 points

        # Store submission
        submission = {
            "id": len(submissions_db) + 1,
            "assignment_id": assignment_id,
            "child_name": child_name,
            "score": score,
            "points_earned": points_earned,
            "feedback": feedback,
            "improvement": improvement,
            "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "week": time.strftime("%Y-W%U"),  # Year-Week format for leaderboard
        }
        submissions_db.append(submission)

        # Update leaderboard
        week_key = submission['week']
        if week_key not in leaderboard_db:
            leaderboard_db[week_key] = {}

        if child_name not in leaderboard_db[week_key]:
            leaderboard_db[week_key][child_name] = {
                "total_points": 0,
                "submissions": 0,
                "average_score": 0
            }

        leaderboard_db[week_key][child_name]['total_points'] += points_earned
        leaderboard_db[week_key][child_name]['submissions'] += 1
        leaderboard_db[week_key][child_name]['average_score'] = (
            leaderboard_db[week_key][child_name]['total_points'] /
            leaderboard_db[week_key][child_name]['submissions']
        ) / 10  # Convert back to 0-10 scale

        # Create labels from the image description for display
        labels = [{"label": word, "confidence": 0.9} for word in image_description.split()[:5]]

        return jsonify({
            "score": score,
            "points_earned": points_earned,
            "feedback": feedback,
            "improvement": improvement,
            "vision_description": image_description,  # Full AI description
            "labels_detected": labels,  # Simplified labels for UI
            "colors_detected": colors[:3],   # Top 3 colors
            "success": True
        })

    except Exception as e:
        print(f"Error grading submission: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get leaderboard for current week.
    Query params: ?period=weekly (default) or monthly
    Returns: {"leaderboard": [...], "period": "weekly"}
    """
    try:
        period = request.args.get('period', 'weekly')
        current_week = time.strftime("%Y-W%U")

        # Get data for current week
        week_data = leaderboard_db.get(current_week, {})

        # Convert to list and sort by total points
        leaderboard = []
        for name, stats in week_data.items():
            leaderboard.append({
                "name": name,
                "total_points": stats['total_points'],
                "submissions": stats['submissions'],
                "average_score": round(stats['average_score'], 1)
            })

        # Sort by total points (descending)
        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)

        # Add rankings
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1

        # Return top 10 (or all if less than 10)
        return jsonify({
            "leaderboard": leaderboard[:10],
            "period": period,
            "week": current_week,
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/my-submissions/<child_name>', methods=['GET'])
def get_child_submissions(child_name):
    """
    Get all submissions for a specific child.
    Returns: {"submissions": [...]}
    """
    try:
        child_submissions = [
            s for s in submissions_db
            if s['child_name'].lower() == child_name.lower()
        ]

        # Sort by most recent first
        child_submissions.sort(key=lambda x: x['submitted_at'], reverse=True)

        # Calculate total stats
        total_points = sum(s['points_earned'] for s in child_submissions)
        avg_score = sum(s['score'] for s in child_submissions) / len(child_submissions) if child_submissions else 0

        return jsonify({
            "submissions": child_submissions,
            "total_submissions": len(child_submissions),
            "total_points": total_points,
            "average_score": round(avg_score, 1),
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


# ========================================
# HEALTH CHECK
# ========================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    import torch
    return jsonify({
        "status": "healthy",
        "groq_key_configured": bool(GROQ_API_KEY),
        "youtube_key_configured": bool(YOUTUBE_API_KEY),
        "image_api": "pollinations.ai (no key needed)",
        "kids_grading": "Local Qwen2-VL-2B-Instruct",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "cuda_available": torch.cuda.is_available()
    })


if __name__ == '__main__':
    # Check if API keys are configured
    if not GROQ_API_KEY:
        print("WARNING: GROQ_API_KEY not found in environment variables")

    print("Image generation: Using Pollinations.ai (free, no API key needed)")
    app.run(debug=True, port=5000)
