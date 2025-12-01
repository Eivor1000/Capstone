# Frontend Authentication Setup Guide

## 🎉 What's Been Added

Complete authentication system with beautiful UI for your AI Creative Suite!

### ✅ New Components Created

1. **AuthContext.jsx** (`frontend/src/context/AuthContext.jsx`)
   - JWT token management
   - Login/Register/Logout functions
   - Auto token refresh
   - Protected API calls helper

2. **Login.jsx** (`frontend/src/components/Login.jsx`)
   - Beautiful login page
   - Username/Email + Password fields
   - Guest access option
   - Error handling with feedback

3. **Signup.jsx** (`frontend/src/components/Signup.jsx`)
   - Comprehensive registration form
   - Required: username, email, password
   - Optional: full name, age, phone
   - Password strength indicator
   - Real-time validation

4. **Profile.jsx** (`frontend/src/components/Profile.jsx`)
   - User profile management
   - Two tabs: Profile Info & Change Password
   - Update personal details
   - Account statistics display

5. **ProtectedRoute.jsx** (`frontend/src/components/ProtectedRoute.jsx`)
   - Route protection wrapper
   - Auto redirect to login if not authenticated
   - Loading state during auth check

### ✅ Updated Components

1. **App.jsx** - Added:
   - AuthProvider wrapper
   - Login/Signup routes
   - Protected Profile route
   - All authentication imports

2. **HomePage.jsx** - Added:
   - Navigation header with auth buttons
   - User profile button (when logged in)
   - Login/Signup buttons (when guest)
   - Personalized welcome message

---

## 🚀 How to Test

### Step 1: Start Backend Server

```bash
cd story-generator/backend
python app.py
```

Server should start on `http://localhost:5000`

### Step 2: Start Frontend Server

```bash
cd story-generator/frontend
npm run dev
```

Frontend should start on `http://localhost:5173` or `http://localhost:3000`

### Step 3: Test Authentication Flow

1. **Open Home Page**: Navigate to `http://localhost:5173`
2. **Click "Sign Up"**: Create a new account
   - Fill in username, email, password (required)
   - Optional: add phone, full name, age
3. **Auto Login**: After signup, you're automatically logged in
4. **See Personalized Welcome**: "Welcome back, [username]!"
5. **Click Profile Button**: View and edit your profile
6. **Test Logout**: Click logout and verify guest state
7. **Test Login**: Sign in with your credentials

---

## 📋 Routes Available

### Public Routes (No Login Required)
- `/` - Home page
- `/login` - Login page
- `/signup` - Signup page
- `/story-generator` - Story Generator feature
- `/study-assistant` - Study Assistant feature
- `/kids-challenge` - Kids Challenge feature

### Protected Routes (Login Required)
- `/profile` - User profile page (redirects to /login if not authenticated)

---

## 🎨 UI Features

### Login Page
- Clean, modern design
- Username/Email field (accepts both)
- Password field
- "Continue as Guest" option
- Link to signup page
- Back to home button

### Signup Page
- Comprehensive form layout
- Required fields marked with asterisk
- Password strength indicator (weak/medium/strong)
- Password confirmation
- Optional fields section
- Form validation with error messages
- Auto-login after registration

### Profile Page
- Gradient header with user info
- Two tabs: Profile & Password
- Read-only fields (username, email)
- Editable fields (full name, phone, age)
- Account statistics cards
- Logout button
- Success/error feedback

### Navigation
- Displays on home page
- Shows "Sign In" & "Sign Up" for guests
- Shows "Profile" & "Logout" for logged-in users
- Responsive design

---

## 🔒 Security Features

### JWT Authentication
- Access tokens stored in localStorage
- Refresh tokens for long sessions
- Auto token refresh on 401 errors
- Secure token transmission

### Password Security
- Minimum 8 characters required
- Bcrypt hashing on backend
- Password confirmation on signup
- Strength indicator

### Route Protection
- ProtectedRoute component for sensitive pages
- Auto redirect to login
- Save intended destination for post-login redirect

---

## 🔧 Configuration

### Backend URL
The frontend is configured to connect to: `http://localhost:5000`

If your backend runs on a different URL, update in:
- `frontend/src/context/AuthContext.jsx` (all fetch calls)

Example:
```javascript
const API_URL = 'http://localhost:5000';

const response = await fetch(`${API_URL}/api/auth/login`, {
  // ...
});
```

