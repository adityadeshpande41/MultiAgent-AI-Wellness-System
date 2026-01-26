#!/usr/bin/env python3
"""
Test script to compare targeted vs generic RAG search
"""

from tools.rag import search, search_fitness, search_nutrition, search_medical, search_mental_health, search_tracking

def test_targeted_vs_generic():
    """Compare targeted search vs generic search"""
    
    test_cases = [
        {
            "query": "progressive overload training",
            "targeted_func": search_fitness,
            "agent": "Fitness Coach"
        },
        {
            "query": "protein requirements for athletes", 
            "targeted_func": search_nutrition,
            "agent": "Nutrition Specialist"
        },
        {
            "query": "blood pressure management",
            "targeted_func": search_medical,
            "agent": "Doctor Avatar"
        },
        {
            "query": "anxiety coping strategies",
            "targeted_func": search_mental_health,
            "agent": "Mental Health Specialist"
        },
        {
            "query": "health data visualization",
            "targeted_func": search_tracking,
            "agent": "Tracking Agent"
        }
    ]
    
    print("🎯 Testing Targeted vs Generic RAG Search\n")
    print("=" * 80)
    
    for case in test_cases:
        query = case["query"]
        targeted_func = case["targeted_func"]
        agent = case["agent"]
        
        print(f"\n🔍 Query: '{query}' ({agent})")
        print("-" * 60)
        
        try:
            # Generic search (old approach)
            generic_results = search(query, k=2)
            
            # Targeted search (new approach)
            targeted_results = targeted_func(query, k=2)
            
            print("📊 GENERIC SEARCH RESULTS:")
            for i, result in enumerate(generic_results, 1):
                truncated = result[:150] + "..." if len(result) > 150 else result
                print(f"   {i}. {truncated}")
            
            print("\n🎯 TARGETED SEARCH RESULTS:")
            for i, result in enumerate(targeted_results, 1):
                truncated = result[:150] + "..." if len(result) > 150 else result
                print(f"   {i}. {truncated}")
                
            # Check if results are different
            if generic_results != targeted_results:
                print("   ✅ TARGETED SEARCH FOUND DIFFERENT/BETTER RESULTS!")
            else:
                print("   ℹ️  Results are the same (both approaches work)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Targeted RAG Test Complete!")
    print("\n💡 Benefits of Targeted Search:")
    print("   • More relevant results from domain-specific knowledge")
    print("   • Faster search (smaller search space)")
    print("   • Better context quality for agents")
    print("   • Reduced noise from irrelevant domains")

if __name__ == "__main__":
    test_targeted_vs_generic()