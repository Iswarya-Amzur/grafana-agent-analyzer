import React, { useState } from 'react';

const ScreenshotUploader = () => {
  const [infraFile, setInfraFile] = useState(null);
  const [systemFile, setSystemFile] = useState(null);
  const [customDate, setCustomDate] = useState(new Date().toISOString().split('T')[0]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (type, event) => {
    const file = event.target.files[0];
    if (file) {
      if (type === 'infra') {
        setInfraFile(file);
      } else {
        setSystemFile(file);
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!infraFile || !systemFile) {
      setUploadStatus('Please select both Infrastructure and System screenshots');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('infra_screenshot', infraFile);
      formData.append('system_screenshot', systemFile);
      formData.append('date', customDate);

      const response = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadStatus('Screenshots uploaded successfully!');
        // Reset form
        setInfraFile(null);
        setSystemFile(null);
        setCustomDate(new Date().toISOString().split('T')[0]);
        // Reset file inputs
        document.getElementById('infra-upload').value = '';
        document.getElementById('system-upload').value = '';
      } else {
        const errorData = await response.json();
        setUploadStatus(`Upload failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const FileUploadCard = ({ title, type, file, icon }) => (
    <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-grafana-orange transition-colors duration-200">
      <div className="p-6">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
            {icon}
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
          <label
            htmlFor={`${type}-upload`}
            className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-grafana-orange hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-grafana-orange transition-colors duration-200"
          >
            Choose File
          </label>
          <input
            id={`${type}-upload`}
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(type, e)}
            className="hidden"
          />
          {file && (
            <div className="mt-3 p-3 bg-gray-50 rounded-md">
              <p className="text-sm text-gray-600 font-medium">Selected file:</p>
              <p className="text-sm text-gray-900 truncate">{file.name}</p>
              <p className="text-xs text-gray-500">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const ServerIcon = () => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
    </svg>
  );

  const ChartIcon = () => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* File Upload Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <FileUploadCard
            title="Infrastructure Screenshot"
            type="infra"
            file={infraFile}
            icon={<ServerIcon />}
          />
          <FileUploadCard
            title="System Screenshot"
            type="system"
            file={systemFile}
            icon={<ChartIcon />}
          />
        </div>

        {/* Date Input */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="flex-1">
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
                Screenshot Date (Optional)
              </label>
              <input
                type="date"
                id="date"
                value={customDate}
                onChange={(e) => setCustomDate(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-grafana-orange focus:border-grafana-orange sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-500">
                Defaults to today's date if not specified
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button and Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col items-center space-y-4">
            <button
              type="submit"
              disabled={isUploading || !infraFile || !systemFile}
              className={`w-full md:w-auto px-8 py-3 text-base font-medium rounded-md transition-all duration-200 ${
                isUploading || !infraFile || !systemFile
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-grafana-blue text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-grafana-blue transform hover:scale-105'
              }`}
            >
              {isUploading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                'Upload Screenshots'
              )}
            </button>

            {uploadStatus && (
              <div className={`text-center p-3 rounded-md w-full ${
                uploadStatus.includes('successfully') 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : uploadStatus.includes('failed') || uploadStatus.includes('Please select')
                  ? 'bg-red-50 text-red-800 border border-red-200'
                  : 'bg-blue-50 text-blue-800 border border-blue-200'
              }`}>
                {uploadStatus}
              </div>
            )}
          </div>
        </div>

        {/* Upload Requirements */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Upload Requirements</h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Both Infrastructure and System screenshots are required</li>
                  <li>Supported formats: PNG, JPG, JPEG, GIF</li>
                  <li>Maximum file size: 10MB per image</li>
                  <li>Date defaults to today if not specified</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ScreenshotUploader;
