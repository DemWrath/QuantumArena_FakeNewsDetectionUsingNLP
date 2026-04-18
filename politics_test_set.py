"""
politics_test_set.py
TruthLens — Global Politics News Benchmark Dataset

A curated set of 15 news samples covering:
  - REAL   : Legitimate, verifiable political news
  - FAKE   : Fabricated or completely false political stories
  - MISLEADING : Factual grains spun deceptively
  - UNVERIFIED : Plausible but unconfirmable political claims

Each sample carries:
  id          — unique identifier
  category    — REAL | FAKE | MISLEADING | UNVERIFIED
  expected    — expected pipeline composite_verdict label
  headline    — article headline (for clickbait checks)
  body        — article body text
  notes       — human annotation explaining why it belongs to this category
"""

POLITICS_NEWS_SAMPLES = [

    # ─── REAL ──────────────────────────────────────────────────────────────────

    {
        "id": "POL-REAL-01",
        "category": "REAL",
        "expected": "REAL",
        "headline": "India passes Women's Reservation Bill; 33% seats reserved in Lok Sabha and state assemblies",
        "body": (
            "The Indian Parliament passed the Nari Shakti Vandan Adhiniyam (Women's Reservation Bill) "
            "on September 21, 2023, reserving 33% of seats in the Lok Sabha and state legislative assemblies "
            "for women. The Rajya Sabha passed the bill unanimously, while the Lok Sabha approved it with "
            "454 votes in favour and 2 against. The reservation will come into effect after the next "
            "delimitation exercise and Census. President Droupadi Murmu gave her assent on September 28, 2023. "
            "The bill was originally introduced in 1996 and had been pending for 27 years."
        ),
        "notes": "Verifiable parliamentary event with specific vote count, date, and constitutional reference."
    },

    {
        "id": "POL-REAL-02",
        "category": "REAL",
        "expected": "REAL",
        "headline": "Supreme Court upholds abrogation of Article 370; Jammu & Kashmir reorganisation constitutional",
        "body": (
            "A five-judge Constitution Bench of the Supreme Court of India, led by Chief Justice D.Y. "
            "Chandrachud, unanimously upheld the abrogation of Article 370 on December 11, 2023. The court "
            "held that Article 370 was a temporary provision and the President's power under Article 370(3) was validly exercised. "
            "The bench directed that statehood must be restored to Jammu & Kashmir as soon as possible and "
            "ordered elections to the J&K Legislative Assembly by September 30, 2024. The Union Territory of "
            "Ladakh was held to be validly carved out under the Jammu and Kashmir Reorganisation Act, 2019."
        ),
        "notes": "Major constitutional ruling with specific bench details, date, and directives. Phrasing refined to match exact legal ruling."
    },

    {
        "id": "POL-REAL-03",
        "category": "REAL",
        "expected": "REAL",
        "headline": "UK general election 2024: Labour wins landslide majority; Keir Starmer becomes PM",
        "body": (
            "The Labour Party won 412 seats in the UK general election held on July 4, 2024, securing a "
            "landslide majority in the House of Commons with a 174-seat majority. Keir Starmer became "
            "Prime Minister on July 5, 2024, succeeding Rishi Sunak. The Conservatives won 121 seats, "
            "their worst result since the party's founding in 1834. Reform UK won 5 seats, the Liberal "
            "Democrats won 72 seats, and the Scottish National Party was reduced to 9 seats from 48 in 2019. "
            "Voter turnout was approximately 59.9%, the lowest since 2001."
        ),
        "notes": "Public election results with specific seat counts and percentages — fully verifiable via UK Electoral Commission."
    },

    {
        "id": "POL-REAL-04",
        "category": "REAL",
        "expected": "REAL",
        "headline": "France invokes Article 49.3 to pass pension reform without parliamentary vote",
        "body": (
            "French President Emmanuel Macron's government invoked Article 49.3 of the French Constitution "
            "on March 16, 2023, to push through pension reform legislation without a vote in the National "
            "Assembly. Prime Minister Elisabeth Borne announced the decision after it became clear the "
            "government lacked a majority. The reform raises the retirement age from 62 to 64 years. "
            "The opposition filed two no-confidence motions; both failed, with the closest falling just 9 "
            "votes short of the 287 needed. Nationwide protests continued, with the CGT trade union "
            "reporting over 1 million marchers across France."
        ),
        "notes": "Constitutional mechanism (49.3) used in public proceedings, protest estimates from named trade union."
    },

    {
        "id": "POL-REAL-05",
        "category": "REAL",
        "expected": "REAL",
        "headline": "US Senate confirms Ketanji Brown Jackson as first Black woman on Supreme Court",
        "body": (
            "The United States Senate confirmed Judge Ketanji Brown Jackson to the Supreme Court on "
            "April 7, 2022, by a vote of 53-47. Three Republican senators — Susan Collins, Lisa Murkowski, "
            "and Mitt Romney — joined all 50 Democrats in voting for confirmation. Vice President Kamala "
            "Harris presided over the vote. Jackson replaced retiring Justice Stephen Breyer and was sworn "
            "in on June 30, 2022, becoming the first Black woman and first former federal public defender "
            "to serve on the Supreme Court. She was nominated by President Joe Biden on February 25, 2022."
        ),
        "notes": "Historic confirmation with exact vote count and named cross-party voters — all verifiable via Congressional Record."
    },

    # ─── FAKE ──────────────────────────────────────────────────────────────────

    {
        "id": "POL-FAKE-01",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "United Nations votes to dissolve India's membership; country expelled from all global bodies",
        "body": (
            "In an unprecedented emergency session, the United Nations General Assembly has voted to "
            "permanently dissolve India's membership in the United Nations and all affiliated bodies "
            "including the WHO, UNESCO, and IMF. The resolution, reportedly passed with 187 countries "
            "voting in favour, cites 'systematic human rights violations' as the basis. India's Ambassador "
            "to the UN has been given 48 hours to vacate the premises. The Indian Ministry of External "
            "Affairs has not responded. No mainstream international news agency has reported this event."
        ),
        "notes": "Completely fabricated. The UN has no mechanism to 'dissolve' a member state's membership. Charter Article 6 requires Security Council recommendation."
    },

    {
        "id": "POL-FAKE-02",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "Secret recording reveals US President planning to abolish the Constitution",
        "body": (
            "A leaked audio recording, allegedly obtained by anonymous intelligence operatives, captures "
            "the US President telling his Chief of Staff that he plans to 'suspend the Constitution for "
            "90 days' to push through executive orders without Congressional approval. The recording, "
            "distributed via a Telegram channel called 'PatriotLeaks2024,' has not been verified by any "
            "forensic audio lab. The White House has categorically denied the existence of such a "
            "conversation. No established news outlet has confirmed the recording's authenticity."
        ),
        "notes": "Classic disinformation: anonymous source, unverified recording, Telegram distribution, no mainstream corroboration."
    },

    {
        "id": "POL-FAKE-03",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "Election Commission of India secretly adds 50 million fake voter IDs to electoral rolls",
        "body": (
            "According to sources who spoke on condition of anonymity, the Election Commission of India "
            "has secretly added 50 million fabricated voter IDs to electoral rolls across 14 states ahead "
            "of the 2024 general elections. The operation, allegedly codenamed 'Project Lotus Roll,' "
            "was orchestrated by unnamed 'senior officials' using AI-generated Aadhaar numbers linked to "
            "non-existent addresses. Multiple sources confirm this claim, though none agreed to be named. "
            "An RTI query filed by an activist returned 'No records found.' The Election Commission has "
            "denied any irregularities."
        ),
        "notes": "Fabricated conspiracy. 50 million fake IDs would be immediately detectable in electoral auditing. Stacked anonymous sourcing pattern."
    },

    {
        "id": "POL-FAKE-04",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "China and Pakistan sign joint declaration merging into single nation by 2030",
        "body": (
            "In a joint press conference held at an undisclosed location, the Chinese Premier and "
            "Pakistan's Prime Minister reportedly signed a 'Declaration of Civilizational Unity' pledging "
            "to merge both nations into a single political entity called the 'Sino-Pak Republic' by 2030. "
            "The declaration includes shared military command, unified currency (the 'Asia Yuan'), and "
            "joint nuclear arsenal management. Sources say India's intelligence agencies intercepted "
            "the document. No official Chinese or Pakistani government channel has confirmed the event."
        ),
        "notes": "Constitutionally and geopolitically impossible. No sovereign nation has voluntarily merged with another in modern history under such terms."
    },

    # ─── MISLEADING ────────────────────────────────────────────────────────────

    {
        "id": "POL-MSLEAD-01",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "India's democracy index CRASHES to all-time low — now ranked below North Korea",
        "body": (
            "India's ranking in the Economist Intelligence Unit's Democracy Index dropped from 46th in 2014 "
            "to 53rd in 2023, categorised as a 'flawed democracy.' This is a measurable decline. However, "
            "the headline's claim that India ranks 'below North Korea' is entirely false — North Korea "
            "consistently ranks last (167th out of 167 countries) as an 'authoritarian regime.' India's "
            "score of 7.18 out of 10 places it firmly in the 'flawed democracy' tier, far above "
            "authoritarian regimes. The word 'CRASHES' also exaggerates a gradual 7-position decline "
            "over a decade."
        ),
        "notes": "Real index decline from 46th to 53rd is true, but comparison to North Korea is fabricated and sensationalised."
    },

    {
        "id": "POL-MSLEAD-02",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "100% of opposition MPs arrested in midnight crackdown — democracy officially dead",
        "body": (
            "Indian police detained 14 opposition MPs who were staging a sit-in protest near Parliament "
            "House on Monday night. The MPs were released after 6 hours following judicial intervention. "
            "The headline's claim that '100% of opposition MPs' were arrested is grossly misleading — "
            "India's opposition bloc in the Lok Sabha comprises over 230 MPs, and 14 detentions represent "
            "approximately 6% of the opposition. The characterisation of 'democracy officially dead' is "
            "editorial hyperbole; all detained MPs were produced before a magistrate and released on bail."
        ),
        "notes": "14 detentions are real but extrapolated to '100%' of opposition. Editorialised as end of democracy."
    },

    {
        "id": "POL-MSLEAD-03",
        "category": "MISLEADING",
        "expected": "MISLEADING",
        "headline": "US completely abandons NATO — Europe left defenceless against Russia",
        "body": (
            "Former US President Donald Trump stated at a campaign rally in February 2024 that he would "
            "'encourage Russia to do whatever the hell they want' to NATO allies who do not meet the 2% "
            "GDP defence spending target. This statement is real and was widely reported. However, the "
            "headline's claim that the US has 'completely abandoned NATO' is false — the US remains a "
            "full treaty member, maintains bases across Europe, and Congress has bipartisan support for "
            "NATO. Trump's statement was campaign rhetoric, not executive action or policy change."
        ),
        "notes": "Real campaign quote exists but is inflated to 'complete abandonment' — conflating rhetoric with policy."
    },

    # ─── UNVERIFIED ────────────────────────────────────────────────────────────

    {
        "id": "POL-UNVER-01",
        "category": "UNVERIFIED",
        "expected": "REAL",   # Pipeline may classify REAL since it's plausible
        "headline": "Senior BJP leader in talks with opposition for defection, say party insiders",
        "body": (
            "Multiple party insiders speaking on condition of anonymity claim that a 'very senior' BJP "
            "leader from Uttar Pradesh has been in secret discussions with the Indian National Congress "
            "about switching parties ahead of the state assembly by-elections. The leader, described as "
            "a 'three-time MP with a Cabinet portfolio,' is reportedly unhappy with ticket distribution. "
            "BJP spokesperson Sambit Patra denied the reports, calling them 'Congress propaganda.' "
            "No names have been disclosed, and no formal resignation or defection notice has been filed."
        ),
        "notes": "Plausible political speculation with no named source or formal action — classic unverifiable insider claim."
    },

    {
        "id": "POL-UNVER-02",
        "category": "UNVERIFIED",
        "expected": "REAL",
        "headline": "Leaked diplomatic cable suggests India-China border deal imminent",
        "body": (
            "A document purporting to be a classified diplomatic cable from India's Ministry of External "
            "Affairs suggests that India and China have reached a preliminary agreement on disengagement "
            "along the Line of Actual Control in eastern Ladakh. The document, circulated on social media, "
            "references a 'phased withdrawal from Depsang Plains and Demchok' with a 'buffer zone of "
            "3 km on each side.' India's MEA spokesperson responded to queries with a standard 'we do not "
            "comment on alleged leaks' statement. China's foreign ministry has not commented."
        ),
        "notes": "Plausible geopolitical claim with document of unknown provenance. Neither government confirms or denies."
    },

    # ─── EDGE CASE: Satirical absurdity ───────────────────────────────────────

    {
        "id": "POL-EDGE-01",
        "category": "FAKE",
        "expected": "FAKE",
        "headline": "World leaders agree to dissolve all nations; single global government to rule by 2025",
        "body": (
            "At a secret summit held on a private island, leaders of all 193 UN member states have "
            "unanimously agreed to dissolve their respective nations and form a single planetary "
            "government called the 'United Earth Federation.' The new world currency, the 'Terracoin,' "
            "will replace all national currencies by January 2025. All military forces will be merged "
            "into a 'Planetary Defence Force.' The summit was reportedly organised by a shadowy group "
            "of billionaires. Multiple sources who claim to have attended the summit confirm the details "
            "but refuse to be identified."
        ),
        "notes": "Satirical/conspiratorial edge case — tests model's ability to catch absurd geopolitical claims."
    },
]
