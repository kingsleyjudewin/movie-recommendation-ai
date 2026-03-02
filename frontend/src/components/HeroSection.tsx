import { motion } from "framer-motion";

export default function HeroSection() {
  return (
    <motion.div
      className="flex flex-col items-center text-center mb-16 md:mb-20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="relative">
        {/* Faint blur behind title */}
        <div
          className="absolute inset-0 -inset-x-20 -inset-y-8 rounded-full pointer-events-none"
          style={{
            background: "radial-gradient(ellipse, hsl(28 25% 78% / 0.04), transparent 70%)",
            filter: "blur(30px)",
          }}
        />
        <motion.h1
          className="relative font-serif text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold tracking-tight text-gradient-shimmer text-light-sweep"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
        >
          CineMind AI
        </motion.h1>
      </div>
      <motion.p
        className="mt-5 md:mt-6 text-muted-foreground text-base md:text-lg font-light tracking-wide max-w-md"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.7, ease: [0.22, 1, 0.36, 1] }}
        style={{ animation: "breathe 5s ease-in-out infinite" }}
      >
        Intelligent movie suggestions based on your mood.
      </motion.p>
    </motion.div>
  );
}
