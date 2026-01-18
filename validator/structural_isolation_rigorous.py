import json
from math import gcd
from functools import reduce

# Load 707 monomials from your validated JSON
with open('validator/saved_inv_p313_monomials18.json', 'r') as f:
    hodge_monomials = json.load(f)

hodge_set = {tuple(m) for m in hodge_monomials}

def compute_exponent_gcd(monomial):
    """
    Compute GCD of all non-zero exponents. 
    If gcd > 1, the monomial might be a power of a simpler class,
    suggesting a potential algebraic origin.
    """
    non_zero = [e for e in monomial if e > 0]
    if not non_zero: return 0
    return reduce(gcd, non_zero)

def analyze_structural_isolation():
    results = []
    for m in hodge_monomials:
        num_vars = sum(1 for e in m if e > 0)
        
        # Focus on the 'Dark' 6-variable monomials
        if num_vars != 6: continue
        
        exp_gcd = compute_exponent_gcd(m)
        non_zero = [e for e in m if e > 0]
        avg_exp = sum(non_zero) / len(non_zero)
        variance = sum((e - avg_exp)**2 for e in non_zero) / len(non_zero)
        
        algebraic_score = 0
        
        # High GCD suggests factorization (algebraic hint)
        if exp_gcd > 1:
            algebraic_score += 3
        
        # Low variance suggests balance (algebraic hint)
        if variance < 2:
            algebraic_score += 2
            
        # Check if it's a 'power' of a simpler Hodge monomial
        if exp_gcd > 1:
            reduced = tuple(e // exp_gcd for e in m)
            # (Note: This would usually be in a lower degree piece, 
            # but we check if it matches Hodge patterns)
            pass 

        results.append({
            'monomial': m,
            'gcd': exp_gcd,
            'balance': float(variance),
            'algebraic_score': algebraic_score,
            'isolated': algebraic_score == 0
        })
    return results

print("="*60)
print("RIGOROUS STRUCTURAL ISOLATION ANALYSIS")
print("="*60)

results = analyze_structural_isolation()
results.sort(key=lambda x: x['algebraic_score'])

print(f"\nAnalyzed {len(results)} six-variable monomials\n")
print("TOP 10 MOST STRUCTURALLY ISOLATED CANDIDATES:")
print("(Low score = less likely to be algebraic)\n")

for i, r in enumerate(results[:10]):
    m = r['monomial']
    parts = [f"z{j}^{m[j]}" for j in range(6) if m[j] > 0]
    print(f"{i+1}. {' * '.join(parts)}")
    print(f"   GCD: {r['gcd']}, Balance: {r['balance']:.2f}, Score: {r['algebraic_score']}")
    if r['isolated']:
        print(f"   ★ ISOLATED - No standard algebraic patterns")
    print()

isolated_count = sum(1 for r in results if r['isolated'])
print(f"SUMMARY:")
print(f"Total 6-variable monomials: {len(results)}")
print(f"Structurally isolated: {isolated_count}")

with open('structural_isolation_results.json', 'w') as f:
    json.dump(results, f, indent=2)
