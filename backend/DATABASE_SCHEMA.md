# Database Schema Design

## Overview
PostgreSQL database schema for AI Creative Suite with user authentication and full data persistence.

---

## Tables

### 1. **users** (User Authentication & Profile)
Primary table for user accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique user ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Unique username |
| email | VARCHAR(100) | UNIQUE, NOT NULL | User email |
| phone | VARCHAR(20) | UNIQUE | Phone number |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| full_name | VARCHAR(100) | | User's full name |
| age | INTEGER | | User's age |
| profile_image | TEXT | | Base64 or URL to profile image |
| role | VARCHAR(20) | DEFAULT 'user' | 'user', 'parent', 'teacher', 'admin' |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| last_login | TIMESTAMP | | Last login timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |

**Indexes:**
- `idx_users_username` on `username`
- `idx_users_email` on `email`

---

### 2. **stories** (Story Generator Feature)
Stores all generated stories with cover images.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique story ID |
| user_id | INTEGER | FOREIGN KEY → users(id) | Story owner |
| title | VARCHAR(200) | | Story title (auto-generated or custom) |
| prompt | TEXT | NOT NULL | Original user prompt |
| story_text | TEXT | NOT NULL | Generated story content |
| cover_image_data | TEXT | | Base64 encoded cover image |
| word_count | INTEGER | | Story word count |
| created_at | TIMESTAMP | DEFAULT NOW() | Generation timestamp |
| is_favorite | BOOLEAN | DEFAULT FALSE | User marked as favorite |

**Indexes:**
- `idx_stories_user_id` on `user_id`
- `idx_stories_created_at` on `created_at`

---

### 3. **study_sessions** (Study Assistant - Topics)
Main study sessions for summaries and explanations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique session ID |
| user_id | INTEGER | FOREIGN KEY → users(id) | Student user |
| topic | VARCHAR(200) | NOT NULL | Topic/title |
| input_text | TEXT | NOT NULL | Original text submitted |
| mode | VARCHAR(20) | NOT NULL | 'summarize', 'explain' |
| output_text | TEXT | NOT NULL | AI generated response |
| created_at | TIMESTAMP | DEFAULT NOW() | Session timestamp |

**Indexes:**
- `idx_study_sessions_user_id` on `user_id`
- `idx_study_sessions_mode` on `mode`

---

### 4. **quizzes** (Study Assistant - Quiz Generation)
Stores generated quizzes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique quiz ID |
| user_id | INTEGER | FOREIGN KEY → users(id) | Student user |
| topic | VARCHAR(200) | NOT NULL | Quiz topic |
| input_text | TEXT | NOT NULL | Source text for quiz |
| mcqs | JSON | NOT NULL | Array of MCQ objects |
| qas | JSON | NOT NULL | Array of Q&A objects |
| created_at | TIMESTAMP | DEFAULT NOW() | Quiz creation time |

**JSON Structure for mcqs:**
```json
[
  {
    "question": "What is...",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "explanation": "..."
  }
]
```

**JSON Structure for qas:**
```json
[
  {
    "question": "Explain...",
    "answer": "..."
  }
]
```

**Indexes:**
- `idx_quizzes_user_id` on `user_id`

---

### 5. **quiz_attempts** (Study Assistant - Quiz Results)
Stores user's quiz attempt results and scores.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique attempt ID |
| quiz_id | INTEGER | FOREIGN KEY → quizzes(id) | Which quiz |
| user_id | INTEGER | FOREIGN KEY → users(id) | Who took it |
| mcq_score | INTEGER | | MCQ score (out of total) |
| mcq_total | INTEGER | | Total MCQ questions |
| answers | JSON | | User's answers |
| completed_at | TIMESTAMP | DEFAULT NOW() | Attempt timestamp |

**Indexes:**
- `idx_quiz_attempts_user_id` on `user_id`
- `idx_quiz_attempts_quiz_id` on `quiz_id`

---

