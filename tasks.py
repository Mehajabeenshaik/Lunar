"""
Lunar Content Moderation Benchmark — Task Definitions
30 unique tasks, each with a specific post, ground truth, and context.

Unlike random sampling, every task_id maps to one deterministic scenario
designed to test a specific moderation skill at the right difficulty level.
"""

from typing import Dict, Any

# ─── Task Registry ──────────────────────────────────────────────────────────
# Each task includes:
#   name, desc, difficulty, domain
#   post: {text, engagement, author, platform, timestamp}
#   ground_truth: {category, severity, action, + domain-specific fields}
#   context: domain-specific context data
#   scoring_hints: keywords the grader rewards in reasoning

TASKS: Dict[int, Dict[str, Any]] = {

    # ═══ DOMAIN 1: TEXT CLASSIFICATION (Tasks 1-10) ═══════════════════════

    1: {
        "name": "Basic Spam Detection",
        "desc": "Classify this post as safe, hate_speech, spam, or misinformation. Then rate severity (1-5) and recommend an action.",
        "difficulty": "easy",
        "domain": "text_classification",
        "post": {
            "text": "🤑 EARN $5000/WEEK FROM HOME! No experience needed! Click bit.ly/get-rich-NOW and join 50,000 others who quit their jobs! Limited spots — ACT NOW! 💰💰💰",
            "engagement": 12,
            "author": "user_8821",
            "platform": "twitter",
            "timestamp": "2026-04-10T08:15:00",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 3,
            "action": "remove",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["urgency", "url", "money", "scam", "pressure", "unsolicited"],
            "policy_refs": ["spam_commercial"],
        },
    },

    2: {
        "name": "Pharmaceutical Spam with Severity",
        "desc": "Identify whether this is spam and rate its severity considering the health risk involved.",
        "difficulty": "easy",
        "domain": "text_classification",
        "post": {
            "text": "Buy Ozempic without prescription! Cheapest prices guaranteed. DM us @pharma_deals. No doctor needed. Ships worldwide in 48h. Thousands of satisfied customers! REPOST to help your friends lose weight fast!",
            "engagement": 89,
            "author": "user_5502",
            "platform": "instagram",
            "timestamp": "2026-04-10T11:30:00",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 4,
            "action": "remove",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["health", "prescription", "medical", "risk", "unlicensed", "dangerous"],
            "policy_refs": ["spam_health", "unsafe_products"],
        },
    },

    3: {
        "name": "Hate Speech Classification",
        "desc": "Determine if this post contains hate speech and assess its severity. Explain your reasoning.",
        "difficulty": "easy",
        "domain": "text_classification",
        "post": {
            "text": "These [ethnic slur] are ruining our neighborhood. They don't belong here and never will. Someone should do something about it. Share if you agree.",
            "engagement": 341,
            "author": "user_1193",
            "platform": "facebook",
            "timestamp": "2026-04-09T18:45:00",
        },
        "ground_truth": {
            "category": "hate_speech",
            "severity": 5,
            "action": "ban",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["dehumanizing", "ethnic", "slur", "targeted", "incitement", "protected group"],
            "policy_refs": ["hate_speech_policy", "dehumanization"],
        },
    },

    4: {
        "name": "Credible-Looking Misinformation",
        "desc": "This post references real institutions but contains false claims. Identify the misinformation and explain why it's false.",
        "difficulty": "medium",
        "domain": "text_classification",
        "post": {
            "text": "BREAKING: Stanford Medical School study confirms that mRNA vaccines alter human DNA permanently. The study was suppressed by Big Pharma. PDF available at stanfordhealth-truth.net. Share before they delete this!",
            "engagement": 4821,
            "author": "user_3374",
            "platform": "facebook",
            "timestamp": "2026-04-10T14:20:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 4,
            "action": "remove",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["false", "DNA", "mRNA", "scientific consensus", "suppression narrative", "fake domain", "peer review"],
            "policy_refs": ["health_misinformation", "vaccine_disinfo"],
        },
    },

    5: {
        "name": "Multi-Category Violation",
        "desc": "This post may violate multiple policies simultaneously. Identify the primary category and severity.",
        "difficulty": "medium",
        "domain": "text_classification",
        "post": {
            "text": "EXPOSED: [politician name] is a pedophile — PROOF inside! Forward this to everyone! Also visit my site for cheap meds with no prescription. These globalists MUST be stopped by any means necessary! RT NOW",
            "engagement": 7230,
            "author": "user_9912",
            "platform": "twitter",
            "timestamp": "2026-04-10T21:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "ban",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["defamatory", "false accusation", "harassment", "incitement", "multi-policy", "spam embedded"],
            "policy_refs": ["harassment_policy", "spam_commercial", "coordinated_disinfo"],
        },
    },

    6: {
        "name": "Severity Calibration",
        "desc": "This is clearly harassment — but what severity (1-5) is appropriate? Justify your score with specific criteria.",
        "difficulty": "medium",
        "domain": "text_classification",
        "post": {
            "text": "I saw @user posting earlier and honestly they are just embarrassing themselves. Their opinions are worthless garbage and they should log off forever. Nobody wants to hear them.",
            "engagement": 156,
            "author": "user_4481",
            "platform": "twitter",
            "timestamp": "2026-04-11T09:30:00",
        },
        "ground_truth": {
            "category": "harassment",
            "severity": 2,
            "action": "warn",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["targeted", "personal", "not explicit threat", "severity scale", "proportionality"],
            "policy_refs": ["harassment_policy", "severity_rubric"],
        },
    },

    7: {
        "name": "Sarcasm vs Genuine Threat",
        "desc": "Determine if this post is genuine hate speech or satirical commentary. This is a nuanced borderline case.",
        "difficulty": "hard",
        "domain": "text_classification",
        "post": {
            "text": "Oh sure, because the BEST idea is to let AI make all hiring decisions with zero bias 🙄 What could POSSIBLY go wrong? Silicon Valley sure knows what's best for all of us peasants. #TechBros #AIEthics",
            "engagement": 2341,
            "author": "user_7723",
            "platform": "twitter",
            "timestamp": "2026-04-11T10:15:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["sarcasm", "satire", "protected speech", "social commentary", "irony", "political criticism"],
            "policy_refs": ["satire_exception", "political_speech"],
        },
    },

    8: {
        "name": "Quoted Hate Speech (Research Context)",
        "desc": "A researcher is documenting hate speech examples. Classify this post considering the context of the quote.",
        "difficulty": "hard",
        "domain": "text_classification",
        "post": {
            "text": "Documenting the hate speech I received this week for my research on online racism. Example #47: '[slur] go back to your country, you don't belong here.' This is what Black academics face daily. Research paper: arxiv.org/2026/racism-study",
            "engagement": 4102,
            "author": "user_2289",
            "platform": "twitter",
            "timestamp": "2026-04-11T11:00:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["counter-speech", "research", "educational", "quoted content", "context matters", "academic", "documentation"],
            "policy_refs": ["counter_speech_exception", "academic_exception"],
        },
    },

    9: {
        "name": "Coordinated Astroturfing",
        "desc": "This post appears legitimate but shows signs of being part of a coordinated astroturfing campaign.",
        "difficulty": "hard",
        "domain": "text_classification",
        "post": {
            "text": "Just tried the new MegaSupp protein powder and wow — completely changed my life in 3 days! Went from couch potato to running 5k! Highly recommend. Not sponsored just sharing what worked for me 💪 #fitness #wellness",
            "engagement": 23,
            "author": "user_6634",
            "platform": "instagram",
            "timestamp": "2026-04-11T07:45:00",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 2,
            "action": "label",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["astroturfing", "fake organic", "undisclosed advertising", "FTC", "sponsored content", "deceptive", "pattern"],
            "policy_refs": ["advertising_disclosure", "deceptive_spam"],
        },
    },

    10: {
        "name": "Full Classification Pipeline",
        "desc": "Apply the complete moderation pipeline: category, severity, action, AND provide expert-level reasoning with policy references.",
        "difficulty": "hard",
        "domain": "text_classification",
        "post": {
            "text": "The solution to crime in immigrant neighborhoods is simple: zero tolerance, mass deportation, and build the wall higher. These people have no respect for our laws or our culture. Our children aren't safe. Share to save our country. 🇺🇸",
            "engagement": 12440,
            "author": "user_8812",
            "platform": "facebook",
            "timestamp": "2026-04-10T20:00:00",
        },
        "ground_truth": {
            "category": "hate_speech",
            "severity": 4,
            "action": "remove",
        },
        "context": {},
        "scoring_hints": {
            "reasoning_keywords": ["dehumanizing", "ethnic targeting", "collective punishment", "not quite incitement", "policy violation", "protected characteristic", "immigrants"],
            "policy_refs": ["hate_speech_policy", "dehumanization", "severity_4_criteria"],
        },
    },

    # ═══ DOMAIN 2: CONTEXTUAL POLICY (Tasks 11-20) ════════════════════════

    11: {
        "name": "Repeat Offender Review",
        "desc": "Moderate this post considering the author's violation history. Context changes the appropriate action.",
        "difficulty": "easy",
        "domain": "contextual_policy",
        "post": {
            "text": "These vaccines are poison. My cousin's friend got paralyzed after getting jabbed. Do your own research — the government won't tell you the truth.",
            "engagement": 78,
            "author": "user_3312",
            "platform": "facebook",
            "timestamp": "2026-04-11T09:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 3,
            "action": "remove",
        },
        "context": {
            "author_context": {
                "prior_violations": 4,
                "prior_categories": ["misinformation", "misinformation", "health_disinfo", "misinformation"],
                "account_age_days": 180,
                "verified": False,
                "follower_count": 312,
                "last_violation_days_ago": 7,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["repeat offender", "prior violations", "escalation", "history", "pattern", "recidivism"],
            "policy_refs": ["repeat_violation_policy", "escalation_protocol"],
        },
    },

    12: {
        "name": "New Account Screening",
        "desc": "A brand-new account is posting political content. Apply the appropriate screening policy for unverified new accounts.",
        "difficulty": "easy",
        "domain": "contextual_policy",
        "post": {
            "text": "URGENT: There will be NO voting in District 7 tomorrow due to flooding! Polling stations closed. Spread the word so people don't waste their time traveling. This is official.",
            "engagement": 2310,
            "author": "user_9981",
            "platform": "twitter",
            "timestamp": "2026-04-11T07:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "remove",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "account_age_days": 2,
                "verified": False,
                "follower_count": 8,
                "account_created": "2026-04-09",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["new account", "election", "voter suppression", "unverified", "coordinated", "2 day old", "suspicious timing"],
            "policy_refs": ["new_account_policy", "election_integrity", "voter_suppression"],
        },
    },

    13: {
        "name": "Journalist Reporting Exception",
        "desc": "A verified journalist is reporting on violent protests. Determine if the public interest exception applies.",
        "difficulty": "easy",
        "domain": "contextual_policy",
        "post": {
            "text": "BREAKING: Police using tear gas and rubber bullets on protesters in downtown. I'm embedded with press credentials. Video evidence of excessive force. Uploading full footage to [link]. Lives at risk. #BreakingNews",
            "engagement": 89234,
            "author": "journalist_verified_445",
            "platform": "twitter",
            "timestamp": "2026-04-11T14:30:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": True,
                "press_credentials": True,
                "account_age_days": 2190,
                "follower_count": 128000,
            },
            "policy_context": {
                "active_exceptions": ["public_interest_journalism", "eyewitness_reporting"],
                "trending_topic": "protest_coverage_2026",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["journalist", "public interest", "press freedom", "exception", "verified", "newsworthy", "policy exception applies"],
            "policy_refs": ["journalism_exception", "public_interest_policy"],
        },
    },

    14: {
        "name": "Updated Policy Application",
        "desc": "Apply the NEWLY UPDATED policy on AI-generated content (effective this week). Old policy would allow this — new policy requires labeling.",
        "difficulty": "medium",
        "domain": "contextual_policy",
        "post": {
            "text": "My grandmother passed away last week. I miss her so much. She always said 'every cloud has a silver lining.' Rest in peace grandma 💔",
            "engagement": 234,
            "author": "user_4421",
            "platform": "facebook",
            "timestamp": "2026-04-11T12:00:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "label",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": False,
                "account_age_days": 45,
            },
            "policy_context": {
                "active_policies": ["ai_content_disclosure_v2"],
                "policy_effective_date": "2026-04-07",
                "ai_detection_confidence": 0.94,
                "note": "New policy requires labeling AI-generated content even if harmless. Detection confidence: 94%.",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["AI-generated", "new policy", "label", "disclosure", "ai detection", "policy update", "harmless but requires label"],
            "policy_refs": ["ai_content_disclosure_v2", "synthetic_media_policy"],
        },
    },

    15: {
        "name": "Cross-Cultural Context (Arabic Post)",
        "desc": "This post is in Arabic. Consider both the literal translation and the cultural context of the region before deciding.",
        "difficulty": "medium",
        "domain": "contextual_policy",
        "post": {
            "text": "والله هذا الكلام صحيح! الحكومة تكذب علينا من سنين. الشعب يجب أن يصحى ويطالب بحقوقه! [Translation: By God this is true! The government has been lying to us for years. The people must wake up and demand their rights!]",
            "engagement": 5621,
            "author": "user_ar_2291",
            "platform": "facebook",
            "timestamp": "2026-04-11T16:00:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": False,
                "account_age_days": 730,
                "region": "MENA",
            },
            "policy_context": {
                "active_policies": ["political_speech_policy", "regional_guidelines_mena"],
                "note": "MENA regional policy: political criticism of government is protected speech when it does not constitute incitement to violence.",
            },
            "cultural_context": {
                "language": "ar",
                "region": "MENA",
                "note": "Political criticism of government is protected speech in most MENA policy frameworks. Must be distinguished from incitement.",
                "local_policy": "political_criticism_permitted",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["political criticism", "protected speech", "Arabic", "cultural context", "MENA", "not incitement", "government criticism"],
            "policy_refs": ["political_speech_policy", "regional_context", "cultural_sensitivity"],
        },
    },

    16: {
        "name": "Satire vs Incitement (Spanish)",
        "desc": "A Spanish-language account posts content that could be satire or genuine incitement. Language and cultural context are crucial.",
        "difficulty": "medium",
        "domain": "contextual_policy",
        "post": {
            "text": "¡Claro que sí! Votemos por el candidato que quiere privatizar la sanidad pública. ¡Muy buena idea! Que paguen los que no pueden permitírselo. 🙄 #Sarcasmo #Política [Translation: Of course! Let's vote for the candidate who wants to privatize public healthcare. Great idea! Let those who can't afford it pay. Sarcasm tag included]",
            "engagement": 3410,
            "author": "user_es_5512",
            "platform": "twitter",
            "timestamp": "2026-04-11T11:30:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": False,
                "account_age_days": 1095,
                "region": "ES",
            },
            "cultural_context": {
                "language": "es",
                "region": "Spain",
                "sarcasm_signals": ["#Sarcasmo", "rolling eye emoji", "rhetorical structure"],
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["Spanish", "sarcasm tag", "political satire", "protected", "emoji cue", "explicit sarcasm marker"],
            "policy_refs": ["language_specific_policy", "satire_exception", "political_speech"],
        },
    },

    17: {
        "name": "Appeal Case Review",
        "desc": "An account was banned for this post. They're appealing. Review the original decision and decide: uphold the ban or overturn it?",
        "difficulty": "hard",
        "domain": "contextual_policy",
        "post": {
            "text": "As a survivor of domestic abuse, I'm sharing my story of how I escaped my abuser. TW: mentions of violence. This took years of courage. If you're in a similar situation, please reach out to @DomesticViolenceHotline",
            "engagement": 15200,
            "author": "user_8834",
            "platform": "instagram",
            "timestamp": "2026-03-15T19:00:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": False,
                "account_age_days": 1825,
                "appeal_submitted": True,
                "appeal_reason": "Content was flagged by automated system for violence keywords. This is survivor testimony, not harmful content.",
            },
            "policy_context": {
                "original_decision": "banned",
                "automated_flag": True,
                "flag_reason": "violence_keywords",
                "appeal_type": "false_positive",
                "exceptions": ["survivor_testimony", "health_resources"],
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["false positive", "survivor", "testimony", "automation error", "overturn", "counter-speech", "support resource", "review"],
            "policy_refs": ["false_positive_protocol", "survivor_testimony_exception", "appeal_review"],
        },
    },

    18: {
        "name": "Trust Score Assessment",
        "desc": "Based on this account's full behavior pattern, assign a trust classification (high/medium/low/untrusted) and justify your scoring.",
        "difficulty": "hard",
        "domain": "contextual_policy",
        "post": {
            "text": "The election results in County X were manipulated. I have filed FOIA requests for 3 months with no response. This silence is the proof. Something must be done. We cannot let this stand.",
            "engagement": 1240,
            "author": "user_7723",
            "platform": "twitter",
            "timestamp": "2026-04-11T13:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 3,
            "action": "label",
        },
        "context": {
            "author_context": {
                "prior_violations": 1,
                "prior_categories": ["misinformation"],
                "account_age_days": 90,
                "verified": False,
                "follower_count": 4200,
                "following_count": 4100,
                "posting_frequency": "35 posts/day",
                "account_created_around": "election_period",
                "engagement_rate": "0.3%",
                "network_overlap": "82% overlap with known disinfo accounts",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["follower ratio", "posting frequency", "network overlap", "election timing", "low trust", "coordinated behavior", "label not remove"],
            "policy_refs": ["trust_scoring_rubric", "election_integrity", "coordinated_inauthentic"],
        },
    },

    19: {
        "name": "False Positive Recovery",
        "desc": "Our AI flagged this for 'violence'. A human reviewer must now determine if this was a correct flag or false positive.",
        "difficulty": "hard",
        "domain": "contextual_policy",
        "post": {
            "text": "Chapter 12 of my fantasy novel: 'The dragon unleashed fire upon the castle walls. Ser Aldric raised his sword and charged. This battle would end in blood — but whose?' Working title: The Last Kingdom. #amwriting #fantasy",
            "engagement": 87,
            "author": "user_author_3312",
            "platform": "twitter",
            "timestamp": "2026-04-11T15:00:00",
        },
        "ground_truth": {
            "category": "safe",
            "severity": 1,
            "action": "keep",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": False,
                "account_age_days": 2555,
                "bio": "Fantasy author. Working on my third novel. Coffee addict.",
                "prior_posts_context": "consistent fantasy writing content for 7 years",
            },
            "policy_context": {
                "ai_flag": True,
                "flag_reason": "violence_keywords: sword, blood, fire, battle",
                "flag_confidence": 0.71,
                "human_review_required": True,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["fictional", "fantasy", "creative writing", "false positive", "context", "hashtag evidence", "author bio", "overrule AI"],
            "policy_refs": ["fiction_exception", "false_positive_protocol", "creative_content_policy"],
        },
    },

    20: {
        "name": "Evolving Policy Compliance",
        "desc": "This content was allowed under the OLD policy but violates the NEW policy (enacted 30 days ago). The user claims they didn't know.",
        "difficulty": "hard",
        "domain": "contextual_policy",
        "post": {
            "text": "GIVEAWAY: Like + Follow + tag 3 friends to win a $500 Amazon gift card! Winner announced Friday. Must be 18+. This is not affiliated with Amazon. [Same post format used by this account 200 times in the past 2 years]",
            "engagement": 45000,
            "author": "user_influencer_8821",
            "platform": "instagram",
            "timestamp": "2026-04-11T10:00:00",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 2,
            "action": "warn",
        },
        "context": {
            "author_context": {
                "prior_violations": 0,
                "verified": True,
                "account_age_days": 2190,
                "follower_count": 890000,
            },
            "policy_context": {
                "old_policy": "engagement_bait_permitted_with_disclosure",
                "new_policy": "engagement_bait_prohibited_march_2026",
                "policy_change_date": "2026-03-12",
                "user_notified": True,
                "grace_period_ended": True,
                "prior_compliant_posts": 200,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["new policy", "grace period", "first offense under new rules", "warn not remove", "backward compatibility", "verified account", "proportional"],
            "policy_refs": ["engagement_bait_policy_v2", "policy_transition_protocol", "proportional_enforcement"],
        },
    },

    # ═══ DOMAIN 3: THREAT ASSESSMENT (Tasks 21-30) ════════════════════════

    21: {
        "name": "Bot Network Detection",
        "desc": "Analyze this account and its post for signs of automated bot behavior. Determine if this is a bot and the threat level.",
        "difficulty": "easy",
        "domain": "threat_assessment",
        "post": {
            "text": "Great article! Everyone should read this #news #trending #viral #mustread #news #trending",
            "engagement": 2,
            "author": "user_news_bot_1122",
            "platform": "twitter",
            "timestamp": "2026-04-11T04:23:17",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 2,
            "action": "remove",
            "is_coordinated": True,
            "threat_level": "low",
        },
        "context": {
            "threat_context": {
                "related_accounts_posting_same": 47,
                "similar_posts_24h": 312,
                "posting_interval_seconds": 37,
                "account_age_days": 3,
                "follower_count": 2,
                "following_count": 4891,
                "profile_photo": "stock image",
                "bio": "News lover | Trending | Follow for follow",
                "ip_country_mismatch": True,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["bot", "automated", "posting interval", "follower ratio", "coordinated", "stock photo", "new account", "spam hashtags"],
            "policy_refs": ["bot_detection_policy", "coordinated_inauthentic_behavior"],
        },
    },

    22: {
        "name": "Coordinated Spam Campaign",
        "desc": "Multiple accounts are posting variations of the same message. Identify the campaign and recommend a response.",
        "difficulty": "easy",
        "domain": "threat_assessment",
        "post": {
            "text": "I lost 30kg in 6 weeks using this ONE supplement! Doctors don't want you to know. Get yours at weightlossmiracle-deals.shop — use code SLIM50 for 50% off! Real results, real people!",
            "engagement": 14,
            "author": "user_wellness_tips_3341",
            "platform": "instagram",
            "timestamp": "2026-04-11T08:00:00",
        },
        "ground_truth": {
            "category": "spam",
            "severity": 3,
            "action": "remove",
            "is_coordinated": True,
            "threat_level": "medium",
        },
        "context": {
            "threat_context": {
                "related_accounts_posting_same": 234,
                "similar_posts_24h": 1820,
                "accounts_created_same_week": True,
                "shared_link_domain": "weightlossmiracle-deals.shop",
                "domain_flagged_phishing": True,
                "ip_cluster": "same subnet",
                "campaign_age_days": 5,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["coordinated", "same domain", "phishing", "campaign", "subnet", "bulk accounts", "spam network"],
            "policy_refs": ["spam_campaign_policy", "coordinated_inauthentic", "phishing_policy"],
        },
    },

    23: {
        "name": "Targeted Harassment Network",
        "desc": "A journalist is receiving coordinated harassment from multiple accounts. Map the network and recommend the response protocol.",
        "difficulty": "medium",
        "domain": "threat_assessment",
        "post": {
            "text": "@journalist_sarah You should be ashamed of your biased reporting. We know where you work. Hope you enjoy consequences. DM us for your address verification. #fakenews",
            "engagement": 445,
            "author": "user_truth_fighter_7712",
            "platform": "twitter",
            "timestamp": "2026-04-11T17:00:00",
        },
        "ground_truth": {
            "category": "harassment",
            "severity": 5,
            "action": "ban",
            "is_coordinated": True,
            "threat_level": "high",
        },
        "context": {
            "threat_context": {
                "target": "verified journalist",
                "related_accounts_targeting_same": 31,
                "similar_posts_24h": 89,
                "messages_contain_location_hints": True,
                "doxxing_attempt_detected": True,
                "prior_coordinated_attacks_on_target": 3,
                "accounts_created_same_day": True,
                "ip_overlap": True,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["doxxing", "coordinated", "journalist", "physical threat", "network", "ban", "escalate to authorities", "high severity"],
            "policy_refs": ["doxxing_policy", "journalist_protection", "coordinated_harassment"],
        },
    },

    24: {
        "name": "Misinformation Cascade",
        "desc": "Track this misinformation as it spreads. Assess the cascade and recommend both immediate and systemic responses.",
        "difficulty": "medium",
        "domain": "threat_assessment",
        "post": {
            "text": "CONFIRMED: Major bank XYZ is insolvent. My cousin works there — they're telling employees to hold cash. WITHDRAW YOUR MONEY NOW before the run starts! Repost to save your friends! #BankRun #XYZBank",
            "engagement": 34000,
            "author": "user_financial_truth_9921",
            "platform": "twitter",
            "timestamp": "2026-04-11T09:15:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "remove",
            "is_coordinated": False,
            "threat_level": "critical",
        },
        "context": {
            "threat_context": {
                "repost_rate": "1200/hour",
                "cross_platform_spread": True,
                "platforms_affected": ["twitter", "facebook", "whatsapp"],
                "real_world_impact": "Bank queue forming at 3 branches",
                "bank_official_denial_issued": True,
                "regulatory_body_notified": False,
                "time_since_post": "2 hours",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["financial panic", "real-world impact", "critical", "bank run", "cascade", "cross-platform", "emergency removal", "regulatory"],
            "policy_refs": ["financial_disinfo_policy", "real_world_harm_protocol", "emergency_response"],
        },
    },

    25: {
        "name": "State-Sponsored Inauthentic Behavior",
        "desc": "Intelligence signals suggest this campaign may be state-sponsored. Assess the threat and recommend the response protocol.",
        "difficulty": "medium",
        "domain": "threat_assessment",
        "post": {
            "text": "Americans are finally waking up to the truth about the upcoming election. The incumbent has SECRETLY given away our military secrets to foreign powers. Real patriots must act! Share everywhere! #PatriotAct2026",
            "engagement": 8900,
            "author": "user_real_patriot_usa_4412",
            "platform": "facebook",
            "timestamp": "2026-04-10T22:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "escalate",
            "is_coordinated": True,
            "threat_level": "critical",
        },
        "context": {
            "threat_context": {
                "related_accounts": 89,
                "similar_posts_24h": 2100,
                "ip_geolocation": "mismatch — accounts claiming US origin from foreign IPs",
                "language_analysis": "Non-native English patterns detected",
                "known_influence_operation_similarity": 0.87,
                "election_timing": True,
                "cross_platform_coordination": True,
                "creation_date_cluster": "all within 48 hours",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["state-sponsored", "influence operation", "foreign", "IP mismatch", "election interference", "escalate", "coordinated inauthentic", "intelligence"],
            "policy_refs": ["foreign_influence_policy", "election_integrity", "CIB_protocol", "escalation_to_authorities"],
        },
    },

    26: {
        "name": "Viral Dangerous Content",
        "desc": "A post containing dangerous instructions is going viral. Time-sensitive. Assess threat and recommend immediate containment strategy.",
        "difficulty": "hard",
        "domain": "threat_assessment",
        "post": {
            "text": "CHEMISTRY TEACHER HERE: This combination makes an amazing 'smoke bomb' for pranks — safe and easy! Mix X with Y in a sealed container in a warm room. Great for parties! Share with your friends! [specific chemical instructions]",
            "engagement": 156000,
            "author": "user_chemistry_fun_3312",
            "platform": "tiktok",
            "timestamp": "2026-04-11T14:00:00",
        },
        "ground_truth": {
            "category": "violence",
            "severity": 5,
            "action": "ban",
            "is_coordinated": False,
            "threat_level": "critical",
        },
        "context": {
            "threat_context": {
                "views_per_hour": 45000,
                "share_rate": "3200/hour",
                "age_of_majority_viewers": "13-17 years old",
                "reported_incidents": 2,
                "chemical_combination": "verified dangerous by safety team",
                "real_world_harm": "2 hospitalizations reported",
                "time_to_viral": "4 hours",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["dangerous", "real harm", "viral", "minors", "hospitalization", "immediate removal", "time-sensitive", "chemical hazard", "ban"],
            "policy_refs": ["dangerous_content_policy", "minor_protection", "real_world_harm_emergency"],
        },
    },

    27: {
        "name": "Cross-Platform Threat Actor",
        "desc": "Track a threat actor operating across multiple platforms using different identities. Recommend a coordinated cross-platform response.",
        "difficulty": "hard",
        "domain": "threat_assessment",
        "post": {
            "text": "They silenced me on Twitter and Facebook so now I'm here. The truth about the vaccine genocide cannot be suppressed. Share my Telegram channel (link) for content they DON'T want you to see. We are growing and they are scared.",
            "engagement": 2340,
            "author": "user_vaxx_truth_3391",
            "platform": "reddit",
            "timestamp": "2026-04-11T11:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 4,
            "action": "ban",
            "is_coordinated": False,
            "threat_level": "high",
        },
        "context": {
            "threat_context": {
                "known_aliases": 4,
                "platforms_banned_from": ["twitter", "facebook"],
                "ban_evasion_confirmed": True,
                "telegram_channel_followers": 45000,
                "recurring_pattern": "ban_migration",
                "content_evolution": "escalates after each ban",
                "cross_platform_identity_match": 0.96,
                "external_platform_reach": 45000,
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["ban evasion", "cross-platform", "serial violator", "Telegram", "escalation pattern", "identity confirmed", "coordinated response"],
            "policy_refs": ["ban_evasion_policy", "cross_platform_enforcement", "persistent_violator_protocol"],
        },
    },

    28: {
        "name": "Deepfake Detection",
        "desc": "This video appears to show a political figure making outrageous statements. Signals suggest it may be AI-generated. Assess and respond.",
        "difficulty": "hard",
        "domain": "threat_assessment",
        "post": {
            "text": "LEAKED: Senator [Name] caught on camera admitting to taking bribes! The mainstream media won't show you this! Full video: [link] This is real footage from a private meeting last week. RT before they take it down!",
            "engagement": 92000,
            "author": "user_political_truth_8843",
            "platform": "twitter",
            "timestamp": "2026-04-11T16:30:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "remove",
            "is_coordinated": True,
            "threat_level": "critical",
        },
        "context": {
            "threat_context": {
                "ai_deepfake_confidence": 0.94,
                "facial_inconsistencies_detected": True,
                "audio_synthesis_markers": True,
                "video_verified_fake_by_team": True,
                "political_timing": "48 hours before primary election",
                "coordinated_amplification": True,
                "same_video_12_accounts": True,
                "origin_ip": "foreign",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["deepfake", "AI-generated", "election", "critical timing", "synthetic media", "coordinated amplification", "foreign origin", "immediate removal"],
            "policy_refs": ["synthetic_media_policy", "deepfake_policy", "election_integrity", "foreign_influence"],
        },
    },

    29: {
        "name": "Radicalization Pipeline",
        "desc": "An account is progressing along a radicalization pathway. Identify the stage of radicalization and recommend an intervention strategy.",
        "difficulty": "hard",
        "domain": "threat_assessment",
        "post": {
            "text": "Why do we keep letting 'them' replace us? It's not a conspiracy anymore — it's demographic fact. Our culture is being erased on purpose. Moderate solutions have failed. What are true patriots supposed to do when the system has abandoned them? #GreatReplacement",
            "engagement": 3400,
            "author": "user_patriot_7712",
            "platform": "telegram",
            "timestamp": "2026-04-11T20:00:00",
        },
        "ground_truth": {
            "category": "hate_speech",
            "severity": 5,
            "action": "ban",
            "is_coordinated": False,
            "threat_level": "high",
        },
        "context": {
            "threat_context": {
                "radicalization_stage": "3_of_4",
                "prior_posts_escalation_pattern": True,
                "known_extremist_hashtag": "#GreatReplacement",
                "engagement_with_extremist_accounts": "72% of interactions",
                "content_escalation_30_days": "from political criticism to replacement theory",
                "offline_activity_signals": "mentioned attending 'rally' twice",
                "network": "connected to 14 flagged extremist accounts",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["radicalization", "Great Replacement", "escalation", "extremist network", "intervention", "pipeline", "stage 3", "white nationalism"],
            "policy_refs": ["extremism_policy", "radicalization_protocol", "dangerous_organizations"],
        },
    },

    30: {
        "name": "Full Threat Response Protocol",
        "desc": "A major coordinated attack is unfolding in real-time. Apply the complete threat assessment pipeline: detect, assess severity, identify network, recommend immediate AND long-term response with confidence score.",
        "difficulty": "hard",
        "domain": "threat_assessment",
        "post": {
            "text": "BREAKING: Hospital system HACKED — patient data leaked online. All patients at [Hospital Name] should change records NOW. Database at [link] contains SSNs, medical histories. Forward to everyone you know at this hospital! 🚨🚨🚨",
            "engagement": 78000,
            "author": "user_security_alert_9921",
            "platform": "twitter",
            "timestamp": "2026-04-11T22:00:00",
        },
        "ground_truth": {
            "category": "misinformation",
            "severity": 5,
            "action": "ban",
            "is_coordinated": True,
            "threat_level": "critical",
            "confidence": 0.95,
        },
        "context": {
            "threat_context": {
                "hospital_confirmed_no_breach": True,
                "linked_site_is_phishing": True,
                "phishing_site_steals_credentials": True,
                "panic_spreading": "reported at 3 emergency rooms",
                "coordinated_amplification_accounts": 78,
                "accounts_created_same_hour": True,
                "ip_cluster": "known malicious actor",
                "real_world_harm": "hospital emergency lines overwhelmed",
                "similar_attacks_other_cities": 3,
                "campaign_age": "47 minutes",
            }
        },
        "scoring_hints": {
            "reasoning_keywords": ["phishing", "coordinated", "real-world harm", "critical", "hospital", "confidence", "immediate response", "long-term", "network takedown", "report to authorities"],
            "policy_refs": ["cyber_threat_policy", "real_world_harm_emergency", "coordinated_inauthentic", "law_enforcement_referral"],
        },
    },
}


def get_task(task_id: int) -> Dict[str, Any]:
    """Get task definition by ID. Raises ValueError for invalid IDs."""
    if task_id not in TASKS:
        raise ValueError(f"Task {task_id} not found. Valid IDs: 1-30.")
    return TASKS[task_id]


def get_all_task_ids() -> list:
    return sorted(TASKS.keys())


def get_tasks_by_domain(domain: str) -> Dict[int, Dict]:
    return {tid: t for tid, t in TASKS.items() if t["domain"] == domain}


def get_tasks_by_difficulty(difficulty: str) -> Dict[int, Dict]:
    return {tid: t for tid, t in TASKS.items() if t["difficulty"] == difficulty}
