# Kernels Production Deployment Guide

This guide explains how to deploy the kernels functionality to production.

## Quick Deploy Steps

### 1. Build the React App for Production
```bash
cd /path/to/cube-kernels-2/frontend
npm run build
```

### 2. Copy Built Files (Automated)
```bash
cd /path/to/cube
python build_kernels.py
```

This script automatically:
- Builds the React app
- Copies files to `staticfiles/kernels/`
- Updates the template with correct file hashes
- Creates build info for tracking

### 3. Deploy to Heroku
```bash
git add .
git commit -m "Add kernels production build"
git push heroku main
```

### 4. Run Migrations (if needed)
```bash
heroku run python manage.py migrate
heroku run python manage.py populate_candidates
```

## Manual Steps (if automated script fails)

### 1. Build React App
```bash
cd cube-kernels-2/frontend
npm run build
```

### 2. Copy Files
```bash
cp -r build/* /path/to/cube/staticfiles/kernels/
```

### 3. Update Template
Edit `cards/templates/cards/kernels.html` and update the script/CSS file names with the correct hashes from the build.

## Verification

### Local Testing
1. Run Django server: `python manage.py runserver`
2. Visit `http://localhost:8000/kernels/`
3. Should see kernels interface working (not iframe)

### Production Testing
1. Deploy to Heroku
2. Visit `https://your-app.herokuapp.com/kernels/`
3. Verify full functionality:
   - Cards load with images
   - Drag and drop works
   - API calls succeed
   - No console errors

## Production vs Development

**Development Mode:**
- Loads React app from `localhost:3000` in iframe
- Real-time updates during development
- Shows "Development Mode" notice

**Production Mode:**
- Serves built React app as static files
- Optimized and minified
- API calls use relative URLs
- No iframe, direct integration

## Troubleshooting

### Static Files Not Loading
```bash
heroku run python manage.py collectstatic --noinput
```

### API Errors
- Check CORS settings in `settings.py`
- Verify API endpoints are working: `/api/candidates/`, `/api/kernels/`

### JavaScript Errors
- Check browser console for errors
- Verify file paths in template match actual built files
- Ensure React app was built with production API URLs

## File Structure

```
cube/
├── staticfiles/kernels/          # Built React app
│   ├── static/css/main.*.css     # Bundled CSS
│   ├── static/js/main.*.js       # Main React bundle
│   ├── static/js/*.chunk.js      # Code-split chunks
│   └── build_info.json           # Build metadata
├── cards/templates/cards/kernels.html  # Integration template
└── build_kernels.py              # Automated build script
```

## Notes

- The React app automatically detects production vs development environment
- File hashes change with each build - template must be updated
- Static files are served by WhiteNoise in production
- All API calls use relative URLs in production for proper domain handling