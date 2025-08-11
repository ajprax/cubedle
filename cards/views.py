from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json
from .models import Card


def landing_page(request):
    """Landing page with navigation to other sections"""
    total_cards = Card.objects.count()
    context = {
        'total_cards': total_cards
    }
    return render(request, 'cards/landing.html', context)


def head_to_head(request):
    """Head-to-head voting page"""
    card1, card2 = Card.get_random_pair_for_voting()
    
    if not card1 or not card2:
        # Not enough cards for voting
        context = {
            'error': 'Need at least 2 cards in the database to start voting.'
        }
        return render(request, 'cards/head_to_head.html', context)
    
    context = {
        'card1': card1,
        'card2': card2
    }
    return render(request, 'cards/head_to_head.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def vote(request):
    """Process a vote and return new pair of cards"""
    try:
        data = json.loads(request.body)
        winner_id = data.get('winner_id')
        loser_id = data.get('loser_id')
        
        if not winner_id or not loser_id:
            return JsonResponse({'error': 'Missing winner_id or loser_id'}, status=400)
        
        winner_card = get_object_or_404(Card, id=winner_id)
        loser_card = get_object_or_404(Card, id=loser_id)
        
        # Update ratings
        Card.update_ratings_after_vote(winner_card, loser_card)
        
        # Get new pair for next vote
        card1, card2 = Card.get_random_pair_for_voting()
        
        if card1 and card2:
            response_data = {
                'card1': {
                    'id': card1.id,
                    'name': card1.name,
                    'image_uri': card1.get_image_uri(0),
                    'image_uri_back': card1.get_image_uri(1) if card1.has_multiple_faces() else None,
                    'has_multiple_faces': card1.has_multiple_faces(),
                    'has_flippable_faces': card1.has_flippable_faces(),
                    'rotation_angle': card1.get_rotation_angle()
                },
                'card2': {
                    'id': card2.id,
                    'name': card2.name,
                    'image_uri': card2.get_image_uri(0),
                    'image_uri_back': card2.get_image_uri(1) if card2.has_multiple_faces() else None,
                    'has_multiple_faces': card2.has_multiple_faces(),
                    'has_flippable_faces': card2.has_flippable_faces(),
                    'rotation_angle': card2.get_rotation_angle()
                }
            }
        else:
            response_data = {'error': 'Not enough cards for voting'}
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def suggest_card(request):
    """Card suggestion page"""
    return render(request, 'cards/suggest.html')


@csrf_exempt
@require_http_methods(["POST"])
def search_card(request):
    """Search for a card via Scryfall API"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)
        
        # Check if it's a Scryfall URL
        if 'scryfall.com' in query:
            # Extract card path from URL
            if '/card/' in query:
                parts = query.split('/card/')
                if len(parts) > 1:
                    # Get everything after /card/ and remove any query parameters
                    full_path = parts[1].split('?')[0]
                    # Split by '/' and take only set and collector number (first 2 parts)
                    path_parts = full_path.split('/')
                    if len(path_parts) >= 2:
                        card_path = f"{path_parts[0]}/{path_parts[1]}"
                        response = requests.get(f'https://api.scryfall.com/cards/{card_path}')
                    else:
                        return JsonResponse({'error': 'Invalid Scryfall URL format'}, status=400)
                else:
                    return JsonResponse({'error': 'Invalid Scryfall URL'}, status=400)
            else:
                return JsonResponse({'error': 'Invalid Scryfall URL format'}, status=400)
        else:
            # Search by name
            response = requests.get('https://api.scryfall.com/cards/named', params={'exact': query})
            if response.status_code == 404:
                # Try fuzzy search
                response = requests.get('https://api.scryfall.com/cards/named', params={'fuzzy': query})
        
        if response.status_code == 200:
            card_data = response.json()
            return JsonResponse({'card': card_data})
        else:
            return JsonResponse({'error': 'Card not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_card(request):
    """Add a card to the database"""
    try:
        data = json.loads(request.body)
        card_data = data.get('card_data')
        
        if not card_data:
            return JsonResponse({'error': 'Card data is required'}, status=400)
        
        # Check if card already exists
        existing_card = Card.objects.filter(scryfall_id=card_data['id']).first()
        if existing_card:
            return JsonResponse({'message': 'Card already exists in database', 'existed': True})
        
        # Create new card
        card = Card.objects.create(
            name=card_data['name'],
            scryfall_id=card_data['id'],
            image_uris=card_data.get('image_uris', {}),
            card_faces=card_data.get('card_faces', []),
            layout=card_data.get('layout', 'normal')
        )
        
        return JsonResponse({'message': 'Card added successfully', 'existed': False})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def bulk_add_cards(request):
    """Add multiple cards to the database from a text input"""
    try:
        data = json.loads(request.body)
        card_list = data.get('card_list', '').strip()
        
        if not card_list:
            return JsonResponse({'error': 'Card list is required'}, status=400)
        
        lines = [line.strip() for line in card_list.split('\n') if line.strip()]
        
        results = {
            'total': len(lines),
            'added': 0,
            'existed': 0,
            'errors': 0,
            'error_details': []
        }
        
        for line in lines:
            try:
                # Determine if it's a URL or card name
                if 'scryfall.com' in line:
                    card_data = search_card_by_url_internal(line)
                else:
                    card_data = search_card_by_name_internal(line)
                
                if card_data:
                    # Check if card already exists
                    existing_card = Card.objects.filter(scryfall_id=card_data['id']).first()
                    if existing_card:
                        results['existed'] += 1
                    else:
                        # Create new card
                        Card.objects.create(
                            name=card_data['name'],
                            scryfall_id=card_data['id'],
                            image_uris=card_data.get('image_uris', {}),
                            card_faces=card_data.get('card_faces', []),
                            layout=card_data.get('layout', 'normal')
                        )
                        results['added'] += 1
                else:
                    results['errors'] += 1
                    results['error_details'].append(f"Card not found: {line}")
                    
            except Exception as e:
                results['errors'] += 1
                results['error_details'].append(f"Error processing '{line}': {str(e)}")
        
        return JsonResponse(results)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def search_card_by_url_internal(url):
    """Internal function to search card by URL"""
    try:
        if '/card/' in url:
            parts = url.split('/card/')
            if len(parts) > 1:
                full_path = parts[1].split('?')[0]
                path_parts = full_path.split('/')
                if len(path_parts) >= 2:
                    card_path = f"{path_parts[0]}/{path_parts[1]}"
                    response = requests.get(f'https://api.scryfall.com/cards/{card_path}')
                    if response.status_code == 200:
                        return response.json()
        return None
    except:
        return None


def search_card_by_name_internal(name):
    """Internal function to search card by name"""
    try:
        # Try exact match first
        response = requests.get('https://api.scryfall.com/cards/named', params={'exact': name})
        if response.status_code == 200:
            return response.json()
        
        # Try fuzzy search
        response = requests.get('https://api.scryfall.com/cards/named', params={'fuzzy': name})
        if response.status_code == 200:
            return response.json()
        
        return None
    except:
        return None


def standings(request):
    """Standings page showing all cards sorted by rating"""
    cards = Card.objects.all().order_by('-rating', 'rating_deviation')
    
    context = {
        'cards': cards
    }
    return render(request, 'cards/standings.html', context)


def diagnostics(request):
    """Hidden diagnostics page for card management"""
    context = {}
    
    search_query = request.GET.get('search', '')
    if search_query:
        cards = Card.objects.filter(name__icontains=search_query).order_by('name')
        context['cards'] = cards
        context['search_query'] = search_query
    
    return render(request, 'cards/diagnostics.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def update_card(request):
    """Update card fields via diagnostics page"""
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        field = data.get('field')
        value = data.get('value')
        
        if not card_id or not field:
            return JsonResponse({'error': 'Card ID and field are required'}, status=400)
        
        card = get_object_or_404(Card, id=card_id)
        
        # Validate and convert field values
        if field == 'name':
            card.name = str(value)
        elif field == 'rating':
            card.rating = float(value)
        elif field == 'rating_deviation':
            card.rating_deviation = float(value)
        elif field == 'volatility':
            card.volatility = float(value)
        elif field == 'layout':
            card.layout = str(value)
        else:
            return JsonResponse({'error': 'Invalid field'}, status=400)
        
        card.save()
        return JsonResponse({'success': True, 'message': f'Updated {field} successfully'})
        
    except ValueError as e:
        return JsonResponse({'error': f'Invalid value: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_card(request):
    """Delete card via diagnostics page"""
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        if not card_id:
            return JsonResponse({'error': 'Card ID is required'}, status=400)
        
        card = get_object_or_404(Card, id=card_id)
        card_name = card.name
        card.delete()
        
        return JsonResponse({'success': True, 'message': f'Deleted "{card_name}" successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
