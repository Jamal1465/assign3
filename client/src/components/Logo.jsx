import React from 'react';

function Logo({ className = "w-10 h-10", iconClassName = "w-6 h-6" }) {
  return (
    <div className={`${className} bg-[#4FC3F7] rounded-lg flex items-center justify-center`}>
      <svg className={`${iconClassName} text-white`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    </div>
  );
}

export default Logo;


