import { useEffect, useState, useCallback } from "react";
import { motion, useSpring } from "framer-motion";

type CursorVariant = "default" | "button" | "card" | "input";

export default function CustomCursor() {
  const [variant, setVariant] = useState<CursorVariant>("default");
  const [visible, setVisible] = useState(false);
  const [clicking, setClicking] = useState(false);

  const springConfig = { damping: 25, stiffness: 300, mass: 0.5 };
  const x = useSpring(0, springConfig);
  const y = useSpring(0, springConfig);
  const ringX = useSpring(0, { damping: 18, stiffness: 140, mass: 0.8 });
  const ringY = useSpring(0, { damping: 18, stiffness: 140, mass: 0.8 });

  useEffect(() => {
    const move = (e: MouseEvent) => {
      x.set(e.clientX);
      y.set(e.clientY);
      ringX.set(e.clientX);
      ringY.set(e.clientY);
      if (!visible) setVisible(true);
    };

    const handleOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.closest("button, a, [role='button']")) setVariant("button");
      else if (target.closest("[data-cursor='card']")) setVariant("card");
      else if (target.closest("input, textarea")) setVariant("input");
      else setVariant("default");
    };

    const down = () => setClicking(true);
    const up = () => setClicking(false);
    const leave = () => setVisible(false);

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseover", handleOver);
    window.addEventListener("mousedown", down);
    window.addEventListener("mouseup", up);
    window.addEventListener("mouseleave", leave);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseover", handleOver);
      window.removeEventListener("mousedown", down);
      window.removeEventListener("mouseup", up);
      window.removeEventListener("mouseleave", leave);
    };
  }, [visible, x, y, ringX, ringY]);

  if (typeof window !== "undefined" && "ontouchstart" in window) return null;

  const ringSize =
    variant === "button" ? 48 :
    variant === "card" ? 56 :
    variant === "input" ? 4 : 36;
  const ringHeight = variant === "input" ? 24 : ringSize;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-[9999]"
      style={{ opacity: visible ? 1 : 0, transition: "opacity 0.3s" }}
    >
      {/* Play triangle cursor */}
      <motion.div
        className="absolute"
        style={{
          x,
          y,
          translateX: "-50%",
          translateY: "-50%",
        }}
        animate={{
          scale: clicking ? 0.85 : 1,
        }}
        transition={{ type: "spring", damping: 20, stiffness: 300 }}
      >
        <svg
          width="14"
          height="16"
          viewBox="0 0 14 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M1 1.5L13 8L1 14.5V1.5Z"
            fill="hsl(220, 20%, 93%)"
            fillOpacity={variant === "input" ? 0 : 0.9}
            stroke="hsl(220, 20%, 93%)"
            strokeWidth="1"
            strokeOpacity={variant === "input" ? 0 : 0.5}
            strokeLinejoin="round"
          />
        </svg>
      </motion.div>

      {/* Ring follower */}
      <motion.div
        className="absolute rounded-full"
        style={{
          x: ringX,
          y: ringY,
          translateX: "-50%",
          translateY: "-50%",
          border: "1px solid",
        }}
        animate={{
          width: ringSize,
          height: ringHeight,
          borderRadius: variant === "input" ? 2 : ringSize,
          borderColor:
            variant === "button"
              ? "hsl(28 25% 78% / 0.5)"
              : variant === "card"
              ? "hsl(28 25% 78% / 0.35)"
              : "hsl(220 20% 93% / 0.2)",
          boxShadow:
            variant === "button"
              ? "0 0 20px 2px hsl(28 25% 78% / 0.15)"
              : variant === "card"
              ? "0 0 15px 2px hsl(28 25% 78% / 0.08)"
              : "none",
        }}
        transition={{ type: "spring", damping: 20, stiffness: 250 }}
      />
    </div>
  );
}
