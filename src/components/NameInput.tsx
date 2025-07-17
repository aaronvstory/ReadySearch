import React, { useState } from 'react';
import { Plus, X, User } from 'lucide-react';

interface NameInputProps {
  onNamesChange: (names: string[]) => void;
  existingNames: string[];
  disabled: boolean;
}

const NameInput: React.FC<NameInputProps> = ({
  onNamesChange,
  existingNames,
  disabled
}) => {
  const [currentName, setCurrentName] = useState('');

  const handleAddName = () => {
    if (!currentName.trim()) return;
    
    const trimmedName = currentName.trim();
    
    // Check for duplicates
    if (existingNames.includes(trimmedName)) {
      alert('This name is already in the list.');
      return;
    }
    
    // Validate name (basic validation)
    if (trimmedName.length < 2) {
      alert('Name must be at least 2 characters long.');
      return;
    }
    
    // Add the name
    const newNames = [...existingNames, trimmedName];
    onNamesChange(newNames);
    setCurrentName('');
  };

  const handleRemoveName = (index: number) => {
    const newNames = existingNames.filter((_, i) => i !== index);
    onNamesChange(newNames);
  };

  const handleClearAll = () => {
    if (existingNames.length > 0 && 
        window.confirm('Are you sure you want to clear all names?')) {
      onNamesChange([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddName();
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-xl font-semibold mb-4 flex items-center">
        <User className="h-5 w-5 mr-2" />
        Manual Name Entry
      </h3>
      
      {/* Input field */}
      <div className="space-y-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={currentName}
            onChange={(e) => setCurrentName(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter a name (e.g., John Smith)"
            disabled={disabled}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleAddName}
            disabled={!currentName.trim() || disabled}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded transition-colors flex items-center"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
        
        {/* Name list */}
        {existingNames.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">
                {existingNames.length} name{existingNames.length !== 1 ? 's' : ''} added
              </span>
              <button
                onClick={handleClearAll}
                disabled={disabled}
                className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Clear All
              </button>
            </div>
            
            <div className="max-h-40 overflow-y-auto space-y-1">
              {existingNames.map((name, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-gray-700 rounded px-3 py-2 text-sm"
                >
                  <span className="text-white">{name}</span>
                  <button
                    onClick={() => handleRemoveName(index)}
                    disabled={disabled}
                    className="text-red-400 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed ml-2"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {existingNames.length === 0 && (
          <div className="text-center py-4 text-gray-400 text-sm">
            No names added yet. Type a name above and click + to add it.
          </div>
        )}
      </div>
    </div>
  );
};

export default NameInput;