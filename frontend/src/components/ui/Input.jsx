import React from 'react';

const Input = ({ 
  placeholder, 
  value, 
  onChange, 
  type = 'text', 
  className = '', 
  style = {},
  ...props 
}) => {
  return (
    <input
      type={type}
      className={`inp ${className}`}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      style={style}
      {...props}
    />
  );
};

export default Input;
