'use client';

import { useState, useEffect } from 'react';

export interface MobileState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isTouchDevice: boolean;
  orientation: 'portrait' | 'landscape';
  screenWidth: number;
  screenHeight: number;
}

export function useMobile(): MobileState {
  const [state, setState] = useState<MobileState>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    isTouchDevice: false,
    orientation: 'portrait',
    screenWidth: 1920,
    screenHeight: 1080,
  });

  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      
      setState({
        isMobile: width < 640,
        isTablet: width >= 640 && width < 1024,
        isDesktop: width >= 1024,
        isTouchDevice,
        orientation: width > height ? 'landscape' : 'portrait',
        screenWidth: width,
        screenHeight: height,
      });
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    window.addEventListener('orientationchange', checkMobile);

    return () => {
      window.removeEventListener('resize', checkMobile);
      window.removeEventListener('orientationchange', checkMobile);
    };
  }, []);

  return state;
}

export function useSwipeGesture(
  onSwipeLeft?: () => void,
  onSwipeRight?: () => void,
  onSwipeUp?: () => void,
  onSwipeDown?: () => void,
  threshold: number = 50
) {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    if (!touchStart || !touchEnd) return;

    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    if (absDeltaX > threshold || absDeltaY > threshold) {
      if (absDeltaX > absDeltaY) {
        if (deltaX > 0 && onSwipeRight) {
          onSwipeRight();
        } else if (deltaX < 0 && onSwipeLeft) {
          onSwipeLeft();
        }
      } else {
        if (deltaY > 0 && onSwipeDown) {
          onSwipeDown();
        } else if (deltaY < 0 && onSwipeUp) {
          onSwipeUp();
        }
      }
    }

    setTouchStart(null);
    setTouchEnd(null);
  }, [touchEnd, touchStart, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, threshold]);

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  return {
    onTouchStart,
    onTouchMove,
  };
}

export function useLongPress(
  callback: () => void,
  duration: number = 500
) {
  const [longPressTriggered, setLongPressTriggered] = useState(false);
  const timeout = useState<NodeJS.Timeout | null>(null);

  const start = () => {
    setLongPressTriggered(false);
    const id = setTimeout(() => {
      callback();
      setLongPressTriggered(true);
    }, duration);
    timeout[1](id);
  };

  const clear = () => {
    timeout[0] && clearTimeout(timeout[0]);
    setLongPressTriggered(false);
  };

  return {
    onMouseDown: start,
    onMouseUp: clear,
    onMouseLeave: clear,
    onTouchStart: start,
    onTouchEnd: clear,
    longPressTriggered,
  };
}
