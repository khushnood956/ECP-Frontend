import React from 'react';
import EdutantIcon from './EdutantIcon';

const EdutantLoader = ({ variant = 'inline', size = 32, message = 'Loading...' }) => {
  // Styles for keyframe animations (injected dynamically or via index.css)
  const pulseStyle = {
    animation: 'edutantPulse 1.5s ease-in-out infinite'
  };

  const spinnerStyle = {
    animation: 'edutantSpin 0.8s linear infinite',
    border: '2px solid var(--bg-gray)',
    borderTop: '2px solid var(--primary-green)',
    borderRadius: '50%',
    width: size,
    height: size,
    display: 'inline-block'
  };

  if (variant === 'button') {
    return <span style={spinnerStyle}></span>;
  }

  if (variant === 'full') {
    return (
      <div 
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'var(--bg-white)',
          zIndex: 9999,
          gap: '1rem',
          animation: 'edutantFadeIn 0.3s ease-out'
        }}
      >
        <div style={pulseStyle}>
          <EdutantIcon size={64} />
        </div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-dark)', margin: 0 }}>Edutant</h3>
        {message && <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', margin: 0 }}>{message}</p>}
      </div>
    );
  }

  // default: 'inline'
  return (
    <div 
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        gap: '0.75rem',
        width: '100%',
        animation: 'edutantFadeIn 0.3s ease-out'
      }}
    >
      <div style={pulseStyle}>
        <EdutantIcon size={size} />
      </div>
      {message && <span style={{ fontSize: '0.875rem', color: 'var(--text-gray)' }}>{message}</span>}
    </div>
  );
};

export default EdutantLoader;
