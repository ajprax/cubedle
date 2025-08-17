from rest_framework import serializers
from .models import Card, Kernel, KernelCard, CandidateCard


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class KernelCardSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    
    class Meta:
        model = KernelCard
        fields = ['id', 'card', 'added_at']


class KernelSerializer(serializers.ModelSerializer):
    cards = KernelCardSerializer(many=True, read_only=True)
    card_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Kernel
        fields = ['id', 'name', 'order', 'cards', 'card_count', 'created_at', 'updated_at']
    
    def get_card_count(self, obj):
        return obj.cards.count()


class CandidateCardSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    
    class Meta:
        model = CandidateCard
        fields = ['id', 'card']