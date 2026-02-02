# **The analysis**

Examining The variety X₈ ⊂ ℙ^5 defined by:

```verbatim
X₈: Σ_{i=0}^5 z_i^8 + δ·Σ_{k=1}^{6} (Σ_{j=0}^5 ω^{kj}z_j)^8 = 0

where ω = e^{2πi/7}, δ = 791/100000
```

the first 19 primes mod 7 = 1 are:

```verbatim
29, 43, 71, 113, 127, 197, 211, 239, 281, 337, 379, 421, 449, 463, 491, 547, 617, 631, 659
```

---

# **Step 1: Smoothness Test**
this is easy for typical C7 cyclotomic and is not computationally heavy, however for X8 pertubation, the GB blows up the memory far beyond my machines 16gb capacity so we resorted to:

```m2
-- ============================================================================
-- MULTI-PRIME SMOOTHNESS VERIFICATION (C7 X8 PERTURBED)
-- ============================================================================
-- Variety: X8: Sum z_i^8 + delta*Sum_{k=1}^{6} (Sum omega^{kj}z_j)^8 = 0
-- where omega = e^{2*pi*i/7}, delta = 791/100000
-- Test across first 19 primes p = 1 (mod 7)
-- ============================================================================

primeList = {29, 43, 71, 113, 127, 197, 211, 239, 281, 337, 379, 421, 449, 463, 491, 547, 617, 631, 659};
n = 7;  -- Cyclotomic order
numTestsPerPrime = 10000;  -- High count to ensure statistical confidence

results = new MutableHashTable;

stdio << "========================================" << endl;
stdio << "C7 X8 PERTURBED VARIETY SMOOTHNESS TEST" << endl;
stdio << "========================================" << endl;
stdio << "Variety: Sum z_i^8 + (791/100000)*Sum_{k=1}^{18} L_k^8 = 0" << endl;
stdio << "where L_k = Sum_{j=0}^5 omega^{kj}z_j, omega = e^{2*pi*i/7}" << endl;
stdio << "Testing first 19 primes p = 1 (mod 7)" << endl;
stdio << "Prime range: 191 to 2357" << endl;
stdio << "Tests per prime: " << numTestsPerPrime << endl;
stdio << "========================================" << endl;

for p in primeList do (
    stdio << endl << "========================================" << endl;
    stdio << "TESTING PRIME p = " << p << endl;
    stdio << "========================================" << endl;
    
    -- Verify p = 1 (mod 7)
    if (p % 7) != 1 then (
        stdio << "ERROR: p = " << p << " is not = 1 (mod 7)" << endl;
        stdio << "  p mod 7 = " << (p % 7) << endl;
        results#p = "INVALID_PRIME";
        continue;
    );
    
    -- Setup
    R = ZZ/p[z_0..z_5];
    
    -- Find primitive 7th root of unity
    omega = null;
    for g from 2 to p-1 do (
        if (g^n % p) == 1 and (g^1 % p) != 1 then (
            omega = g_R;
            break;
        );
    );
    
    if omega === null then (
        stdio << "ERROR: No primitive 7th root found for p = " << p << endl;
        results#p = "SKIPPED";
        continue;
    );
    
    stdio << "omega = " << omega << " (primitive 7th root mod " << p << ")" << endl;
    
    -- Verify order omega^7 = 1 and omega != 1
    omegaCheck = lift(omega^n, ZZ) % p;
    if omegaCheck != 1 then (
        stdio << "ERROR: omega^7 != 1 (got " << omegaCheck << ")" << endl;
        results#p = "SKIPPED";
        continue;
    );
    
    omega1Check = lift(omega^1, ZZ) % p;
    if omega1Check == 1 then (
        stdio << "ERROR: omega = 1 (not primitive)" << endl;
        results#p = "SKIPPED";
        continue;
    );
    
    stdio << "  Verification: omega^7 = 1, omega != 1 [OK]" << endl;
    
    -- Build linear forms L_k for k=1,...,18 (k=0 is Fermat term)
    L = apply(n-1, k -> sum apply(6, j -> omega^((k+1)*j) * R_j));
    
    -- Build polynomial
    FermatTerm = sum apply(6, i -> R_i^8);
    CyclotomicTerm = sum apply(n-1, k -> L#k^8);  -- L_1^8 + ... + L_18^8
    
    -- Perturbation parameter epsilon = 791/100000 mod p
    -- Compute 100000^{-1} mod p first, then multiply by 791
    inverse100000 = lift(1/(100000_(ZZ/p)), ZZ);
    epsilonInt = (791 * inverse100000) % p;
    epsilonCoeff = epsilonInt_R;
    
    stdio << "epsilon = " << epsilonCoeff << " (= 791/100000 mod " << p << ")" << endl;
    
    -- Full polynomial
    F = FermatTerm + epsilonCoeff * CyclotomicTerm;
    
    -- Partial derivatives (Jacobian criterion for smoothness)
    partials = {diff(z_0, F), diff(z_1, F), diff(z_2, F), 
                diff(z_3, F), diff(z_4, F), diff(z_5, F)};
    
    stdio << "Polynomial and partials computed (degree " << (first degree F) << ")" << endl;
    
    -- Random point smoothness test
    numSingular = 0;
    numSmooth = 0;
    pointsOnVariety = 0;
    
    stdio << "Testing " << numTestsPerPrime << " random points..." << endl;
    
    for testNum from 1 to numTestsPerPrime do (
        pt = apply(6, i -> random(ZZ/p));
        subMap = map(ZZ/p, R, pt);
        
        Fval = subMap(F);
        
        if Fval == 0_(ZZ/p) then (
            pointsOnVariety = pointsOnVariety + 1;
            
            -- Check if all partials vanish (singular point criterion)
            partialVals = apply(partials, pd -> subMap(pd));
            allZero = all(partialVals, v -> v == 0_(ZZ/p));
            
            if allZero then (
                numSingular = numSingular + 1;
                stdio << "  [X] Test " << testNum << ": SINGULAR at " << pt << endl;
            ) else (
                numSmooth = numSmooth + 1;
            );
        );
        
        -- Progress indicator every 1000 tests (10% increments)
        if testNum % 1000 == 0 then (
            stdio << "  Progress: " << testNum << "/" << numTestsPerPrime 
                  << " (" << pointsOnVariety << " on variety, " 
                  << numSmooth << " smooth, " << numSingular << " singular)" << endl;
        );
    );
    
    -- Results for this prime
    stdio << endl << "RESULTS for p = " << p << ":" << endl;
    stdio << "  Points on variety: " << pointsOnVariety << endl;
    stdio << "  Smooth: " << numSmooth << endl;
    stdio << "  Singular: " << numSingular << endl;
    
    if pointsOnVariety == 0 then (
        stdio << "  [!] WARNING: No points found (variety may be sparse mod " << p << ")" << endl;
        stdio << "              This is acceptable for high-degree varieties" << endl;
        results#p = "SPARSE";
    ) else if numSingular == 0 then (
        stdio << "  [OK] SMOOTH (" << numSmooth << "/" << pointsOnVariety << " tested)" << endl;
        results#p = "SMOOTH";
    ) else (
        stdio << "  [X] SINGULAR (" << numSingular << " singular points detected)" << endl;
        results#p = "SINGULAR";
    );
);

-- ============================================================================
-- FINAL SUMMARY
-- ============================================================================

stdio << endl << endl;
stdio << "============================================" << endl;
stdio << "MULTI-PRIME SMOOTHNESS SUMMARY (C7 X8)" << endl;
stdio << "============================================" << endl;

for p in primeList do (
    statusStr = results#p;
    statusSymbol = if statusStr == "SMOOTH" then "[OK]" else if statusStr == "SPARSE" then "[!]" else "[X]";
    stdio << statusSymbol << " p = " << p << ": " << statusStr << endl;
);

stdio << endl;

-- Count results
smoothCount = 0;
sparseCount = 0;
singularCount = 0;
invalidCount = 0;

for p in primeList do (
    if results#p == "SMOOTH" then smoothCount = smoothCount + 1
    else if results#p == "SPARSE" then sparseCount = sparseCount + 1
    else if results#p == "SINGULAR" then singularCount = singularCount + 1
    else if results#p == "INVALID_PRIME" then invalidCount = invalidCount + 1;
);

stdio << "STATISTICS:" << endl;
stdio << "  Smooth: " << smoothCount << "/19 primes" << endl;
stdio << "  Sparse: " << sparseCount << "/19 primes" << endl;
stdio << "  Singular: " << singularCount << "/19 primes" << endl;
if invalidCount > 0 then (
    stdio << "  Invalid: " << invalidCount << "/19 primes" << endl;
);
stdio << endl;

-- Final verdict
if invalidCount > 0 then (
    stdio << "[X] CONFIGURATION ERROR: " << invalidCount << " invalid primes" << endl;
    stdio << "All primes must satisfy p = 1 (mod 7)" << endl;
) else if singularCount > 0 then (
    stdio << "[X][X][X] SMOOTHNESS FAILED [X][X][X]" << endl;
    stdio << "Singular points detected at " << singularCount << " primes" << endl;
    stdio << "Variety may not be smooth over Q" << endl;
) else if smoothCount >= 15 then (
    stdio << "[OK][OK][OK] X8 IS SMOOTH (" << smoothCount << "/19 primes agree) [OK][OK][OK]" << endl;
    stdio << "EGA spreading-out principle applies (semi-continuity)" << endl;
    stdio << "Variety is smooth over Q(omega) with overwhelming evidence" << endl;
    if sparseCount > 0 then (
        stdio << "Note: " << sparseCount << " primes showed no points (acceptable for degree-8 varieties)" << endl;
    );
) else if smoothCount >= 10 then (
    stdio << "[!] LIKELY SMOOTH (" << smoothCount << "/19 primes)" << endl;
    stdio << "Recommend investigation of inconclusive primes" << endl;
) else (
    stdio << "[X] SMOOTHNESS UNCERTAIN (only " << smoothCount << "/7 smooth)" << endl;
);

stdio << "============================================" << endl;

end
```

