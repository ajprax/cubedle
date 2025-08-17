import React, { useEffect, useRef } from 'react';
import { useDroppable } from '@dnd-kit/core';
import { CandidateCard } from '../types';
import CardComponent from './CardComponent';

interface CandidateBankProps {
  candidates: CandidateCard[];
}

const CandidateBank: React.FC<CandidateBankProps> = ({ candidates }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  const { setNodeRef, isOver } = useDroppable({
    id: 'candidate-bank',
    data: { type: 'candidate-bank' }
  });

  // Handle arrow key scrolling
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!scrollContainerRef.current) return;
      
      const container = scrollContainerRef.current;
      const cardWidth = 180; // Approximate card width including margins
      
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        container.scrollLeft -= cardWidth;
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        container.scrollLeft += cardWidth;
      }
    };

    // Add event listener to window for global key handling
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div
      ref={setNodeRef}
      style={{
        height: '33vh', // Bottom 1/3 of screen
        backgroundColor: isOver ? '#e8f5e8' : '#f9f9f9',
        borderTop: '2px solid #ccc',
        padding: '16px',
        overflow: 'hidden',
      }}
    >
      <h2 style={{ margin: '0 0 16px 0' }}>
        Candidates ({candidates.length})
      </h2>
      
      <div
        ref={scrollContainerRef}
        style={{
          height: 'calc(100% - 60px)',
          overflowX: 'auto',
          overflowY: 'hidden',
          display: 'flex',
          gap: '8px',
          padding: '8px 0',
          // Custom scrollbar styling is handled by CSS
        }}
      >
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            style={{
              flexShrink: 0,
              width: '160px',
            }}
          >
            <CardComponent
              card={candidate.card}
              dragId={`candidate-${candidate.card.id}`}
            />
          </div>
        ))}
      </div>
      
      <div
        style={{
          marginTop: '8px',
          fontSize: '12px',
          color: '#666',
          textAlign: 'center',
        }}
      >
        Use arrow keys to scroll • Drag cards to kernels
      </div>
    </div>
  );
};

export default CandidateBank;