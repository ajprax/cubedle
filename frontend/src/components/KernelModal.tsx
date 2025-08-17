import React, { useState, useEffect } from 'react';
import { useDroppable } from '@dnd-kit/core';
import { Kernel } from '../types';
import CardComponent from './CardComponent';
import { kernelAPI } from '../api';

interface KernelModalProps {
  kernel: Kernel;
  onClose: () => void;
  onUpdate: (updatedKernel: Kernel) => void;
  onDelete: (kernelId: number) => void;
  onRefreshData?: () => void;
}

const KernelModal: React.FC<KernelModalProps> = ({ kernel, onClose, onUpdate, onDelete, onRefreshData }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [kernelName, setKernelName] = useState(kernel.name);
  const [hovering, setHovering] = useState(false);
  const [fadeTimer, setFadeTimer] = useState<NodeJS.Timeout | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { setNodeRef, isOver } = useDroppable({
    id: `kernel-modal-${kernel.id}`,
    data: { kernel, type: 'kernel-modal' }
  });

  useEffect(() => {
    if (hovering) {
      if (fadeTimer) {
        clearTimeout(fadeTimer);
        setFadeTimer(null);
      }
    } else {
      const timer = setTimeout(() => {
        setHovering(false);
      }, 3000);
      setFadeTimer(timer);
    }

    return () => {
      if (fadeTimer) {
        clearTimeout(fadeTimer);
      }
    };
  }, [hovering, fadeTimer]);

  const handleSaveName = async () => {
    try {
      await kernelAPI.update(kernel.id, { name: kernelName });
      onUpdate({ ...kernel, name: kernelName });
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update kernel name:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveName();
    }
    if (e.key === 'Escape') {
      setKernelName(kernel.name);
      setIsEditing(false);
    }
  };

  const handleNameClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
  };

  const handleDeleteKernel = async () => {
    try {
      await kernelAPI.delete(kernel.id);
      onDelete(kernel.id);
      if (onRefreshData) {
        onRefreshData();
      }
      onClose();
    } catch (error) {
      console.error('Failed to delete kernel:', error);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        ref={setNodeRef}
        style={{
          backgroundColor: isOver ? '#e3f2fd' : 'white',
          borderRadius: '8px',
          padding: '24px',
          maxWidth: '90vw',
          maxHeight: '90vh',
          width: '80vw',
          height: '80vh',
          overflow: 'hidden',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '20px',
            position: 'relative',
          }}
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={() => setHovering(false)}
        >
          {isEditing ? (
            <input
              type="text"
              value={kernelName}
              onChange={(e) => setKernelName(e.target.value)}
              onBlur={handleSaveName}
              onKeyDown={handleKeyPress}
              autoFocus
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                border: '2px solid #2196f3',
                borderRadius: '4px',
                padding: '4px 8px',
                backgroundColor: '#f0f8ff',
              }}
            />
          ) : (
            <h2
              onClick={handleNameClick}
              style={{
                margin: 0,
                fontSize: '24px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {kernel.name} ({kernel.cards.length})
              <span
                style={{
                  fontSize: '16px',
                  opacity: hovering ? 1 : 0,
                  transition: 'opacity 0.3s',
                  color: '#666',
                }}
              >
                ✏️
              </span>
            </h2>
          )}
          
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              style={{
                background: 'none',
                border: '1px solid #f44336',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '14px',
                cursor: 'pointer',
                color: '#f44336',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f44336';
                e.currentTarget.style.color = 'white';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#f44336';
              }}
            >
              Delete
            </button>
            
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#666',
              }}
            >
              ×
            </button>
          </div>
        </div>

        {/* Cards Grid */}
        <div
          style={{
            height: 'calc(100% - 80px)',
            overflowY: 'auto',
            padding: '8px',
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
              gap: '8px',
            }}
          >
            {kernel.cards.map((kernelCard) => (
              <CardComponent
                key={kernelCard.id}
                card={kernelCard.card}
                dragId={`modal-${kernel.id}-card-${kernelCard.card.id}`}
              />
            ))}
          </div>
        </div>

        {/* Delete Confirmation Dialog */}
        {showDeleteConfirm && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 2000,
            }}
            onClick={() => setShowDeleteConfirm(false)}
          >
            <div
              style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '24px',
                maxWidth: '400px',
                textAlign: 'center',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 style={{ margin: '0 0 16px 0', color: '#f44336' }}>
                Delete Kernel
              </h3>
              <p style={{ margin: '0 0 24px 0', color: '#666' }}>
                Are you sure you want to delete "{kernel.name}"?
                {kernel.cards.length > 0 && (
                  <><br />The {kernel.cards.length} card{kernel.cards.length !== 1 ? 's' : ''} in this kernel will be returned to candidates.</>
                )}
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
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
                <button
                  onClick={handleDeleteKernel}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KernelModal;