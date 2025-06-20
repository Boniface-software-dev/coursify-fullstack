// client/src/App.js
import React, { useState, useEffect } from 'react';
// BrowserRouter: The main router component that enables client-side routing.
// Routes: A container for Route components. Only one Route inside Routes can be active at a time.
// Route: Defines a specific URL path and the component to render when that path is active.
// Link: Used for navigation between routes (prevents full page reloads).
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Import your page components. We will create these files next.
import CourseListPage from './pages/CourseListPage';
import CourseDetailPage from './pages/CourseDetailPage';
import MyCoursesPage from './pages/MyCoursesPage';
import CourseFormPage from './pages/CourseFormPage'; // For Add/Edit Course

// Import your main CSS file for global styles.
import './App.css'; 

// --- NavBar Component ---
// This component will be displayed on every page (because it's outside <Routes>).
function NavBar() {
  return (
    <nav className="navbar">
      {/* Link to the homepage */}
      <Link to="/" className="navbar-brand">Coursify</Link>
      <div className="navbar-links">
        {/* Links for navigation */}
        <Link to="/" className="nav-link">All Courses</Link>
        <Link to="/my_courses" className="nav-link">My Courses</Link>
        <Link to="/courses/new" className="nav-link">Add Course</Link>
        {/* Placeholder for Login/Logout links (you'll implement authentication later) */}
        <Link to="/login" className="nav-link">Login</Link>
      </div>
    </nav>
  );
}

// --- Main App Component ---
function App() {
  // In a real app, you would manage user authentication state here (e.g., isLoggedIn, currentUser)
  // For now, we keep it simple.

  return (
    // <Router> wraps your entire application to enable routing.
    <Router>
      {/* The NavBar is placed outside <Routes> so it appears on every page. */}
      <NavBar />
      {/* A container div for consistent page layout. */}
      <div className="container">
        {/* <Routes> acts like a switch, rendering only the first <Route> that matches the current URL. */}
        <Routes>
          {/* Route for the homepage: renders CourseListPage when the path is exactly "/" */}
          <Route path="/" element={<CourseListPage />} />
          {/* Route for individual course details:
             ":id" is a URL parameter, meaning it will match /courses/1, /courses/2, etc.
             The actual ID can be accessed inside CourseDetailPage.js using useParams(). */}
          <Route path="/courses/:id" element={<CourseDetailPage />} />
          {/* Route for the user's enrolled courses page */}
          <Route path="/my_courses" element={<MyCoursesPage />} />
          {/* Route for adding new courses (will contain a form) */}
          <Route path="/courses/new" element={<CourseFormPage />} />
          {/* Placeholder for a login route (future) */}
          {/* <Route path="/login" element={<LoginPage />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App; // Export the App component to be used by index.js