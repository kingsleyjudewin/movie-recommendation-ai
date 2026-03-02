import { motion } from "framer-motion";
import MovieCard, { type Movie } from "./MovieCard";

interface ResultGridProps {
  movies: Movie[];
  onMovieClick: (movie: Movie) => void;
}

export default function ResultGrid({ movies, onMovieClick }: ResultGridProps) {
  if (movies.length === 0) return null;

  return (
    <motion.div
      className="w-full max-w-4xl mx-auto mt-14 md:mt-20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5">
        {movies.map((movie, i) => (
          <MovieCard
            key={movie.title}
            movie={movie}
            index={i}
            onClick={() => onMovieClick(movie)}
          />
        ))}
      </div>
    </motion.div>
  );
}
