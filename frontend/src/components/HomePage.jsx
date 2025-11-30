import React from 'react'
import { useNavigate } from 'react-router-dom'

function HomePage() {
  const navigate = useNavigate()

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
      title: 'Feature 3',
      description: 'Coming soon - Add your third amazing AI feature here',
      icon: (
        <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      gradient: 'from-green-500 to-emerald-500',
      route: '/feature-3',
      features: ['Feature X', 'Feature Y', 'Feature Z', 'Feature W'],
      comingSoon: true
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
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 mb-4">
            AI Creative Suite
          </h1>
          <p className="text-gray-600 text-xl max-w-2xl mx-auto">
            Unleash your creativity with our powerful AI-powered tools. Choose a feature to get started!
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
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

        {/* Footer Info */}
        <div className="text-center mt-16">
          <p className="text-gray-500 text-sm">
            Powered by Groq AI, Pollinations.ai, and cutting-edge AI technologies
          </p>
        </div>
      </div>
    </div>
  )
}

export default HomePage
