# Upgrading to GoldMiner 2.0

## What's New

GoldMiner 2.0 features a completely redesigned user interface that addresses all the limitations of v1:

### Key Improvements

1. **Full Idea Control**
   - ✅ Edit any generated idea
   - ✅ Delete unwanted ideas
   - ✅ Manually trigger validation
   - ✅ Stop goldmining process anytime

2. **Better Organization**
   - ✅ Kanban board view
   - ✅ Filter by status and score
   - ✅ Sort by date, score, or title
   - ✅ Persistent ideas in database

3. **Export & Analytics**
   - ✅ Export to CSV, JSON, Markdown
   - ✅ Visual analytics dashboard
   - ✅ Track success rates
   - ✅ View idea distribution

## Upgrade Steps

### Using Docker (Recommended)

1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Rebuild and run**
   ```bash
   ./run.sh
   ```

   The script will automatically:
   - Rebuild with the new UI
   - Preserve your existing data
   - Start the enhanced version

### Manual Upgrade

1. **Update code**
   ```bash
   git pull origin main
   ```

2. **Install any new dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the new version**
   ```bash
   python start_v2.py
   ```

## Data Migration

Your existing ideas are preserved! The v2 UI will:
- Load all existing ideas from the database
- Display them in the new Kanban view
- Allow you to edit/manage them

## Breaking Changes

None! The v2 UI is fully backward compatible. The API remains unchanged, only the frontend has been enhanced.

## New UI Guide

### Idea Board Tab
- Central hub for all ideas
- Three columns: Pending, Validated, Rejected
- Quick actions on each card
- Advanced filtering options

### Gold Mining Tab
- Real-time progress display
- Stop button to halt process
- Live idea updates
- Detailed validation scores

### Quick Generate Tab
- Generate ideas without validation
- Batch generation (5 at once)
- Immediate results

### Analytics Tab
- Visual charts and metrics
- Export functionality
- Success rate tracking

### Settings Tab
- API configuration
- Display preferences
- Cache management

## Troubleshooting

### UI Not Loading?
1. Clear browser cache
2. Check API is running: `curl http://localhost:8000/health`
3. Restart services: `docker-compose restart`

### Ideas Not Showing?
1. Click "Reload All Ideas" in Settings
2. Check browser console for errors
3. Verify database connection

### Export Not Working?
1. Ensure you have ideas to export
2. Try different export formats
3. Check browser download settings

## Need Help?

- Check the logs: `docker-compose logs -f`
- Review the API docs: http://localhost:8000/docs
- File an issue on GitHub

## Rollback to v1

If you need to rollback:

```bash
# Stop current services
docker-compose down

# Checkout v1 code
git checkout v1.0

# Rebuild and run
./run.sh
```

Your data will remain intact!