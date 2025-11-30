import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

// Backend API URL
const API_BASE_URL = 'http://localhost:5000/api'

function StoryGenerator() {
  const navigate = useNavigate()
  // State management
  const [prompt, setPrompt] = useState('')
  const [story, setStory] = useState('')
  const [imageData, setImageData] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState('')
  const [error, setError] = useState('')
  const [storyTitle, setStoryTitle] = useState('')
  const [isReading, setIsReading] = useState(false)

  /**
   * Main function to generate story and cover image
   */
  const handleGenerate = async () => {
    // Validation
    if (!prompt.trim()) {
      setError('Please enter a story prompt')
      return
    }

    // Reset state
    setError('')
    setStory('')
    setImageData('')
    setStoryTitle('')
    setLoading(true)

    try {
      // Step 1: Generate Story
      setLoadingStage('Generating your story...')
      const storyResponse = await axios.post(`${API_BASE_URL}/generate-story`, {
        prompt: prompt
      })

      if (!storyResponse.data.success) {
        throw new Error(storyResponse.data.error || 'Failed to generate story')
      }

      const generatedStory = storyResponse.data.story
      setStory(generatedStory)

      // Extract a title from the prompt (first 50 chars or create from prompt)
      const title = prompt.length > 50 ? prompt.substring(0, 50) + '...' : prompt
      setStoryTitle(title)

      // Step 2: Generate Cover Image
      setLoadingStage('Creating cover image... (this may take a moment)')
      const imageResponse = await axios.post(`${API_BASE_URL}/generate-image`, {
        prompt: prompt
      })

      if (!imageResponse.data.success) {
        throw new Error(imageResponse.data.error || 'Failed to generate image')
      }

      setImageData(imageResponse.data.image_data)
      setLoadingStage('Complete!')

    } catch (err) {
      console.error('Error:', err)
      setError(
        err.response?.data?.error ||
        err.message ||
        'An error occurred while generating your story. Please try again.'
      )
    } finally {
      setLoading(false)
      setLoadingStage('')
    }
  }

  /**
   * Download PDF with story and cover image
   */
  const handleDownloadPDF = async () => {
    if (!story || !imageData) {
      setError('Story and image must be generated first')
      return
    }

    setLoading(true)
    setLoadingStage('Creating PDF...')

    try {
      const response = await axios.post(
        `${API_BASE_URL}/create-pdf`,
        {
          story: story,
          image_data: imageData,
          title: storyTitle || 'My Story'
        },
        {
          responseType: 'blob' // Important for file download
        }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'story_with_cover.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

    } catch (err) {
      console.error('Error:', err)
      setError('Failed to create PDF. Please try again.')
    } finally {
      setLoading(false)
      setLoadingStage('')
    }
  }

  /**
   * Read story aloud using Web Speech API (browser-based, free)
   */
  const handleReadAloud = () => {
    if (!story) {
      setError('Please generate a story first')
      return
    }

    if (isReading) {
      // Stop reading
      window.speechSynthesis.cancel()
      setIsReading(false)
      return
    }

    // Clear any previous errors
    setError('')

    // Check if browser supports speech synthesis
    if (!window.speechSynthesis) {
      setError('Your browser does not support text-to-speech. Please try Chrome, Edge, or Safari.')
      return
    }

    // Function to start speaking
    const speak = () => {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(story)

      // Configure voice settings
      utterance.rate = 0.9  // Slightly slower for better comprehension
      utterance.pitch = 1.0
      utterance.volume = 1.0
      utterance.lang = 'en-US'

      // Get available voices
      const voices = window.speechSynthesis.getVoices()

      if (voices.length > 0) {
        // Try to find a good English voice
        const preferredVoice = voices.find(voice =>
          voice.lang === 'en-US' && (voice.name.includes('Google') || voice.name.includes('Microsoft'))
        ) || voices.find(voice => voice.lang.startsWith('en-'))

        if (preferredVoice) {
          utterance.voice = preferredVoice
          console.log('Using voice:', preferredVoice.name)
        }
      }

      // Event handlers
      utterance.onstart = () => {
        console.log('Speech started')
        setIsReading(true)
      }

      utterance.onend = () => {
        console.log('Speech ended')
        setIsReading(false)
      }

      utterance.onerror = (event) => {
        console.error('Speech error:', event.error, event)
        setIsReading(false)

        // Provide specific error messages
        if (event.error === 'network') {
          setError('Network error. Please check your internet connection.')
        } else if (event.error === 'synthesis-unavailable') {
          setError('Text-to-speech is not available. Please try a different browser.')
        } else if (event.error === 'text-too-long') {
          setError('Story is too long for browser speech. Try a shorter story.')
        } else {
          setError(`Speech error: ${event.error}. Please try again.`)
        }
      }

      // Start speaking
      try {
        window.speechSynthesis.speak(utterance)
        console.log('Speech synthesis started')
      } catch (err) {
        console.error('Failed to speak:', err)
        setError('Failed to start speech. Please try again.')
        setIsReading(false)
      }
    }

    // Load voices and speak
    const voices = window.speechSynthesis.getVoices()

    if (voices.length === 0) {
      // Voices not loaded yet, wait for them
      console.log('Waiting for voices to load...')
      window.speechSynthesis.onvoiceschanged = () => {
        console.log('Voices loaded:', window.speechSynthesis.getVoices().length)
        speak()
      }

      // Fallback: try to speak after a short delay
      setTimeout(() => {
        if (window.speechSynthesis.getVoices().length === 0) {
          console.log('No voices available, trying anyway...')
        }
        speak()
      }, 100)
    } else {
      // Voices already loaded
      speak()
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Back to Home Button */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-purple-600 hover:text-purple-800 font-semibold transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </button>
      </div>

      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
          AI Story Generator
        </h1>
        <p className="text-gray-600 text-lg">
          Create magical stories with AI-generated cover images
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <label className="block text-gray-700 text-lg font-semibold mb-3">
          What story would you like to create?
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="E.g., A fantasy story about a dragon who loves books and starts a library in a magical forest..."
          className="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none resize-none transition-colors"
          rows="4"
          disabled={loading}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || !prompt.trim()}
          className="mt-4 w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-4 px-8 rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-lg"
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
            'Generate Story & Cover'
          )}
        </button>
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

      {/* Results Section */}
      {(story || imageData) && (
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Cover Image */}
          {imageData && (
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Cover Image
              </h2>
              <div className="rounded-xl overflow-hidden shadow-lg">
                <img
                  src={`data:image/png;base64,${imageData}`}
                  alt="Story Cover"
                  className="w-full h-auto"
                />
              </div>
            </div>
          )}

          {/* Story Text */}
          {story && (
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Your Story
              </h2>
              <div className="bg-gray-50 rounded-xl p-6 max-h-[500px] overflow-y-auto prose prose-lg">
                <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {story}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      {story && imageData && (
        <div className="flex flex-wrap gap-4 justify-center">
          {/* Read Aloud Button */}
          <button
            onClick={handleReadAloud}
            disabled={loading}
            className={`${
              isReading
                ? 'bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700'
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700'
            } text-white font-bold py-4 px-8 rounded-xl disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.05] active:scale-[0.95] shadow-xl`}
          >
            <span className="flex items-center">
              {isReading ? (
                <>
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Stop Reading
                </>
              ) : (
                <>
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                  Read Aloud
                </>
              )}
            </span>
          </button>

          {/* Download PDF Button */}
          <button
            onClick={handleDownloadPDF}
            disabled={loading}
            className="bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-4 px-8 rounded-xl hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-[1.05] active:scale-[0.95] shadow-xl"
          >
            <span className="flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF
            </span>
          </button>
        </div>
      )}

      {/* Footer */}
      <div className="text-center mt-12 text-gray-500 text-sm">
        <p>Powered by Groq AI and Pollinations.ai</p>
      </div>
    </div>
  )
}

export default StoryGenerator
