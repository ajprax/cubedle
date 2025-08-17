from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Card, Kernel, KernelCard, CandidateCard
from .serializers import CardSerializer, KernelSerializer, CandidateCardSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer


class KernelViewSet(viewsets.ModelViewSet):
    queryset = Kernel.objects.all()
    serializer_class = KernelSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete method to return cards to candidates before deleting kernel"""
        kernel = self.get_object()
        
        # Get all cards in this kernel
        kernel_cards = KernelCard.objects.filter(kernel=kernel)
        
        # Return each card to candidates
        for kernel_card in kernel_cards:
            CandidateCard.objects.get_or_create(card=kernel_card.card)
        
        # Delete the kernel (this will cascade delete KernelCard instances)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def add_card(self, request, pk=None):
        kernel = self.get_object()
        card_id = request.data.get('card_id')
        
        if not card_id:
            return Response({'error': 'card_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        card = get_object_or_404(Card, id=card_id)
        
        # Remove from candidates if it exists
        CandidateCard.objects.filter(card=card).delete()
        
        # Remove from any other kernel
        KernelCard.objects.filter(card=card).delete()
        
        # Add to this kernel
        kernel_card, created = KernelCard.objects.get_or_create(
            kernel=kernel,
            card=card
        )
        
        return Response({'success': True, 'created': created})
    
    @action(detail=True, methods=['post'])
    def remove_card(self, request, pk=None):
        kernel = self.get_object()
        card_id = request.data.get('card_id')
        
        if not card_id:
            return Response({'error': 'card_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        card = get_object_or_404(Card, id=card_id)
        
        # Remove from kernel
        KernelCard.objects.filter(kernel=kernel, card=card).delete()
        
        # Add back to candidates
        CandidateCard.objects.get_or_create(card=card)
        
        return Response({'success': True})
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder kernels by providing a list of kernel IDs in the desired order"""
        kernel_ids = request.data.get('kernel_ids', [])
        
        if not kernel_ids:
            return Response({'error': 'kernel_ids list is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the order field for each kernel
        for index, kernel_id in enumerate(kernel_ids):
            try:
                kernel = Kernel.objects.get(id=kernel_id)
                kernel.order = index
                kernel.save()
            except Kernel.DoesNotExist:
                return Response({'error': f'Kernel {kernel_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'success': True})


class CandidateCardViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateCardSerializer
    
    def get_queryset(self):
        # Only show cards that are not already in kernels
        # Sort by number of colors, then color identity, then CMC
        return CandidateCard.objects.select_related('card').filter(
            card__kernelcard__isnull=True
        ).order_by(
            'card__num_colors',
            'card__color_sort_key', 
            'card__cmc',
            'card__name'
        )
    
    @action(detail=False, methods=['post'])
    def move_to_kernel(self, request):
        card_id = request.data.get('card_id')
        kernel_id = request.data.get('kernel_id')
        
        if not card_id or not kernel_id:
            return Response(
                {'error': 'card_id and kernel_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        card = get_object_or_404(Card, id=card_id)
        kernel = get_object_or_404(Kernel, id=kernel_id)
        
        # Remove from candidates
        CandidateCard.objects.filter(card=card).delete()
        
        # Remove from any other kernel
        KernelCard.objects.filter(card=card).delete()
        
        # Add to specified kernel
        KernelCard.objects.create(kernel=kernel, card=card)
        
        return Response({'success': True})