"""
KinderKraft - Flask Backend with Database Integration
Includes: Story Generator, Study Assistant, Kids Challenge, User Authentication
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
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
from datetime import timedelta
import torch

# Local imports
from models import db, User, Story, StudySession, Quiz, QuizAttempt, KidsAssignment, KidsSubmission, VideoSearch
from database import init_database, get_database_url, seed_kids_assignments, create_test_user
from auth import register_auth_routes, get_current_user
from qwen_grader import get_grader

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# ========================================
# Configuration
# ========================================

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': int(os.getenv('SQLALCHEMY_POOL_SIZE', 10)),
    'pool_timeout': int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', 30)),
    'pool_recycle': int(os.getenv('SQLALCHEMY_POOL_RECYCLE', 1800)),  # 30 mins instead of 1 hour
    'max_overflow': int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 20)),
    'pool_pre_ping': True,  # Test connections before using them
}

# JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_EXPIRY_HOURS', 24)))
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')

# Flask
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'another-secret-key')

# CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Initialize extensions
jwt = JWTManager(app)
db_instance = init_database(app)

# Register authentication routes
register_auth_routes(app)

# API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# API URLs
POLLINATIONS_API_URL = "https://image.pollinations.ai/prompt/"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


# ========================================
# STORY GENERATOR ENDPOINTS (with database)
# ========================================

@app.route('/api/generate-story', methods=['POST'])
@jwt_required(optional=True)
def generate_story():
    """
    Generate a creative story using Groq API
    Saves to database if user is logged in
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Generate story
        story_prompt = f"""You are a creative storyteller. Write an engaging and imaginative story based on this prompt: "{prompt}"

The story should be:
- Between 500-1000 words
- Have a clear beginning, middle, and end
- Include vivid descriptions and engaging characters
- Be creative and captivating

Write the complete story now:"""

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": story_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=2000,
        )

        story = chat_completion.choices[0].message.content
        word_count = len(story.split())

        # Save to database if user is logged in
        story_id = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                new_story = Story(
                    user_id=user_id,
                    title=prompt[:100],  # First 100 chars as title
                    prompt=prompt,
                    story_text=story,
                    word_count=word_count
                )
                db.session.add(new_story)
                db.session.commit()
                story_id = new_story.id
                print(f"✅ Story saved to database (ID: {story_id})")
        except Exception as e:
            print(f"⚠️  Could not save story (user not logged in or error): {e}")
            db.session.rollback()

        return jsonify({
            "story": story,
            "story_id": story_id,
            "word_count": word_count,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate cover image using Pollinations.ai"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        image_prompt = f"book cover art: {prompt}, artistic, high quality"

        from urllib.parse import quote
        encoded_prompt = quote(image_prompt)

        image_url = f"{POLLINATIONS_API_URL}{encoded_prompt}?width=768&height=768&nologo=true&enhance=true"

        print(f"Requesting image from: {image_url[:100]}...")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                timeout = 60 + (attempt * 30)
                print(f"Attempt {attempt + 1}/{max_retries} with {timeout}s timeout...")

                response = requests.get(image_url, timeout=timeout)

                if response.status_code == 200:
                    import base64
                    image_bytes = response.content

                    if len(image_bytes) < 100:
                        raise Exception("Received invalid image data")

                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                    print("Image generated successfully!")
                    return jsonify({
                        "image_data": image_base64,
                        "success": True
                    })
                else:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return jsonify({
                            "error": f"Image generation failed with status {response.status_code}",
                            "success": False
                        }), response.status_code

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return jsonify({
                        "error": "Image generation timed out. Please try again.",
                        "success": False
                    }), 504

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/stories/save-image', methods=['POST'])
@jwt_required()
def save_story_image():
    """Save/update cover image for a story"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        story_id = data.get('story_id')
        image_data = data.get('image_data')

        if not story_id or not image_data:
            return jsonify({"error": "story_id and image_data required"}), 400

        story = Story.query.filter_by(id=story_id, user_id=user_id).first()
        if not story:
            return jsonify({"error": "Story not found"}), 404

        story.cover_image_data = image_data
        db.session.commit()

        return jsonify({"success": True, "message": "Image saved"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/create-pdf', methods=['POST'])
def create_pdf():
    """Create PDF with cover and story"""
    try:
        data = request.get_json()
        story = data.get('story', '')
        image_data_base64 = data.get('image_data', '')
        title = data.get('title', 'My Story')

        if not story or not image_data_base64:
            return jsonify({"error": "Story and image data are required"}), 400

        import base64
        image_bytes = base64.b64decode(image_data_base64)

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story_elements = []

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

        # Cover image
        img_buffer = BytesIO(image_bytes)
        pil_image = PILImage.open(img_buffer)

        page_width, page_height = letter
        img_width, img_height = pil_image.size
        aspect = img_height / float(img_width)

        display_width = page_width - 1*inch
        display_height = display_width * aspect

        if display_height > page_height - 2*inch:
            display_height = page_height - 2*inch
            display_width = display_height / aspect

        img_io = BytesIO()
        pil_image.save(img_io, format='PNG')
        img_io.seek(0)

        cover_image = Image(img_io, width=display_width, height=display_height)
        story_elements.append(Spacer(1, 1*inch))
        story_elements.append(cover_image)
        story_elements.append(PageBreak())

        # Story content
        story_elements.append(Spacer(1, 0.5*inch))
        story_elements.append(Paragraph(title, title_style))
        story_elements.append(Spacer(1, 0.3*inch))

        paragraphs = story.split('\n')
        for para in paragraphs:
            if para.strip():
                story_elements.append(Paragraph(para.strip(), body_style))
                story_elements.append(Spacer(1, 0.1*inch))

        doc.build(story_elements)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='story_with_cover.pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ========================================
# STORYBOOK GENERATOR ENDPOINTS (Hybrid: Pollinations + DreamShaper)
# ========================================

@app.route('/api/generate-storybook', methods=['POST'])
@jwt_required(optional=True)
def generate_storybook():
    """
    Generate an interactive storybook with 10 paragraphs and illustrations
    Supports both Pollinations (fast) and DreamShaper (premium quality)
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required", "success": False}), 400

        if not groq_client:
            return jsonify({"error": "Story generation service unavailable", "success": False}), 500

        print(f"Generating storybook for prompt: {prompt}")

        # Step 1: Generate story with title and 10 paragraphs
        story_prompt = f"""You are a children's storybook author. Create a magical storybook based on this theme: "{prompt}"

Requirements:
1. Generate a captivating story title
2. Write exactly 10 paragraphs
3. Each paragraph should be 90-110 words
4. Use simple, narrative, storybook-style language suitable for children
5. Make the story flow naturally with a beginning, middle, and end
6. Include vivid descriptions of scenes, characters, and settings

Format your response EXACTLY like this:
TITLE: [Your story title here]

PARAGRAPH 1:
[First paragraph here]

PARAGRAPH 2:
[Second paragraph here]

...continue for all 10 paragraphs...

PARAGRAPH 10:
[Tenth paragraph here]"""

        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a creative children's storybook author."},
                {"role": "user", "content": story_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=3000
        )

        story_text = completion.choices[0].message.content
        
        # Parse the story
        lines = story_text.strip().split('\n')
        title = ""
        paragraphs = []
        current_paragraph = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('PARAGRAPH'):
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
            elif line and not line.startswith('PARAGRAPH'):
                current_paragraph += " " + line

        # Add the last paragraph
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())

        # Ensure we have exactly 10 paragraphs
        if len(paragraphs) < 10:
            return jsonify({
                "error": f"Story generation incomplete. Only {len(paragraphs)} paragraphs generated.",
                "success": False
            }), 500

        paragraphs = paragraphs[:10]  # Take first 10 if more

        print(f"Story generated: {title}")
        print(f"Paragraphs: {len(paragraphs)}")

        # Step 2: Generate images for each paragraph using SD v1.5
        images = []
        print("Generating images with Stable Diffusion v1.5 (local model)...")
        
        try:
            from sd_v15_generator import get_generator
            generator = get_generator()
            
            for idx, paragraph in enumerate(paragraphs, 1):
                print(f"Generating image {idx}/10 with SD v1.5...")
                
                # Summarize paragraph to 20-30 words for clear prompts
                words = paragraph.split()[:25]  # Take first ~25 words
                scene_summary = ' '.join(words).replace('\n', ' ').strip()
                
                # Highly realistic prompt with photorealistic quality
                enhanced_prompt = (
                    f"{scene_summary}, "
                    "photorealistic, hyperrealistic, ultra detailed, "
                    "8k quality, realistic lighting and shadows, "
                    "full scene view, wide angle, everything in frame, "
                    "natural colors, detailed textures, "
                    "professional photography quality, cinematic"
                )
                
                # Negative prompt for clean realistic results
                negative_prompt = (
                    "illustration, painting, drawing, sketch, cartoon, anime, "
                    "cropped, cut off, out of frame, partial view, "
                    "dark, scary, horror, "
                    "blurry, low quality, grainy, pixelated, "
                    "text, watermark, signature, "
                    "bad anatomy, deformed, distorted, ugly, "
                    "artificial, fake looking, oversaturated"
                )
                
                # Generate with high quality settings for realistic images
                image_base64 = generator.generate_image_base64(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=35,  # More steps for better quality
                    guidance_scale=7.5,      # Standard guidance
                    width=1024,              # High resolution for realism
                    height=1024
                )
                
                images.append(image_base64)
                print(f"✓ Image {idx}/10 complete")
                
                # Clear CUDA cache between images
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
        except Exception as e:
            print(f"SD-Turbo error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Image generation failed: {str(e)}",
                "success": False
            }), 500

        # Save to database if user is logged in
        user_id = None
        try:
            user_id = get_jwt_identity()
        except:
            pass

        if user_id:
            try:
                full_story = '\n\n'.join(paragraphs)
                story_record = Story(
                    user_id=user_id,
                    prompt=prompt,
                    story_text=full_story,
                    title=title
                )
                db.session.add(story_record)
                db.session.commit()
                print(f"Storybook saved to database for user {user_id}")
            except Exception as e:
                print(f"Error saving storybook to database: {str(e)}")

        return jsonify({
            "success": True,
            "title": title,
            "paragraphs": paragraphs,
            "images": images
        })

    except Exception as e:
        print(f"Error generating storybook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/stories/my-stories', methods=['GET'])
@jwt_required()
def get_my_stories():
    """Get all stories for logged-in user"""
    try:
        user_id = get_jwt_identity()
        stories = Story.query.filter_by(user_id=user_id).order_by(Story.created_at.desc()).all()

        return jsonify({
            "success": True,
            "stories": [story.to_dict() for story in stories],
            "total": len(stories)
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ========================================
# STUDY ASSISTANT ENDPOINTS (with database)
# ========================================

@app.route('/api/summarize', methods=['POST'])
@jwt_required(optional=True)
def summarize_text():
    """Summarize text and save to database"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        prompt = f"""Summarize the following text in 3-5 clear bullet points suitable for a student. Make it concise and easy to understand:

{text}

Provide the summary as bullet points."""

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1000,
        )

        summary = chat_completion.choices[0].message.content

        # Save to database if logged in
        session_id = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                topic = text[:100]  # First 100 chars as topic
                session = StudySession(
                    user_id=user_id,
                    topic=topic,
                    input_text=text,
                    mode='summarize',
                    output_text=summary
                )
                db.session.add(session)
                db.session.commit()
                session_id = session.id
        except:
            db.session.rollback()

        return jsonify({
            "summary": summary,
            "session_id": session_id,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/explain', methods=['POST'])
@jwt_required(optional=True)
def explain_concept():
    """Explain concept and save to database"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        prompt = f"""Explain the following concept in detail for a student. Your explanation should include:

1. A simple, clear definition
2. Key points to understand
3. Real-world examples
4. Analogies if helpful
5. Why this is important

Concept/Text:
{text}

Provide a comprehensive but easy-to-understand explanation."""

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=2000,
        )

        explanation = chat_completion.choices[0].message.content

        # Save to database
        session_id = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                topic = text[:100]
                session = StudySession(
                    user_id=user_id,
                    topic=topic,
                    input_text=text,
                    mode='explain',
                    output_text=explanation
                )
                db.session.add(session)
                db.session.commit()
                session_id = session.id
        except:
            db.session.rollback()

        return jsonify({
            "explanation": explanation,
            "session_id": session_id,
            "success": True
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/generate-revision', methods=['POST'])
@jwt_required(optional=True)
def generate_revision():
    """Generate MCQs and Q&A, save to database"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "Text is required"}), 400

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

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=3000,
        )

        response_text = chat_completion.choices[0].message.content

        import json
        import re

        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()

        try:
            revision_data = json.loads(response_text)

            if 'mcqs' not in revision_data or 'qas' not in revision_data:
                raise ValueError("Invalid JSON structure")

            revision_data['mcqs'] = revision_data['mcqs'][:10]
            revision_data['qas'] = revision_data['qas'][:5]

            # Save to database
            quiz_id = None
            try:
                user_id = get_jwt_identity()
                if user_id:
                    topic = text[:100]
                    quiz = Quiz(
                        user_id=user_id,
                        topic=topic,
                        input_text=text,
                        mcqs=revision_data['mcqs'],
                        qas=revision_data['qas']
                    )
                    db.session.add(quiz)
                    db.session.commit()
                    quiz_id = quiz.id
            except:
                db.session.rollback()

            return jsonify({
                "mcqs": revision_data['mcqs'],
                "qas": revision_data['qas'],
                "quiz_id": quiz_id,
                "success": True
            })

        except json.JSONDecodeError:
            return jsonify({
                "error": "Failed to parse revision questions. Please try again.",
                "raw_response": response_text,
                "success": False
            }), 500

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/quiz/submit-score', methods=['POST'])
@jwt_required()
def submit_quiz_score():
    """Submit quiz score"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        quiz_id = data.get('quiz_id')
        mcq_score = data.get('mcq_score')
        mcq_total = data.get('mcq_total')
        answers = data.get('answers')

        if not quiz_id or mcq_score is None:
            return jsonify({"error": "quiz_id and mcq_score required"}), 400

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            mcq_score=mcq_score,
            mcq_total=mcq_total,
            answers=answers
        )
        db.session.add(attempt)
        db.session.commit()

        return jsonify({
            "success": True,
            "attempt_id": attempt.id,
            "message": "Score saved"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/study/history', methods=['GET'])
@jwt_required()
def get_study_history():
    """Get study history for user"""
    try:
        user_id = get_jwt_identity()

        sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.created_at.desc()).limit(20).all()
        quizzes = Quiz.query.filter_by(user_id=user_id).order_by(Quiz.created_at.desc()).limit(20).all()

        return jsonify({
            "success": True,
            "sessions": [s.to_dict() for s in sessions],
            "quizzes": [q.to_dict() for q in quizzes]
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ========================================
# VIDEO SEARCH ENDPOINTS (with database)
# ========================================

@app.route('/api/find-videos', methods=['POST'])
@jwt_required(optional=True)
def find_educational_videos():
    """Find educational YouTube videos and save to database"""
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

        # Extract topic using Groq
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

        # Search YouTube with educational filters
        educational_keywords = f"{topic} explained tutorial educational lesson"

        params = {
            'part': 'snippet',
            'q': educational_keywords,
            'type': 'video',
            'videoEmbeddable': 'true',
            'videoSyndicated': 'true',
            'safeSearch': 'strict',
            'relevanceLanguage': 'en',
            'maxResults': 3,
            'order': 'relevance',
            'videoDuration': 'medium',
            'key': YOUTUBE_API_KEY
        }

        response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)

        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_message = error_data.get('error', {}).get('message', 'YouTube API error')

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

        for item in youtube_data.get('items', []):
            video_id = item['id'].get('videoId')
            if not video_id:
                continue

            snippet = item['snippet']
            title = snippet.get('title', '').lower()
            description = snippet.get('description', '').lower()

            # Skip non-educational content
            skip_keywords = ['game', 'gaming', 'funny', 'prank', 'vlog', 'challenge', 'reaction']
            if any(keyword in title or keyword in description for keyword in skip_keywords):
                continue

            video_data = {
                'video_id': video_id,
                'title': snippet.get('title', 'Untitled'),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'description': snippet.get('description', '')[:200],
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'published_at': snippet.get('publishedAt', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }

            videos.append(video_data)

        if not videos:
            return jsonify({
                "error": "No suitable educational videos found. Try a different topic.",
                "success": False,
                "topic": topic
            }), 404

        # Save to database
        search_id = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                search = VideoSearch(
                    user_id=user_id,
                    input_text=text,
                    extracted_topic=topic,
                    videos=videos[:3]
                )
                db.session.add(search)
                db.session.commit()
                search_id = search.id
        except:
            db.session.rollback()

        print(f"Found {len(videos)} educational videos for topic: {topic}")

        return jsonify({
            "topic": topic,
            "videos": videos[:3],
            "search_id": search_id,
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
# KIDS CHALLENGE ENDPOINTS (with database)
# ========================================

@app.route('/api/kids/assignments', methods=['GET'])
def get_assignments():
    """Get all active assignments for Kids Creative Challenge"""
    try:
        active_assignments = KidsAssignment.query.filter_by(is_active=True).all()

        return jsonify({
            "assignments": [a.to_dict() for a in active_assignments],
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get a specific assignment by ID"""
    try:
        assignment = KidsAssignment.query.get(assignment_id)

        if not assignment:
            return jsonify({
                "error": "Assignment not found",
                "success": False
            }), 404

        return jsonify({
            "assignment": assignment.to_dict(),
            "success": True
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/submit', methods=['POST'])
@jwt_required(optional=True)
def submit_assignment():
    """
    Submit an assignment for AI grading using local Qwen2-VL-2B-Instruct model.
    Saves submission to database.
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
        assignment = KidsAssignment.query.get(assignment_id)
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

            # Analyze and grade using Qwen2-VL model
            grading_result = grader.analyze_image(
                image_bytes=image_bytes,
                assignment_title=assignment.title,
                assignment_description=assignment.description,
                assignment_criteria=assignment.criteria
            )

            # Extract results
            image_description = grading_result.get('description', 'Creative work detected')
            score = grading_result.get('score', 7.5)
            feedback = grading_result.get('feedback', 'Great effort!')
            improvement = grading_result.get('improvement', 'Keep practicing and being creative!')

            print(f"Qwen2-VL grading complete: Score={score}/10")

            # Color analysis
            from collections import Counter
            img_buffer = BytesIO(image_bytes)
            img = PILImage.open(img_buffer)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            colors_found = []
            width, height = img.size
            step = 20
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
        points_earned = int(score * 10)

        # Get user_id if logged in
        user_id = None
        try:
            user_id = get_jwt_identity()
        except:
            pass

        # Store submission in database
        week = time.strftime("%Y-W%U")
        submission = KidsSubmission(
            assignment_id=assignment_id,
            user_id=user_id,
            child_name=child_name,
            score=score,
            points_earned=points_earned,
            feedback=feedback,
            improvement=improvement,
            vision_description=image_description,
            week=week
        )

        db.session.add(submission)
        
        # Use flush() to get the ID without committing yet
        # This avoids accessing submission.id after a potentially failed commit
        try:
            db.session.flush()
            submission_id = submission.id
            db.session.commit()
            print(f"✅ Submission saved to database (ID: {submission_id})")
        except Exception as db_error:
            db.session.rollback()
            print(f"⚠️ Database error: {str(db_error)}")
            # Try one more time with a fresh connection
            try:
                db.session.add(submission)
                db.session.flush()
                submission_id = submission.id
                db.session.commit()
                print(f"✅ Submission saved on retry (ID: {submission_id})")
            except Exception as retry_error:
                db.session.rollback()
                print(f"❌ Failed to save submission after retry: {str(retry_error)}")
                submission_id = None

        # Create labels from description
        labels = [{"label": word, "confidence": 0.9} for word in image_description.split()[:5]]

        return jsonify({
            "score": score,
            "points_earned": points_earned,
            "feedback": feedback,
            "improvement": improvement,
            "vision_description": image_description,
            "labels_detected": labels,
            "colors_detected": colors[:3],
            "submission_id": submission_id,
            "success": True
        })

    except Exception as e:
        print(f"Error grading submission: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/kids/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard for current week"""
    try:
        current_week = time.strftime("%Y-W%U")

        # Get all submissions for current week
        submissions = KidsSubmission.query.filter_by(week=current_week).all()

        # Aggregate by child name
        leaderboard_dict = {}
        for sub in submissions:
            name = sub.child_name
            if name not in leaderboard_dict:
                leaderboard_dict[name] = {
                    "name": name,
                    "total_points": 0,
                    "submissions": 0,
                    "average_score": 0
                }

            leaderboard_dict[name]['total_points'] += sub.points_earned
            leaderboard_dict[name]['submissions'] += 1

        # Calculate average scores
        for entry in leaderboard_dict.values():
            entry['average_score'] = round(
                entry['total_points'] / entry['submissions'] / 10, 1
            )

        # Sort by total points (descending)
        leaderboard = sorted(
            leaderboard_dict.values(),
            key=lambda x: x['total_points'],
            reverse=True
        )

        # Add rankings
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1

        return jsonify({
            "leaderboard": leaderboard[:10],
            "period": "weekly",
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
    """Get all submissions for a specific child"""
    try:
        submissions = KidsSubmission.query.filter_by(
            child_name=child_name
        ).order_by(KidsSubmission.submitted_at.desc()).all()

        # Calculate total stats
        total_points = sum(s.points_earned for s in submissions)
        avg_score = sum(float(s.score) for s in submissions) / len(submissions) if submissions else 0

        return jsonify({
            "submissions": [s.to_dict() for s in submissions],
            "total_submissions": len(submissions),
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

    # Test database connection
    db_status = "connected"
    try:
        db.session.execute(db.text('SELECT 1'))
    except:
        db_status = "error"

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "groq_key_configured": bool(GROQ_API_KEY),
        "youtube_key_configured": bool(YOUTUBE_API_KEY),
        "image_api": "pollinations.ai (no key needed)",
        "kids_grading": "Local Qwen2-VL-2B-Instruct",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "cuda_available": torch.cuda.is_available()
    })


# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    with app.app_context():
        # Create test user if enabled
        if os.getenv('CREATE_TEST_USER', 'False').lower() == 'true':
            create_test_user()

    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"""
========================================
🚀 AI Creative Suite Backend Starting
========================================
Database: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}@***
JWT Enabled: ✅
CORS Origins: {cors_origins}
Server: http://{host}:{port}
========================================
    """)

    app.run(host=host, port=port, debug=debug)
