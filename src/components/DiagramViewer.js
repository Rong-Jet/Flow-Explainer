import React, { useState } from 'react';
import { Mermaid } from 'mermaid-react';
import './DiagramViewer.css';

const DiagramViewer = ({ svgContent, mermaidCode }) => {
  const [activeTab, setActiveTab] = useState('diagram');
  
  // Function to download the SVG
  const downloadSVG = () => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'diagram.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="diagram-viewer">
      <div className="tabs">
        <button 
          className={`tab-button ${activeTab === 'diagram' ? 'active' : ''}`}
          onClick={() => setActiveTab('diagram')}
        >
          Diagram
        </button>
        <button 
          className={`tab-button ${activeTab === 'code' ? 'active' : ''}`}
          onClick={() => setActiveTab('code')}
        >
          Mermaid Code
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'diagram' && (
          <div className="diagram-container">
            <div 
              className="diagram" 
              dangerouslySetInnerHTML={{ __html: svgContent }} 
            />
            <button 
              className="download-button" 
              onClick={downloadSVG}
            >
              Download SVG
            </button>
          </div>
        )}
        
        {activeTab === 'code' && (
          <div className="code-container">
            <pre className="mermaid-code">{mermaidCode}</pre>
            <button 
              className="copy-button" 
              onClick={() => navigator.clipboard.writeText(mermaidCode)}
            >
              Copy Code
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiagramViewer; 