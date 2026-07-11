import React from 'react';

const ContentRenderer = ({ content }) => {
  if (!content) return null;

  // Split by double newline to get blocks
  const blocks = content.split('\n\n').map(block => block.trim()).filter(block => block.length > 0);

  return (
    <div className="content">
      {blocks.map((block, index) => {
        // Check for heading levels
        if (block.startsWith('## ')) {
          const text = block.slice(3);
          return <h2 key={`h2-${index}`}>{text}</h2>;
        }
        if (block.startsWith('### ')) {
          const text = block.slice(4);
          return <h3 key={`h3-${index}`}>{text}</h3>;
        }
        // Check for formula block
        if (block === '[FORMULA]') {
          return <div key={`formula-${index}`} className="formula">
            [FORMULA]
          </div>;
        }
        // Check for tip block
        if (block.startsWith('[TIP] ')) {
          const text = block.slice(6);
          return <div key={`tip-${index}`} className="tip">
            <strong>Tip:</strong> {text}
          </div>;
        }
        // Default to paragraph
        return <p key={`p-${index}`}>{block}</p>;
      })}
    </div>
  );
};

export default ContentRenderer;