# TarangFX - Testing Guide

## Quick Test Checklist

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python bot.py
```

### Test 1: Basic File Upload
1. Send any audio file to bot
2. Verify download progress shows up
3. Check file info is displayed correctly
4. Confirm buttons appear

**Expected Result:**
- Download completes without timeout
- Audio info shows codec, bitrate, duration, size
- Processing options buttons displayed

### Test 2: Format Conversion
1. Send audio file
2. Click "Convert Format"
3. Select MP3
4. Choose 320k bitrate
5. Click "Confirm & Process"

**Expected Result:**
- Processing completes without hanging
- Converted file is sent back
- "Continue Editing" option appears
- Original file persists in session

### Test 3: Custom EQ Command
1. Send audio file
2. Reply to the audio message with:
   ```
   /eq --60hz +3db --1khz -2db --5khz +2db
   ```
3. Click "Confirm & Process"

**Expected Result:**
- EQ settings parsed correctly
- Processing shows EQ bands applied
- Output file has EQ applied
- Can verify with spectrum analyzer

### Test 4: Pedalboard Effects
1. Send audio file
2. Click "Apply Effects"
3. Select "Reverb"
4. Select "Compressor"
5. Click "Done"

**Expected Result:**
- Both effects added to settings
- Processing applies effects in sequence
- Output has reverb and compression
- Audible difference in sound

### Test 5: Multi-Step Processing
1. Send audio file
2. Apply EQ with `/eq --100hz +2db`
3. Click "Continue Editing"
4. Click "Apply Effects"
5. Add "Reverb"
6. Click "Confirm & Process"

**Expected Result:**
- Both EQ and reverb applied
- Original file still available
- Each step completes successfully
- Final output has all processing

### Test 6: Session Persistence
1. Send audio file
2. Apply any processing
3. Click "Continue Editing"
4. Wait 2 minutes
5. Apply another operation

**Expected Result:**
- File still available after 2 minutes
- Can apply additional processing
- Session expires after 5 minutes total
- Auto-cleanup removes old files

### Test 7: Cancel Operation
1. Send audio file
2. Start any operation
3. Click "Cancel"
4. Verify session cleared

**Expected Result:**
- Session deleted from memory/database
- Temporary files cleaned up
- New file upload starts fresh session

### Test 8: Error Handling
1. Send audio file
2. Try invalid EQ command: `/eq invalid`
3. Verify helpful error message

**Expected Result:**
- Clear error message displayed
- Format example provided
- No crash or hang
- User can retry

### Test 9: Download Retry
1. Simulate poor connection (optional)
2. Send large audio file (>50MB)
3. Monitor download progress

**Expected Result:**
- Progress updates every 2 seconds
- Auto-retry on timeout
- Eventually succeeds
- No manual intervention needed

### Test 10: Help System
1. Send `/help`
2. Click "EQ Guide"
3. Read EQ documentation
4. Click "Back to Help"
5. Explore other help sections

**Expected Result:**
- All help sections load correctly
- Buttons work smoothly
- Content is informative
- Navigation is intuitive

## Advanced Testing

### Database Integration Test (with Supabase)
```bash
# Add to .env
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

# Run bot
python bot.py
```

1. Send audio file
2. Check Supabase dashboard for session record
3. Apply processing
4. Verify session updated
5. Wait 5+ minutes
6. Check session auto-deleted

### Stress Test (Multiple Users)
```python
# Simple concurrent test script
import asyncio
from pyrogram import Client

async def test_user(user_id):
    # Simulate user sending file and processing
    pass

# Run 10 concurrent users
await asyncio.gather(*[test_user(i) for i in range(10)])
```

### Memory Leak Test
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python'

# Send multiple files
# Process each one
# Verify memory doesn't continuously grow
```

## Common Issues & Solutions

### Issue: "Module not found: pedalboard"
**Solution:**
```bash
pip install --upgrade pip
pip install pedalboard==0.9.8
```

### Issue: "FFmpeg not found"
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg libsndfile1

# macOS
brew install ffmpeg libsndfile
```

### Issue: Download timeouts
**Solution:**
- Check internet connection
- Bot automatically retries 5 times
- Increase timeout in download_manager.py if needed

### Issue: Database connection fails
**Solution:**
- Bot falls back to in-memory storage
- Verify SUPABASE_URL and SUPABASE_ANON_KEY
- Check Supabase project is active

### Issue: EQ not working
**Solution:**
- Check frequency range (20Hz-40kHz)
- Check gain range (-20dB to +20dB)
- Use format: `/eq --100hz +2db`
- Reply to audio message, don't send as new message

## Performance Benchmarks

### Expected Processing Times
- Small file (<5MB): 5-15 seconds
- Medium file (5-50MB): 15-45 seconds
- Large file (50-500MB): 1-5 minutes
- Very large (500MB-2GB): 5-15 minutes

### Memory Usage
- Idle: ~100MB
- Processing small file: ~200MB
- Processing large file: ~500MB
- With 10 concurrent users: ~1-2GB

### Database Queries
- Get session: <10ms
- Create session: <20ms
- Update session: <15ms
- Cleanup expired: <100ms

## Feature Validation

### EQ Command
Test frequencies:
```bash
/eq --20hz +3db      # Sub-bass boost
/eq --100hz +2db     # Bass boost
/eq --500hz -1db     # Low-mid cut
/eq --1khz +1db      # Presence boost
/eq --5khz +2db      # Air/brightness
/eq --10khz +1db     # Sparkle
```

### Effects Chain
Test combinations:
1. Compressor → Reverb (standard)
2. Distortion → Delay (creative)
3. EQ → Compressor → Limiter (mastering)
4. Chorus → Reverb (lush)

### 3D Audio Positions
Test azimuth angles:
- 0° (front)
- 90° (right)
- -90° (left)
- 180° (behind)

## Regression Testing

After any code changes, verify:
1. Basic file upload still works
2. Format conversion completes
3. EQ command parses correctly
4. Effects apply properly
5. Session persistence works
6. Auto-cleanup runs
7. Error handling catches issues
8. Help system loads

## Load Testing

### Simulated Load
```bash
# Use Apache Bench or similar
# Send 100 requests over 10 seconds
# Monitor response times
# Check for failures
```

### Expected Results
- 95%+ success rate
- <1% timeout rate
- No memory leaks
- No crashes
- Database handles load

## Monitoring

### Key Metrics to Track
1. **Download Success Rate**: >95%
2. **Processing Success Rate**: >98%
3. **Average Response Time**: <30s
4. **Memory Usage**: <500MB per user
5. **Error Rate**: <2%
6. **Session Cleanup Rate**: 100%

### Logging
Check logs for:
- Download retries
- Processing errors
- Database failures
- Session expirations
- FFmpeg errors

## Sign-Off Checklist

Before deploying to production:
- [ ] All 10 basic tests pass
- [ ] Database integration works
- [ ] Error handling verified
- [ ] Help system complete
- [ ] Documentation updated
- [ ] Memory leaks checked
- [ ] Load testing completed
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Rollback plan ready

## Conclusion

This testing guide ensures all features work correctly and the bot is production-ready. Run through all tests before deploying to users.

For issues or questions, check:
1. Error logs
2. Supabase dashboard (if using)
3. GitHub issues
4. Documentation

Happy testing!
