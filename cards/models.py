from django.db import models
import json
import random
import math
from .glicko2 import Glicko2


class Card(models.Model):
    name = models.CharField(max_length=200, unique=True)
    scryfall_id = models.CharField(max_length=36, unique=True)
    
    # Glicko-2 rating system fields
    rating = models.FloatField(default=1500.0)
    rating_deviation = models.FloatField(default=350.0)
    volatility = models.FloatField(default=0.06)
    
    # Scryfall data for display
    image_uris = models.JSONField(default=dict)  # stores image URLs
    card_faces = models.JSONField(default=list)  # for double-faced cards
    layout = models.CharField(max_length=50, default='normal')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_image_uri(self, face=0):
        """Get image URI for display, handling different card layouts"""
        # For split cards, double-faced cards, etc. - check card_faces first
        if self.card_faces and len(self.card_faces) > face:
            face_image = self.card_faces[face].get('image_uris', {}).get('normal', '')
            if face_image:
                return face_image
        
        # Fallback to main image_uris (for normal cards)
        if self.image_uris and 'normal' in self.image_uris:
            return self.image_uris.get('normal', '')
        
        # If no normal image, try other sizes as fallback
        if self.image_uris:
            for size in ['large', 'border_crop', 'art_crop', 'png', 'small']:
                if size in self.image_uris:
                    return self.image_uris[size]
        
        return ''
    
    def has_multiple_faces(self):
        """Check if card has multiple faces (transform, modal_dfc, etc.)"""
        return len(self.card_faces) > 1
    
    def has_flippable_faces(self):
        """Check if card has faces that can be flipped between (not split/adventure cards)"""
        if len(self.card_faces) <= 1:
            return False
        
        # Only these layouts have truly flippable faces where you see one side at a time
        flippable_layouts = [
            'transform',        # Double-faced transforming cards
            'modal_dfc',        # Modal double-faced cards
            'reversible_card',  # Reversible cards
        ]
        
        return self.layout in flippable_layouts
    
    def needs_rotation(self):
        """Determine if card needs rotation based on layout"""
        rotation_layouts = ['battle', 'flip']
        return self.layout in rotation_layouts
    
    def get_rotation_angle(self):
        """Get rotation angle for card display"""
        if self.layout == 'battle':
            return 90
        elif self.layout == 'flip':
            return 180
        return 0
    
    @classmethod
    def update_ratings_after_vote(cls, winner_card, loser_card):
        """Update ratings for two cards after a head-to-head vote"""
        new_winner_rating, new_winner_rd, new_winner_vol, new_loser_rating, new_loser_rd, new_loser_vol = Glicko2.update_ratings(
            winner_card.rating, winner_card.rating_deviation, winner_card.volatility,
            loser_card.rating, loser_card.rating_deviation, loser_card.volatility,
            1.0  # Winner gets outcome = 1.0
        )
        
        # Update winner
        winner_card.rating = new_winner_rating
        winner_card.rating_deviation = new_winner_rd
        winner_card.volatility = new_winner_vol
        winner_card.save()
        
        # Update loser
        loser_card.rating = new_loser_rating
        loser_card.rating_deviation = new_loser_rd
        loser_card.volatility = new_loser_vol
        loser_card.save()
    
    @classmethod
    def get_random_pair_for_voting(cls):
        """Get a random pair of cards for head-to-head voting, with preference for high uncertainty cards"""
        all_cards = list(cls.objects.all())
        
        if len(all_cards) < 2:
            return None, None
        
        # Create weights based on rating deviation (higher RD = higher weight)
        # Add a base weight so all cards have some chance of being selected
        base_weight = 1.0
        weights = [base_weight + card.rating_deviation / 100.0 for card in all_cards]
        
        # Select first card using weighted random
        card1 = random.choices(all_cards, weights=weights)[0]
        
        # Remove selected card and its weight for second selection
        remaining_cards = [card for card in all_cards if card.id != card1.id]
        remaining_weights = [weights[i] for i, card in enumerate(all_cards) if card.id != card1.id]
        
        # Select second card
        card2 = random.choices(remaining_cards, weights=remaining_weights)[0]
        
        return card1, card2
