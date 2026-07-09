import React from 'react';
import { Link } from 'wouter';
import chapters from '../chapters.json';

const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Chương Tennis Hiện Đại 2026</h1>
      <p>     12 chương của cẩm nang tennis sinh cơ học hiện đại.</p>
      <div className="chapters-grid">
        {chapters.map(chapter => (
          <Link key={chapter.id} to={`/manual/${chapter.id}.html`} className="chapter-card">
            <h2>Chương {chapter.id}</h2>
            <h3>{chapter.title}</h3>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default HomePage;