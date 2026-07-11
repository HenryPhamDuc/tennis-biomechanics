import React from 'react';
import { Switch, Route, Link, useLocation } from 'wouter';
import HomePage from './pages/HomePage';
import ChapterPage from './pages/ChapterPage';
import './styles/global.css';

function App() {
  const location = useLocation();
  return (
    <>
      <header className="app-header">
        <div className="container">
          <h1>Sinh Cơ Học Tennis</h1>
          <p>Cẩm Nang 2026</p>
        </div>
      </header>
      <main>
        <Switch>
          <Route path="/manual/:id(\\d+)(\\.html)?" component={ChapterPage} />
          <Route path="/" component={HomePage} />
        </Switch>
      </main>
      <footer className="app-footer">
        <div className="container">
          <p>&copy; 2026 Henry Phạm Đức. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}

export default App;