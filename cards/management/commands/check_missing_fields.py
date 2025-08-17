from django.core.management.base import BaseCommand
from cards.models import Card
from django.db.models import Q


class Command(BaseCommand):
    help = 'Check for cards with missing MTG-specific fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed breakdown of missing fields per card',
        )

    def handle(self, *args, **options):
        total_cards = Card.objects.count()
        self.stdout.write(f'Total cards in database: {total_cards}')
        
        # Check for various missing fields
        missing_checks = {
            'type_line': Card.objects.filter(Q(type_line='') | Q(type_line__isnull=True)),
            'mana_cost': Card.objects.filter(Q(mana_cost='') | Q(mana_cost__isnull=True)),
            'oracle_text': Card.objects.filter(Q(oracle_text='') | Q(oracle_text__isnull=True)),
            'colors': Card.objects.filter(Q(colors=[]) | Q(colors__isnull=True)),
            'color_identity': Card.objects.filter(Q(color_identity=[]) | Q(color_identity__isnull=True)),
            'keywords': Card.objects.filter(Q(keywords=[]) | Q(keywords__isnull=True)),
            'cmc': Card.objects.filter(Q(cmc=0) | Q(cmc__isnull=True)),
        }
        
        self.stdout.write(f'\n=== Missing Field Analysis ===')
        
        any_missing = False
        for field_name, queryset in missing_checks.items():
            count = queryset.count()
            if count > 0:
                any_missing = True
                percentage = (count / total_cards) * 100
                self.stdout.write(f'{field_name}: {count} cards ({percentage:.1f}%)')
                
                if options['detailed'] and count <= 10:  # Only show details for small numbers
                    for card in queryset[:10]:
                        self.stdout.write(f'  - {card.name} (ID: {card.id})')
                elif options['detailed'] and count > 10:
                    self.stdout.write(f'  (showing first 10 of {count}):')
                    for card in queryset[:10]:
                        self.stdout.write(f'  - {card.name} (ID: {card.id})')
        
        if not any_missing:
            self.stdout.write(self.style.SUCCESS('✓ All cards have complete MTG data!'))
        
        # Cards that need comprehensive updates (missing type_line is good indicator)
        needs_update = Card.objects.filter(
            Q(type_line='') | Q(type_line__isnull=True)
        ).exclude(scryfall_id='')
        
        if needs_update.exists():
            self.stdout.write(f'\n=== Cards Needing Full Update ===')
            self.stdout.write(f'{needs_update.count()} cards need comprehensive MTG data update')
            
            if options['detailed']:
                self.stdout.write('\nSample cards needing update:')
                for card in needs_update[:5]:
                    self.stdout.write(f'  - {card.name} (Scryfall ID: {card.scryfall_id})')
        
        # Cards with no scryfall_id (cannot be updated)
        no_scryfall = Card.objects.filter(Q(scryfall_id='') | Q(scryfall_id__isnull=True))
        if no_scryfall.exists():
            self.stdout.write(f'\n=== Warning: Cards Without Scryfall ID ===')
            self.stdout.write(f'{no_scryfall.count()} cards have no Scryfall ID and cannot be auto-updated')
            if options['detailed']:
                for card in no_scryfall[:5]:
                    self.stdout.write(f'  - {card.name} (ID: {card.id})')
        
        self.stdout.write(f'\n=== Summary ===')
        self.stdout.write(f'Total cards: {total_cards}')
        self.stdout.write(f'Cards needing update: {needs_update.count()}')
        self.stdout.write(f'Cards without Scryfall ID: {no_scryfall.count()}')
        self.stdout.write(f'Complete cards: {total_cards - needs_update.count() - no_scryfall.count()}')