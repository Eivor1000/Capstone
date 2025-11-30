import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './components/HomePage'
import StoryGenerator from './components/StoryGenerator'
import StudyAssistant from './components/StudyAssistant'

function App() {
  return (
    <Router>
      <Routes>
        {/* Home Page - Feature Selection */}
        <Route path="/" element={<HomePage />} />

        {/* Story Generator Feature */}
        <Route path="/story-generator" element={
          <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
            <StoryGenerator />
          </div>
        } />

        {/* Study Assistant Feature */}
        <Route path="/study-assistant" element={<StudyAssistant />} />

        <Route path="/feature-3" element={
          <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-5xl font-bold text-green-600 mb-4">Feature 3</h1>
              <p className="text-gray-600 text-xl mb-8">Coming Soon!</p>
              <a href="/" className="bg-green-600 text-white px-8 py-3 rounded-xl hover:bg-green-700 transition-colors">
                Back to Home
              </a>
            </div>
          </div>
        } />
      </Routes>
    </Router>
  )
}

export default App