### CORS Configuration
Make sure backend allows frontend origin in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📊 How Data is Saved

### When User is Logged In
All activities are automatically saved to database:
- ✅ Stories generated (with prompts, text, images)
- ✅ Study sessions (summaries, explanations)
- ✅ Quizzes taken and scores
- ✅ Kids challenge submissions
- ✅ Video searches

### When User is Guest
Features work normally, but data is NOT saved to database.

To enable data saving, user must:
1. Sign up for an account
2. Login
3. Then all future activities will be saved

---

## 🎯 User Flow Example

### New User Journey
1. Visit home page → See "Sign In" & "Sign Up" buttons
2. Click "Sign Up" → Fill registration form
3. Submit → Auto login → Redirected to home
4. See "Welcome back, [username]!" message
5. Use features → All data saved to their account
6. Click profile → View/edit details
7. Logout → Return to guest state

### Returning User Journey
1. Visit home page → Click "Sign In"
2. Enter credentials → Login
3. See personalized welcome
4. Access profile button in header
5. All feature usage saved to database

---

## 🐛 Troubleshooting

### "Network error. Please try again."
**Cause**: Backend server not running or wrong URL

**Fix**:
```bash
# Start backend
cd story-generator/backend
python app.py

# Verify it's running on http://localhost:5000
curl http://localhost:5000/health
```

### "Username already exists"
**Cause**: Username taken by another user

**Fix**: Choose a different username

### Profile page redirects to login
**Cause**: Not authenticated or token expired

**Fix**: Login again

### Changes not saving to database
**Cause**: Database not configured

**Fix**: Follow `DATABASE_INTEGRATION_STATUS.md`:
1. Install PostgreSQL
2. Create database `ai_creative_suite`
3. Update `.env` with database credentials
4. Restart backend server

---

## 📝 Test User

A test user is created automatically on backend startup:

```
Username: testuser
Email: test@example.com
Password: password123
```

You can use this to test login immediately!

---

## 🎨 Customization

### Change Color Scheme
Primary colors are purple and blue. To change:

**Login.jsx, Signup.jsx, Profile.jsx**:
- Find: `from-purple-600 to-blue-600`
- Replace with your gradient colors

**HomePage.jsx**:
- Find: `from-purple-600 to-blue-600`
- Replace navigation button colors

### Add More Profile Fields
To add new user fields (e.g., "bio", "avatar"):

1. **Backend**: Update `models.py` User model
2. **Backend**: Update `auth.py` registration/update functions
3. **Frontend**: Add field to `Signup.jsx`
4. **Frontend**: Add field to `Profile.jsx`

---

## 🚀 Next Steps

### Optional Enhancements

1. **History Pages**
   - Create "My Stories" page
   - Create "My Quizzes" page
   - Create "My Submissions" page

2. **Social Features**
   - Share stories with other users
   - Public leaderboard
   - Follow system

3. **Email Verification**
   - Send verification email on signup
   - Require email verification to use features

4. **Password Reset**
   - "Forgot Password?" link
   - Email password reset token
   - Reset password page

5. **Profile Picture Upload**
   - Add image upload to profile
   - Store in S3 or local filesystem
   - Display avatar in navigation

---

## ✅ Checklist

Before going live, ensure:

- [ ] Backend server running on port 5000
- [ ] Frontend server running on port 5173/3000
- [ ] PostgreSQL database created and configured
- [ ] `.env` file has correct DATABASE_URL
- [ ] JWT_SECRET_KEY is a strong random string
- [ ] CORS origins configured correctly
- [ ] Test user can register
- [ ] Test user can login
- [ ] Profile page loads correctly
- [ ] Logout works
- [ ] Protected routes redirect to login
- [ ] Data saves to database when logged in

---

## 📚 Files Modified/Created

### Created:
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/components/Login.jsx`
- `frontend/src/components/Signup.jsx`
- `frontend/src/components/Profile.jsx`
- `frontend/src/components/ProtectedRoute.jsx`
- `FRONTEND_SETUP_GUIDE.md` (this file)

### Modified:
- `frontend/src/App.jsx`
- `frontend/src/components/HomePage.jsx`

---

## 🎉 You're All Set!

The complete authentication system is now integrated into your AI Creative Suite!

**Try it out**:
1. Start backend: `python app.py`
2. Start frontend: `npm run dev`
3. Visit: `http://localhost:5173`
4. Click "Sign Up" and create an account!

All your stories, quizzes, and submissions will now be saved to your account!
