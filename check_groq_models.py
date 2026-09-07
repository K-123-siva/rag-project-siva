"""
Groq Model Availability Checker
Check which Groq models are currently available for your API key
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_groq_models():
    """Check available Groq models using the API"""
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    print("=" * 60)
    print("GROQ MODEL AVAILABILITY CHECK")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Key: {api_key[:20]}..." if len(api_key) > 20 else api_key)
    print()
    
    # Check models via API
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            
            print(f"✓ Successfully retrieved {len(models)} models\n")
            print("-" * 60)
            print("AVAILABLE MODELS:")
            print("-" * 60)
            
            # Group models by type
            production_models = []
            preview_models = []
            other_models = []
            
            for model in models:
                model_id = model.get("id", "unknown")
                created = model.get("created", 0)
                owned_by = model.get("owned_by", "unknown")
                
                model_info = {
                    "id": model_id,
                    "created": datetime.fromtimestamp(created).strftime('%Y-%m-%d') if created else "N/A",
                    "owned_by": owned_by
                }
                
                # Categorize
                if "llama" in model_id.lower():
                    production_models.append(model_info)
                elif "openai" in model_id.lower() or "gpt" in model_id.lower():
                    production_models.append(model_info)
                elif "whisper" in model_id.lower():
                    other_models.append(model_info)
                else:
                    preview_models.append(model_info)
            
            # Display Production Models
            if production_models:
                print("\n🚀 PRODUCTION MODELS (LLMs):")
                for i, m in enumerate(production_models, 1):
                    print(f"  {i}. {m['id']}")
                    print(f"     Created: {m['created']} | Owner: {m['owned_by']}")
            
            # Display Other Models
            if other_models:
                print("\n🎯 OTHER MODELS (Audio, etc.):")
                for i, m in enumerate(other_models, 1):
                    print(f"  {i}. {m['id']}")
                    print(f"     Created: {m['created']} | Owner: {m['owned_by']}")
            
            # Display Preview Models
            if preview_models:
                print("\n🧪 PREVIEW MODELS:")
                for i, m in enumerate(preview_models, 1):
                    print(f"  {i}. {m['id']}")
                    print(f"     Created: {m['created']} | Owner: {m['owned_by']}")
            
            print("\n" + "=" * 60)
            print("DEPRECATION WARNINGS:")
            print("=" * 60)
            
            # Check for deprecated models
            deprecated_found = []
            for model in models:
                model_id = model.get("id")
                if "llama-3.3-70b-versatile" in model_id or "llama-3.1-8b-instant" in model_id:
                    deprecated_found.append(model_id)
            
            if deprecated_found:
                print("⚠️  The following models are in your list but may be deprecated:")
                for m in deprecated_found:
                    print(f"   - {m}")
                print("\n   These models moved to Enterprise tier only on June 17, 2026")
            else:
                print("✓ No known deprecated models found in active list")
            
            print("\n" + "=" * 60)
            print("RECOMMENDATION:")
            print("=" * 60)
            print("For RAG applications, use:")
            print("  • openai/gpt-oss-120b (balanced performance)")
            print("  • openai/gpt-oss-20b (faster, cheaper)")
            print("\nFull documentation: https://console.groq.com/docs/models")
            
        elif response.status_code == 401:
            print("❌ Authentication failed")
            print("Your GROQ_API_KEY may be invalid or expired")
            print(f"Status code: {response.status_code}")
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("Please check your internet connection")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_groq_models()
