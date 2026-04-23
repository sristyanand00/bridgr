import React from 'react';
import Icon from './Icon.jsx';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  icon, 
  iconPosition = 'left',
  disabled = false,
  onClick,
  className = '',
  style = {},
  ...props 
}) => {
  const baseClasses = 'btn';
  const variantClasses = {
    primary: 'bg',
    secondary: 'bgl',
  };
  const sizeClasses = {
    small: 'bsm',
    medium: '',
    large: '',
  };

  const classes = [
    baseClasses,
    variantClasses[variant] || variantClasses.primary,
    sizeClasses[size] || sizeClasses.medium,
    className
  ].filter(Boolean).join(' ');

  const renderIcon = () => {
    if (!icon) return null;
    return <Icon name={icon} s={size === 'small' ? 13 : 16} c={variant === 'primary' ? 'white' : 'currentColor'} />;
  };

  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
      style={{
        opacity: disabled ? 0.45 : 1,
        cursor: disabled ? 'not-allowed' : 'none',
        ...style
      }}
      {...props}
    >
      {iconPosition === 'left' && renderIcon()}
      <span>{children}</span>
      {iconPosition === 'right' && renderIcon()}
    </button>
  );
};

export default Button;
