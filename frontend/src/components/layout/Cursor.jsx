import React from 'react';
import { useCursor } from '../../hooks';

const Cursor = () => {
  const { dotRef, ringRef } = useCursor();

  return (
    <>
      <div ref={dotRef} className="cursor-dot" />
      <div ref={ringRef} className="cursor-ring" />
    </>
  );
};

export default Cursor;
