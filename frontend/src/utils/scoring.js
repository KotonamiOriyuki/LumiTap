// Created: 23:00
// Version 1.2
// Every scripts related to scoring systems
// Changelog: Dec 16, 21:00 Added score calculation to the script
// Changelog: Dec 18, 20:00 added EP color display
// Changelog: Dec 31, 10:00 now each combo counts to the final score

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
// Chenxi Liu: now each combo counts to the final score
export function calculateScore(judgment, totalNotes, currentCombo) {
  if (totalNotes === 0) return { accInc: 0, comboInc: 0 }

  let accInc = 0
  const singleNoteAccValue = 900000 / totalNotes
  if (judgment === 'great') accInc = singleNoteAccValue
  if (judgment === 'good') accInc = singleNoteAccValue * 0.5

  let comboInc = 0
  if (judgment !== 'miss' && currentCombo > 0) {
    const getNormalizedVal = (c) => {
      const ratio = c / totalNotes
      const rawSigmoid = (r) => 1 / (1 + Math.exp(-10 * (r - 0.5)))
      const minS = rawSigmoid(0)
      const maxS = rawSigmoid(1)
      return (rawSigmoid(ratio) - minS) / (maxS - minS)
    }
    comboInc = 100000 * (getNormalizedVal(currentCombo) - getNormalizedVal(currentCombo - 1))
  }

  return { accInc, comboInc }
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

// Zheng Wu: implement EP color display on the personal information
export function getEPColor(ep) {
  if (ep < 5) return '#4caf50'
  if (ep < 7) return '#2196f3'
  if (ep < 9) return '#9c27b0'
  if (ep < 10) return '#ffb300'
  return '#ffd700'
}

export function isHighEP(ep) {
  return ep >= 10
}