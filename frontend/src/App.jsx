import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import HomePage from './components/HomePage'
import StoryGenerator from './components/StoryGenerator'
import StudyAssistant from './components/StudyAssistant'
import KidsChallenge from './components/KidsChallenge'
import Login from './components/Login'
import Signup from './components/Signup'
import Profile from './components/Profile'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Home Page - Feature Selection */}
          <Route path="/" element={<HomePage />} />

          {/* Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Profile Route */}
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />

          {/* Story Generator Feature */}
          <Route path="/story-generator" element={
            <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
              <StoryGenerator />
            </div>
          } />

          {/* Study Assistant Feature */}
          <Route path="/study-assistant" element={<StudyAssistant />} />

          {/* Kids Creative Challenge Feature */}
          <Route path="/kids-challenge" element={<KidsChallenge />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
