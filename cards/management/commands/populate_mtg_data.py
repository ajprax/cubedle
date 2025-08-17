from django.core.management.base import BaseCommand
from django.db import transaction
from cards.models import Card
import requests
import time
import json
import os


class Command(BaseCommand):
    help = 'Populate MTG-specific fields for existing cards using Scryfall API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of cards to process (for testing)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of cards to process before committing to database',
        )
        parser.add_argument(
            '--start-from',
            type=int,
            default=0,
            help='Skip the first N cards (for resuming interrupted runs)',
        )
        parser.add_argument(
            '--rate-limit',
            type=float,
            default=0.1,
            help='Seconds to wait between API requests (default: 0.1)',
        )

    def handle(self, *args, **options):
        # Get cards that need MTG data (those missing type_line)
        base_queryset = Card.objects.filter(
            type_line__in=['', None]
        ).exclude(scryfall_id='').order_by('id')
        
        # Apply start_from offset
        if options['start_from'] > 0:
            base_queryset = base_queryset[options['start_from']:]
            self.stdout.write(f'Starting from card #{options["start_from"]}')
        
        # Apply limit
        if options['limit']:
            cards_to_update = base_queryset[:options['limit']]
        else:
            cards_to_update = base_queryset
        
        total_cards = len(cards_to_update)
        self.stdout.write(f'Found {total_cards} cards that need MTG data')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
        
        updated_count = 0
        error_count = 0
        batch_count = 0
        cards_in_batch = []
        
        # Detect if running on Heroku
        is_heroku = 'DYNO' in os.environ
        if is_heroku:
            self.stdout.write('Detected Heroku environment - using batch processing')
        
        for i, card in enumerate(cards_to_update, 1):
            # Less verbose output for large runs
            if total_cards > 50 and i % 10 == 0:
                self.stdout.write(f'Processing batch {i//10}: cards {i-9}-{min(i, total_cards)}')
            elif total_cards <= 50:
                self.stdout.write(f'Processing {i}/{total_cards}: {card.name}')
            
            try:
                # Fetch card data from Scryfall
                response = requests.get(
                    f'https://api.scryfall.com/cards/{card.scryfall_id}',
                    timeout=15,
                    headers={'User-Agent': 'MTG-Cube-App/1.0'}
                )
                
                if response.status_code == 200:
                    card_data = response.json()
                    
                    if not options['dry_run']:
                        # Update MTG-specific fields
                        card.mana_cost = card_data.get('mana_cost', '')
                        card.cmc = card_data.get('cmc', 0)
                        card.type_line = card_data.get('type_line', '')
                        card.oracle_text = card_data.get('oracle_text', '')
                        card.power = card_data.get('power')
                        card.toughness = card_data.get('toughness')
                        card.colors = card_data.get('colors', [])
                        card.color_identity = card_data.get('color_identity', [])
                        card.keywords = card_data.get('keywords', [])
                        
                        # Add to batch for processing
                        cards_in_batch.append(card)
                    
                    updated_count += 1
                    
                    if total_cards <= 50:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {card_data.get("type_line", "Unknown")} (CMC: {card_data.get("cmc", 0)})')
                        )
                
                elif response.status_code == 404:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Card not found on Scryfall: {card.name}')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ API error {response.status_code} for {card.name}')
                    )
                
                # Process batch when it reaches batch_size
                if len(cards_in_batch) >= options['batch_size'] and not options['dry_run']:
                    with transaction.atomic():
                        for batch_card in cards_in_batch:
                            batch_card.save()  # This will calculate num_colors and color_sort_key
                    batch_count += len(cards_in_batch)
                    self.stdout.write(f'Saved batch of {len(cards_in_batch)} cards (total saved: {batch_count})')
                    cards_in_batch = []
                
                # Rate limiting - be more conservative for Heroku
                rate_limit = options['rate_limit']
                if is_heroku:
                    rate_limit = max(rate_limit, 0.15)  # Minimum 150ms on Heroku
                time.sleep(rate_limit)
                
            except requests.RequestException as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Network error for {card.name}: {str(e)}')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Unexpected error for {card.name}: {str(e)}')
                )
        
        # Save any remaining cards in the final batch
        if cards_in_batch and not options['dry_run']:
            with transaction.atomic():
                for batch_card in cards_in_batch:
                    batch_card.save()
            batch_count += len(cards_in_batch)
            self.stdout.write(f'Saved final batch of {len(cards_in_batch)} cards')
        
        self.stdout.write(f'\n=== Summary ===')
        self.stdout.write(f'Total processed: {total_cards}')
        self.stdout.write(f'Successfully updated: {updated_count}')
        self.stdout.write(f'Errors: {error_count}')
        self.stdout.write(f'Success rate: {(updated_count/(updated_count+error_count)*100):.1f}%' if (updated_count+error_count) > 0 else 'N/A')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS(f'MTG data population complete! Updated {batch_count} cards in database.'))