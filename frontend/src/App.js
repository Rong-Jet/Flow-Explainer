import React from 'react';
import './App.css';
import JsonUploader from './components/JsonUploader';
import DiagramViewer from './components/DiagramViewer';

function App() {
  const [diagram, setDiagram] = React.useState(null);
  const [mermaidCode, setMermaidCode] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleDiagramGenerated = (data) => {
    setDiagram(data.diagram_image);
    setMermaidCode(data.mermaid_code);
    setLoading(false);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Flow Explainer</h1>
        <p>Upload a JSON file to generate a diagram</p>
      </header>
      <main>
        <JsonUploader 
          onUploadStart={() => {
            setLoading(true);
            setError('');
          }}
          onDiagramGenerated={handleDiagramGenerated}
          onError={handleError}
        />
        
        {loading && <div className="loading">Generating diagram...</div>}
        {error && <div className="error">{error}</div>}
        
        {diagram && (
          <DiagramViewer 
            svgContent={diagram} 
            mermaidCode={mermaidCode}
          />
        )}
      </main>
    </div>
  );
}

export default App; 