import React from 'react';

const EdutantIcon = ({ size = 28, className = '' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'inline-block', verticalAlign: 'middle', transition: 'transform 0.3s ease' }}
    >
      <rect x="15" y="15" width="70" height="70" rx="18" stroke="var(--primary-green)" strokeWidth="8" fill="var(--primary-green-light)" />
      <path
        d="M35 32 H65 M35 50 H57 M35 68 H65 M35 32 V68"
        stroke="var(--primary-green)"
        strokeWidth="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default EdutantIcon;
