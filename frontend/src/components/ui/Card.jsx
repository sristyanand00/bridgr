import React from 'react';

const Card = ({ children, className = '', style = {}, hover = true, ...props }) => {
  const baseClasses = 'mc';
  const hoverClasses = hover ? '' : '';
  
  const classes = [
    baseClasses,
    hoverClasses,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style} {...props}>
      {children}
    </div>
  );
};

export default Card;
