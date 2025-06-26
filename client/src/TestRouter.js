import React from 'react';
import { useNavigate } from 'react-router-dom';

function TestRouter() {
  const navigate = useNavigate();
  
  return (
    <div>
      <h1>Router Test</h1>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
}

export default TestRouter;