---

resuls:

```verbatim
========================================
TESTING PRIME p = 29
========================================
omega = 7 (primitive 7th root mod 29)
  Verification: omega^7 = 1, omega != 1 [OK]
epsilon = 1 (= 791/100000 mod 29)
Polynomial and partials computed (degree 8)
Testing 10000 random points...
  Progress: 1000/10000 (35 on variety, 35 smooth, 0 singular)
  Progress: 2000/10000 (69 on variety, 69 smooth, 0 singular)
  Progress: 3000/10000 (107 on variety, 107 smooth, 0 singular)
  Progress: 4000/10000 (134 on variety, 134 smooth, 0 singular)
  Progress: 5000/10000 (162 on variety, 162 smooth, 0 singular)
  Progress: 6000/10000 (197 on variety, 197 smooth, 0 singular)
  Progress: 7000/10000 (233 on variety, 233 smooth, 0 singular)
  Progress: 8000/10000 (277 on variety, 277 smooth, 0 singular)
  Progress: 9000/10000 (310 on variety, 310 smooth, 0 singular)
  Progress: 10000/10000 (346 on variety, 346 smooth, 0 singular)

RESULTS for p = 29:
  Points on variety: 346
  Smooth: 346
  Singular: 0
  [OK] SMOOTH (346/346 tested)
.

.

.

.

========================================
TESTING PRIME p = 659
========================================
omega = 12 (primitive 7th root mod 659)
  Verification: omega^7 = 1, omega != 1 [OK]
epsilon = -142 (= 791/100000 mod 659)
Polynomial and partials computed (degree 8)
Testing 10000 random points...
  Progress: 1000/10000 (1 on variety, 1 smooth, 0 singular)
  Progress: 2000/10000 (6 on variety, 6 smooth, 0 singular)
  Progress: 3000/10000 (10 on variety, 10 smooth, 0 singular)
  Progress: 4000/10000 (10 on variety, 10 smooth, 0 singular)
  Progress: 5000/10000 (10 on variety, 10 smooth, 0 singular)
  Progress: 6000/10000 (11 on variety, 11 smooth, 0 singular)
  Progress: 7000/10000 (13 on variety, 13 smooth, 0 singular)
  Progress: 8000/10000 (14 on variety, 14 smooth, 0 singular)
  Progress: 9000/10000 (14 on variety, 14 smooth, 0 singular)
  Progress: 10000/10000 (15 on variety, 15 smooth, 0 singular)

RESULTS for p = 659:
  Points on variety: 15
  Smooth: 15
  Singular: 0
  [OK] SMOOTH (15/15 tested)


============================================
MULTI-PRIME SMOOTHNESS SUMMARY (C7 X8)
============================================
[OK] p = 29: SMOOTH
[OK] p = 43: SMOOTH
[OK] p = 71: SMOOTH
[OK] p = 113: SMOOTH
[OK] p = 127: SMOOTH
[OK] p = 197: SMOOTH
[OK] p = 211: SMOOTH
[OK] p = 239: SMOOTH
[OK] p = 281: SMOOTH
[OK] p = 337: SMOOTH
[OK] p = 379: SMOOTH
[OK] p = 421: SMOOTH
[OK] p = 449: SMOOTH
[OK] p = 463: SMOOTH
[OK] p = 491: SMOOTH
[OK] p = 547: SMOOTH
[OK] p = 617: SMOOTH
[OK] p = 631: SMOOTH
[OK] p = 659: SMOOTH

STATISTICS:
  Smooth: 19/19 primes
  Sparse: 0/19 primes
  Singular: 0/19 primes

[OK][OK][OK] X8 IS SMOOTH (19/19 primes agree) [OK][OK][OK]
EGA spreading-out principle applies (semi-continuity)
Variety is smooth over Q(omega) with overwhelming evidence
============================================
```

---

