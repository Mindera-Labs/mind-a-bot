import React, { useEffect, useRef, useState } from 'react';
import { RotateCcw, RotateCw } from 'react-feather';
import './JoystickComponent.scss';

interface JoystickProps {
  onMove: (x: number, y: number) => void;
  onRotate: (z: number) => void;
  onRelease: () => void;
  size?: number;
}

export const JoystickComponent: React.FC<JoystickProps> = ({ 
  onMove, 
  onRotate,
  onRelease, 
  size = 150 
}) => {
  const joystickRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleStart = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    setDragging(true);
    if (joystickRef.current) {
      const rect = joystickRef.current.getBoundingClientRect();
      const center = {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
      };

      let clientX, clientY;
      if ('touches' in e) {
        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;
      } else {
        clientX = e.clientX;
        clientY = e.clientY;
      }

      updateJoystickPosition(clientX, clientY, center);
    }
  };

  const updateJoystickPosition = (clientX: number, clientY: number, center: { x: number, y: number }) => {
    const maxDistance = size / 3;
    let x = clientX - center.x;
    let y = clientY - center.y;

    const distance = Math.sqrt(x * x + y * y);
    if (distance > maxDistance) {
      x = (x / distance) * maxDistance;
      y = (y / distance) * maxDistance;
    }

    const normalizedX = x / maxDistance;
    const normalizedY = -y / maxDistance;

    setPosition({ x, y });
    onMove(normalizedX, normalizedY);
  };

  const handleMove = (e: MouseEvent | TouchEvent) => {
    if (!dragging || !joystickRef.current) return;

    const rect = joystickRef.current.getBoundingClientRect();
    const center = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };

    let clientX, clientY;
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    updateJoystickPosition(clientX, clientY, center);
  };

  const handleEnd = () => {
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    onRelease();
  };

  useEffect(() => {
    if (dragging) {
      window.addEventListener('mousemove', handleMove);
      window.addEventListener('mouseup', handleEnd);
      window.addEventListener('touchmove', handleMove);
      window.addEventListener('touchend', handleEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleEnd);
      window.removeEventListener('touchmove', handleMove);
      window.removeEventListener('touchend', handleEnd);
    };
  }, [dragging]);

  return (
    <div 
      className="joystick-container" 
      ref={joystickRef}
      style={{ width: size, height: size }}
    >
      <div 
        className="joystick-base"
        onMouseDown={handleStart}
        onTouchStart={handleStart}
      >
        <div 
          className="joystick-stick"
          style={{
            transform: `translate(${position.x}px, ${position.y}px)`
          }}
        />
      </div>
      <div className="rotation-controls">
        <button
          className="rotation-button"
          onMouseDown={() => onRotate(-0.5)}
          onMouseUp={() => onRotate(0)}
          onMouseLeave={() => onRotate(0)}
          onTouchStart={() => onRotate(-0.5)}
          onTouchEnd={() => onRotate(0)}
        >
          <RotateCcw />
        </button>
        <button
          className="rotation-button"
          onMouseDown={() => onRotate(0.5)}
          onMouseUp={() => onRotate(0)}
          onMouseLeave={() => onRotate(0)}
          onTouchStart={() => onRotate(0.5)}
          onTouchEnd={() => onRotate(0)}
        >
          <RotateCw />
        </button>
      </div>
    </div>
  );
};
