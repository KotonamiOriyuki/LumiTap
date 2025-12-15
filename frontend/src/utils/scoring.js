// Created: 23:00
// Version 1.0
// Every scripts related to scoring systems

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