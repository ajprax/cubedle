import React, { useState, useEffect } from 'react';
import { Kernel } from '../types';
import KernelThumbnail from './KernelThumbnail';
import KernelModal from './KernelModal';
import { kernelAPI } from '../api';

interface KernelsBankProps {
  kernels: Kernel[];
  onKernelsChange: (kernels: Kernel[]) => void;
  onRefreshData?: () => void;
}

const KernelsBank: React.FC<KernelsBankProps> = ({ kernels, onKernelsChange, onRefreshData }) => {
  const [selectedKernel, setSelectedKernel] = useState<Kernel | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newKernelName, setNewKernelName] = useState('');

  // Update selectedKernel when kernels prop changes (e.g., after drag & drop)
  useEffect(() => {
    if (selectedKernel) {
      const updatedKernel = kernels.find(k => k.id === selectedKernel.id);
      if (updatedKernel) {
        setSelectedKernel(updatedKernel);
      } else {
        // Kernel was deleted
        setSelectedKernel(null);
      }
    }
  }, [kernels, selectedKernel]);

  const handleKernelClick = (kernel: Kernel) => {
    setSelectedKernel(kernel);
  };

  const handleKernelUpdate = (updatedKernel: Kernel) => {
    const updatedKernels = kernels.map(k => 
      k.id === updatedKernel.id ? updatedKernel : k
    );
    onKernelsChange(updatedKernels);
    setSelectedKernel(updatedKernel);
  };

  const handleKernelDelete = (kernelId: number) => {
    const updatedKernels = kernels.filter(k => k.id !== kernelId);
    onKernelsChange(updatedKernels);
    setSelectedKernel(null);
  };

  const handleCreateKernel = async () => {
    if (!newKernelName.trim()) return;

    try {
      const response = await kernelAPI.create({ name: newKernelName });
      const newKernel = response.data;
      onKernelsChange([...kernels, newKernel]);
      setNewKernelName('');
      setIsCreating(false);
    } catch (error) {
      console.error('Failed to create kernel:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCreateKernel();
    }
    if (e.key === 'Escape') {
      setIsCreating(false);
      setNewKernelName('');
    }
  };

  const handleMoveKernel = async (kernelId: number, direction: 'left' | 'right') => {
    const currentIndex = kernels.findIndex(k => k.id === kernelId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'left' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= kernels.length) return;

    // Create new array with swapped positions
    const newKernels = [...kernels];
    [newKernels[currentIndex], newKernels[newIndex]] = [newKernels[newIndex], newKernels[currentIndex]];

    // Optimistically update UI
    onKernelsChange(newKernels);

    try {
      // Send new order to server
      const kernelIds = newKernels.map(k => k.id);
      await kernelAPI.reorder(kernelIds);
    } catch (error) {
      console.error('Failed to reorder kernels:', error);
      // Revert on error
      onKernelsChange(kernels);
    }
  };

  return (
    <div
      style={{
        height: '67vh', // Top 2/3 of screen
        overflowY: 'auto',
        padding: '16px',
        borderBottom: '2px solid #ccc',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px',
        }}
      >
        <h2 style={{ margin: 0 }}>Kernels ({kernels.length})</h2>
        
        {isCreating ? (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Kernel name..."
              value={newKernelName}
              onChange={(e) => setNewKernelName(e.target.value)}
              onKeyDown={handleKeyPress}
              autoFocus
              style={{
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            <button
              onClick={handleCreateKernel}
              disabled={!newKernelName.trim()}
              style={{
                padding: '8px 16px',
                backgroundColor: '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Create
            </button>
            <button
              onClick={() => {
                setIsCreating(false);
                setNewKernelName('');
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#ccc',
                color: 'black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsCreating(true)}
            style={{
              padding: '8px 16px',
              backgroundColor: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            + New Kernel
          </button>
        )}
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
          gap: '16px',
        }}
      >
        {kernels.map((kernel, index) => (
          <KernelThumbnail
            key={kernel.id}
            kernel={kernel}
            onClick={() => handleKernelClick(kernel)}
            onMoveLeft={() => handleMoveKernel(kernel.id, 'left')}
            onMoveRight={() => handleMoveKernel(kernel.id, 'right')}
            canMoveLeft={index > 0}
            canMoveRight={index < kernels.length - 1}
          />
        ))}
      </div>

      {selectedKernel && (
        <KernelModal
          kernel={selectedKernel}
          onClose={() => setSelectedKernel(null)}
          onUpdate={handleKernelUpdate}
          onDelete={handleKernelDelete}
          onRefreshData={onRefreshData}
        />
      )}
    </div>
  );
};

export default KernelsBank;