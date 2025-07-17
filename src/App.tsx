import React, { useState, useRef } from 'react';
import { 
  Upload, 
  Play, 
  Download, 
  Settings, 
  FileText, 
  Search, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Clock,
  Users,
  BarChart3,
  Pause,
  RotateCcw
} from 'lucide-react';
import NameInput from './components/NameInput';

interface SearchResult {
  name: string;
  status: 'Match' | 'No Match' | 'Error' | 'Pending';
  timestamp?: string;
  error?: string;
  matches_found?: number;
}

interface AutomationConfig {
  delay: number;
  retries: number;
  headless: boolean;
  timeout: number;
}

function App() {
  const [names, setNames] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [config, setConfig] = useState<AutomationConfig>({
    delay: 2.5,
    retries: 3,
    headless: true,
    timeout: 30
  });
  const [showConfig, setShowConfig] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // API base URL - adjust this based on your Flask server
  const API_BASE_URL = 'http://localhost:5000/api';

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const lines = text.split('\n').filter(line => line.trim());
        const headers = lines[0].toLowerCase();
        
        let nameList: string[] = [];
        if (headers.includes('name')) {
          // CSV with headers
          nameList = lines.slice(1).map(line => {
            const columns = line.split(',');
            return columns[0].trim().replace(/"/g, '');
          }).filter(name => name);
        } else {
          // Simple list
          nameList = lines.map(line => line.trim()).filter(name => name);
        }
        
        setNames(nameList);
        setResults(nameList.map(name => ({ name, status: 'Pending' })));
        setCurrentIndex(0);
      };
      reader.readAsText(file);
    }
  };

  const startAutomation = async () => {
    if (names.length === 0) return;
    
    try {
      setApiError(null);
      setIsRunning(true);
      setCurrentIndex(0);
      
      // Start automation session
      const response = await fetch(`${API_BASE_URL}/start-automation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ names }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSessionId(data.session_id);
      
      // Start polling for updates
      pollSessionStatus(data.session_id);
      
    } catch (error) {
      console.error('Error starting automation:', error);
      setApiError(error instanceof Error ? error.message : 'Failed to start automation');
      setIsRunning(false);
    }
  };

  const pollSessionStatus = async (sessionId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/session/${sessionId}/status`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const sessionData = await response.json();
        
        // Update current index
        setCurrentIndex(sessionData.current_index);
        
        // Update results
        if (sessionData.results && sessionData.results.length > 0) {
          setResults(prev => {
            const newResults = [...prev];
            sessionData.results.forEach((result: any, index: number) => {
              if (newResults[index]) {
                newResults[index] = {
                  name: result.name,
                  status: result.status,
                  timestamp: result.timestamp ? new Date(result.timestamp).toLocaleString() : undefined,
                  error: result.error,
                  matches_found: result.matches_found
                };
              }
            });
            return newResults;
          });
        }
        
        // Check if automation is complete
        if (sessionData.status === 'completed' || sessionData.status === 'error' || sessionData.status === 'stopped') {
          clearInterval(pollInterval);
          setIsRunning(false);
          
          if (sessionData.status === 'error') {
            setApiError(sessionData.error_message || 'Automation failed');
          }
        }
        
      } catch (error) {
        console.error('Error polling session status:', error);
        clearInterval(pollInterval);
        setIsRunning(false);
        setApiError('Lost connection to automation service');
      }
    }, 2000); // Poll every 2 seconds
  };

  const stopAutomation = async () => {
    if (!sessionId) {
      setIsRunning(false);
      return;
    }
    
    try {
      await fetch(`${API_BASE_URL}/session/${sessionId}/stop`, {
        method: 'POST',
      });
      setIsRunning(false);
    } catch (error) {
      console.error('Error stopping automation:', error);
      setIsRunning(false);
    }
  };

  const resetResults = () => {
    setResults(names.map(name => ({ name, status: 'Pending' })));
    setCurrentIndex(0);
  };

  const downloadResults = () => {
    const csvContent = [
      'name,status,timestamp,error',
      ...results.map(r => `"${r.name}","${r.status}","${r.timestamp || ''}","${r.error || ''}"`)
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `readysearch_results_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const addSampleNames = () => {
    const sampleNames = [
      'John Smith',
      'Jane Doe',
      'Robert Johnson',
      'Mary Williams',
      'David Brown',
      'Sarah Davis',
      'Michael Wilson',
      'Lisa Anderson'
    ];
    setNames(sampleNames);
    setResults(sampleNames.map(name => ({ name, status: 'Pending' })));
  };

  const handleNamesChange = (newNames: string[]) => {
    setNames(newNames);
    setResults(newNames.map(name => ({ name, status: 'Pending' })));
    setCurrentIndex(0);
  };

  const getStatusIcon = (status: SearchResult['status']) => {
    switch (status) {
      case 'Match':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'No Match':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      case 'Error':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-400" />;
    }
  };

  const getStatusColor = (status: SearchResult['status']) => {
    switch (status) {
      case 'Match':
        return 'text-green-400';
      case 'No Match':
        return 'text-gray-400';
      case 'Error':
        return 'text-red-400';
      default:
        return 'text-yellow-400';
    }
  };

  const stats = {
    total: results.length,
    matches: results.filter(r => r.status === 'Match').length,
    noMatches: results.filter(r => r.status === 'No Match').length,
    errors: results.filter(r => r.status === 'Error').length,
    pending: results.filter(r => r.status === 'Pending').length
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-center mb-4">
            ReadySearch.com.au Automation
          </h1>
          <p className="text-gray-300 text-center max-w-2xl mx-auto">
            Production-ready automation tool for performing exact name searches on ReadySearch.com.au
          </p>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* File Upload */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <Upload className="h-5 w-5 mr-2" />
                Input Names
              </h3>
              
              <div className="space-y-4">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
                >
                  <FileText className="h-5 w-5 mr-2" />
                  Upload CSV File
                </button>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                
                <button
                  onClick={addSampleNames}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition-colors text-sm"
                >
                  Use Sample Names
                </button>
                
                {names.length > 0 && (
                  <div className="text-sm text-gray-300">
                    <Users className="h-4 w-4 inline mr-1" />
                    {names.length} names loaded
                  </div>
                )}
              </div>
            </div>

            {/* Manual Name Input */}
            <NameInput 
              onNamesChange={handleNamesChange}
              existingNames={names}
              disabled={isRunning}
            />

            {/* Controls */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-semibold mb-4 flex items-center">
                <Play className="h-5 w-5 mr-2" />
                Controls
              </h3>
              
              <div className="space-y-3">
                <button
                  onClick={startAutomation}
                  disabled={names.length === 0 || isRunning}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg transition-colors flex items-center justify-center"
                >
                  {isRunning ? (
                    <>
                      <Clock className="h-5 w-5 mr-2 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5 mr-2" />
                      Start Automation
                    </>
                  )}
                </button>
                
                {isRunning && (
                  <button
                    onClick={stopAutomation}
                    className="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                  >
                    <Pause className="h-5 w-5 mr-2" />
                    Stop
                  </button>
                )}
                
                <button
                  onClick={resetResults}
                  disabled={isRunning}
                  className="w-full bg-gray-600 hover:bg-gray-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                >
                  <RotateCcw className="h-5 w-5 mr-2" />
                  Reset
                </button>
                
                <button
                  onClick={downloadResults}
                  disabled={results.every(r => r.status === 'Pending')}
                  className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                >
                  <Download className="h-5 w-5 mr-2" />
                  Download Results
                </button>
              </div>
            </div>

            {/* Configuration */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <button
                onClick={() => setShowConfig(!showConfig)}
                className="w-full flex items-center justify-between text-xl font-semibold mb-4"
              >
                <div className="flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  Configuration
                </div>
                <span className="text-sm">{showConfig ? '−' : '+'}</span>
              </button>
              
              {showConfig && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Delay Between Searches (seconds)
                    </label>
                    <input
                      type="number"
                      value={config.delay}
                      onChange={(e) => setConfig({...config, delay: parseFloat(e.target.value)})}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      min="1"
                      max="10"
                      step="0.5"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Max Retries
                    </label>
                    <input
                      type="number"
                      value={config.retries}
                      onChange={(e) => setConfig({...config, retries: parseInt(e.target.value)})}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      min="1"
                      max="5"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      value={config.timeout}
                      onChange={(e) => setConfig({...config, timeout: parseInt(e.target.value)})}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
                      min="10"
                      max="60"
                    />
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.headless}
                      onChange={(e) => setConfig({...config, headless: e.target.checked})}
                      className="mr-2"
                    />
                    <label className="text-sm">Headless Mode</label>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-2xl font-bold text-blue-400">{stats.total}</div>
                <div className="text-sm text-gray-300">Total</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-2xl font-bold text-green-400">{stats.matches}</div>
                <div className="text-sm text-gray-300">Matches</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-2xl font-bold text-gray-400">{stats.noMatches}</div>
                <div className="text-sm text-gray-300">No Match</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-2xl font-bold text-red-400">{stats.errors}</div>
                <div className="text-sm text-gray-300">Errors</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
                <div className="text-2xl font-bold text-yellow-400">{stats.pending}</div>
                <div className="text-sm text-gray-300">Pending</div>
              </div>
            </div>

            {/* API Error Display */}
            {apiError && (
              <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                  <span className="text-red-400 font-medium">Connection Error</span>
                </div>
                <p className="text-red-300 text-sm mt-2">{apiError}</p>
                <p className="text-gray-400 text-xs mt-2">
                  Make sure the Python API server is running on localhost:5000
                </p>
              </div>
            )}

            {/* Progress */}
            {isRunning && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Progress</span>
                  <span className="text-sm text-gray-300">
                    {currentIndex + 1} / {names.length}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentIndex + 1) / names.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Results Table */}
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="p-4 border-b border-gray-700">
                <h3 className="text-xl font-semibold flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Search Results
                </h3>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {results.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No names loaded. Upload a CSV file or use sample names to get started.</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-700">
                    {results.map((result, index) => (
                      <div 
                        key={index} 
                        className={`p-4 flex items-center justify-between ${
                          index === currentIndex && isRunning ? 'bg-blue-900/20' : ''
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(result.status)}
                          <span className="font-medium">{result.name}</span>
                        </div>
                        
                        <div className="text-right">
                          <div className={`font-medium ${getStatusColor(result.status)}`}>
                            {result.status}
                          </div>
                          {result.timestamp && (
                            <div className="text-xs text-gray-400">
                              {result.timestamp}
                            </div>
                          )}
                          {result.error && (
                            <div className="text-xs text-red-400">
                              {result.error}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-400 text-sm">
          <p>ReadySearch.com.au Automation Tool - Built with React and Tailwind CSS</p>
          <p className="mt-2">
            This is a demonstration interface. The actual automation runs with Python and Playwright.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;