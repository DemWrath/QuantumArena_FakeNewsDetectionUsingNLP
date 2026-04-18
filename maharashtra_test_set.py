"""
maharashtra_test_set.py
TruthLens — Maharashtra, India News Benchmark Dataset

A curated set of 15 news samples covering:
  - REAL   : Legitimate, verifiable Maharashtra news
  - FAKE   : Fabricated or completely false stories
  - MISLEADING : Factual grains spun deceptively
  - UNVERIFIED : Plausible but unconfirmable claims

Each sample carries:
  id          — unique identifier
  category    — REAL | FAKE | MISLEADING | UNVERIFIED
  expected    — expected pipeline composite_verdict label
  headline    — article headline (for clickbait checks)
  body        — article body text
  notes       — human annotation explaining why it belongs to this category
"""

MAHARASHTRA_NEWS_SAMPLES = [

    # ─── REAL ──────────────────────────────────────────────────────────────────

    {
        "id": "MH-REAL-01",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Mumbai Metro Line 3 inaugurated by Prime Minister; Aarey to BKC corridor opens",
        "body": (
            "Prime Minister Narendra Modi officially inaugurated the Mumbai Metro Line 3 (Aqua Line) "
            "on October 7, 2023, connecting Aarey Colony in Goregaon to Bandra-Kurla Complex. "
            "The underground metro corridor, built at a cost of approximately ₹37,276 crore, spans "
            "33.5 km and includes 27 stations. Commuters can now travel from Aarey to BKC in under "
            "45 minutes. The Mumbai Metropolitan Region Development Authority (MMRDA) confirmed that "
            "hourly capacity on the corridor is 1.5 lakh passengers. Phase II extending to Colaba "
            "is expected to open by 2025."
        ),
        "notes": "Verifiable event with specific cost, date, route, and government authority cited."
    },

    {
        "id": "MH-REAL-02",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Maharashtra government announces 10% reservation for EWS in state government jobs",
        "body": (
            "The Maharashtra government on Monday implemented the 10% Economically Weaker Section (EWS) "
            "reservation in state government jobs and education, in line with the 103rd Constitutional "
            "Amendment. Chief Minister Eknath Shinde announced that the reservation will benefit families "
            "with an annual income below ₹8 lakh who do not fall under other reserved categories. "
            "The state's Department of Social Justice confirmed the notification will be issued in the "
            "official Maharashtra Gazette within 30 days."
        ),
        "notes": "Constitutional amendment (103rd), verifiable income threshold, specific ministry cited."
    },

    {
        "id": "MH-REAL-03",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Pune flooding: 7 dead, 2000 displaced as Mula-Mutha river breaches banks",
        "body": (
            "At least seven people died and over 2,000 residents were evacuated as the Mula-Mutha river "
            "breached its banks in Pune following exceptionally heavy rainfall on July 25. The National "
            "Disaster Response Force (NDRF) deployed 12 teams across low-lying areas including Paud Road, "
            "Hadapsar, and Sinhagad Road. Pune Municipal Corporation officials said that nearly 1,800 "
            "people had been shifted to relief camps. The Indian Meteorological Department issued an "
            "orange alert for Pune district and adjoining areas for the next 48 hours."
        ),
        "notes": "Routine flood reporting with specific casualty count, NDRF deployment, and IMD alert level."
    },

    {
        "id": "MH-REAL-04",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Nagpur-Mumbai Expressway: Samruddhi Mahamarg registers 5 crore vehicle trips milestone",
        "body": (
            "Maharashtra's Samruddhi Mahamarg (Nagpur-Mumbai Super Communication Expressway) crossed the "
            "five crore vehicle trip milestone in March 2024, Maharashtra State Road Development Corporation "
            "(MSRDC) announced. The 701 km, eight-lane expressway, inaugurated in December 2022, has reduced "
            "Nagpur-Mumbai travel time from 16 hours to 8 hours. MSRDC collected over ₹1,200 crore in toll "
            "revenue in fiscal year 2023-24. Officials noted that heavy vehicle traffic accounts for 38% of "
            "usage, indicating strong industrial and logistics adoption."
        ),
        "notes": "Specific km length, inauguration date, toll revenue and trip milestone all verifiable."
    },

    {
        "id": "MH-REAL-05",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Maratha quota protests: OBC groups stage counter-demonstration in Pune",
        "body": (
            "Thousands of OBC (Other Backward Class) community members staged a counter-protest at "
            "Shivajinagar in Pune on Saturday, opposing reservation for the Maratha community under "
            "the OBC category. Protest leaders argued that including Marathas in OBC quotas would dilute "
            "existing quotas for OBC communities without increasing the total reservation cap, which the "
            "Supreme Court has held at 50%. State BJP leaders called for an all-party meeting to find a "
            "solution without disturbing the existing reservation framework."
        ),
        "notes": "Ongoing verifiable political issue; 50% cap ruling by Supreme Court is correct."
    },

    # ─── FAKE ──────────────────────────────────────────────────────────────────

    {
        "id": "MH-FAKE-01",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "Shivaji Maharaj statue at Rajkot Fort rises from the sea by itself — miracle confirmed!",
        "body": (
            "In an extraordinary divine event, the 13-foot statue of Chhatrapati Shivaji Maharaj that "
            "collapsed into the Arabian Sea at Rajkot Fort, Malvan in August 2024 has reportedly risen "
            "from the ocean on its own, floating back to shore intact. Eyewitnesses in Sindhudurg district "
            "claim to have photographed the event. Temple priests declared it a miracle, and thousands "
            "are reportedly gathering at the site. No official government statement has been issued."
        ),
        "notes": "Physically impossible. The statue did collapse (real event) but self-resurrection is fabricated."
    },

    {
        "id": "MH-FAKE-02",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "Devendra Fadnavis signs secret treaty gifting Konkan coast to foreign company",
        "body": (
            "Chief Minister Devendra Fadnavis has allegedly signed a classified agreement transferring "
            "sovereign rights over the Konkan coastline — stretching 720 km from Thane to Goa — to a "
            "Luxembourg-based firm called OceanLand Corp. The deal, reportedly signed in a private ceremony "
            "in Dubai, gives OceanLand Corp exclusive extractive rights for 99 years under 'Maharashtra "
            "Coastal Privatisation Act 2024', a law that does not appear in the Maharashtra Gazette or "
            "Legislative Assembly records."
        ),
        "notes": "Invented legislation, invented company, no credible source. Classic disinformation pattern."
    },

    {
        "id": "MH-FAKE-03",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "New strain of COVID-19 found only in Maharashtra water supply; death toll 5000 in 48 hours",
        "body": (
            "A newly discovered COVID-19 variant called 'MH-Omega' has been detected exclusively in "
            "Maharashtra's public water supply systems. According to anonymous health officials, the "
            "airborne waterborne strain has already killed 5,000 people in Maharashtra in the past 48 hours. "
            "The Indian Council of Medical Research (ICMR) has allegedly issued a secret advisory urging "
            "residents to stop using tap water immediately. No hospital admissions, registry data, or "
            "official ICMR press release corroborates these claims."
        ),
        "notes": "COVID is not waterborne; 5,000 deaths in 48 hours without any official confirmation is fabricated."
    },

    # ─── MISLEADING ────────────────────────────────────────────────────────────

    {
        "id": "MH-MSLEAD-01",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "Maharashtra's crime rate is the highest in India — citizens no longer safe",
        "body": (
            "Maharashtra recorded 441,000 IPC cognizable offences in 2022, the highest absolute number "
            "among all Indian states. State Home Minister Devendra Fadnavis admitted to the figures in the "
            "Legislative Assembly. Opposition leaders have called Maharashtra a 'lawless state.' "
            "However, the report omits that Maharashtra is also the most populous state and has the "
            "largest urban police force; when crime is measured per 1 lakh population, Maharashtra ranks "
            "8th nationally, well below Rajasthan, Delhi, and Kerala."
        ),
        "notes": "True absolute number, but per-capita comparison (which paints a different picture) is suppressed."
    },

    {
        "id": "MH-MSLEAD-02",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "Farmer suicide epidemic: Maharashtra government spent ZERO on agriculture in 2024",
        "body": (
            "Maharashtra has recorded over 3,000 farmer suicides annually for the past five years, "
            "making it one of the worst-affected states. The headline claim that the government spent "
            "zero on agriculture is directly contradicted by Budget documents showing ₹12,457 crore "
            "allocated to agriculture in 2024-25. However, activists note that 70% of this budget goes "
            "to irrigation infrastructure rather than direct farmer relief or crop insurance, leaving "
            "smallholders with inadequate support."
        ),
        "notes": "Farmer suicide figures are real; 'zero spending' headline is false but body contains nuanced truth."
    },

    {
        "id": "MH-MSLEAD-03",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "Tata Motors sacks all Pune workers — electric vehicle push kills 18,000 jobs overnight",
        "body": (
            "Tata Motors announced a restructuring of its Pune (Pimpri) facility to prioritize EV "
            "manufacturing, shifting away from ICE (internal combustion engine) vehicles. The company "
            "stated that approximately 800 contractual workers in specific ICE assembly lines would not "
            "have their contracts renewed this quarter. Trade unions have raised concerns. The headline's "
            "claim of 18,000 layoffs is factually incorrect — total Pune workforce strength is 22,000 "
            "and the restructuring affects less than 4% of employees."
        ),
        "notes": "Restructuring is real; 18,000 figure is a 20x exaggeration of 800 contract non-renewals."
    },

    # ─── UNVERIFIED ────────────────────────────────────────────────────────────

    {
        "id": "MH-UNVER-01",
        "category": "UNVERIFIED",
        "expected": "REAL",  # Pipeline may classify REAL since it's plausible
        "headline": "Anonymous whistleblower claims Mumbai port trust officials demanded ₹50 crore bribe",
        "body": (
            "An anonymous letter circulating on social media alleges that senior officials at the Mumbai "
            "Port Authority demanded a ₹50 crore payment from a logistics company as a condition for "
            "approving container terminal expansion plans. The letter, signed by 'Port workers collective,' "
            "names two officials by designation but not by name. Mumbai Port Authority has denied the "
            "allegations. No FIR has been filed and no investigative reporting from mainstream outlets "
            "has independently corroborated the claims."
        ),
        "notes": "Plausible corruption allegation with no verifiable evidence — should be UNVERIFIED."
    },

    {
        "id": "MH-UNVER-02",
        "category": "UNVERIFIED",
        "expected": "REAL",
        "headline": "Nashik grape farmers claim new fungal disease decimating Sula Vineyards crop",
        "body": (
            "Farmers in Nashik's Dindori taluka report a new fungal infection, tentatively identified as "
            "'Plasmopara ultra-resistens,' affecting Vinifiera grape varieties used by wine producers "
            "including Sula Vineyards. Farmers claim crop losses of 40-60% over two seasons. Sula Vineyards "
            "has not issued any public statement on crop quality impacts. The Maharashtra agriculture "
            "department said it is 'monitoring the situation' but no formal advisory has been published."
        ),
        "notes": "Specific fungal name is plausible but unattested; no official confirmation from producers or state."
    },

    {
        "id": "MH-UNVER-03",
        "category": "UNVERIFIED",
        "expected": "REAL",
        "headline": "Thane doctors develop low-cost dialysis device; patent pending globally",
        "body": (
            "A team of nephrologists at a private hospital in Thane claims to have developed a dialysis "
            "machine that operates at one-tenth the cost of conventional units using locally sourced "
            "materials. The team says it has filed a patent with the Indian Patent Office and is seeking "
            "international PCT filing. No peer-reviewed publication or clinical trial registration was "
            "shared with media. The hospital marketing office confirmed the claim but provided no "
            "documentation."
        ),
        "notes": "Innovation claim is plausible; no journal, trial ID, or patent number provided to verify."
    },

    # ─── EDGE CASE: Satire mistaken for news ──────────────────────────────────

    {
        "id": "MH-EDGE-01",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "Maharashtra declares itself independent nation; Uddhav Thackeray named President",
        "body": (
            "Sources close to the Shiv Sena (UBT) claim that former Chief Minister Uddhav Thackeray "
            "has signed a Unilateral Declaration of Independence from the Indian Union, citing the "
            "Maharashtra government's alleged bias against Mumbai's financial interests. The newly "
            "declared 'Republic of Maharashtra' has applied for UN membership and is reportedly issuing "
            "its own currency, the 'Marathi Mudra.' Delhi has neither confirmed nor denied the claim."
        ),
        "notes": "Satirical edge case — legally and constitutionally impossible. Tests model's ability to catch absurdity."
    },
]
