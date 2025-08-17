import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { Kernel } from '../types';
import CardComponent from './CardComponent';

interface KernelThumbnailProps {
  kernel: Kernel;
  onClick: () => void;
  onMoveLeft?: () => void;
  onMoveRight?: () => void;
  canMoveLeft: boolean;
  canMoveRight: boolean;
}

const KernelThumbnail: React.FC<KernelThumbnailProps> = ({ 
  kernel, 
  onClick, 
  onMoveLeft, 
  onMoveRight, 
  canMoveLeft, 
  canMoveRight 
}) => {
  const { setNodeRef: setDroppableRef, isOver } = useDroppable({
    id: `kernel-${kernel.id}`,
    data: { kernel, type: 'kernel' }
  });

  // Get up to 4 cards for display
  const displayCards = kernel.cards.slice(0, 4);

  return (
    <div
      ref={setDroppableRef}
      className={`kernel-thumbnail ${isOver ? 'drop-over' : ''}`}
      onClick={onClick}
      style={{
        border: '2px solid #ccc',
        borderRadius: '8px',
        padding: '12px',
        margin: '8px',
        minHeight: '200px',
        backgroundColor: isOver ? '#e3f2fd' : '#f5f5f5',
        cursor: 'pointer',
        position: 'relative',
      }}
    >
      {/* Reorder buttons */}
      <div
        style={{
          position: 'absolute',
          top: '8px',
          right: '8px',
          display: 'flex',
          gap: '4px',
          zIndex: 10,
        }}
      >
        {canMoveLeft && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMoveLeft?.();
            }}
            style={{
              width: '20px',
              height: '20px',
              backgroundColor: 'rgba(0,0,0,0.1)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Move left"
          >
            ←
          </button>
        )}
        {canMoveRight && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMoveRight?.();
            }}
            style={{
              width: '20px',
              height: '20px',
              backgroundColor: 'rgba(0,0,0,0.1)',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Move right"
          >
            →
          </button>
        )}
      </div>

      <h3 style={{ margin: '0 0 12px 0', textAlign: 'center' }}>
        {kernel.name} ({kernel.card_count})
      </h3>
      
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '4px',
          height: '160px',
        }}
      >
        {displayCards.map((kernelCard, index) => (
          <div key={kernelCard.id} style={{ overflow: 'hidden' }}>
            <CardComponent
              card={kernelCard.card}
              size="quarter"
              dragId={`kernel-${kernel.id}-card-${kernelCard.card.id}`}
            />
          </div>
        ))}
        
        {/* Fill empty slots */}
        {Array.from({ length: 4 - displayCards.length }).map((_, index) => (
          <div
            key={`empty-${index}`}
            style={{
              backgroundColor: '#ddd',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#666',
              fontSize: '12px',
            }}
          >
            Empty
          </div>
        ))}
      </div>
    </div>
  );
};

export default KernelThumbnail;