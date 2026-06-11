import React from 'react';

export default function AIPulse({ children, isActive = false, isThinking = false }) {
  return (
    <div className={`ai-pulse-wrapper ${isActive ? 'active' : ''} ${isThinking ? 'thinking' : ''}`}>
      <div className="ai-pulse-ring" />
      {children}
    </div>
  );
}
