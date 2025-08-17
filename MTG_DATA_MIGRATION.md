# MTG Data Migration Commands

This document explains how to populate the new MTG-specific fields for existing cards.

## Commands Available

### 1. Check Missing Fields
```bash
python manage.py check_missing_fields [--detailed]
```
- Shows which cards are missing MTG data
- Use `--detailed` to see specific card names
- Safe to run anytime

### 2. Populate MTG Data
```bash
python manage.py populate_mtg_data [options]
```

**Options:**
- `--dry-run`: Show what would be updated without making changes
- `--limit N`: Only process N cards (for testing)
- `--start-from N`: Skip first N cards (for resuming)
- `--batch-size N`: Process N cards before saving (default: 100)
- `--rate-limit N`: Seconds between API calls (default: 0.1)

## Heroku Deployment Steps

### 1. Deploy the Code
```bash
# Make sure all new files are committed
git add cards/management/commands/
git commit -m "Add MTG data migration commands"
git push heroku main
```

### 2. Run Database Migration
```bash
heroku run python manage.py migrate
```

### 3. Check Current Status
```bash
heroku run python manage.py check_missing_fields
```

### 4. Populate MTG Data (Recommended Approach)

**For small batches (testing):**
```bash
heroku run python manage.py populate_mtg_data --limit 10 --dry-run
heroku run python manage.py populate_mtg_data --limit 10
```

**For full population (run in chunks to avoid timeouts):**
```bash
# Process in batches of 100, with larger rate limiting for Heroku
heroku run python manage.py populate_mtg_data --limit 100 --rate-limit 0.2
heroku run python manage.py populate_mtg_data --limit 100 --start-from 100 --rate-limit 0.2
heroku run python manage.py populate_mtg_data --limit 100 --start-from 200 --rate-limit 0.2
# ... continue until all cards are processed
```

**Or for the full dataset (may timeout):**
```bash
heroku run python manage.py populate_mtg_data --rate-limit 0.2
```

### 5. Verify Results
```bash
heroku run python manage.py check_missing_fields
```

## Important Notes

- **Rate Limiting**: Scryfall API allows ~10 requests/second. The script automatically uses more conservative limits on Heroku.
- **Timeouts**: Heroku has 30-minute timeout for `heroku run` commands. For large datasets, process in chunks.
- **Resumable**: Use `--start-from` to resume if a run gets interrupted.
- **Batch Processing**: The script saves cards in batches to handle large datasets efficiently.
- **Error Handling**: Cards with API errors are logged but don't stop the process.

## What Gets Updated

For each card, the script fetches from Scryfall and populates:
- `mana_cost`: The mana cost (e.g., "{2}{U}")
- `cmc`: Converted mana cost (e.g., 3)
- `type_line`: Card type (e.g., "Creature — Human Wizard")
- `oracle_text`: Rules text
- `power`/`toughness`: For creatures
- `colors`: Color array (e.g., ["U", "W"])
- `color_identity`: Color identity for Commander
- `keywords`: Ability keywords
- `num_colors`: Auto-calculated number of colors
- `color_sort_key`: Auto-calculated sorting key

## Recovery

If something goes wrong:
1. Check the error logs from the command output
2. Use `--dry-run` to test before making changes
3. The original card name, scryfall_id, and rating data are never modified
4. You can re-run the command safely - it only updates cards missing data

## Example Output

```
Found 983 cards that need MTG data
Processing batch 1: cards 1-10
Processing batch 2: cards 11-20
Saved batch of 100 cards (total saved: 100)
...
=== Summary ===
Total processed: 983
Successfully updated: 978
Errors: 5
Success rate: 99.5%
MTG data population complete! Updated 978 cards in database.
```