### 6. **kids_assignments** (Kids Challenge - Assignments)
Creative assignments for kids.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Assignment ID |
| title | VARCHAR(100) | NOT NULL | Assignment title |
| description | TEXT | NOT NULL | What to do |
| type | VARCHAR(20) | NOT NULL | 'coloring', 'drawing', 'craft' |
| difficulty | VARCHAR(20) | NOT NULL | 'easy', 'medium', 'hard' |
| criteria | TEXT | NOT NULL | Grading criteria |
| points_possible | INTEGER | DEFAULT 100 | Max points |
| image_url | TEXT | | Template/example image |
| is_active | BOOLEAN | DEFAULT TRUE | Currently available |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- `idx_kids_assignments_active` on `is_active`

---

### 7. **kids_submissions** (Kids Challenge - Submissions)
Kids' submitted artwork with AI grading.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Submission ID |
| assignment_id | INTEGER | FOREIGN KEY → kids_assignments(id) | Which assignment |
| user_id | INTEGER | FOREIGN KEY → users(id), NULL | Parent's account (optional) |
| child_name | VARCHAR(50) | NOT NULL | Child's name |
| image_data | TEXT | | Base64 image (optional storage) |
| image_url | TEXT | | URL to stored image |
| score | DECIMAL(3,1) | NOT NULL | AI score (0.0-10.0) |
| points_earned | INTEGER | NOT NULL | Points awarded |
| feedback | TEXT | NOT NULL | AI positive feedback |
| improvement | TEXT | | AI suggestion |
| vision_description | TEXT | | AI vision analysis |
| submitted_at | TIMESTAMP | DEFAULT NOW() | Submission time |
| week | VARCHAR(10) | | Week identifier (YYYY-WXX) |

**Indexes:**
- `idx_kids_submissions_assignment` on `assignment_id`
- `idx_kids_submissions_child` on `child_name`
- `idx_kids_submissions_week` on `week`

---

### 8. **video_searches** (Educational Videos)
Tracks video search history.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Search ID |
| user_id | INTEGER | FOREIGN KEY → users(id) | Who searched |
| study_session_id | INTEGER | FOREIGN KEY → study_sessions(id), NULL | Related study session |
| input_text | TEXT | NOT NULL | Original text |
| extracted_topic | VARCHAR(200) | NOT NULL | AI extracted topic |
| videos | JSON | NOT NULL | Array of video objects |
| searched_at | TIMESTAMP | DEFAULT NOW() | Search timestamp |

**JSON Structure for videos:**
```json
[
  {
    "video_id": "abc123",
    "title": "...",
    "channel": "...",
    "thumbnail": "...",
    "url": "..."
  }
]
```

**Indexes:**
- `idx_video_searches_user_id` on `user_id`

---

## Relationships

```
users (1) ──→ (N) stories
users (1) ──→ (N) study_sessions
users (1) ──→ (N) quizzes
users (1) ──→ (N) quiz_attempts
users (1) ──→ (N) kids_submissions
users (1) ──→ (N) video_searches

quizzes (1) ──→ (N) quiz_attempts

kids_assignments (1) ──→ (N) kids_submissions

study_sessions (1) ──→ (N) video_searches (optional)
```

---

## Database Views (Optional)

### user_stats
Aggregate statistics per user:
- Total stories generated
- Total study sessions
- Total quizzes taken
- Average quiz score
- Kids submissions count (if parent)

### weekly_leaderboard
Kids Challenge leaderboard for current week.

---

## Migrations

Initial migration will:
1. Create all tables
2. Create indexes
3. Create foreign key constraints
4. Insert default kids_assignments data

---

## Security Considerations

1. **Password Hashing**: Use bcrypt with salt
2. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
3. **Data Validation**: Validate all inputs before DB insertion
4. **API Keys**: Never store in database, use environment variables
5. **User Isolation**: All queries filtered by user_id (except admin)

---

## Environment Variables Required

```env
# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_creative_suite
# Or separate components:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_creative_suite
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
```

---

## Backup Strategy

- Daily automated backups
- Keep 7 days of backups
- Use `pg_dump` for PostgreSQL backups

---

This schema supports all 4 features with proper relationships and scalability!
