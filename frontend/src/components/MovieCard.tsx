import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

export interface Movie {
  title: string;
  genres: string[];
  averageRating: number;
  finalScore: number; // 0–1 float from the engine
  why: string;
}

interface MovieCardProps {
  movie: Movie;
  index: number;
  onClick?: () => void;
}

function useCountUp(target: number, duration = 1200, delay = 0) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const timeout = setTimeout(() => {
      const start = performance.now();
      const tick = (now: number) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        setValue(Math.round(eased * target));
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }, delay);
    return () => clearTimeout(timeout);
  }, [target, duration, delay]);
  return value;
}

export default function MovieCard({ movie, index, onClick }: MovieCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  // Convert 0–1 float to 0–100 integer for the animated counter
  const matchPercent = Math.round(movie.finalScore * 100);
  const matchDisplay = useCountUp(matchPercent, 1200, index * 100 + 600);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const cx = e.clientX - rect.left - rect.width / 2;
    const cy = e.clientY - rect.top - rect.height / 2;
    cardRef.current.style.setProperty("--mx", `${cx}px`);
    cardRef.current.style.setProperty("--my", `${cy}px`);
  };

  return (
    <motion.div
      ref={cardRef}
      data-cursor="card"
      onClick={onClick}
      className={`glass-panel-enhanced p-6 group hover:border-primary/20 transition-all duration-500 relative overflow-hidden${onClick ? " cursor-pointer" : ""}`}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.6,
        delay: index * 0.1,
        ease: [0.22, 1, 0.36, 1],
      }}
      whileHover={{
        rotateX: -2,
        rotateY: 3,
        scale: 1.02,
        transition: { duration: 0.3 },
      }}
      onMouseMove={handleMouseMove}
      style={{ transformStyle: "preserve-3d" }}
    >
      {/* Cursor-following gradient highlight */}
      <div
        className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background:
            "radial-gradient(300px circle at calc(50% + var(--mx, 0px)) calc(50% + var(--my, 0px)), hsl(28 25% 78% / 0.06), transparent 60%)",
        }}
      />
      {/* Vignette overlay */}
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl"
        style={{
          background:
            "linear-gradient(135deg, transparent 60%, hsl(222 25% 6% / 0.3))",
        }}
      />

      <h3 className="relative font-serif text-xl font-semibold text-foreground mb-1 group-hover:text-primary transition-colors duration-300">
        {movie.title}
      </h3>
      <p className="relative text-muted-foreground text-xs tracking-wide mb-1">
        {movie.genres.join(" · ")}
      </p>
      <p className="relative text-muted-foreground/60 text-xs font-light italic mb-4 line-clamp-2">
        {movie.why}
      </p>
      <div className="relative flex items-center justify-between">
        <span className="imdb-badge">IMDb {movie.averageRating.toFixed(1)}</span>
        <span className="text-muted-foreground text-xs font-light">
          {matchDisplay}% match
        </span>
      </div>
      {onClick && (
        <p className="relative mt-3 text-muted-foreground/30 text-xs font-light group-hover:text-muted-foreground/50 transition-colors duration-300 text-right">
          click for details
        </p>
      )}
    </motion.div>
  );
}
