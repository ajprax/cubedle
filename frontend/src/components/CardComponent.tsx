import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { Card } from '../types';

interface CardComponentProps {
  card: Card;
  size?: 'full' | 'quarter';
  dragId?: string;
}

const CardComponent: React.FC<CardComponentProps> = ({ 
  card, 
  size = 'full',
  dragId
}) => {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: dragId || `card-${card.id}`,
    data: { card, type: 'card' }
  });

  const getImageUrl = () => {
    // First try image_filename (for compatibility with kernels app data)
    if (card.image_filename) {
      return `http://localhost:8002/media/images/${card.image_filename}`;
    }
    
    // Then try image_uris from target app
    if (card.image_uris && card.image_uris.normal) {
      return card.image_uris.normal;
    }
    
    // Try card_faces for double-faced cards
    if (card.card_faces && card.card_faces.length > 0 && card.card_faces[0].image_uris) {
      return card.card_faces[0].image_uris.normal || card.card_faces[0].image_uris.large;
    }
    
    return '/api/placeholder/488/680';
  };

  const getCardHeight = () => {
    if (size === 'quarter') {
      return '30vh';
    }
    return '30vh'; // Roughly 30% of screen height as specified
  };

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className={`card-component ${isDragging ? 'dragging' : ''}`}
      style={{
        height: getCardHeight(),
        aspectRatio: '5/7', // Standard MTG card ratio
        opacity: isDragging ? 0.5 : 1,
        cursor: 'grab',
        position: 'relative',
        borderRadius: '8px',
        overflow: 'hidden',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'inline-block',
      }}
    >
      <img
        src={getImageUrl()}
        alt={card.name}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          borderRadius: '8px',
        }}
        onError={(e) => {
          // Fallback to a placeholder if image fails to load
          e.currentTarget.src = '/api/placeholder/488/680';
        }}
      />
      
      {/* Hidden searchable text behind the image - only for full-size cards (candidates) */}
      {size === 'full' && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            pointerEvents: 'none',
            fontSize: '1px',
            overflow: 'hidden',
            zIndex: -1,
          }}
        >
          {card.name} {card.oracle_text} {card.type_line}
        </div>
      )}
    </div>
  );
};

export default CardComponent;