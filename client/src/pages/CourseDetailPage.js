import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchCourseDetails } from '../api';

function CourseDetailPage() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchCourseDetails(id)
      .then(data => {
        setCourse(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching course details:", error);
        setError(error);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <p>Loading course details...</p>;
  }

  if (error) {
    return (
      <div className="error-message">
        <h2>Error Loading Course</h2>
        <p>{error.message}. Please ensure the course ID exists.</p>
        <Link to="/" className="view-details-button">Back to All Courses</Link>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="error-message">
        <h2>Course Not Found</h2>
        <p>The course with ID {id} could not be found.</p>
        <Link to="/" className="view-details-button">Back to All Courses</Link>
      </div>
    );
  }

  return (
    <div className="course-detail-page">
      <Link to="/" className="back-button">← Back to All Courses</Link>
      <h2>{course.title}</h2>
      <div className="course-info">
        <p><strong>Description:</strong> {course.description}</p>
        <p><strong>Difficulty:</strong> {course.difficulty}</p>
        <p><strong>Duration:</strong> {course.duration_hours} hours</p>
        <p><strong>Instructor:</strong> 
          {course.instructor ? course.instructor.username : 'Unknown Instructor'}
        </p>
      </div>

      <div className="course-actions">
        <button className="action-button primary">Enroll in Course</button>
      </div>

      <div className="reviews-list">
        <h3>Reviews ({course.reviews?.length || 0})</h3>
        {course.reviews && course.reviews.length > 0 ? (
          course.reviews.map(review => (
            <div key={review.id} className="review-card">
              <p><strong>Rating:</strong> {review.rating} / 5</p>
              <p><strong>Reviewed by:</strong> 
                {review.user ? review.user.username : 'Anonymous'}
              </p>
              <p>{review.text_content}</p>
            </div>
          ))
        ) : (
          <p>No reviews yet. Be the first to add one!</p>
        )}
      </div>

      <div className="add-review-section">
        <h3>Add Your Review</h3>
        <p>Review form will go here.</p>
      </div>
    </div>
  );
}

export default CourseDetailPage;