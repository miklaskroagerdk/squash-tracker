import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Trophy, Users, Calendar, Plus, Target, UserCheck, Zap, Star, X, CheckCircle, RotateCcw } from 'lucide-react'
import './App.css'

const API_BASE = '/api'

function App() {
  const [players, setPlayers] = useState([])
  const [sessions, setSessions] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [highlights, setHighlights] = useState({ recent_matches: [], stats: {} })
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('dashboard')
  const [selectedPlayers, setSelectedPlayers] = useState([])
  const [selectedPlayersForSession, setSelectedPlayersForSession] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [sessionMatches, setSessionMatches] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [newPlayerName, setNewPlayerName] = useState('')

  // Fetch data on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        // Load data sequentially to avoid race conditions
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
        setPlayers([]) // Ensure consistent state
      }
    } catch (error) {
      console.error('Error fetching players:', error)
      setPlayers([]) // Ensure consistent state
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
        setSessions([]) // Ensure consistent state
      }
    } catch (error) {
      console.error('Error fetching sessions:', error)
      setSessions([]) // Ensure consistent state
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
        setLeaderboard([]) // Ensure consistent state
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      setLeaderboard([]) // Ensure consistent state
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
        setHighlights({ recent_matches: [], stats: {} }) // Ensure consistent state
      }
    } catch (error) {
      console.error('Error fetching highlights:', error)
      setHighlights({ recent_matches: [], stats: {} }) // Ensure consistent state
    }
  }

  const fetchSessionDetails = async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
      if (response.ok) {
        const sessionData = await response.json()
        setCurrentSession(sessionData)
        
        // Format matches to match frontend expectations
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

  // Generate matches for selected players
  const generateMatches = (selectedPlayerIds) => {
    const playerList = selectedPlayerIds.map(id => players.find(p => p.id === id)).filter(Boolean)
    const matches = []
    
    // Generate round-robin matches
    for (let i = 0; i < playerList.length; i++) {
      for (let j = i + 1; j < playerList.length; j++) {
        matches.push({
          player1: playerList[i],
          player2: playerList[j],
          player1_score: '',
          player2_score: '',
          completed: false
        })
      }
    }
    
    // If we have fewer than 5 matches, duplicate some randomly to reach 5
    while (matches.length < 5 && playerList.length >= 2) {
      const randomMatch = matches[Math.floor(Math.random() * matches.length)]
      matches.push({
        player1: randomMatch.player1,
        player2: randomMatch.player2,
        player1_score: '',
        player2_score: '',
        completed: false
      })
    }
    
    return matches.slice(0, 5) // Limit to 5 matches by default
  }

  // Handle checkbox change with proper state management
  const handlePlayerSelection = (playerId, isChecked) => {
    setSelectedPlayersForSession(prevSelected => {
      if (isChecked) {
        // Add player if not already selected
        return prevSelected.includes(playerId) ? prevSelected : [...prevSelected, playerId]
      } else {
        // Remove player
        return prevSelected.filter(id => id !== playerId)
      }
    })
  }

  // Create new session with selected players
  const createSessionWithPlayers = async () => {
    console.log('Creating session with players:', selectedPlayersForSession)
    console.log('Available players:', players)
    
    if (selectedPlayersForSession.length < 2) {
      alert('Please select at least 2 players to create a session.')
      return
    }

    try {
      console.log('Sending session creation request...')
      // Create the session with player_ids
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_ids: selectedPlayersForSession
        })
      })
      
      console.log('Session creation response:', response.status)
      
      if (response.ok) {
        const session = await response.json()
        console.log('Session created:', session)
        setCurrentSession(session)
        
        // The backend already created matches, so we just need to format them for the frontend
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

  // Add another match to current session
  const addAnotherMatch = async () => {
    const selectedPlayers = selectedPlayersForSession.map(id => players.find(p => p.id === id))
    if (selectedPlayers.length >= 2 && currentSession) {
      // Add a random match between selected players
      const player1 = selectedPlayers[Math.floor(Math.random() * selectedPlayers.length)]
      let player2 = selectedPlayers[Math.floor(Math.random() * selectedPlayers.length)]
      while (player2.id === player1.id && selectedPlayers.length > 1) {
        player2 = selectedPlayers[Math.floor(Math.random() * selectedPlayers.length)]
      }
      
      try {
        // Save the new match to the backend
        const matchResponse = await fetch(`${API_BASE}/matches`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: currentSession.id,
            player1_id: player1.id,
            player2_id: player2.id
            // Don't include scores - let them be null initially
          })
        })
        
        if (matchResponse.ok) {
          const savedMatch = await matchResponse.json()
          const newMatch = {
            id: savedMatch.id,
            player1,
            player2,
            player1_score: '',
            player2_score: '',
            completed: false
          }
          
          setSessionMatches([...sessionMatches, newMatch])
          fetchSessions() // Refresh session list
        }
      } catch (error) {
        console.error('Error adding match:', error)
      }
    }
  }

  // Remove match from session
  const removeMatch = async (matchIndex, matchId = null) => {
    if (matchId) {
      // If match is already saved to database, delete it
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
      // Remove from local state if not saved yet
      setSessionMatches(sessionMatches.filter((_, index) => index !== matchIndex))
    }
  }

  // Update match score - Fixed to prevent page jumping
  const updateMatchScore = (matchIndex, field, value) => {
    // Prevent the page from scrolling to top when entering scores
    const updatedMatches = [...sessionMatches]
    updatedMatches[matchIndex][field] = value
    setSessionMatches(updatedMatches)
    
    // Prevent any default behavior that might cause scrolling
    event?.preventDefault()
  }

  // Validate match scores - Fixed to allow 11-0 scores
  const validateMatchScores = (player1Score, player2Score) => {
    // Convert to numbers
    const p1Score = parseInt(player1Score, 10)
    const p2Score = parseInt(player2Score, 10)
    
    // Check if both scores are valid numbers
    if (isNaN(p1Score) || isNaN(p2Score)) {
      return { valid: false, message: "Both scores must be valid numbers" }
    }
    
    // Check if scores are non-negative
    if (p1Score < 0 || p2Score < 0) {
      return { valid: false, message: "Scores cannot be negative" }
    }
    
    // Check if there's a clear winner with at least 11 points
    const maxScore = Math.max(p1Score, p2Score)
    const minScore = Math.min(p1Score, p2Score)
    
    // Winner must have at least 11 points
    if (maxScore < 11) {
      return { valid: false, message: "Winner must have at least 11 points" }
    }
    
    // Special case: Allow 11-0 scores (shutout wins)
    if ((p1Score === 11 && p2Score === 0) || (p1Score === 0 && p2Score === 11)) {
      return { valid: true }
    }
    
    // For scores above 11, check if there's a clear winner (2 point difference)
    if (maxScore > 11 && maxScore - minScore < 2) {
      return { valid: false, message: "Winner must have at least a 2 point lead when score is above 11" }
    }
    
    // Ensure there's actually a winner (scores can't be equal)
    if (p1Score === p2Score) {
      return { valid: false, message: "There must be a clear winner - scores cannot be equal" }
    }
    
    return { valid: true }
  }

  // Submit individual match
  const submitMatch = async (matchIndex) => {
    const match = sessionMatches[matchIndex]
    
    if (!match.player1_score || !match.player2_score) {
      alert('Please enter scores for both players.')
      return
    }

    // Validate scores
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
      console.log('Submitting match:', match.id, 'with scores:', match.player1_score, match.player2_score)
      
      // Always use PUT to update existing matches
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
        console.log('Match updated successfully:', savedMatch)
        
        // Update local state to mark match as completed and include ELO changes
        const updatedMatches = [...sessionMatches]
        updatedMatches[matchIndex] = {
          ...match,
          completed: true,
          player1_score: savedMatch.player1_score,
          player2_score: savedMatch.player2_score,
          winner_name: savedMatch.winner_name,
          elo_changes: savedMatch.elo_changes // Store ELO changes for display
        }
        setSessionMatches(updatedMatches)
        
        // Refresh leaderboard, sessions, and highlights
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

  // Complete session
  const completeSession = async () => {
    if (!currentSession) return
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${currentSession.id}/complete`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const updatedSession = await response.json()
        setCurrentSession(updatedSession)
        fetchSessions()
      }
    } catch (error) {
      console.error('Error completing session:', error)
    }
  }

  // Reopen session
  const reopenSession = async () => {
    if (!currentSession) return
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${currentSession.id}/reopen`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const updatedSession = await response.json()
        setCurrentSession(updatedSession)
        fetchSessions()
      }
    } catch (error) {
      console.error('Error reopening session:', error)
    }
  }

  // Delete session
  const deleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session? This will delete all matches and revert ELO changes.')) {
      return
    }
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // Refresh all data after deletion
        await fetchSessions()
        await fetchLeaderboard()
        await fetchHighlights()
        
        // If we're currently viewing the deleted session, go back to dashboard
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

  // Get emoji for leaderboard position
  const getPositionEmoji = (position, total) => {
    if (position === 1) return '🏆'
    if (position === 2) return '🥈'
    if (position === 3) return '🥉'
    if (position === total) return '💩'
    return ''
  }

  // Dashboard View
  const DashboardView = () => {
    if (loading) {
      return (
        <div className="space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2">
              🏆 Squash Match Tracker
            </h1>
            <p className="text-muted-foreground">
              Loading your squash data...
            </p>
          </div>
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">
            🏆 Squash Match Tracker
          </h1>
          <p className="text-muted-foreground">
            Track matches and crown the ultimate champion
          </p>
        </div>
      
        <div className="flex gap-4 justify-center">
          <Button onClick={() => setCurrentView('newSession')} className="bg-green-600 hover:bg-green-700 text-white">
            <Plus className="h-4 w-4 mr-2" />
            New Session
          </Button>
          <Button variant="outline" onClick={() => setCurrentView('managePlayer')} className="border-blue-600 text-blue-600 hover:bg-blue-50">
            <Users className="h-4 w-4 mr-2" />
            Manage Players
          </Button>
        </div>

        {/* Leaderboard */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Leaderboard
          </CardTitle>
          <CardDescription>Ranking based on ELO rating</CardDescription>
        </CardHeader>
        <CardContent>
          {leaderboard.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No matches yet! Create your first session to start tracking.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Rank</TableHead>
                  <TableHead>Player</TableHead>
                  <TableHead>ELO Rating</TableHead>
                  <TableHead>Matches</TableHead>
                  <TableHead>Win Rate</TableHead>
                  <TableHead>Avg Points</TableHead>
                  <TableHead>Total Points</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leaderboard.map((player, index) => (
                  <TableRow key={player.id}>
                    <TableCell className="font-medium">
                      {getPositionEmoji(index + 1, leaderboard.length)} #{index + 1}
                    </TableCell>
                    <TableCell>{player.name}</TableCell>
                    <TableCell className="font-bold text-blue-600">{player.elo_rating}</TableCell>
                    <TableCell>{player.matches_played}</TableCell>
                    <TableCell>{player.win_rate}%</TableCell>
                    <TableCell>{player.points_per_match}</TableCell>
                    <TableCell>{player.total_points}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Highlights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Latest Highlights
          </CardTitle>
          <CardDescription>Recent match results and ELO changes</CardDescription>
        </CardHeader>
        <CardContent>
          {highlights.recent_matches.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No recent matches to highlight yet!
            </p>
          ) : (
            <div className="space-y-4">
              {/* Summary Stats */}
              {highlights.stats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{highlights.stats.matches_today || 0}</div>
                    <div className="text-sm text-blue-800">Matches Today</div>
                  </div>
                  {highlights.stats.biggest_elo_gain && (
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">+{highlights.stats.biggest_elo_gain.elo_change}</div>
                      <div className="text-sm text-green-800">Biggest ELO Gain</div>
                      <div className="text-xs text-green-700">{highlights.stats.biggest_elo_gain.player_name}</div>
                    </div>
                  )}
                  {highlights.stats.biggest_elo_loss && (
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">{highlights.stats.biggest_elo_loss.elo_change}</div>
                      <div className="text-sm text-red-800">Biggest ELO Loss</div>
                      <div className="text-xs text-red-700">{highlights.stats.biggest_elo_loss.player_name}</div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Recent Matches */}
              <div className="space-y-3">
                <h4 className="font-semibold text-sm text-gray-700">Recent Match Results</h4>
                {highlights.recent_matches.slice(0, 5).map((match, index) => (
                  <div key={match.match_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <span className="font-medium">{match.player1_name}</span>
                        <span className="mx-2 text-gray-500">{match.player1_score}-{match.player2_score}</span>
                        <span className="font-medium">{match.player2_name}</span>
                      </div>
                      <Badge variant={match.winner_name !== 'Draw' ? 'default' : 'secondary'} className="text-xs">
                        {match.winner_name === 'Draw' ? 'Draw' : `${match.winner_name} wins`}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <div className={`px-2 py-1 rounded ${match.player1_elo_change >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {match.player1_elo_change >= 0 ? '+' : ''}{match.player1_elo_change}
                      </div>
                      <div className={`px-2 py-1 rounded ${match.player2_elo_change >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {match.player2_elo_change >= 0 ? '+' : ''}{match.player2_elo_change}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Recent Sessions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No sessions yet. Create your first session!
            </p>
          ) : (
            <div className="space-y-3">
              {sessions.slice(0, 5).map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Session #{session.id}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(session.created_at).toLocaleDateString('en-US')} • {session.matches?.length || 0} matches
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {session.completed ? (
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Completed
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-blue-600 border-blue-600">
                        In Progress
                      </Badge>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => fetchSessionDetails(session.id)}
                      className="border-gray-300 text-gray-600 hover:bg-gray-50"
                    >
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteSession(session.id)}
                      className="border-red-300 text-red-600 hover:bg-red-50 hover:border-red-400"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
    )
  }

  // New Session View
  const NewSessionView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Create New Session</h1>
        <Button variant="outline" onClick={() => setCurrentView('dashboard')} className="border-gray-300 text-gray-600 hover:bg-gray-50">
          Back to Dashboard
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Select Players for Today
          </CardTitle>
          <CardDescription>
            Choose who's playing today. We'll automatically generate 5 matches.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {players.map((player) => (
            <div key={player.id} className="flex items-center space-x-2">
              <Checkbox
                id={`player-${player.id}`}
                checked={selectedPlayersForSession.includes(player.id)}
                onCheckedChange={(checked) => handlePlayerSelection(player.id, checked)}
              />
              <Label htmlFor={`player-${player.id}`} className="text-sm font-medium">
                {player.name}
              </Label>
            </div>
          ))}
          
          <div className="pt-4">
            <Button 
              onClick={createSessionWithPlayers}
              disabled={selectedPlayersForSession.length < 2}
              className={`w-full ${selectedPlayersForSession.length >= 2 ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
            >
              {selectedPlayersForSession.length < 2 
                ? 'Select at least 2 players' 
                : `Create Session with ${selectedPlayersForSession.length} Players`
              }
            </Button>
            {selectedPlayersForSession.length < 2 && (
              <p className="text-sm text-muted-foreground mt-2">
                Select at least 2 players to create a session
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  // Session View
  const SessionView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Session #{currentSession?.id}</h1>
          <p className="text-muted-foreground">
            {currentSession?.completed ? 'Completed' : 'In Progress'} • {sessionMatches.length} matches
          </p>
        </div>
        <div className="flex gap-2">
          {!currentSession?.completed && (
            <Button onClick={completeSession} variant="outline" className="bg-green-50 text-green-600 border-green-600 hover:bg-green-100">
              <CheckCircle className="h-4 w-4 mr-2" />
              Complete Session
            </Button>
          )}
          {currentSession?.completed && (
            <Button onClick={reopenSession} variant="outline" className="bg-blue-50 text-blue-600 border-blue-600 hover:bg-blue-100">
              <RotateCcw className="h-4 w-4 mr-2" />
              Reopen Session
            </Button>
          )}
          <Button 
            onClick={() => deleteSession(currentSession?.id)} 
            variant="outline" 
            className="border-red-300 text-red-600 hover:bg-red-50 hover:border-red-400"
          >
            <X className="h-4 w-4 mr-2" />
            Delete Session
          </Button>
          <Button variant="outline" onClick={() => setCurrentView('dashboard')} className="border-gray-300 text-gray-600 hover:bg-gray-50">
            Back to Dashboard
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {sessionMatches.map((match, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">
                  Match {index + 1}: {match.player1.name} vs {match.player2.name}
                </h3>
                <div className="flex items-center gap-2">
                  {match.completed && (
                    <Badge variant="outline" className="text-green-600 border-green-600">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Completed
                    </Badge>
                  )}
                  {!currentSession?.completed && !match.completed && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeMatch(index, match.id)}
                      className="text-red-600 hover:text-red-700 border-red-300 hover:border-red-400 hover:bg-red-50"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
              
              {!match.completed && !currentSession?.completed && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-6">
                    <div className="text-center">
                      <Label className="text-lg font-medium mb-2 block">{match.player1.name}</Label>
                      <Input
                        type="number"
                        min="0"
                        max="99"
                        value={match.player1_score}
                        onChange={(e) => {
                          e.preventDefault()
                          updateMatchScore(index, 'player1_score', e.target.value)
                        }}
                        className="text-center text-2xl font-bold h-16 text-blue-600"
                        placeholder="0"
                        // Prevent auto-focus and page jumping
                        autoFocus={false}
                        onFocus={(e) => {
                          e.target.select()
                          e.preventDefault()
                        }}
                        // Prevent any scrolling behavior
                        onInput={(e) => e.preventDefault()}
                        style={{ scrollMarginTop: 0 }}
                      />
                    </div>
                    <div className="text-center">
                      <Label className="text-lg font-medium mb-2 block">{match.player2.name}</Label>
                      <Input
                        type="number"
                        min="0"
                        max="99"
                        value={match.player2_score}
                        onChange={(e) => {
                          e.preventDefault()
                          updateMatchScore(index, 'player2_score', e.target.value)
                        }}
                        className="text-center text-2xl font-bold h-16 text-blue-600"
                        placeholder="0"
                        // Prevent auto-focus and page jumping
                        autoFocus={false}
                        onFocus={(e) => {
                          e.target.select()
                          e.preventDefault()
                        }}
                        // Prevent any scrolling behavior
                        onInput={(e) => e.preventDefault()}
                        style={{ scrollMarginTop: 0 }}
                      />
                    </div>
                  </div>
                  <div className="flex justify-center">
                    <Button 
                      onClick={() => submitMatch(index)}
                      disabled={!match.player1_score || !match.player2_score}
                      className={`px-8 py-3 text-lg ${
                        match.player1_score && match.player2_score 
                          ? 'bg-green-600 hover:bg-green-700 text-white' 
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                      size="lg"
                    >
                      Submit Match
                    </Button>
                  </div>
                </div>
              )}
              
              {match.completed && (
                <div className="space-y-3">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-800">
                      Final Score: {match.player1.name} {match.player1_score} - {match.player2_score} {match.player2.name}
                    </div>
                    {match.winner_name && (
                      <div className="text-sm text-green-600 font-medium">
                        🏆 {match.winner_name} wins!
                      </div>
                    )}
                  </div>
                  
                  {match.elo_changes && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-3 text-center">ELO Changes</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{match.elo_changes.player1.name}</div>
                          <div className="text-sm text-gray-600">{match.elo_changes.player1.elo_before} → {match.elo_changes.player1.elo_after}</div>
                          <div className={`text-lg font-bold ${match.elo_changes.player1.elo_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {match.elo_changes.player1.elo_change >= 0 ? '+' : ''}{match.elo_changes.player1.elo_change}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-gray-800">{match.elo_changes.player2.name}</div>
                          <div className="text-sm text-gray-600">{match.elo_changes.player2.elo_before} → {match.elo_changes.player2.elo_after}</div>
                          <div className={`text-lg font-bold ${match.elo_changes.player2.elo_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {match.elo_changes.player2.elo_change >= 0 ? '+' : ''}{match.elo_changes.player2.elo_change}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
        
        {!currentSession?.completed && (
          <Button onClick={addAnotherMatch} variant="outline" className="w-full bg-blue-50 text-blue-600 border-blue-300 hover:bg-blue-100">
            <Plus className="h-4 w-4 mr-2" />
            Add Another Match
          </Button>
        )}
      </div>
    </div>
  )

  // Manage Players View
  const ManagePlayersView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Manage Players</h1>
        <Button variant="outline" onClick={() => setCurrentView('dashboard')} className="border-gray-300 text-gray-600 hover:bg-gray-50">
          Back to Dashboard
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add New Player</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter player name..."
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addPlayer()}
            />
            <Button onClick={addPlayer} className="bg-green-600 hover:bg-green-700 text-white">Add Player</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Current Players</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {players.map((player) => (
              <div key={player.id} className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">{player.name}</span>
                <span className="text-sm text-muted-foreground">
                  Added {new Date(player.created_at).toLocaleDateString('en-US')}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case 'newSession':
        return <NewSessionView />
      case 'session':
        return <SessionView />
      case 'managePlayer':
        return <ManagePlayersView />
      default:
        return <DashboardView />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {renderCurrentView()}
      </div>
    </div>
  )
}

export default App

