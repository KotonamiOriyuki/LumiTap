// Created: 23:00
// Version 1.1
// Every scripts related to scoring systems
// Changelog: Dec 16, 21:00 Added score calculation to the script

// Chenxi Liu: obtain the color for different difficulties
export function getDifficultyStyle(level) {
  if (level < 5) {
    return { bg: '#c8e6c9', text: '#2e7d32' }
  } else if (level < 7) {
    return { bg: '#fff9c4', text: '#f9a825' }
  } else if (level < 10) {
    return { bg: '#e1bee7', text: '#7b1fa2' }
  } else {
    return { bg: '#ffcdd2', text: '#c62828' }
  }
}

// Rongze Fan: use sigmoid function to calculate smooth score
export function calculateScore(greatCount, goodCount, missCount, maxCombo, totalNotes) {
  const totalJudgments = greatCount + goodCount + missCount
  if (totalJudgments === 0) return { score: 0, accuracy: 0 }

  const accuracy = ((greatCount * 100 + goodCount * 50) / (totalJudgments * 100)) * 100
  const accScore = 900000 * (accuracy / 100)

  const comboRatio = maxCombo / totalNotes
  const sigmoid = 1 / (1 + Math.exp(-10 * (comboRatio - 0.5)))
  const comboScore = 100000 * sigmoid

  const score = Math.round(accScore + comboScore)

  return { score, accuracy: Math.round(accuracy * 100) / 100 }
}

export function getRank(accuracy) {
  if (accuracy >= 100) return 'SS'
  if (accuracy >= 95) return 'S'
  if (accuracy >= 93) return 'A'
  if (accuracy >= 87) return 'B'
  if (accuracy >= 83) return 'C'
  return 'D'
}

export function getRankColor(rank) {
  const colors = {
    'SS': '#ffb300',
    'S': '#ffb300',
    'A': '#4caf50',
    'B': '#2196f3',
    'C': '#9c27b0',
    'D': '#f44336'
  }
  return colors[rank] || '#ffffff'
}