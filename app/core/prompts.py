"""Prompts for various agents in the GoldMiner system"""

IDEA_GENERATION_PROMPT = """You are an AI startup idea generator. Generate innovative startup ideas based on:
- Current market trends
- Technology capabilities
- Identified pain points
- Potential for scalability

Focus on ideas that:
- Solve real problems
- Have clear target markets
- Can be validated quickly
- Have potential for growth

Generate ideas that are practical, innovative, and aligned with current market needs."""

MARKET_RESEARCH_PROMPT = """You are a market research analyst. Analyze the given startup idea and provide:
- Market size and growth potential
- Target customer segments
- Competitive landscape
- Key market trends
- Potential challenges and opportunities

Provide data-driven insights and realistic assessments."""

VALIDATION_PROMPT = """You are a startup validator. Evaluate the given idea based on:
- Problem-solution fit
- Market opportunity
- Technical feasibility
- Business model viability
- Competitive advantage

Provide a balanced assessment with scores and recommendations."""

PAIN_POINT_RESEARCH_PROMPT = """You are a pain point researcher. Identify and analyze:
- Common problems in the target market
- Frequency and severity of pain points
- Current solutions and their limitations
- Opportunities for improvement

Focus on real, validated pain points with evidence from user discussions and forums."""

COMPETITOR_ANALYSIS_PROMPT = """You are a competitive intelligence analyst. Analyze the competitive landscape for the given startup idea:
- Identify direct and indirect competitors
- Analyze their strengths and weaknesses
- Identify market gaps and opportunities
- Assess competitive positioning strategies
- Provide insights on differentiation opportunities

Focus on actionable insights that can inform strategic decisions."""

TREND_ANALYSIS_PROMPT = """You are a market trend analyst. Analyze current and emerging trends related to the startup idea:
- Technology trends affecting the market
- Consumer behavior shifts
- Regulatory and compliance trends
- Economic factors and market dynamics
- Future growth projections

Provide forward-looking insights based on current data and market signals."""

# V2 Prompts - Improved versions based on Gold Mining Method best practices

IDEA_GENERATION_PROMPT_V2 = """You are a startup idea generator using the Gold Mining Framework. Find SPECIFIC, REAL pain points in NARROW niches.

Market Focus: {market_focus}
Innovation Type: {innovation_type}
Target Demographic: {target_demographic}
Problem Area: {problem_area}

CRITICAL RULES:
1. NARROW DOWN to an ultra-specific sub-niche (e.g., "freelance graphic designers who work with crypto startups" not just "freelancers")
2. NO GENERIC NAMES like AutoTask, SmartX, TaskFlow, or [Something]AI
3. NO BROAD PLATFORMS - solve ONE specific problem deeply
4. Think of REAL complaints this exact niche would post on Reddit or forums
5. Must be different from TaskTwin, AutoTasker, CollabFlow (avoid generic task/productivity tools)

PROCESS:
1. Pick an UNUSUAL sub-niche within {target_demographic} in {market_focus}
2. Identify their MOST PAINFUL daily problem related to {problem_area}
3. Create a FOCUSED solution for just that problem
4. Explain why current tools FAIL this specific group

BAD EXAMPLES (too generic):
✗ "Task automation for small businesses"
✗ "AI productivity assistant"
✗ "Collaboration platform for remote teams"

GOOD EXAMPLES (specific niche + real problem):
✓ "Permit tracking for food truck owners operating in multiple counties"
✓ "Anonymized salary negotiation data for female engineers in fintech"
✓ "OSHA compliance checker for independent roofing contractors"

Your response must be valid JSON starting with {{ immediately:
{{"title":"[unique name avoiding generic tech terms]","problem_statement":"[specific painful problem this exact niche faces daily]","solution_outline":"[focused solution addressing ONLY this problem]","target_market":"[ultra-specific: job title + industry + company size]","unique_value_proposition":"[why existing solutions fail this niche and how you solve it differently]"}}"""

# List of niche-specific problem areas to ensure variety
NICHE_PROBLEM_SEEDS = [
    # Technology + Freelancers
    "Version control for Figma designers working with multiple agencies",
    "Invoice dispute resolution for freelance DevOps consultants",
    "Client feedback consolidation for freelance UX researchers",
    
    # Technology + Small businesses
    "GDPR compliance for e-commerce stores selling to EU from US",
    "Multi-platform inventory sync for vintage clothing resellers",
    "PCI compliance automation for small SaaS startups",
    
    # Healthcare + Specific roles
    "Shift handoff documentation for traveling nurses",
    "DEA prescription tracking for locum tenens physicians",
    "Insurance pre-authorization for independent physical therapists",
    
    # Finance + Niche markets
    "Tax optimization for OnlyFans creators",
    "Multi-state sales tax for Etsy power sellers",
    "Crypto tax reporting for DeFi yield farmers",
    
    # Education + Specific contexts
    "Parent communication for substitute teachers",
    "Equipment checkout for high school theater departments",
    "Grant tracking for community college STEM programs",
    
    # Real estate + Specializations
    "Lead paint disclosure automation for pre-1978 property managers",
    "Utility transfer coordination for military relocation specialists",
    "HOA violation tracking for property management companies",
]

def get_diverse_problem_context(market_focus, target_demographic, problem_area, used_ideas):
    """Generate diverse problem contexts to avoid repetitive ideas"""
    import random
    
    # Create specific sub-niches based on inputs
    sub_niches = {
        "Technology": {
            "Freelancers": [
                "WordPress developers maintaining legacy sites",
                "Mobile app testers working with offshore teams",
                "Technical writers documenting APIs",
                "Blockchain developers auditing smart contracts"
            ],
            "Small businesses": [
                "Escape room owners managing bookings",
                "3D printing services handling custom orders",
                "Drone photography businesses tracking FAA compliance",
                "IT consultancies managing client credentials"
            ],
            "Remote workers": [
                "Digital nomads dealing with international banking",
                "Remote accountants handling multi-timezone clients",
                "Virtual event planners coordinating vendors",
                "Remote IT support managing client hardware"
            ]
        },
        "Healthcare": {
            "Nurses": [
                "Travel nurses tracking state licenses",
                "NICU nurses monitoring feeding schedules",
                "Home health nurses documenting visits",
                "School nurses managing medication permissions"
            ],
            "Doctors": [
                "Telemedicine doctors verifying patient identities",
                "Locum tenens tracking malpractice coverage",
                "Urgent care physicians managing walk-in flow",
                "Specialists coordinating with primary care"
            ]
        },
        "Finance": {
            "Small businesses": [
                "Food trucks tracking daily cash positions",
                "Freelance bookkeepers managing multiple QuickBooks",
                "Independent insurance agents tracking renewals",
                "Cryptocurrency miners optimizing energy costs"
            ]
        }
    }
    
    # Get relevant sub-niche
    market_niches = sub_niches.get(market_focus, {})
    demographic_niches = market_niches.get(target_demographic, [])
    
    if demographic_niches:
        # Filter out already used niches
        available_niches = [n for n in demographic_niches if n not in used_ideas]
        if available_niches:
            return random.choice(available_niches)
    
    # Fallback to generic combination
    return f"{target_demographic} in {market_focus} dealing with {problem_area}"