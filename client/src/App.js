// This is the main entry point for our React application.
// BrowserRouter: The main router component that enables client-side routing.
// Routes: A container for Route components. Only one Route inside Routes can be active at a time.
// Route: Defines a specific URL path and the component to render when that path is active.
// Link: Used for navigation between routes (prevents full page reloads).
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/AuthContext';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Import your page components. We will create these files next.
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute'; // For protecting routes


import CourseListPage from './pages/CourseListPage';
import CourseDetailPage from './pages/CourseDetailPage';
import MyCoursesPage from './pages/MyCoursesPage';
import CourseFormPage from './pages/CourseFormPage'; // For Add/Edit Course

// Import your main CSS file for global styles.
import './App.css'; 

// --- NavBar Component ---
// This component will be displayed on every page (because it's outside <Routes>).
function NavBar() {
  const { currentUser, logout } = useAuth();
  
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">Coursify</Link>
      <div className="navbar-links">
        <Link to="/" className="nav-link">All Courses</Link>
        <Link to="/my_courses" className="nav-link">My Courses</Link>
        {currentUser && <Link to="/courses/new" className="nav-link">Add Course</Link>}
        
        {currentUser ? (
          <button onClick={logout} className="nav-link">Logout</button>
        ) : (
          <Link to="/login" className="nav-link">Login</Link>
        )}
      </div>
    </nav>
  );
}

// --- Main App Component ---
function App() {
  return (
    <AuthProvider>
      <Router>
        <NavBar />
        <div className="container">
          <Routes>
  <Route path="/" element={<CourseListPage />} />
  <Route path="/courses/:id" element={<CourseDetailPage />} />
  
  <Route path="/login" element={<LoginPage />} />
  
  <Route 
    path="/my_courses" 
    element={
      <ProtectedRoute>
        <MyCoursesPage />
      </ProtectedRoute>
    } 
  />
  
  <Route 
    path="/courses/new" 
    element={
      <ProtectedRoute>
        <CourseFormPage />
      </ProtectedRoute>
    } 
  />
</Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; // Export the App component to be used by index.js