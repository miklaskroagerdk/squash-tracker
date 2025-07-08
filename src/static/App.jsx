import React, { useState, useEffect } from 'react'
import './App.css'

const API_BASE = '/api'

function App() {
  const [players, setPlayers] = useState([])
  const [sessions, setSessions] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [highlights, setHighlights] = useState({ recent_matches: [], stats: {} })
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('dashboard')
  const [selectedPlayersForSession, setSelectedPlayersForSession] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [sessionMatches, setSessionMatches] = useState([])
  const [newPlayerName, setNewPlayerName] = useState('')

  // Fetch data on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        await fetchPlayers()
        await fetchSessions()
        await fetchLeaderboard()
        await fetchHighlights()
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // API calls
  const fetchPlayers = async () => {
    try {
      const response = await fetch(`${API_BASE}/players`)
      if (response.ok) {
        const data = await response.json()
        setPlayers(data)
      } else {
        console.error('Failed to fetch players:', response.status)
        setPlayers([])
      }
    } catch (error) {
      console.error('Error fetching players:', error)
      setPlayers([])
    }
  }

  const fetchSessions = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`)
      if (response.ok) {
        const data = await response.json()
        setSessions(data)
      } else {
        console.error('Failed to fetch sessions:', response.status)
        setSessions([])
      }
    } catch (error) {
      console.error('Error fetching sessions:', error)
      setSessions([])
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${API_BASE}/leaderboard`)
      if (response.ok) {
        const data = await response.json()
        setLeaderboard(data)
      } else {
        console.error('Failed to fetch leaderboard:', response.status)
        setLeaderboard([])
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      setLeaderboard([])
    }
  }

  const fetchHighlights = async () => {
    try {
      const response = await fetch(`${API_BASE}/highlights`)
      if (response.ok) {
        const data = await response.json()
        setHighlights(data || { recent_matches: [], stats: {} })
      } else {
        console.error('Failed to fetch highlights:', response.status)
        setHighlights({ recent_matches: [], stats: {} })
      }
    } catch (error) {
      console.error('Error fetching highlights:', error)
      setHighlights({ recent_matches: [], stats: {} })
    }
  }

  const fetchSessionDetails = async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
      if (response.ok) {
        const sessionData = await response.json()
        setCurrentSession(sessionData)
        
        const formattedMatches = (sessionData.matches || []).map(match => ({
          id: match.id,
          player1: {
            id: match.player1_id,
            name: match.player1_name
          },
          player2: {
            id: match.player2_id,
            name: match.player2_name
          },
          player1_score: match.player1_score !== null ? match.player1_score : '',
          player2_score: match.player2_score !== null ? match.player2_score : '',
          completed: match.player1_score !== null && match.player2_score !== null
        }))
        
        setSessionMatches(formattedMatches)
        setCurrentView('session')
      }
    } catch (error) {
      console.error('Error fetching session details:', error)
    }
  }

  const addPlayer = async () => {
    if (!newPlayerName.trim()) return
    
    try {
      const response = await fetch(`${API_BASE}/players`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newPlayerName.trim() })
      })
      
      if (response.ok) {
        setNewPlayerName('')
        fetchPlayers()
      }
    } catch (error) {
      console.error('Error adding player:', error)
    }
  }

  const handlePlayerSelection = (playerId, isChecked) => {
    setSelectedPlayersForSession(prevSelected => {
      if (isChecked) {
        return prevSelected.includes(playerId) ? prevSelected : [...prevSelected, playerId]
      } else {
        return prevSelected.filter(id => id !== playerId)
      }
    })
  }

  const createSessionWithPlayers = async () => {
    console.log('Creating session with players:', selectedPlayersForSession)
    
    if (selectedPlayersForSession.length < 2) {
      alert('Please select at least 2 players to create a session.')
      return
    }

    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_ids: selectedPlayersForSession
        })
      })
      
      if (response.ok) {
        const session = await response.json()
        setCurrentSession(session)
        
        const formattedMatches = (session.matches || []).map(match => ({
          id: match.id,
          player1: {
            id: match.player1_id,
            name: match.player1_name
          },
          player2: {
            id: match.player2_id,
            name: match.player2_name
          },
          player1_score: match.player1_score !== null ? match.player1_score : '',
          player2_score: match.player2_score !== null ? match.player2_score : '',
          completed: match.player1_score !== null && match.player2_score !== null
        }))
        
        setSessionMatches(formattedMatches)
        setCurrentView('session')
        fetchSessions()
      } else {
        const errorData = await response.json()
        console.error('Error response:', errorData)
        alert(`Error creating session: ${errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error creating session:', error)
      alert('Error creating session. Please try again.')
    }
  }

  const deleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session? This will delete all matches and revert ELO changes.')) {
      return
    }
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        await fetchSessions()
        await fetchLeaderboard()
        await fetchHighlights()
        
        if (currentSession && currentSession.id === sessionId) {
          setCurrentView('dashboard')
          setCurrentSession(null)
        }
      } else {
        const errorData = await response.json()
        alert(`Error deleting session: ${errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Error deleting session. Please try again.')
    }
  }

  const updateMatchScore = (matchIndex, field, value) => {
    const updatedMatches = [...sessionMatches]
    updatedMatches[matchIndex][field] = value
    setSessionMatches(updatedMatches)
  }

  const validateMatchScores = (player1Score, player2Score) => {
    const p1Score = parseInt(player1Score, 10)
    const p2Score = parseInt(player2Score, 10)
    
    if (isNaN(p1Score) || isNaN(p2Score)) {
      return { valid: false, message: "Both scores must be valid numbers" }
    }
    
    if (p1Score < 0 || p2Score < 0) {
      return { valid: false, message: "Scores cannot be negative" }
    }
    
    const maxScore = Math.max(p1Score, p2Score)
    const minScore = Math.min(p1Score, p2Score)
    
    if (maxScore < 11) {
      return { valid: false, message: "Winner must have at least 11 points" }
    }
    
    if ((p1Score === 11 && p2Score === 0) || (p1Score === 0 && p2Score === 11)) {
      return { valid: true }
    }
    
    if (maxScore > 11 && maxScore - minScore < 2) {
      return { valid: false, message: "Winner must have at least a 2 point lead when score is above 11" }
    }
    
    if (p1Score === p2Score) {
      return { valid: false, message: "There must be a clear winner - scores cannot be equal" }
    }
    
    return { valid: true }
  }

  const submitMatch = async (matchIndex) => {
    const match = sessionMatches[matchIndex]
    
    if (!match.player1_score || !match.player2_score) {
      alert('Please enter scores for both players.')
      return
    }

    const validation = validateMatchScores(match.player1_score, match.player2_score)
    if (!validation.valid) {
      alert(validation.message)
      return
    }

    if (!match.id) {
      alert('Match ID not found. Please refresh the page and try again.')
      return
    }

    try {
      const response = await fetch(`${API_BASE}/matches/${match.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player1_score: parseInt(match.player1_score),
          player2_score: parseInt(match.player2_score)
        })
      })
      
      if (response.ok) {
        const savedMatch = await response.json()
        
        const updatedMatches = [...sessionMatches]
        updatedMatches[matchIndex] = {
          ...match,
          completed: true,
          player1_score: savedMatch.player1_score,
          player2_score: savedMatch.player2_score,
          winner_name: savedMatch.winner_name,
          elo_changes: savedMatch.elo_changes
        }
        setSessionMatches(updatedMatches)
        
        fetchLeaderboard()
        fetchSessions()
        fetchHighlights()
      } else {
        const errorData = await response.json()
        console.error('Error response:', errorData)
        alert(`Error submitting match: ${errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error submitting match:', error)
      alert('Error submitting match. Please try again.')
    }
  }

  const removeMatch = async (matchIndex, matchId = null) => {
    if (matchId) {
      try {
        const response = await fetch(`${API_BASE}/matches/${matchId}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          fetchSessions()
          fetchLeaderboard()
        }
      } catch (error) {
        console.error('Error deleting match:', error)
      }
    } else {
      setSessionMatches(sessionMatches.filter((_, index) => index !== matchIndex))
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>🏆 Squash Match Tracker</h1>
        <p>Loading your squash data...</p>
        <div style={{ margin: '20px' }}>⏳</div>
      </div>
    )
  }

  if (currentView === 'newSession') {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h1>Create New Session</h1>
          <button onClick={() => setCurrentView('dashboard')} style={{ padding: '10px 20px' }}>
            Back to Dashboard
          </button>
        </div>

        <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
          <h3>Select Players for Today</h3>
          <p>Choose who's playing today. We'll automatically generate matches.</p>
          
          <div style={{ marginBottom: '20px' }}>
            {players.map((player) => (
              <div key={player.id} style={{ margin: '10px 0' }}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedPlayersForSession.includes(player.id)}
                    onChange={(e) => handlePlayerSelection(player.id, e.target.checked)}
                    style={{ marginRight: '10px' }}
                  />
                  {player.name}
                </label>
              </div>
            ))}
          </div>
          
          <button 
            onClick={createSessionWithPlayers}
            disabled={selectedPlayersForSession.length < 2}
            style={{ 
              padding: '15px 30px', 
              fontSize: '16px',
              backgroundColor: selectedPlayersForSession.length >= 2 ? '#22c55e' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: selectedPlayersForSession.length >= 2 ? 'pointer' : 'not-allowed'
            }}
          >
            {selectedPlayersForSession.length < 2 
              ? 'Select at least 2 players' 
              : `Create Session with ${selectedPlayersForSession.length} Players`
            }
          </button>
        </div>
      </div>
    )
  }

  if (currentView === 'session') {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h1>Session #{currentSession?.id}</h1>
            <p>{currentSession?.completed ? 'Completed' : 'In Progress'} • {sessionMatches.length} matches</p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              onClick={() => deleteSession(currentSession?.id)} 
              style={{ 
                padding: '10px 20px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px'
              }}
            >
              Delete Session
            </button>
            <button 
              onClick={() => setCurrentView('dashboard')} 
              style={{ padding: '10px 20px' }}
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {sessionMatches.map((match, index) => (
            <div key={index} style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3>Match {index + 1}: {match.player1.name} vs {match.player2.name}</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {match.completed && (
                    <span style={{ color: '#22c55e', fontWeight: 'bold' }}>✓ Completed</span>
                  )}
                  {!currentSession?.completed && !match.completed && (
                    <button
                      onClick={() => removeMatch(index, match.id)}
                      style={{ 
                        padding: '5px 10px',
                        backgroundColor: '#ef4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px'
                      }}
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
              
              {!match.completed && !currentSession?.completed && (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                        {match.player1.name}
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="99"
                        value={match.player1_score}
                        onChange={(e) => updateMatchScore(index, 'player1_score', e.target.value)}
                        style={{ 
                          textAlign: 'center', 
                          fontSize: '24px', 
                          fontWeight: 'bold',
                          padding: '15px',
                          width: '100px',
                          border: '2px solid #3b82f6',
                          borderRadius: '8px'
                        }}
                        placeholder="0"
                      />
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                        {match.player2.name}
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="99"
                        value={match.player2_score}
                        onChange={(e) => updateMatchScore(index, 'player2_score', e.target.value)}
                        style={{ 
                          textAlign: 'center', 
                          fontSize: '24px', 
                          fontWeight: 'bold',
                          padding: '15px',
                          width: '100px',
                          border: '2px solid #3b82f6',
                          borderRadius: '8px'
                        }}
                        placeholder="0"
                      />
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <button 
                      onClick={() => submitMatch(index)}
                      disabled={!match.player1_score || !match.player2_score}
                      style={{
                        padding: '15px 30px',
                        fontSize: '18px',
                        backgroundColor: match.player1_score && match.player2_score ? '#22c55e' : '#ccc',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: match.player1_score && match.player2_score ? 'pointer' : 'not-allowed'
                      }}
                    >
                      Submit Match
                    </button>
                  </div>
                </div>
              )}
              
              {match.completed && (
                <div>
                  <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                      Final Score: {match.player1.name} {match.player1_score} - {match.player2_score} {match.player2.name}
                    </div>
                    {match.winner_name && (
                      <div style={{ color: '#22c55e', fontWeight: 'bold' }}>
                        🏆 {match.winner_name} wins!
                      </div>
                    )}
                  </div>
                  
                  {match.elo_changes && (
                    <div style={{ backgroundColor: '#f3f4f6', padding: '15px', borderRadius: '8px' }}>
                      <h4 style={{ textAlign: 'center', marginBottom: '15px' }}>ELO Changes</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontWeight: 'bold' }}>{match.elo_changes.player1.name}</div>
                          <div>{match.elo_changes.player1.elo_before} → {match.elo_changes.player1.elo_after}</div>
                          <div style={{ 
                            fontSize: '18px', 
                            fontWeight: 'bold',
                            color: match.elo_changes.player1.elo_change >= 0 ? '#22c55e' : '#ef4444'
                          }}>
                            {match.elo_changes.player1.elo_change >= 0 ? '+' : ''}{match.elo_changes.player1.elo_change}
                          </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontWeight: 'bold' }}>{match.elo_changes.player2.name}</div>
                          <div>{match.elo_changes.player2.elo_before} → {match.elo_changes.player2.elo_after}</div>
                          <div style={{ 
                            fontSize: '18px', 
                            fontWeight: 'bold',
                            color: match.elo_changes.player2.elo_change >= 0 ? '#22c55e' : '#ef4444'
                          }}>
                            {match.elo_changes.player2.elo_change >= 0 ? '+' : ''}{match.elo_changes.player2.elo_change}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (currentView === 'managePlayer') {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h1>Manage Players</h1>
          <button onClick={() => setCurrentView('dashboard')} style={{ padding: '10px 20px' }}>
            Back to Dashboard
          </button>
        </div>

        <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
          <h3>Add New Player</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              placeholder="Enter player name..."
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addPlayer()}
              style={{ padding: '10px', flex: 1 }}
            />
            <button 
              onClick={addPlayer} 
              style={{ 
                padding: '10px 20px',
                backgroundColor: '#22c55e',
                color: 'white',
                border: 'none',
                borderRadius: '8px'
              }}
            >
              Add Player
            </button>
          </div>
        </div>

        <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
          <h3>Current Players</h3>
          <div>
            {players.map((player) => (
              <div key={player.id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '10px',
                border: '1px solid #eee',
                borderRadius: '4px',
                margin: '5px 0'
              }}>
                <span style={{ fontWeight: 'bold' }}>{player.name}</span>
                <span style={{ color: '#666' }}>
                  Added {new Date(player.created_at).toLocaleDateString('en-US')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Dashboard View
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1>🏆 Squash Match Tracker</h1>
        <p>Track matches and crown the ultimate champion</p>
      </div>
    
      <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginBottom: '30px' }}>
        <button 
          onClick={() => setCurrentView('newSession')} 
          style={{ 
            padding: '15px 30px',
            backgroundColor: '#22c55e',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px'
          }}
        >
          ➕ New Session
        </button>
        <button 
          onClick={() => setCurrentView('managePlayer')} 
          style={{ 
            padding: '15px 30px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px'
          }}
        >
          👥 Manage Players
        </button>
      </div>

      {/* Leaderboard */}
      <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>🏆 Leaderboard</h2>
        <p>Ranking based on ELO rating</p>
        {leaderboard.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            No matches yet! Create your first session to start tracking.
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f3f4f6' }}>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Rank</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Player</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>ELO Rating</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Matches</th>
                <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((player, index) => (
                <tr key={player.id}>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {index === 0 ? '🏆' : index === 1 ? '🥈' : index === 2 ? '🥉' : ''} #{index + 1}
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{player.name}</td>
                  <td style={{ padding: '10px', border: '1px solid #ddd', fontWeight: 'bold', color: '#3b82f6' }}>
                    {player.elo_rating}
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{player.matches_played}</td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{player.win_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Recent Sessions */}
      <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
        <h2>📅 Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            No sessions yet. Create your first session!
          </p>
        ) : (
          <div>
            {sessions.slice(0, 5).map((session) => (
              <div key={session.id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '15px',
                border: '1px solid #eee',
                borderRadius: '8px',
                margin: '10px 0'
              }}>
                <div>
                  <p style={{ fontWeight: 'bold', margin: '0' }}>Session #{session.id}</p>
                  <p style={{ color: '#666', margin: '5px 0 0 0' }}>
                    {new Date(session.created_at).toLocaleDateString('en-US')} • {session.matches?.length || 0} matches
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  {session.completed ? (
                    <span style={{ color: '#22c55e', fontWeight: 'bold' }}>✓ Completed</span>
                  ) : (
                    <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>In Progress</span>
                  )}
                  <button
                    onClick={() => fetchSessionDetails(session.id)}
                    style={{ 
                      padding: '8px 15px',
                      backgroundColor: '#f3f4f6',
                      border: '1px solid #ccc',
                      borderRadius: '4px'
                    }}
                  >
                    View
                  </button>
                  <button
                    onClick={() => deleteSession(session.id)}
                    style={{ 
                      padding: '8px 12px',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px'
                    }}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default App

