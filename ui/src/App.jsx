/**
 * App.jsx — Router for the Antenatal Review Board.
 * 3 routes: Landing (/), Dashboard (/dashboard), About (/about)
 */
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import AboutPage from './pages/AboutPage';

const pageVariants = {
  initial: { opacity: 0, y: 32, filter: 'blur(6px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -32, filter: 'blur(6px)' },
};

const pageTransition = { duration: 0.45, ease: [0.22, 1, 0.36, 1] };

function PageWrapper({ children }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={pageTransition}
    >
      {children}
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageWrapper><LandingPage /></PageWrapper>} />
        <Route path="/dashboard" element={<PageWrapper><DashboardPage /></PageWrapper>} />
        <Route path="/about" element={<PageWrapper><AboutPage /></PageWrapper>} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <a href="#main-content" className="skip-to-content">Skip to content</a>
      <main id="main-content" tabIndex={-1}>
        <AnimatedRoutes />
      </main>
    </BrowserRouter>
  );
}
