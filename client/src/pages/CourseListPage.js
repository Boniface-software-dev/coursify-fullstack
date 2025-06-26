import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchCourses } from '../api';

function CourseListPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchCourses()
      .then(data => {
        setCourses(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching courses:", error);
        setError(error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading courses...</p>;
  }

  if (error) {
    return (
      <div className="error-message">
        <h2>Error Loading Courses</h2>
        <p>{error.message}. Please ensure your Flask backend is running on http://localhost:5555.</p>
      </div>
    );
  }

  if (courses.length === 0) {
    return <p>No courses found. Try seeding your database!</p>;
  }

  return (
    <div className="course-list-page">
      <h2>All Courses</h2>
      <div className="courses-grid">
        {courses.map(course => (
          <div key={course.id} className="course-card">
            <h3>{course.title}</h3>
            <p><strong>Difficulty:</strong> {course.difficulty}</p>
            <p><strong>Duration:</strong> {course.duration_hours} hours</p>
            <Link to={`/courses/${course.id}`} className="view-details-button">
              View Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CourseListPage;