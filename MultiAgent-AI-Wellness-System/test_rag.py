#!/usr/bin/env python3
"""
Test script to verify RAG system is working with comprehensive knowledge bases
"""

from tools.rag import search

def test_rag_queries():
    """Test various queries across different domains"""
    
    test_queries = [
        # Fitness queries
        "progressive overload strength training",
        "HIIT workout protocols",
        "muscle fiber types",
        
        # Nutrition queries  
        "protein requirements athletes",
        "intermittent fasting benefits",
        "micronutrient deficiencies",
        
        # Medical queries
        "blood pressure management",
        "diabetes prevention",
        "mental health anxiety",
        
        # Tracking queries
        "health metrics biomarkers",
        "wearable device accuracy",
        "data visualization techniques"
    ]
    
    print("🔍 Testing RAG System with Comprehensive Knowledge Bases\n")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        try:
            results = search(query, k=2)  # Get top 2 results
            
            if results:
                for j, result in enumerate(results, 1):
                    # Truncate long results for readability
                    truncated = result[:200] + "..." if len(result) > 200 else result
                    print(f"   Result {j}: {truncated}")
            else:
                print("   No results found")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ RAG System Test Complete!")

if __name__ == "__main__":
    test_rag_queries()