"""
Chain step functions for Creative Agent
All AI chain processing steps in one module
"""
import json
from typing import Any, Dict, List

from utils import get_current_context, call_gemini_json


def step_brief_normalizer(
    model,
    product: str,
    description: str,
    audience: str,
    tone: str,
    language: str,
) -> Dict[str, Any]:
    """Step 1 – Normalize raw user inputs into a clean brief JSON."""
    raw_input = {
        "product": product,
        "description": description,
        "audience": audience,
        "tone": tone,
        "language": language,
    }

    prompt = (
        "Role: Brief Normalizer\n"
        "Task: Given a raw brief, produce a clean, standardized JSON object that will be passed to other steps.\n"
        "Input JSON:\n"
        f"{json.dumps(raw_input, ensure_ascii=False)}\n"
        "Output JSON schema (no additional fields):\n"
        "{\n"
        "  \"product\": string,\n"
        "  \"description\": string,\n"
        "  \"audience\": string,\n"
        "  \"tone\": string,\n"
        "  \"language\": \"English\" | \"Arabic\",\n"
        "  \"objectives\": string[],\n"
        "  \"constraints\": string[]\n"
        "}\n"
        "Rules:\n"
        "- The default target market is Riyadh, Saudi Arabia (KSA). If the input audience is generic or empty, enrich it with this specific context.\n"
        "- Correct typos and normalize while preserving meaning.\n"
        "- Use concise phrasing.\n"
        "- Do not include nulls; use [] for empty arrays.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.4)


def step_market_intelligence(model, brief: Dict[str, Any]) -> Dict[str, Any]:
    """Step 2 – Generate KSA market insights and competitive landscape."""
    current_context = get_current_context()
    payload = {"brief": brief, "current_context": current_context}
    prompt = (
        "Role: Market Intelligence Analyst\n"
        "Task: Analyze the KSA market context and provide strategic insights for the campaign brief.\n"
        f"IMPORTANT: Today is {current_context['context_note']}. Current cultural events: {', '.join(current_context['cultural_events'])}.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema:\n"
        "{\n"
        "  \"market_insights\": {\n"
        "    \"cultural_moments\": string[],\n"
        "    \"local_trends\": string[],\n"
        "    \"target_behaviors\": string[],\n"
        "    \"competitive_landscape\": string[],\n"
        "    \"opportunities\": string[],\n"
        "    \"seasonal_relevance\": string[]\n"
        "  }\n"
        "}\n"
        "Rules:\n"
        "- Use the current date and season provided to give timely, relevant insights.\n"
        "- Focus on Riyadh/KSA market specifically unless different location specified.\n"
        "- Consider current season, weather, cultural events happening NOW.\n"
        "- Include seasonal shopping patterns, behavioral changes, cultural moments.\n"
        "- Identify 3-5 items per category.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.6)


def step_angle_generator(model, brief: Dict[str, Any], market_insights: Dict[str, Any]) -> Dict[str, Any]:
    """Step 3 – Generate exactly 5 distinct creative angles with market intelligence."""
    current_context = get_current_context()
    payload = {"brief": brief, "market_insights": market_insights.get("market_insights", {}), "current_context": current_context}
    prompt = (
        "Role: Creative Strategist\n"
        "Task: Using the brief and market insights, propose exactly 5 distinct creative angles for ad campaigns.\n"
        f"CURRENT TIMING CONTEXT: {current_context['context_note']}. Today is {current_context['weekday']}.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema (exactly 5):\n"
        "{\n"
        "  \"angles\": [\n"
        "    {\n"
        "      \"id\": \"1\"..\"5\",\n"
        "      \"title\": string,\n"
        "      \"insight\": string,\n"
        "      \"key_message\": string,\n"
        "      \"cultural_hook\": string,\n"
        "      \"timing_consideration\": string\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Use the current date/season to create timely, relevant angles.\n"
        "- Leverage market insights to create culturally resonant angles for Riyadh/KSA.\n"
        "- Each angle must tap into what's happening NOW - current season, events, behaviors.\n"
        "- Consider immediate timing opportunities (current weather, seasonal activities, cultural moments).\n"
        "- Angles must be distinct and non-overlapping.\n"
        "- Tailor to the audience and tone.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.7)


def step_idea_writer(
    model,
    brief: Dict[str, Any],
    angles: Dict[str, Any],
) -> Dict[str, Any]:
    """Step 4 – Write 3 detailed campaign ideas (A, B, C)."""
    payload = {"brief": brief, "angles": angles.get("angles", [])}
    prompt = (
        "Role: Idea Writer\n"
        "Task: Using the brief and angles, write exactly 3 campaign ideas (A, B, C) with required fields.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema (exactly 3):\n"
        "{\n"
        "  \"ideas\": [\n"
        "    {\n"
        "      \"label\": \"A\"|\"B\"|\"C\",\n"
        "      \"based_on_angle_id\": \"1\"..\"5\",\n"
        "      \"tagline\": string,\n"
        "      \"script_30s\": string,\n"
        "      \"captions\": { \"instagram\": string, \"x\": string },\n"
        "      \"cta\": string\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Constraints:\n"
        "- Scripts and captions must be culturally and locally relevant for the Riyadh, Saudi Arabia (KSA) market unless a different audience is specified.\n"
        "- Longer narrative: ~130–170 words (about 40s), with a clear beginning, middle, and end.\n"
        "- Captions are punchy; no hashtags unless essential.\n"
        "- Align with tone and audience.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.85)


def step_critic_improve(
    model,
    brief: Dict[str, Any],
    ideas: Dict[str, Any],
) -> Dict[str, Any]:
    """Step 5 – Critique and revise weak ideas; output only improved versions."""
    payload = {"brief": brief, "ideas": ideas.get("ideas", [])}
    prompt = (
        "Role: Critic & Improve\n"
        "Task: Review the ideas, identify weaknesses, and revise them. Output only the improved versions.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema:\n"
        "{\n"
        "  \"ideas\": [\n"
        "    {\n"
        "      \"label\": \"A\"|\"B\"|\"C\",\n"
        "      \"based_on_angle_id\": \"1\"..\"5\",\n"
        "      \"tagline\": string,\n"
        "      \"script_30s\": string,\n"
        "      \"captions\": { \"instagram\": string, \"x\": string },\n"
        "      \"cta\": string\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Review for cultural appropriateness for the Riyadh/KSA market. Revise any idea that might not land well.\n"
        "- Keep original strengths; fix clarity, hook, and CTA strength.\n"
        "- Ensure each idea is distinct; remove redundancy.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.6)


def step_compliance_check(model, brief: Dict[str, Any], ideas: Dict[str, Any]) -> Dict[str, Any]:
    """Step 6 – Verify adherence to KSA advertising guidelines and cultural appropriateness."""
    payload = {"brief": brief, "ideas": ideas.get("ideas", [])}
    prompt = (
        "Role: Compliance & Cultural Reviewer\n"
        "Task: Review campaign ideas for compliance with KSA advertising guidelines and cultural appropriateness.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema:\n"
        "{\n"
        "  \"ideas\": [\n"
        "    {\n"
        "      \"label\": \"A\"|\"B\"|\"C\",\n"
        "      \"based_on_angle_id\": \"1\"..\"5\",\n"
        "      \"tagline\": string,\n"
        "      \"script_30s\": string,\n"
        "      \"captions\": { \"instagram\": string, \"x\": string },\n"
        "      \"cta\": string,\n"
        "      \"compliance_notes\": string\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Ensure compliance with Saudi Arabia advertising regulations and cultural sensitivities.\n"
        "- Check for appropriate representation, modest imagery suggestions, respectful tone.\n"
        "- Verify timing considerations (prayer times, cultural events, weekends).\n"
        "- Remove or revise any potentially problematic content.\n"
        "- Add brief compliance notes explaining any changes made.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.4)


def step_localize_polish(
    model,
    brief: Dict[str, Any],
    ideas: Dict[str, Any],
) -> Dict[str, Any]:
    """Step 7 – Final refinement to requested language & tone."""
    payload = {
        "language": brief.get("language", "English"),
        "tone": brief.get("tone", ""),
        "ideas": ideas.get("ideas", []),
    }
    prompt = (
        "Role: Localize/Polish\n"
        "Task: Refine the ideas to the requested language and tone. If the language is Arabic, fully localize the content to natural Modern Standard Arabic. If the language is English, just polish the existing English text for clarity and impact.\n"
        "Style Guide (apply strictly):\n"
        "- Use a friendly, conversational second-person voice (\"you\").\n"
        "- Prefer short sentences (8–15 words) and simple everyday words.\n"
        "- Open scripts with a concrete moment or scenario (e.g., \"Imagine...\", \"It's 2 PM in Riyadh...\").\n"
        "- Show, not tell: add 1–2 light sensory cues without hype.\n"
        "- Keep scripts ~120–160 words, split into 3–5 short paragraphs.\n"
        "- Captions: IG slightly expressive; X concise and punchy. Avoid unnecessary hashtags.\n"
        "- Do not invent product claims; no health/functional promises.\n"
        "Input JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False)}\n"
        "Output JSON schema (same as input ideas schema):\n"
        "{\n"
        "  \"ideas\": [\n"
        "    {\n"
        "      \"label\": \"A\"|\"B\"|\"C\",\n"
        "      \"based_on_angle_id\": \"1\"..\"5\",\n"
        "      \"tagline\": string,\n"
        "      \"script_30s\": string,\n"
        "      \"captions\": { \"instagram\": string, \"x\": string },\n"
        "      \"cta\": string\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Perform a final cultural polish to ensure content is appropriate and effective for the target market (defaulting to Riyadh, KSA).\n"
        "- Preserve meaning while adjusting tone.\n"
        "- For Arabic, use proper Modern Standard Arabic, not transliteration.\n"
        "- For English, focus on polishing grammar, style, and flow.\n"
        "- Respond ONLY with minified JSON."
    )
    return call_gemini_json(model, prompt, temperature=0.5)


def step_final_presenter(ideas: List[Dict[str, Any]]) -> str:
    """Render final Markdown from ideas JSON. No JSON is shown to the user."""
    # Expect labels A, B, C
    by_label = {idea.get("label", "").upper(): idea for idea in ideas}
    ordered = [by_label.get("A"), by_label.get("B"), by_label.get("C")]
    ordered = [i for i in ordered if i]

    sections = []
    for idea in ordered:
        label = idea.get("label", "").upper()
        tagline = idea.get("tagline", "").strip()
        script_30s = idea.get("script_30s", "").strip()
        captions = idea.get("captions", {}) or {}
        ig = captions.get("instagram", "").strip()
        xcap = captions.get("x", "").strip()
        cta = idea.get("cta", "").strip()

        # Show compliance notes if available (for transparency)
        compliance_notes = idea.get("compliance_notes", "").strip()
        compliance_section = f"\n\n*Compliance Notes: {compliance_notes}*" if compliance_notes else ""

        section = (
            f"### Option {label}\n"
            f"#### {tagline}\n\n"
            f"> {script_30s}\n\n"
            f"**Captions**\n- **IG**: {ig}\n- **X**: {xcap}\n\n"
            f"**CTA**: {cta}{compliance_section}\n"
        )
        sections.append(section)

    return "\n\n".join(sections)
