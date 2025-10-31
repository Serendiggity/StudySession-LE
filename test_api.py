#!/usr/bin/env python3
"""
Test script to verify Google Gemini API connection.
Phase 1: API Setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test connection to Google Gemini API."""

    print("=" * 60)
    print("Insolvency Study Assistant - API Connection Test")
    print("=" * 60)
    print()

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ ERROR: GEMINI_API_KEY not set in .env file")
        print()
        print("To fix this:")
        print("  1. Go to https://aistudio.google.com/apikey")
        print("  2. Create or sign in to your Google account")
        print("  3. Click 'Create API Key'")
        print("  4. Copy the key")
        print("  5. Edit .env file and replace 'your_gemini_api_key_here' with your actual key")
        print()
        return False

    print("✓ API key found in .env file")
    print()

    # Try to import Lang Extract
    print("Testing Lang Extract import...")
    try:
        import langextract as lx
        print("✓ Lang Extract imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Lang Extract: {e}")
        print()
        print("To fix this:")
        print("  1. Activate virtual environment: source venv/bin/activate")
        print("  2. Install dependencies: pip install -r requirements.txt")
        return False

    print()

    # Try to import Google Generative AI
    print("Testing Google Generative AI import...")
    try:
        import google.generativeai as genai
        print("✓ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google Generative AI: {e}")
        print()
        print("To fix this:")
        print("  pip install google-generativeai")
        return False

    print()

    # Test simple API call with Google Generative AI directly
    print("Testing API connection with Gemini...")
    print("(This may take 10-20 seconds on first run)")
    print()

    try:
        # Test with direct API call first
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(
            "Respond with exactly: 'API test successful'"
        )

        print("✓ API call successful!")
        print()
        print("Response from Gemini:")
        print(f"  • {response.text}")
        print()

        # Now test Lang Extract with a simple example
        print("Testing Lang Extract integration...")

        example = lx.data.ExampleData(
            text="The Bankruptcy and Insolvency Act (BIA) governs bankruptcy in Canada.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="act",
                    extraction_text="Bankruptcy and Insolvency Act",
                    attributes={"abbreviation": "BIA"}
                )
            ]
        )

        result = lx.extract(
            text_or_documents="The Companies' Creditors Arrangement Act (CCAA) is another insolvency statute.",
            prompt_description="Extract the name of the Act and its abbreviation.",
            examples=[example],
            model_id="gemini-2.5-flash"
        )

        print("✓ Lang Extract working!")
        print(f"  • Extractions found: {len(result.extractions)}")

        print()
        print("=" * 60)
        print("✓ All tests passed! API is working correctly.")
        print("=" * 60)
        print()
        print("You're ready to proceed with Phase 2: PDF Processing!")
        print()
        return True

    except Exception as e:
        print(f"❌ API call failed: {e}")
        print()
        print("Common issues:")
        print("  • Invalid API key - check your key in .env file")
        print("  • Rate limiting - wait a moment and try again")
        print("  • Network issues - check your internet connection")
        print()
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
