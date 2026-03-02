import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, User, Film } from "lucide-react";
import type { Movie } from "./MovieCard";

interface MovieDetails {
  title: string;
  summary: string;
  cast: string[];
}

interface MovieDetailModalProps {
  movie: Movie | null;
  onClose: () => void;
}

export default function MovieDetailModal({ movie, onClose }: MovieDetailModalProps) {
  const [details, setDetails] = useState<MovieDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch details from the API whenever the selected movie changes.
  useEffect(() => {
    if (!movie) {
      setDetails(null);
      setError(null);
      return;
    }

    setLoading(true);
    setDetails(null);
    setError(null);

    const params = new URLSearchParams({ title: movie.title });
    fetch(`/api/movie/details?${params}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        return res.json() as Promise<MovieDetails>;
      })
      .then((data) => setDetails(data))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load details"))
      .finally(() => setLoading(false));
  }, [movie]);

  // Close on Escape key.
  useEffect(() => {
    if (!movie) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [movie, onClose]);

  return (
    <AnimatePresence>
      {movie && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="glass-panel-enhanced w-full max-w-lg pointer-events-auto relative overflow-hidden"
              initial={{ opacity: 0, scale: 0.92, y: 24 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 24 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            >
              {/* Decorative gradient */}
              <div
                className="pointer-events-none absolute inset-0 opacity-30"
                style={{
                  background:
                    "radial-gradient(ellipse at top left, hsl(28 25% 78% / 0.12), transparent 60%)",
                }}
              />

              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 z-10 p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors duration-200"
                aria-label="Close"
              >
                <X size={18} />
              </button>

              <div className="relative p-6 pt-5">
                {/* Header */}
                <div className="pr-8 mb-4">
                  <h2 className="font-serif text-2xl font-semibold text-foreground mb-1">
                    {movie.title}
                  </h2>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="imdb-badge">IMDb {movie.averageRating.toFixed(1)}</span>
                    {movie.genres.slice(0, 3).map((g) => (
                      <span
                        key={g}
                        className="text-xs text-muted-foreground/70 border border-white/10 px-2 py-0.5 rounded-full"
                      >
                        {g}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Why this was recommended */}
                <p className="text-xs text-muted-foreground/50 font-light italic mb-5 leading-relaxed">
                  {movie.why}
                </p>

                {/* Divider */}
                <div className="border-t border-white/8 mb-5" />

                {/* Loading skeleton */}
                {loading && (
                  <div className="space-y-3 animate-pulse">
                    <div className="flex items-center gap-2 mb-3">
                      <Film size={14} className="text-muted-foreground/40" />
                      <div className="h-3 bg-white/8 rounded w-24" />
                    </div>
                    <div className="h-3 bg-white/8 rounded w-full" />
                    <div className="h-3 bg-white/8 rounded w-5/6" />
                    <div className="h-3 bg-white/8 rounded w-4/6" />
                    <div className="flex items-center gap-2 mt-5 mb-3">
                      <User size={14} className="text-muted-foreground/40" />
                      <div className="h-3 bg-white/8 rounded w-16" />
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-7 bg-white/8 rounded-full w-24" />
                      ))}
                    </div>
                  </div>
                )}

                {/* Error */}
                {error && !loading && (
                  <p className="text-sm text-red-400/70 font-light">{error}</p>
                )}

                {/* Content */}
                {details && !loading && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    {/* Story summary */}
                    <div className="mb-5">
                      <div className="flex items-center gap-2 mb-2">
                        <Film size={13} className="text-primary/60" />
                        <span className="text-xs font-medium text-muted-foreground tracking-widest uppercase">
                          Story
                        </span>
                      </div>
                      <p className="text-sm text-foreground/80 leading-relaxed">
                        {details.summary}
                      </p>
                    </div>

                    {/* Cast */}
                    {details.cast.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <User size={13} className="text-primary/60" />
                          <span className="text-xs font-medium text-muted-foreground tracking-widest uppercase">
                            Cast
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {details.cast.map((actor) => (
                            <span
                              key={actor}
                              className="text-xs text-foreground/70 bg-white/5 border border-white/10 px-3 py-1 rounded-full"
                            >
                              {actor}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
