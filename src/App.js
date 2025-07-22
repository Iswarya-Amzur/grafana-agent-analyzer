import React from 'react';
import ScreenshotUploader from './components/ScreenshotUploader';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Grafana Screenshot Uploader
          </h1>
          <p className="text-gray-600">
            Upload your Infrastructure and System monitoring screenshots
          </p>
        </header>
        <ScreenshotUploader />
      </div>
    </div>
  );
}

export default App;
