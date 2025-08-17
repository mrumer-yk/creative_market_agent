"""
Creative Agent – Streamlit app for Cycls' AI challenge

Clean modular architecture with separated concerns:
- utils.py: Configuration, API, and context utilities
- chain.py: All AI chain step functions
- app.py: Streamlit UI only

Stack: Python + Streamlit + Gemini API (google-generativeai)
"""

from __future__ import annotations

import streamlit as st

# Import our modular components
from utils import (
    get_api_key, init_genai, create_model, 
    get_current_context, DEFAULT_AUDIENCE
)
from chain import (
    step_brief_normalizer, step_market_intelligence, step_angle_generator,
    step_idea_writer, step_critic_improve, step_compliance_check,
    step_localize_polish, step_final_presenter
)


# -----------------------------
# Streamlit App
# -----------------------------




def main() -> None:
    st.set_page_config(page_title="Creative Agent", page_icon="🎬", layout="centered")
    st.title("Creative Agent")
    st.caption("AI-powered multi-step creative generator (Gemini) - Enhanced for KSA Market")
    
    # Show current context
    current_context = get_current_context()
    st.info(f"📅 {current_context['context_note']} | Current events: {', '.join(current_context['cultural_events'])}")

    with st.form("creative_form", clear_on_submit=False):
        product = st.text_input("Product", placeholder="e.g., Cycls Smart Bottle")
        description = st.text_area(
            "Description",
            placeholder="Briefly describe the product, features, or offer",
            height=120,
        )
        audience = st.text_input("Audience", placeholder="e.g., health-conscious millennials in Riyadh")
        tone = st.text_input("Tone", placeholder="e.g., friendly, inspiring, bold")
        language = st.selectbox("Language", ["English", "Arabic"], index=0)
        submitted = st.form_submit_button("Generate")

    if submitted:
        # --- New Requirement: Default audience to Riyadh/KSA ---
        final_audience = audience.strip()
        if not final_audience:
            final_audience = DEFAULT_AUDIENCE
        # ---------------------------------------------------------

        api_key = get_api_key()
        if not api_key:
            st.error("Missing API key. Please set GEMINI_API_KEY/GOOGLE_API_KEY in Secrets or env.")
            st.stop()

        init_genai(api_key)
        model = create_model(model_name="gemini-1.5-flash")

        try:
            with st.spinner("Normalizing brief..."):
                brief = step_brief_normalizer(
                    model, product, description, final_audience, tone, language
                )

            with st.spinner("Analyzing KSA market intelligence..."):
                market_insights = step_market_intelligence(model, brief)

            with st.spinner("Generating culturally-informed creative angles..."):
                angles = step_angle_generator(model, brief, market_insights)

            with st.spinner("Writing campaign ideas..."):
                ideas = step_idea_writer(model, brief, angles)

            with st.spinner("Critiquing and improving ideas..."):
                improved = step_critic_improve(model, brief, ideas)

            with st.spinner("Checking compliance and cultural guidelines..."):
                compliant = step_compliance_check(model, brief, improved)

            with st.spinner("Localizing and polishing..."):
                localized = step_localize_polish(model, brief, compliant)

            final_ideas = localized.get("ideas", [])
            if not isinstance(final_ideas, list) or len(final_ideas) == 0:
                st.error("The model returned no ideas. Please try again.")
                st.stop()

            markdown = step_final_presenter(final_ideas)
            st.markdown(markdown)

        except Exception as e:
            st.error(f"Generation failed: {e}")


if __name__ == "__main__":
    main()
