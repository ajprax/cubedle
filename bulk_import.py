#!/usr/bin/env python
"""
Bulk import script for adding cards from a text file to the database.
Each line should contain either a card name or a Scryfall URL.
Cards already in the database will not be modified.

Usage:
    python bulk_import.py <filename>

Example:
    python bulk_import.py cards_to_add.txt
"""

import os
import sys
import django
import requests
import time
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cube_voting.settings')
django.setup()

from cards.models import Card


def search_card_by_name(card_name):
    """Search for a card by name using Scryfall API"""
    try:
        # Try exact match first
        response = requests.get('https://api.scryfall.com/cards/named', 
                              params={'exact': card_name})
        if response.status_code == 200:
            return response.json()
        
        # Try fuzzy search if exact match fails
        response = requests.get('https://api.scryfall.com/cards/named', 
                              params={'fuzzy': card_name})
        if response.status_code == 200:
            return response.json()
        
        return None
    except Exception as e:
        print(f"Error searching for '{card_name}': {e}")
        return None


def search_card_by_url(url):
    """Search for a card by Scryfall URL"""
    try:
        if '/card/' in url:
            parts = url.split('/card/')
            if len(parts) > 1:
                # Get everything after /card/ and remove any query parameters
                full_path = parts[1].split('?')[0]
                # Split by '/' and take only set and collector number (first 2 parts)
                path_parts = full_path.split('/')
                if len(path_parts) >= 2:
                    card_path = f"{path_parts[0]}/{path_parts[1]}"
                    response = requests.get(f'https://api.scryfall.com/cards/{card_path}')
                    if response.status_code == 200:
                        return response.json()
        return None
    except Exception as e:
        print(f"Error fetching card from URL '{url}': {e}")
        return None


def add_card_to_database(card_data):
    """Add a card to the database if it doesn't already exist"""
    try:
        # Check if card already exists
        existing_card = Card.objects.filter(scryfall_id=card_data['id']).first()
        if existing_card:
            print(f"  ↳ Card '{card_data['name']}' already exists in database, skipping")
            return False
        
        # Create new card
        card = Card.objects.create(
            name=card_data['name'],
            scryfall_id=card_data['id'],
            image_uris=card_data.get('image_uris', {}),
            card_faces=card_data.get('card_faces', []),
            layout=card_data.get('layout', 'normal')
        )
        print(f"  ✓ Added '{card_data['name']}' to database")
        return True
    except Exception as e:
        print(f"  ✗ Error adding '{card_data['name']}' to database: {e}")
        return False


def process_file(filename):
    """Process a text file containing card names or URLs"""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
    
    print(f"Processing file: {filename}")
    print("-" * 50)
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    total_lines = len(lines)
    print(f"Found {total_lines} entries to process\n")
    
    for i, line in enumerate(lines, 1):
        print(f"[{i}/{total_lines}] Processing: {line}")
        
        # Determine if it's a URL or card name
        if 'scryfall.com' in line:
            card_data = search_card_by_url(line)
        else:
            card_data = search_card_by_name(line)
        
        if card_data:
            success = add_card_to_database(card_data)
            if success:
                added_count += 1
            else:
                skipped_count += 1
        else:
            print(f"  ✗ Could not find card: {line}")
            error_count += 1
        
        # Rate limiting - be nice to Scryfall's API
        time.sleep(0.1)
        
        # Add a longer pause every 10 requests
        if i % 10 == 0:
            print("  Pausing briefly to respect rate limits...")
            time.sleep(1)
    
    print("\n" + "=" * 50)
    print("BULK IMPORT COMPLETE")
    print("=" * 50)
    print(f"Total processed: {total_lines}")
    print(f"Successfully added: {added_count}")
    print(f"Already existed (skipped): {skipped_count}")
    print(f"Errors/not found: {error_count}")
    
    if error_count > 0:
        print(f"\n{error_count} cards could not be processed. Check the output above for details.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python bulk_import.py <filename>")
        print("\nExample:")
        print("  python bulk_import.py cards_to_add.txt")
        print("\nFile format:")
        print("  Each line should contain either a card name or Scryfall URL")
        print("  Example content:")
        print("    Lightning Bolt")
        print("    https://scryfall.com/card/m11/146/lightning-bolt")
        print("    Black Lotus")
        sys.exit(1)
    
    filename = sys.argv[1]
    process_file(filename)


if __name__ == '__main__':
    main()