import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './components/HomePage'
import StoryGenerator from './components/StoryGenerator'
import StudyAssistant from './components/StudyAssistant'
import KidsChallenge from './components/KidsChallenge'

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

        {/* Kids Creative Challenge Feature */}
        <Route path="/kids-challenge" element={<KidsChallenge />} />
      </Routes>
    </Router>
  )
}

export default App
