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

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
# Note: HuggingFace API key no longer needed - using Pollinations.ai instead

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Image generation API - Using Pollinations.ai (free, no API key needed)
POLLINATIONS_API_URL = "https://image.pollinations.ai/prompt/"

# YouTube Data API v3 configuration
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "groq_key_configured": bool(GROQ_API_KEY),
        "image_api": "pollinations.ai (no key needed)"
    })


if __name__ == '__main__':
    # Check if API keys are configured
    if not GROQ_API_KEY:
        print("WARNING: GROQ_API_KEY not found in environment variables")

    print("Image generation: Using Pollinations.ai (free, no API key needed)")
    app.run(debug=True, port=5000)
