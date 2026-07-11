import React from 'react';
import chapters from '../chapters.json';
import ContentRenderer from '../components/ContentRenderer';

const ChapterPage = ({ match }) => {
  const { id } = match.params;
  const chapter = chapters.find(c => c.id === Number(id));
  if (!chapter) {
    return <div>Chapter not found</div>;
  }
  return (
    <div className="chapter-page">
      <header className="chapter-header">
        <h1>Chương {chapter.id}: {chapter.title}</h1>
      </header>
      <div className="chapter-content">
        <ContentRenderer content={chapter.content} />
      </div>
    </div>
  );
};

export default ChapterPage;