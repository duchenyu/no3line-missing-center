Subject: Missing-center invariant for No-Three-In-Line solutions (using your database)

Dear Mitchell,

I hope this email finds you well. I am an independent researcher working on the No-Three-In-Line problem, and your `mvr/no-three-in-line` repository has been an invaluable resource for my work — thank you for maintaining it.

I wanted to share a finding that emerged from analyzing the D₄-inequivalent solutions in your database. I defined a new geometric invariant: whether the grid center serves as a circumcenter of some triple of points within a maximal 2n-point configuration. A **missing-center** solution is one where no such triple exists — meaning the center is "invisible" to the configuration's circumcircle structure.

Here is a brief summary of what I found:

**Key Results**

1. **Forbid-accumulator algorithm**: O(1) collinearity check per placement (precomputed accumulators), giving a ~65× speedup over the naive O(k²) approach. Full exhaustive search up to n=13, plus D₄-inequivalent analysis through n=53 via your database.

2. **C₄ theorem**: Any 90°-rotation-symmetric 2n-point solution on an odd-n grid automatically has the center as a circumcenter (and is therefore *not* missing-center). This explains why your rot4 class never produces missing-center solutions.

3. **Even-n threshold is real**: Missing-center solutions first appear at n=12 (the first even n where they exist), driven by collinearity constraints rather than pair-capacity limits. They persist through n=30 in the catalogued classes, then re-disappear for n≥32 — a surprising non-monotonic pattern.

4. **Phase transition at n=31**: The rot2 (180° rotational) class collapses from 44,828 solutions at n=29 to zero at n=31.

All code, data tables, and the full writeup are on GitHub:
https://github.com/aujurd22/no3inline-missing-center

I am sharing this purely to show you how your data enabled this line of inquiry — no action needed on your end, and I'll happily take this email as a "received" if you're busy. If you ever find the missing-center angle interesting, I'd be glad to hear your thoughts, but there's absolutely no pressure to reply.

Thank you again for the database, and for the care you've put into it.

Best regards,
Junrong Du
