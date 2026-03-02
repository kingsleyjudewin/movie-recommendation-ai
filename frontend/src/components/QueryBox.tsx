import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";

interface QueryBoxProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function QueryBox({ onSubmit, isLoading }: QueryBoxProps) {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) onSubmit(query.trim());
  };

  return (
    <motion.div
      className="w-full max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 1, ease: [0.22, 1, 0.36, 1] }}
    >
      <form onSubmit={handleSubmit}>
        <div
          className={`glass-panel-enhanced p-2 transition-all duration-500 ${
            isFocused ? "glass-panel-focus" : ""
          }`}
        >
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="I'm bored. Suggest funny movies in English above 8 IMDb."
              className="flex-1 bg-transparent px-4 py-3 text-foreground placeholder:text-muted-foreground/50 text-sm md:text-base font-sans outline-none"
              disabled={isLoading}
            />
            <div className="relative flex-shrink-0">
              <motion.div
                className="absolute -inset-1 rounded-full opacity-40"
                style={{ background: "radial-gradient(circle, hsl(28 25% 78% / 0.25), transparent)" }}
                animate={{ scale: [1, 1.2, 1], opacity: [0.25, 0.45, 0.25] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="relative flex items-center gap-2 px-5 py-2.5 rounded-xl bg-secondary hover:bg-secondary/80 text-secondary-foreground text-sm font-medium transition-all duration-300 hover:shadow-lg disabled:opacity-40"
              >
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="hidden sm:inline">Suggest</span>
              </button>
            </div>
          </div>
        </div>
      </form>

      <AnimatePresence>
        {isLoading && (
          <motion.div
            className="flex flex-col items-center mt-8 gap-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Floating particles */}
            <div className="relative w-40 h-8">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="loading-particle"
                  style={{ left: `${15 + i * 18}%` }}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <div className="neural-dot" />
              <div className="neural-dot" />
              <div className="neural-dot" />
            </div>
            <p className="text-muted-foreground text-sm font-light tracking-wide">
              Analyzing your mood...
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
