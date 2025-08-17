from django.core.management.base import BaseCommand
from cards.models import Card, CandidateCard


class Command(BaseCommand):
    help = 'Populate candidate cards from existing cards that are not in kernels'

    def handle(self, *args, **options):
        # Get all cards that are not in kernels
        cards_not_in_kernels = Card.objects.filter(kernelcard__isnull=True)
        
        created_count = 0
        for card in cards_not_in_kernels:
            candidate, created = CandidateCard.objects.get_or_create(card=card)
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} candidate cards from {cards_not_in_kernels.count()} available cards'
            )
        )