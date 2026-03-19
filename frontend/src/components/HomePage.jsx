import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function HomePage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuth()

  const features = [
    {
      id: 1,
      title: 'Story Generator',
      description: 'Create magical stories with AI-generated cover images and export to PDF',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      gradient: 'from-purple-500 to-pink-500',
      route: '/story-generator',
      features: ['AI Story Generation', 'Cover Image Creation', 'PDF Export', 'Read Aloud']
    },
    {
      id: 2,
      title: 'AI Study Assistant',
      description: 'Learn, understand, and revise any topic with AI-powered summaries, explanations, and practice questions',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      gradient: 'from-blue-500 to-cyan-500',
      route: '/study-assistant',
      features: ['Summarize Text', 'Detailed Explanations', 'Practice MCQs', 'Q&A Generation'],
      comingSoon: false
    },
    {
      id: 3,
      title: 'Kids Creative Challenge',
      description: 'Fun creative assignments for kids ages 5-8 with AI grading, points, and leaderboards',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      gradient: 'from-pink-500 to-yellow-500',
      route: '/kids-challenge',
      features: ['Creative Assignments', 'AI Image Grading', 'Points & Rewards', 'Weekly Leaderboard'],
      comingSoon: false
    },
    {
      id: 4,
      title: 'Interactive Storybook',
      description: 'Create illustrated storybooks with page-flip animation, narration, and local AI image generation',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      gradient: 'from-indigo-500 via-purple-500 to-pink-500',
      route: '/storybook',
      features: ['10-Page Illustrated Book', 'Page-Flip Animation', 'Auto-Narration', 'AI Illustrations'],
      comingSoon: false
    }
  ]

  const handleFeatureClick = (route, comingSoon) => {
    if (comingSoon) {
      alert('This feature is coming soon! Stay tuned.')
      return
    }
    navigate(route)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                KinderKraft
              </span>
            </div>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <button
                    onClick={() => navigate('/profile')}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition duration-200"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{user?.username}</span>
                  </button>
                  <button
                    onClick={logout}
                    className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition duration-200"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => navigate('/login')}
                    className="px-4 py-2 rounded-lg border border-purple-600 text-purple-600 hover:bg-purple-50 transition duration-200"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => navigate('/signup')}
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 transition duration-200"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 mb-4">
            {isAuthenticated ? `Welcome back, ${user?.username}!` : 'KinderKraft'}
          </h1>
          <p className="text-gray-600 text-xl max-w-2xl mx-auto">
            Unleash your creativity with our powerful AI-powered tools. Choose a feature to get started!
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {features.map((feature) => (
            <div
              key={feature.id}
              onClick={() => handleFeatureClick(feature.route, feature.comingSoon)}
              className="relative bg-white rounded-3xl shadow-2xl p-8 cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-3xl group"
            >
              {/* Coming Soon Badge */}
              {feature.comingSoon && (
                <div className="absolute top-4 right-4 bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full">
                  COMING SOON
                </div>
              )}

              {/* Icon */}
              <div className={`w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-white transform transition-transform group-hover:rotate-6`}>
                {feature.icon}
              </div>

              {/* Title */}
              <h2 className="text-2xl font-bold text-gray-800 text-center mb-3">
                {feature.title}
              </h2>

              {/* Description */}
              <p className="text-gray-600 text-center mb-6">
                {feature.description}
              </p>

              {/* Feature List */}
              <div className="space-y-2 mb-6">
                {feature.features.map((item, index) => (
                  <div key={index} className="flex items-center text-gray-700">
                    <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm">{item}</span>
                  </div>
                ))}
              </div>

              {/* Button */}
              <button
                className={`w-full py-3 px-6 rounded-xl font-bold text-white bg-gradient-to-r ${feature.gradient} hover:shadow-lg transform transition-all ${
                  feature.comingSoon ? 'opacity-50' : ''
                }`}
              >
                {feature.comingSoon ? 'Coming Soon' : 'Get Started →'}
              </button>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}

export default HomePage
