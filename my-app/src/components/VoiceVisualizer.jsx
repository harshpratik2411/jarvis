import { useEffect, useRef, useState } from 'react';

const VoiceVisualizer = ({ isActive, intensity = 0.5 }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const [bars, setBars] = useState(Array(20).fill(4));

  useEffect(() => {
    if (!isActive) {
      setBars(Array(20).fill(4));
      return;
    }

    const interval = setInterval(() => {
      setBars(prev => prev.map(() => {
        const baseHeight = 4;
        const randomHeight = Math.random() * 40 * intensity;
        return baseHeight + randomHeight;
      }));
    }, 100);

    return () => clearInterval(interval);
  }, [isActive, intensity]);

  // Canvas-based circular visualizer
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 80;

    let frame = 0;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (!isActive) {
        // Idle state - gentle pulse
        const pulseRadius = radius + Math.sin(frame * 0.05) * 5;
        ctx.beginPath();
        ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 212, 255, 0.2)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        frame++;
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      // Active voice visualization
      const bars = 60;
      const barWidth = (Math.PI * 2) / bars;

      for (let i = 0; i < bars; i++) {
        const angle = i * barWidth - Math.PI / 2;
        const barHeight = 10 + Math.random() * 30 * intensity + Math.sin(frame * 0.1 + i * 0.2) * 10;
        
        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        const x2 = centerX + Math.cos(angle) * (radius + barHeight);
        const y2 = centerY + Math.sin(angle) * (radius + barHeight);

        const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
        gradient.addColorStop(0, 'rgba(0, 212, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.stroke();
      }

      // Inner glow
      const glowRadius = radius - 10 + Math.sin(frame * 0.1) * 5;
      const glowGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, glowRadius);
      glowGradient.addColorStop(0, 'rgba(0, 212, 255, 0.3)');
      glowGradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
      
      ctx.beginPath();
      ctx.arc(centerX, centerY, glowRadius, 0, Math.PI * 2);
      ctx.fillStyle = glowGradient;
      ctx.fill();

      frame++;
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, intensity]);

  return (
    <div className="relative flex items-center justify-center">
      {/* Canvas circular visualizer */}
      <canvas 
        ref={canvasRef}
        width={300}
        height={300}
        className="absolute"
      />
      
      {/* Bar visualizer at bottom */}
      <div className="flex items-end justify-center gap-1 h-16 mt-48">
        {bars.map((height, index) => (
          <div
            key={index}
            className="w-1.5 bg-gradient-to-t from-jarvis-cyan to-jarvis-cyan/50 rounded-full transition-all duration-100"
            style={{
              height: `${height}px`,
              opacity: isActive ? 1 : 0.3,
              animationDelay: `${index * 0.05}s`
            }}
          />
        ))}
      </div>

      {/* Status text */}
      <div className="absolute -bottom-8 text-center">
        <span className={`text-xs font-medium tracking-widest uppercase ${isActive ? 'text-jarvis-cyan animate-pulse' : 'text-gray-500'}`}>
          {isActive ? 'Listening...' : 'Standby'}
        </span>
      </div>
    </div>
  );
};

export default VoiceVisualizer;
