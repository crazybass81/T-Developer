import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import pages
import ProjectCreationPage from './pages/ProjectCreationPage';
import TaskCreationPage from './pages/TaskCreationPage';
import TaskMonitoringPage from './pages/TaskMonitoringPage';
import TaskReviewPage from './pages/TaskReviewPage';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>T-Developer</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<ProjectCreationPage />} />
            <Route path="/tasks/new" element={<TaskCreationPage />} />
            <Route path="/tasks/:taskId/monitor" element={<TaskMonitoringPage />} />
            <Route path="/tasks/:taskId/review" element={<TaskReviewPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;