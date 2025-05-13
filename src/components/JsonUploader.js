import React, { useState } from 'react';
import axios from 'axios';
import './JsonUploader.css';

const JsonUploader = ({ onUploadStart, onDiagramGenerated, onError }) => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/json') {
      setFile(selectedFile);
    } else {
      setFile(null);
      alert('Please select a valid JSON file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      onError('Please select a JSON file first');
      return;
    }

    onUploadStart();

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Send to Django backend
      const response = await axios.post(
        'http://localhost:8000/api/process-json/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.data.error) {
        onError(response.data.error);
      } else {
        onDiagramGenerated(response.data);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      onError(error.response?.data?.error || 'Error processing the file. Please try again.');
    }
  };

  return (
    <div className="json-uploader">
      <form onSubmit={handleSubmit}>
        <div className="file-input-container">
          <input
            type="file"
            id="json-file"
            accept=".json"
            onChange={handleFileChange}
          />
          <label htmlFor="json-file" className="file-label">
            {file ? file.name : 'Choose JSON file'}
          </label>
        </div>
        <button 
          type="submit" 
          className="upload-button"
          disabled={!file}
        >
          Generate Diagram
        </button>
      </form>
    </div>
  );
};

export default JsonUploader; 