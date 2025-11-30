import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

function KidsChallenge() {
  const navigate = useNavigate();

  // State management
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [childName, setChildName] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [activeTab, setActiveTab] = useState('assignments'); // assignments, submit, leaderboard
  const [mySubmissions, setMySubmissions] = useState([]);

  // Fetch assignments on component mount
  useEffect(() => {
    fetchAssignments();
    fetchLeaderboard();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/kids/assignments`);
      if (response.data.success) {
        setAssignments(response.data.assignments);
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/kids/leaderboard`);
      if (response.data.success) {
        setLeaderboard(response.data.leaderboard);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  const fetchMySubmissions = async (name) => {
    if (!name) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/kids/my-submissions/${name}`);
      if (response.data.success) {
        setMySubmissions(response.data.submissions);
      }
    } catch (error) {
      console.error('Error fetching submissions:', error);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedAssignment || !childName || !imageFile) {
      alert('Please fill in all fields and upload an image!');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Convert image to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result.split(',')[1]; // Remove data:image/...;base64, prefix

        const response = await axios.post(`${API_BASE_URL}/kids/submit`, {
          assignment_id: selectedAssignment.id,
          child_name: childName,
          image_data: base64String
        });

        if (response.data.success) {
          setResult(response.data);
          // Refresh leaderboard
          await fetchLeaderboard();
          // Fetch my submissions
          await fetchMySubmissions(childName);
        } else {
          alert('Error: ' + response.data.error);
        }

        setLoading(false);
      };

      reader.readAsDataURL(imageFile);
    } catch (error) {
      console.error('Error submitting assignment:', error);
      alert('Failed to submit assignment. Please try again.');
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedAssignment(null);
    setImageFile(null);
    setImagePreview('');
    setResult(null);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeEmoji = (type) => {
    switch (type) {
      case 'coloring': return '🎨';
      case 'drawing': return '✏️';
      case 'craft': return '✂️';
      case 'physical': return '🏃';
      default: return '🎯';
    }
  };

  const getRankEmoji = (rank) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return '🏅';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="mb-4 px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition"
          >
            ← Back to Home
          </button>
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500 mb-2">
            Kids Creative Challenge 🎨
          </h1>
          <p className="text-gray-600 text-lg">
            Show your creativity! Complete fun assignments and earn points! (Ages 5-8)
          </p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8 space-x-4">
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'assignments'
                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:shadow-md'
            }`}
          >
            📋 Assignments
          </button>
          <button
            onClick={() => setActiveTab('submit')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'submit'
                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:shadow-md'
            }`}
          >
            📤 Submit Work
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'leaderboard'
                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:shadow-md'
            }`}
          >
            🏆 Leaderboard
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'assignments' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assignments.map((assignment) => (
              <div
                key={assignment.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition transform hover:-translate-y-1"
              >
                <div className="h-48 bg-gradient-to-br from-pink-200 to-purple-200 flex items-center justify-center text-6xl">
                  {getTypeEmoji(assignment.type)}
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold text-gray-800">{assignment.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getDifficultyColor(assignment.difficulty)}`}>
                      {assignment.difficulty}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-4">{assignment.description}</p>
                  <div className="border-t pt-4">
                    <p className="text-sm text-gray-500 mb-2">
                      <strong>What to do:</strong> {assignment.criteria}
                    </p>
                    <div className="flex items-center justify-between mt-4">
                      <span className="text-purple-600 font-bold">
                        🎯 {assignment.points_possible} points
                      </span>
                      <button
                        onClick={() => {
                          setSelectedAssignment(assignment);
                          setActiveTab('submit');
                        }}
                        className="px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg font-semibold hover:shadow-lg transition"
                      >
                        Start →
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'submit' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500">
              Submit Your Creative Work
            </h2>

            {!result ? (
              <div className="space-y-6">
                {/* Assignment Selection */}
                <div>
                  <label className="block text-lg font-semibold text-gray-700 mb-2">
                    Choose Assignment
                  </label>
                  <select
                    value={selectedAssignment?.id || ''}
                    onChange={(e) => {
                      const assignment = assignments.find(a => a.id === parseInt(e.target.value));
                      setSelectedAssignment(assignment);
                    }}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 transition"
                  >
                    <option value="">-- Select an assignment --</option>
                    {assignments.map((assignment) => (
                      <option key={assignment.id} value={assignment.id}>
                        {getTypeEmoji(assignment.type)} {assignment.title} ({assignment.difficulty})
                      </option>
                    ))}
                  </select>
                </div>

                {selectedAssignment && (
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-bold text-purple-800 mb-2">{selectedAssignment.title}</h3>
                    <p className="text-gray-700 mb-2">{selectedAssignment.description}</p>
                    <p className="text-sm text-gray-600">
                      <strong>Instructions:</strong> {selectedAssignment.criteria}
                    </p>
                  </div>
                )}

                {/* Child Name */}
                <div>
                  <label className="block text-lg font-semibold text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    value={childName}
                    onChange={(e) => {
                      setChildName(e.target.value);
                      if (e.target.value) {
                        fetchMySubmissions(e.target.value);
                      }
                    }}
                    placeholder="Enter your name"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 transition"
                  />
                </div>

                {/* Image Upload */}
                <div>
                  <label className="block text-lg font-semibold text-gray-700 mb-2">
                    Upload Your Creative Work
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 transition"
                  />
                  {imagePreview && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-600 mb-2">Preview:</p>
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="max-w-full h-64 object-contain rounded-lg border-2 border-gray-300"
                      />
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleSubmit}
                  disabled={loading || !selectedAssignment || !childName || !imageFile}
                  className={`w-full py-4 rounded-lg font-bold text-white text-lg transition ${
                    loading || !selectedAssignment || !childName || !imageFile
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-pink-500 to-purple-500 hover:shadow-xl transform hover:scale-105'
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      AI is Grading Your Work...
                    </span>
                  ) : (
                    'Submit & Get Graded by AI ✨'
                  )}
                </button>
              </div>
            ) : (
              /* Results Display */
              <div className="space-y-6">
                <div className="text-center">
                  <div className="text-8xl mb-4">
                    {result.score >= 9 ? '🌟' : result.score >= 7 ? '⭐' : '🎨'}
                  </div>
                  <h3 className="text-4xl font-bold text-purple-600 mb-2">
                    Score: {result.score}/10
                  </h3>
                  <p className="text-2xl font-semibold text-pink-600">
                    {result.points_earned} Points Earned!
                  </p>
                </div>

                <div className="bg-green-50 p-6 rounded-lg border-2 border-green-200">
                  <h4 className="font-bold text-green-800 text-xl mb-2">Feedback:</h4>
                  <p className="text-gray-700 text-lg">{result.feedback}</p>
                </div>

                <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
                  <h4 className="font-bold text-blue-800 text-xl mb-2">How to Improve:</h4>
                  <p className="text-gray-700 text-lg">{result.improvement}</p>
                </div>

                {result.labels_detected && result.labels_detected.length > 0 && (
                  <div className="bg-purple-50 p-6 rounded-lg border-2 border-purple-200">
                    <h4 className="font-bold text-purple-800 text-xl mb-2">What AI Saw:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.labels_detected.map((label, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-purple-200 text-purple-800 rounded-full text-sm font-semibold"
                        >
                          {label.label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={resetForm}
                  className="w-full py-4 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg font-bold text-lg hover:shadow-xl transition"
                >
                  Submit Another Assignment 🎨
                </button>
              </div>
            )}

            {/* My Submissions */}
            {mySubmissions.length > 0 && !result && (
              <div className="mt-8 border-t pt-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Your Previous Submissions</h3>
                <div className="space-y-3">
                  {mySubmissions.slice(0, 5).map((submission) => (
                    <div
                      key={submission.id}
                      className="flex items-center justify-between bg-gray-50 p-4 rounded-lg"
                    >
                      <div>
                        <p className="font-semibold text-gray-800">
                          Assignment #{submission.assignment_id}
                        </p>
                        <p className="text-sm text-gray-600">{submission.submitted_at}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-purple-600">{submission.score}/10</p>
                        <p className="text-sm text-gray-600">{submission.points_earned} pts</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'leaderboard' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500">
              Weekly Leaderboard 🏆
            </h2>

            {leaderboard.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-xl">No submissions yet this week!</p>
                <p className="text-gray-400 mt-2">Be the first to submit and top the leaderboard!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {leaderboard.map((entry, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-6 rounded-lg transition ${
                      entry.rank <= 3
                        ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300'
                        : 'bg-gray-50 border-2 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="text-4xl">
                        {getRankEmoji(entry.rank)}
                      </div>
                      <div>
                        <p className={`text-2xl font-bold ${entry.rank <= 3 ? 'text-orange-600' : 'text-gray-800'}`}>
                          #{entry.rank} {entry.name}
                        </p>
                        <p className="text-gray-600">
                          {entry.submissions} submission{entry.submissions !== 1 ? 's' : ''} •
                          Avg: {entry.average_score}/10
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-purple-600">
                        {entry.total_points}
                      </p>
                      <p className="text-sm text-gray-500">points</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {leaderboard.length > 0 && (
              <div className="mt-8 text-center">
                <p className="text-gray-600">
                  Keep submitting creative work to climb the leaderboard!
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default KidsChallenge;
