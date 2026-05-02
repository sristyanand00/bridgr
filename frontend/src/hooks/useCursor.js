import React, { useEffect, useRef } from 'react';



const useCursor = () => {

  const dotRef = useRef(null);

  const ringRef = useRef(null);

  const posRef = useRef({ x: -100, y: -100 });

  const ringPosRef = useRef({ x: -100, y: -100 });

  const animationFrameRef = useRef(null);



  useEffect(() => {

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

    if (mediaQuery.matches) return;



    const handleMouseMove = (event) => { 

      posRef.current = { x: event.clientX, y: event.clientY }; 

    };



    window.addEventListener("mousemove", handleMouseMove);



    const animate = () => {

      if (dotRef.current) {

        dotRef.current.style.transform = `translate(${posRef.current.x - 3}px,${posRef.current.y - 3}px)`;

      }

      

      ringPosRef.current.x += (posRef.current.x - ringPosRef.current.x) * 0.11;

      ringPosRef.current.y += (posRef.current.y - ringPosRef.current.y) * 0.11;

      

      if (ringRef.current) {

        ringRef.current.style.transform = `translate(${ringPosRef.current.x - 14}px,${ringPosRef.current.y - 14}px)`;

      }

      

      animationFrameRef.current = requestAnimationFrame(animate);

    };



    animate();



    return () => { 

      window.removeEventListener("mousemove", handleMouseMove); 

      if (animationFrameRef.current) {

        cancelAnimationFrame(animationFrameRef.current);

      }

    };

  }, []);



  return { dotRef, ringRef };

};



export default useCursor;

