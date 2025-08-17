import React, { useState, useEffect } from 'react';
import {
  DndContext,
  DragOverlay,
  useSensor,
  useSensors,
  PointerSensor,
  KeyboardSensor,
  DragStartEvent,
  DragEndEvent,
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import { Kernel, CandidateCard, Card } from './types';
import { kernelAPI, candidateAPI } from './api';
import KernelsBank from './components/KernelsBank';
import CandidateBank from './components/CandidateBank';
import CardComponent from './components/CardComponent';
import './App.css';

function App() {
  const [kernels, setKernels] = useState<Kernel[]>([]);
  const [candidates, setCandidates] = useState<CandidateCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCard, setActiveCard] = useState<Card | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [kernelsResponse, candidatesResponse] = await Promise.all([
        kernelAPI.getAll(),
        candidateAPI.getAll(),
      ]);
      
      setKernels(kernelsResponse.data);
      setCandidates(candidatesResponse.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const cardData = active.data.current;
    
    if (cardData?.card) {
      setActiveCard(cardData.card);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCard(null);

    if (!over) return;

    const activeData = active.data.current;
    const overData = over.data.current;

    // Handle card movement
    if (!activeData?.card) return;

    const card = activeData.card;
    const overType = overData?.type;

    try {
      if (overType === 'kernel' || overType === 'kernel-modal') {
        const targetKernel = overData?.kernel;
        
        if (!targetKernel) return;
        
        // Move card to kernel
        await candidateAPI.moveToKernel(card.id, targetKernel.id);
        
        // Refresh data
        await loadData();
      } else if (overType === 'candidate-bank') {
        // If card is being moved from a kernel back to candidates
        const sourceKernelMatch = kernels.find(k => 
          k.cards.some(kc => kc.card.id === card.id)
        );
        
        if (sourceKernelMatch) {
          await kernelAPI.removeCard(sourceKernelMatch.id, card.id);
          await loadData();
        }
      }
    } catch (error) {
      console.error('Failed to move card:', error);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading MTG Card Categorizer...
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div style={{ height: '100vh', overflow: 'hidden' }}>
        <KernelsBank 
          kernels={kernels} 
          onKernelsChange={setKernels}
          onRefreshData={loadData}
        />
        <CandidateBank candidates={candidates} />
      </div>
      
      <DragOverlay>
        {activeCard ? (
          <CardComponent card={activeCard} />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}

export default App;
