import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import HTMLFlipBook from 'react-pageflip'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

function Storybook() {
  const navigate = useNavigate()
  const bookRef = useRef()
  const utteranceRef = useRef(null)
  
  // State management
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState('')
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  
  // Storybook data
  const [storybook, setStorybook] = useState(null)
  const [currentPage, setCurrentPage] = useState(0)
  const [isNarrating, setIsNarrating] = useState(false)
  const [autoNarrate, setAutoNarrate] = useState(true)

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  /**
   * Generate storybook
   */
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a story theme')
      return
    }

    setError('')
    setStorybook(null)
    setLoading(true)
    setProgress(0)

    try {
      setLoadingStage('Creating your magical story...')
      setProgress(10)

      const response = await axios.post(`${API_BASE_URL}/generate-storybook`, {
        prompt: prompt
      })

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to generate storybook')
      }

      setProgress(100)
      setStorybook(response.data)
      setLoadingStage('Complete!')
      
      // Start narration automatically after short delay
      if (autoNarrate) {
        setTimeout(() => {
          narratePage(0)
        }, 1000)
      }

    } catch (err) {
      console.error('Error:', err)
      setError(
        err.response?.data?.error ||
        err.message ||
        'An error occurred while generating your storybook. Please try again.'
      )
    } finally {
      setLoading(false)
      setLoadingStage('')
    }
  }

  /**
   * Handle page flip
   */
  const onPageFlip = (e) => {
    const newPage = e.data
    setCurrentPage(newPage)
    
    // Stop current narration
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsNarrating(false)
    }
    
    // Start narration for new page if auto-narrate is enabled
    if (autoNarrate && newPage > 0) {
      setTimeout(() => {
        narratePage(newPage)
      }, 500)
    }
  }

  /**
   * Narrate current page(s)
   */
  const narratePage = (pageIndex) => {
    if (!storybook || !window.speechSynthesis) return

    // Stop any ongoing speech
    window.speechSynthesis.cancel()

    // Page 0 is title page
    if (pageIndex === 0) {
      const titleText = `${storybook.title}. A magical storybook adventure.`
      speakText(titleText)
      return
    }

    // Calculate which paragraph(s) to read
    // Pages 1-2 show paragraphs 0-1, pages 3-4 show paragraphs 2-3, etc.
    const paragraphIndex = pageIndex - 1
    
    if (paragraphIndex >= storybook.paragraphs.length) return

    const textToRead = storybook.paragraphs[paragraphIndex]
    speakText(textToRead)
  }

  /**
   * Speak text using Web Speech API
   */
  const speakText = (text) => {
    if (!window.speechSynthesis) return

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1.0
    utterance.volume = 1.0
    utterance.lang = 'en-US'

    // Get voices
    const voices = window.speechSynthesis.getVoices()
    const preferredVoice = voices.find(voice =>
      voice.lang === 'en-US' && (voice.name.includes('Google') || voice.name.includes('Microsoft'))
    ) || voices.find(voice => voice.lang.startsWith('en-'))

    if (preferredVoice) {
      utterance.voice = preferredVoice
    }

    utterance.onstart = () => setIsNarrating(true)
    utterance.onend = () => setIsNarrating(false)
    utterance.onerror = (e) => {
      console.error('Speech error:', e)
      setIsNarrating(false)
    }

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }

  /**
   * Toggle narration
   */
  const toggleNarration = () => {
    if (!window.speechSynthesis) {
      setError('Text-to-speech is not supported in your browser')
      return
    }

    if (isNarrating) {
      window.speechSynthesis.cancel()
      setIsNarrating(false)
    } else {
      narratePage(currentPage)
    }
  }

  /**
   * Navigate to next/previous page
   */
  const goToNextPage = () => {
    if (bookRef.current) {
      bookRef.current.pageFlip().flipNext()
    }
  }

  const goToPreviousPage = () => {
    if (bookRef.current) {
      bookRef.current.pageFlip().flipPrev()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-100 to-blue-100 py-8 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-purple-700 hover:text-purple-900 font-semibold mb-6 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 mb-3">
            🪄 Interactive Storybook
          </h1>
          <p className="text-gray-700 text-lg">
            Create magical illustrated storybooks with page-flip animation and narration
          </p>
        </div>

        {/* Input Section */}
        {!storybook && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8 max-w-3xl mx-auto">
            <label className="block text-gray-700 text-lg font-semibold mb-3">
              What magical adventure should we create?
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="E.g., A brave princess who befriends a dragon and saves her kingdom from darkness..."
              className="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none resize-none transition-colors"
              rows="4"
              disabled={loading}
            />

            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-4 px-8 rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-xl"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {loadingStage}
                </span>
              ) : (
                '📖 Create Magical Storybook'
              )}
            </button>

            {loading && (
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-center text-gray-600 text-sm mt-2">
                  Generating your storybook with illustrations...
                </p>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl mb-8 shadow-md max-w-3xl mx-auto">
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="font-semibold">{error}</span>
            </div>
          </div>
        )}

        {/* Storybook Display */}
        {storybook && (
          <div className="space-y-6">
            {/* Controls */}
            <div className="bg-white rounded-xl shadow-lg p-4 flex items-center justify-between max-w-4xl mx-auto">
              <button
                onClick={goToPreviousPage}
                disabled={currentPage === 0}
                className="p-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:cursor-not-allowed rounded-lg transition-colors"
              >
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <div className="flex items-center gap-4">
                <button
                  onClick={toggleNarration}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                    isNarrating
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {isNarrating ? (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                      </svg>
                      Stop
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                      Read Aloud
                    </>
                  )}
                </button>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoNarrate}
                    onChange={(e) => setAutoNarrate(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-gray-700 text-sm font-medium">Auto-narrate</span>
                </label>

                <button
                  onClick={() => setStorybook(null)}
                  className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
                >
                  New Story
                </button>
              </div>

              <button
                onClick={goToNextPage}
                disabled={currentPage >= storybook.paragraphs.length}
                className="p-3 bg-purple-100 hover:bg-purple-200 disabled:bg-gray-100 disabled:cursor-not-allowed rounded-lg transition-colors"
              >
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Book */}
            <div className="flex justify-center">
              <HTMLFlipBook
                ref={bookRef}
                width={400}
                height={600}
                size="stretch"
                minWidth={315}
                maxWidth={1000}
                minHeight={400}
                maxHeight={1533}
                maxShadowOpacity={0.5}
                showCover={true}
                mobileScrollSupport={true}
                onFlip={onPageFlip}
                className="storybook"
              >
                {/* Title Page */}
                <div className="bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 p-8 flex flex-col items-center justify-center text-white shadow-2xl h-full">
                  <div className="text-7xl mb-8">📖</div>
                  <h1 className="text-5xl font-bold text-center mb-6 leading-tight">
                    {storybook.title}
                  </h1>
                  <div className="mt-8 text-2xl opacity-90 text-center">
                    A Magical Adventure
                  </div>
                </div>

                {/* Story Pages */}
                {storybook.paragraphs.map((paragraph, index) => (
                  <div key={index} className="bg-gradient-to-br from-amber-50 to-orange-50 flex flex-col shadow-2xl" style={{ height: '100%', minHeight: '600px' }}>
                    {/* Image */}
                    {storybook.images[index] && (
                      <div className="rounded-lg overflow-hidden shadow-lg flex-shrink-0" style={{ height: '55%' }}>
                        <img
                          src={`data:image/png;base64,${storybook.images[index]}`}
                          alt={`Scene ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    
                    {/* Text */}
                    <div className="flex-1 flex flex-col p-6" style={{ minHeight: '45%' }}>
                      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar mb-2">
                        <p className="text-gray-800 leading-relaxed text-base font-serif">
                          {paragraph}
                        </p>
                      </div>
                      <div className="text-center text-gray-500 text-sm font-medium flex-shrink-0 mt-auto">
                        Page {index + 1}
                      </div>
                    </div>
                  </div>
                ))}

                {/* End Page */}
                <div className="bg-gradient-to-br from-yellow-300 via-orange-300 to-red-300 p-8 flex flex-col items-center justify-center text-white shadow-2xl h-full">
                  <div className="text-7xl mb-8">⭐</div>
                  <h2 className="text-5xl font-bold text-center mb-6">
                    The End
                  </h2>
                  <p className="text-2xl text-center opacity-90">
                    We hope you enjoyed this magical adventure!
                  </p>
                </div>
              </HTMLFlipBook>
            </div>

            <div className="text-center text-gray-600 text-sm">
              Page {currentPage + 1} of {storybook.paragraphs.length + 2}
            </div>
          </div>
        )}
      </div>

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e0;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #a0aec0;
        }
      `}</style>
    </div>
  )
}

export default Storybook
