# MTA API Setup Guide

Your current API key appears to be invalid. Here's how to get a working MTA API key:

## Get a Valid MTA API Key

1. **Register at MTA Developer Portal**
   - Go to: https://api.mta.info/
   - Click "Register" and create an account
   - Verify your email (check spam folder)

2. **Request API Access**
   - Log into your account
   - Navigate to "My Account" > "API Keys"
   - Request a new API key
   - Wait for approval (usually takes 1-2 business days)

## Update Your API Key

Once you get your new API key:

1. Open `config.py`
2. Replace the current key with your new one:
   ```python
   MTA_API_KEY = "your_new_api_key_here"
   ```

## Current Fallback System

Until you get a valid API key, the app will:

1. **Try the official MTA API** (will fail with your current key)
2. **Try alternative APIs** (may work without authentication)
3. **Show mock data** (realistic fake arrival times for testing)

## Alternative Solutions

If you can't get an MTA API key:

1. **Third-party APIs**: Some work without authentication
2. **Mock data mode**: The app generates realistic fake data
3. **NYC Open Data**: Some transit data is available publicly

## Testing

Run the app with `python gui.py` - it should work with mock data even if the API fails.

The GUI will show "Using mock data" messages in the console when APIs are unavailable.