import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

// Backend API URL
const API_BASE_URL = 'http://localhost:5000/api'

function StudyAssistant() {
  const navigate = useNavigate()

  // State management
  const [inputText, setInputText] = useState('')
  const [mode, setMode] = useState('') // 'summarize', 'explain', 'revise'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Results state
  const [summary, setSummary] = useState('')
  const [explanation, setExplanation] = useState('')
  const [mcqs, setMcqs] = useState([])
  const [qas, setQas] = useState([])

  // MCQ interaction state
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [revealedAnswers, setRevealedAnswers] = useState({})
  const [score, setScore] = useState(null)

  // Video search state
  const [videos, setVideos] = useState([])
  const [loadingVideos, setLoadingVideos] = useState(false)
  const [videoTopic, setVideoTopic] = useState('')

  /**
   * Handle mode selection and API call
   */
  const handleModeSelect = async (selectedMode) => {
    if (!inputText.trim()) {
      setError('Please enter some text to study')
      return
    }

    // Reset previous results
    setError('')
    setSummary('')
    setExplanation('')
    setMcqs([])
    setQas([])
    setSelectedAnswers({})
    setRevealedAnswers({})
    setScore(null)
    setVideos([])  // Reset videos
    setVideoTopic('')
    setMode(selectedMode)
    setLoading(true)

    try {
      let endpoint = ''
      let response

      switch (selectedMode) {
        case 'summarize':
          endpoint = `${API_BASE_URL}/summarize`
          response = await axios.post(endpoint, { text: inputText })
          if (response.data.success) {
            setSummary(response.data.summary)
          }
          break

        case 'explain':
          endpoint = `${API_BASE_URL}/explain`
          response = await axios.post(endpoint, { text: inputText })
          if (response.data.success) {
            setExplanation(response.data.explanation)
          }
          break

        case 'revise':
          endpoint = `${API_BASE_URL}/generate-revision`
          response = await axios.post(endpoint, { text: inputText })
          if (response.data.success) {
            setMcqs(response.data.mcqs || [])
            setQas(response.data.qas || [])
          }
          break

        default:
          throw new Error('Invalid mode selected')
      }

    } catch (err) {
      console.error('Error:', err)
      setError(
        err.response?.data?.error ||
        err.message ||
        'An error occurred. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  /**
   * Handle MCQ answer selection
   */
  const handleMCQAnswer = (mcqIndex, optionIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [mcqIndex]: optionIndex
    })
  }

  /**
   * Calculate and show score
   */
  const handleSubmitMCQs = () => {
    let correct = 0
    mcqs.forEach((mcq, index) => {
      if (selectedAnswers[index] === mcq.correct_index) {
        correct++
      }
    })
    setScore({ correct, total: mcqs.length })

    // Reveal all answers
    const allRevealed = {}
    mcqs.forEach((_, index) => {
      allRevealed[index] = true
    })
    setRevealedAnswers(allRevealed)
  }

  /**
   * Toggle Q&A answer visibility
   */
  const toggleQAAnswer = (qaIndex) => {
    setRevealedAnswers({
      ...revealedAnswers,
      [`qa-${qaIndex}`]: !revealedAnswers[`qa-${qaIndex}`]
    })
  }

  /**
   * Find educational YouTube videos for the current topic
   */
  const handleFindVideos = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text first')
      return
    }

    setLoadingVideos(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE_URL}/find-videos`, {
        text: inputText
      })

      if (response.data.success) {
        setVideos(response.data.videos)
        setVideoTopic(response.data.topic)
      }

    } catch (err) {
      console.error('Error finding videos:', err)
      const errorMessage = err.response?.data?.error || 'Failed to find videos. Please try again.'

      // If quota exceeded, show fallback
      if (err.response?.status === 429 && err.response?.data?.fallback_url) {
        setError(errorMessage + ' Opening YouTube search in new tab...')
        setTimeout(() => {
          window.open(err.response.data.fallback_url, '_blank')
        }, 1500)
      } else {
        setError(errorMessage)
      }
    } finally {
      setLoadingVideos(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Back to Home Button */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-blue-600 hover:text-blue-800 font-semibold transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Home
          </button>
        </div>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600 mb-3">
            AI Study Assistant
          </h1>
          <p className="text-gray-600 text-lg">
            Learn, Understand, and Revise with AI-powered assistance
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <label className="block text-gray-700 text-lg font-semibold mb-3">
            Enter text or topic to study:
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste a paragraph, topic, or concept you want to learn about..."
            className="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none resize-none transition-colors"
            rows="6"
            disabled={loading}
          />

          {/* Mode Selection Buttons */}
          <div className="mt-6 grid md:grid-cols-3 gap-4">
            <button
              onClick={() => handleModeSelect('summarize')}
              disabled={loading}
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold py-4 px-6 rounded-xl hover:from-purple-600 hover:to-pink-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] shadow-lg"
            >
              <span className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                📝 Summarize
              </span>
            </button>

            <button
              onClick={() => handleModeSelect('explain')}
              disabled={loading}
              className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-bold py-4 px-6 rounded-xl hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] shadow-lg"
            >
              <span className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                🧠 Understand
              </span>
            </button>

            <button
              onClick={() => handleModeSelect('revise')}
              disabled={loading}
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold py-4 px-6 rounded-xl hover:from-green-600 hover:to-emerald-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] shadow-lg"
            >
              <span className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                📚 Revise
              </span>
            </button>
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="mt-6 text-center">
              <div className="inline-flex items-center">
                <svg className="animate-spin h-6 w-6 text-blue-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-gray-700 font-semibold">Processing...</span>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl mb-8 shadow-md">
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Summary Result */}
        {summary && mode === 'summarize' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-purple-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Summary
            </h2>
            <div className="bg-purple-50 rounded-xl p-6 prose prose-lg max-w-none">
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {summary}
              </div>
            </div>
          </div>
        )}

        {/* Explanation Result */}
        {explanation && mode === 'explain' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-blue-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Detailed Explanation
            </h2>
            <div className="bg-blue-50 rounded-xl p-6 prose prose-lg max-w-none">
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {explanation}
              </div>
            </div>
          </div>
        )}

        {/* Revision Mode - MCQs */}
        {mcqs.length > 0 && mode === 'revise' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Multiple Choice Questions ({mcqs.length})
            </h2>

            <div className="space-y-6">
              {mcqs.map((mcq, mcqIndex) => (
                <div key={mcqIndex} className="bg-green-50 rounded-xl p-6 border-2 border-green-200">
                  <p className="font-semibold text-gray-800 mb-4">
                    {mcqIndex + 1}. {mcq.question}
                  </p>

                  <div className="space-y-2">
                    {mcq.options.map((option, optionIndex) => {
                      const isSelected = selectedAnswers[mcqIndex] === optionIndex
                      const isCorrect = mcq.correct_index === optionIndex
                      const showResult = revealedAnswers[mcqIndex]

                      return (
                        <button
                          key={optionIndex}
                          onClick={() => handleMCQAnswer(mcqIndex, optionIndex)}
                          disabled={showResult}
                          className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                            showResult
                              ? isCorrect
                                ? 'bg-green-100 border-green-500 text-green-800'
                                : isSelected
                                ? 'bg-red-100 border-red-500 text-red-800'
                                : 'bg-gray-100 border-gray-300 text-gray-600'
                              : isSelected
                              ? 'bg-blue-100 border-blue-500 text-blue-800'
                              : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center">
                            <span className="font-semibold mr-2">
                              {String.fromCharCode(65 + optionIndex)}.
                            </span>
                            <span>{option}</span>
                            {showResult && isCorrect && (
                              <svg className="w-5 h-5 ml-auto text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </button>
                      )
                    })}
                  </div>

                  {/* Show explanation after reveal */}
                  {revealedAnswers[mcqIndex] && mcq.explanation && (
                    <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                      <p className="text-sm text-blue-800">
                        <span className="font-semibold">Explanation:</span> {mcq.explanation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Submit Button */}
            {!score && (
              <button
                onClick={handleSubmitMCQs}
                className="mt-6 w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold py-4 px-6 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all shadow-lg"
              >
                Submit Answers & See Score
              </button>
            )}

            {/* Score Display */}
            {score && (
              <div className="mt-6 bg-gradient-to-r from-green-500 to-emerald-500 text-white p-6 rounded-xl text-center shadow-lg">
                <h3 className="text-2xl font-bold mb-2">Your Score</h3>
                <p className="text-4xl font-bold">
                  {score.correct} / {score.total}
                </p>
                <p className="text-lg mt-2">
                  {Math.round((score.correct / score.total) * 100)}% Correct
                </p>
              </div>
            )}
          </div>
        )}

        {/* Revision Mode - Q&A */}
        {qas.length > 0 && mode === 'revise' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-indigo-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Short Answer Questions ({qas.length})
            </h2>

            <div className="space-y-4">
              {qas.map((qa, qaIndex) => (
                <div key={qaIndex} className="bg-indigo-50 rounded-xl p-6 border-2 border-indigo-200">
                  <p className="font-semibold text-gray-800 mb-3">
                    Q{qaIndex + 1}: {qa.question}
                  </p>

                  <button
                    onClick={() => toggleQAAnswer(qaIndex)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
                  >
                    {revealedAnswers[`qa-${qaIndex}`] ? 'Hide Answer' : 'Reveal Answer'}
                  </button>

                  {revealedAnswers[`qa-${qaIndex}`] && (
                    <div className="mt-4 p-4 bg-white border-l-4 border-indigo-500 rounded">
                      <p className="text-gray-700">
                        <span className="font-semibold text-indigo-600">Answer:</span> {qa.answer}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Find Video Resources Button - Show after any results */}
        {(summary || explanation || mcqs.length > 0) && !videos.length && (
          <div className="text-center mb-8">
            <button
              onClick={handleFindVideos}
              disabled={loadingVideos}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white font-bold py-4 px-8 rounded-xl hover:from-red-600 hover:to-pink-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.05] shadow-xl"
            >
              <span className="flex items-center">
                {loadingVideos ? (
                  <>
                    <svg className="animate-spin h-6 w-6 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Searching for videos...
                  </>
                ) : (
                  <>
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Find Educational Videos
                  </>
                )}
              </span>
            </button>
            <p className="text-gray-500 text-sm mt-2">Get YouTube videos to help you learn this topic</p>
          </div>
        )}

        {/* Educational Videos Section */}
        {videos.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-red-600 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Educational Videos: {videoTopic}
            </h2>
            <p className="text-sm text-gray-600 mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded">
              ⚠️ For educational purposes only. Videos are filtered for educational content.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              {videos.map((video, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all transform hover:scale-[1.02] cursor-pointer"
                  onClick={() => window.open(video.url, '_blank')}
                >
                  {/* Thumbnail */}
                  <div className="relative">
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="w-full h-40 object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all flex items-center justify-center">
                      <svg className="w-16 h-16 text-white opacity-0 hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                      </svg>
                    </div>
                  </div>

                  {/* Video Info */}
                  <div className="p-4">
                    <h3 className="font-bold text-gray-800 mb-2 line-clamp-2 hover:text-red-600 transition-colors">
                      {video.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3 flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      {video.channel}
                    </p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        window.open(video.url, '_blank')
                      }}
                      className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors font-semibold text-sm"
                    >
                      Watch on YouTube →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Powered by Groq AI & YouTube Data API - Helping students learn better</p>
        </div>
      </div>
    </div>
  )
}

export default StudyAssistant
