import { useState, lazy, Suspense, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import HeroSection from "@/components/HeroSection";
import QueryBox from "@/components/QueryBox";
import ResultGrid from "@/components/ResultGrid";
import CustomCursor from "@/components/CustomCursor";
import MovieDetailModal from "@/components/MovieDetailModal";
import type { Movie } from "@/components/MovieCard";

const ThreeBackground = lazy(() => import("@/components/ThreeBackground"));

const API_URL = "/api/recommend";

export default function Index() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  const handleQuery = useCallback(async (query: string) => {
    setIsLoading(true);
    setMovies([]);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 10 }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(
          (body as { detail?: string }).detail ?? `Server error ${res.status}`
        );
      }

      const data = (await res.json()) as { results: Movie[] };
      setMovies(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <>
      <CustomCursor />
      <Suspense fallback={null}>
        <ThreeBackground />
      </Suspense>
      <div className="vignette-overlay" />
      <div className="radial-glow" />
      <div className="grain-overlay" />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-5 py-20">
        <HeroSection />
        <QueryBox onSubmit={handleQuery} isLoading={isLoading} />

        {error && (
          <AnimatePresence>
            <motion.p
              className="mt-6 text-sm text-red-400/80 font-light tracking-wide"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              {error}
            </motion.p>
          </AnimatePresence>
        )}

        <AnimatePresence>
          {movies.length > 0 && (
            <ResultGrid movies={movies} onMovieClick={setSelectedMovie} />
          )}
        </AnimatePresence>
      </div>

      <MovieDetailModal
        movie={selectedMovie}
        onClose={() => setSelectedMovie(null)}
      />
    </>
  );
}
