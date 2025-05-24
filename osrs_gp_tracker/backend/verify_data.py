#!/usr/bin/env python3
import requests

def verify_database():
    print("🔍 Verifying database population...")
    
    categories = [
        ('farming', 'herbs'),
        ('hunter', 'birdhouses'),
        ('runecraft', 'gotr_strategies'),
        ('slayer', 'monsters')
    ]
    
    total_items = 0
    for activity, category in categories:
        try:
            resp = requests.get(f'http://localhost:5000/api/items/{activity}?category={category}')
            if resp.status_code == 200:
                items = resp.json().get('items', {})
                count = len(items)
                total_items += count
                print(f"✅ {activity}/{category}: {count} items")
                
                # Show first item details
                if items:
                    first_item_id = list(items.keys())[0]
                    first_item = items[first_item_id]
                    print(f"   Example: {first_item.get('name', 'N/A')}")
            else:
                print(f"❌ {activity}/{category}: API error {resp.status_code}")
        except Exception as e:
            print(f"❌ {activity}/{category}: {str(e)}")
    
    print(f"\n📊 Total items in database: {total_items}")
    return total_items > 0

if __name__ == "__main__":
    verify_database() 