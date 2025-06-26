const API_BASE = 'http://localhost:5555';

export const fetchCourses = () => {
  return fetch(`${API_BASE}/courses`)
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || `HTTP error! Status: ${response.status}`);
        });
      }
      return response.json();
    });
};

export const fetchCourseDetails = (id) => {
  return fetch(`${API_BASE}/courses/${id}`)
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || `HTTP error! Status: ${response.status}`);
        });
      }
      return response.json();
    });
};