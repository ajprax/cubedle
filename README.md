# Magic: The Gathering Cube Voting Application

A Django web application for voting on which Magic: The Gathering cards should be included in a cube. Uses the Glicko-2 rating system to rank cards based on head-to-head voting.

## Features

- **Head-to-Head Voting**: Compare two random cards and vote for which should be included
- **Card Suggestions**: Search for and add cards using Scryfall's API
- **Standings**: View all cards ranked by their current ratings
- **Glicko-2 Rating System**: Sophisticated rating algorithm that accounts for uncertainty
- **Card Display**: Proper handling of different card layouts including rotated cards and double-faced cards

## Local Development Setup

1. **Clone and navigate to the project directory**
   ```bash
   cd cube
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv cube_env
   source cube_env/bin/activate  # On Windows: cube_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Visit the application**
   Open http://localhost:8000 in your browser

## Adding Cards

### Via Web Interface
1. Go to "Suggest Cards" page
2. Enter a card name or Scryfall URL
3. Preview the card and click "Add to Database"

### Bulk Import
Use the bulk import script to add multiple cards from a text file:

```bash
python bulk_import.py cards_to_add.txt
```

The text file should contain one card name or Scryfall URL per line:
```
Lightning Bolt
https://scryfall.com/card/m11/146/lightning-bolt
Black Lotus
Ancestral Recall
```

## Heroku Deployment

1. **Create a Heroku app**
   ```bash
   heroku create your-cube-voting-app
   ```

2. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key-here"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Run migrations on Heroku**
   ```bash
   heroku run python manage.py migrate
   ```

## Rating System

The application uses the Glicko-2 rating system with these default values:
- Initial Rating: 1500
- Initial Rating Deviation (RD): 350
- Initial Volatility: 0.06

Cards with higher uncertainty (higher RD) are more likely to appear in voting pairs to quickly establish their true rating.

## Card Display Features

- **Rotation**: Automatically rotates battle cards (90°) and flip cards (180°)
- **Double-faced Cards**: Shows flip buttons and handles front/back display
- **Tooltips**: Hover over cards in standings to see images
- **Responsive Layout**: Works on desktop and mobile devices

## Project Structure

```
cube_voting/
├── cards/                 # Main Django app
│   ├── models.py         # Card model with Glicko-2 fields
│   ├── views.py          # Web views and API endpoints
│   ├── glicko2.py        # Glicko-2 rating algorithm
│   └── templates/        # HTML templates
├── cube_voting/          # Django project settings
├── bulk_import.py        # Bulk card import script
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment config
└── runtime.txt          # Python version for Heroku
```

## API Endpoints

- `POST /vote/` - Submit a vote between two cards
- `POST /search-card/` - Search for a card via Scryfall
- `POST /add-card/` - Add a card to the database

## Contributing

1. Add cards to the database using the web interface or bulk import
2. Vote on head-to-head matchups to improve card ratings
3. Share the application with other cube enthusiasts

## License

This project is open source and available under the MIT License.