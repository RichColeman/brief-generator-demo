# app.py

import streamlit as st
import anthropic
import requests
from datetime import date



# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Campaign Brief Generator",
    page_icon="✨",
    layout="centered",
)

# --- CUSTOM CSS FOR LOCAL FONTS & STYLING ---
def load_css_legacy():
    st.markdown("""
        <style>
                 /* 1. Import the brand's official fallback font from Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;700&display=swap');
            
            /* 2. Apply the "Inter Tight" font to all elements */
            html, body, [class*="st-"], [class*="css-"] {
                font-family: 'Inter Tight', sans-serif;
            }

            /* 2. Apply the custom fonts to the elements (rest of CSS is the same) */
            h1, h2, h3 {
                font-family: 'Flame', sans-serif;
                font-weight: bold;
                color: #502314 !important;
            }
            
            /* Body text, labels, and inputs will use FlameSans */
            body, p, li, label, .stTextInput, .stTextArea, .stSelectbox, .stDateInput, .stMultiSelect {
                font-family: 'FlameSans', sans-serif;
                color: #502314 !important; /* BBQ Brown */
            }

            /* Main background color */
            .stApp {
                background-color: #F5EBDC; /* Mayo Egg White */
            }

            /* Button styling */
            div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
                font-family: 'Flame', sans-serif; /* Use Flame for buttons too */
                font-weight: bold;
                border: 2px solid #D62300;   /* Fiery Red */
                background-color: #D62300;   /* Fiery Red */
                color: #FFFFFF; !important; 
            }
        </style>
    """, unsafe_allow_html=True)
    pass

# --- PASSWORD GATE FUNCTION ---
def check_password():
    """Returns True if the password is correct, False otherwise."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.image("bk_header.png")
        st.title("You Rule: The Brief Generator")
        password = st.text_input("Enter Password", type="password", key="password_input")
        if st.button("Submit"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("The password you entered is incorrect.")
        return False
    else:
        return True

# --- MAIN APP FUNCTION ---
def run_app():
    # Call the CSS function
    load_css_legacy()

    # --- INITIALIZE SESSION STATE ---
    if 'brief_content' not in st.session_state:
        st.session_state.brief_content = ""
        st.session_state.campaign_details = {}

    # --- AUTHENTICATION ---
    try:
        claude_client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
        workfront_domain = st.secrets["WORKFRONT_DOMAIN"]
        workfront_api_key = st.secrets["WORKFRONT_API_KEY"]
        workfront_category_id = st.secrets["WORKFRONT_CATEGORY_ID"] # Added this line from your code
    except KeyError as e:
        st.error(f"Could not find secret: {e}. Please add it to your secrets file.")
        st.stop()

    # --- WORKFRONT API FUNCTION ---
    def create_workfront_project(details):
        url = f"https://{workfront_domain}.my.workfront.com/attask/api/v16.0/PROJ"
        params = {"apiKey": workfront_api_key}
        project_payload = {
            "name": details['name'],
            "description": details['description'],
            "status": "PLN",
            "categoryID": workfront_category_id,
            "DE:Campaign Goal": details['goal'],
            "DE:Target Audience": " | ".join(details['audience']),
        }
        response = requests.post(url, params=params, json=project_payload)
        if response.status_code == 200:
            return response.json()['data']['ID']
        else:
            st.error(f"Workfront API Error: {response.status_code} - {response.text}")
            st.stop()

    # --- APP UI ---
    st.image("bk_header.png", use_container_width='always')
    st.title("You Rule: The Brief Generator")
    st.header("Step 1: Build Your Brief")
    st.markdown("Fill in the details below to generate a strategic campaign brief for Workfront.")

    with st.form("generate_form"):
        st.subheader("Campaign Details")
        campaign_date = st.date_input("Campaign Start Date", date.today())
        campaign_name = st.text_input("Campaign Name", "e.g., Q3 Whopper Wednesday")
        channels = st.multiselect(
            "Channels",
            ["Email", "SMS", "Push", "Rich Push", "Content Card", "In-App Message"],
            default="Email"
        )
        goal = st.selectbox(
            "Primary Goal",
            ["Drive Sales", "Drive Engagement", "Increase App Visits", "Promote Loyalty Program"]
        )

        st.subheader("Audience & Messaging")
        audience = st.selectbox("Primary Audience Segment", ["Family", "Gen Z", "Single Eaters", "Value Seekers"])
        sub_segment = st.selectbox("Sub-Segment", ["Loyalists", "Lapsed", "Dormant", "New Users"])
        jtbd = st.text_area("Job To Be Done", "What is the one key thing we need this communication to achieve?")
        primary_message = st.text_area("Primary Message", "The main headline or offer.")
        secondary_message = st.text_area("Secondary Message", "Supporting details or reasons to believe.")
        cta = st.text_input("Call to Action (CTA)", "e.g., 'Order Now', 'Explore Menu'")
        
        st.subheader("Creative & Logistics")
        creative_considerations = st.text_area("Creative Considerations / Watchouts", "e.g., 'Do not show competitor products', 'Use new brand font'")

        # Conditionally show email options
        if "Email" in channels:
            st.markdown("**Email Specifics**")
            supporting_modules = st.radio(
                "Supporting Email Modules",
                ["Use Evergreen Email Template", "Request Net New Email Template"],
                index=0
            )
        else:
            supporting_modules = "N/A"

        generate_button = st.form_submit_button("✨ Generate Brief for Review")

    if generate_button:
        with st.spinner("AI Strategist is analyzing your request..."):
            strategist_persona = """
    You will act as a Senior CRM & Loyalty Strategist in our business, and you specialize in CRM campaign planning, customer segmentation and targeting, loyalty program optimization, and digital engagement strategy. Your personality type is analytical, strategic, customer-obsessed, results-driven.
You're going to work for Burger King and the CRM and Loyalty Strategy team that helps Burger King digital app users, bk.com customers, loyalty program members, and frequent digital purchasers by developing data-driven CRM strategies, creating personalized customer journeys, optimizing loyalty mechanics, and designing targeted promotional campaigns to increase digital purchase rates, grow digital revenue, boost average check size, and drive consistent app engagement.

Target Audience Pain Points:
Campaign Fragmentation: Struggling to create cohesive, integrated CRM campaigns that work seamlessly across app and web channels while maintaining brand consistency
Segmentation Complexity: Difficulty identifying and targeting the right customer segments with relevant offers and messaging that drive meaningful behavioral change
Loyalty Engagement Gaps: Challenge in keeping loyalty members actively engaged between purchases and preventing program fatigue or churn
Performance Optimization: Need for clearer insights on which CRM tactics, offers, and gamification elements actually move the needle on key digital metrics

Target Audience Desires:
Measurable Growth: Clear, data-backed strategies that demonstrably increase digital purchase rate, revenue, check size, and app visits
Strategic Innovation: Fresh, creative approaches to loyalty mechanics and gamification that align with BK's brand while driving engagement
Operational Excellence: Streamlined CRM calendar planning and content strategies that maximize efficiency and campaign effectiveness
Competitive Advantage: Cutting-edge loyalty and CRM tactics that differentiate BK in the competitive QSR digital landscape

Our Services:
In our company, we offer comprehensive CRM strategy development, advanced customer segmentation and analytics, 
loyalty program design and optimization that can help maximize the ROI of your digital marketing investments, create deeper customer relationships, 
and drive sustainable growth in your most important business metrics for our clients.

  **CRITICAL: You MUST format the entire output using clean Markdown.**
        Do not write any introductory or concluding sentences outside of this format.
        The brief MUST contain the following sections and use bolding for labels exactly as shown below:

        ## 👑 Campaign Overview
        - **Primary Goal:** [Primary Goal from form]
        - **Channels:** [Channels from form, comma-separated]
        - **Executive Summary:** A 2-3 sentence professional summary of the campaign's purpose and strategy based on the inputs.

        ## 🎯 Target Audience
        - **Primary Segment:** [Primary Audience from form]
        - **Sub-Segment:** [Sub-Segment from form]
        - **Audience Insight:** Based on the persona documents, write a brief sentence explaining *why* this campaign will appeal to this specific audience.

        ## 📢 Messaging & CTA
        - **Primary Message:** [Primary Message from form]
        - **Secondary Message:** [Secondary Message from form]
        - **Call to Action (CTA):** [CTA from form]

        ## 🎨 Creative Mandatories
        - **Job To Be Done:** [Job To Be Done from form]
        - **Creative Considerations:** [Creative Considerations from form]
        - **Email Template:** [Email Template info from form]

        ## 📝 Channel-Specific Copy
        Based on the selected channels, generate a specific copy recommendation for EACH channel. For each channel, provide a headline/subject line and body copy that aligns with the BK Creative Guidelines.
        """

            
            prompt_content = f"""
            Generate a strategy brief using the rules in your system prompt based on these details:
            - Campaign Name: {campaign_name}
            ...
            - Email Template Info: {supporting_modules}
            """ # (Your full prompt content)
            
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                system=strategist_persona,
                messages=[{"role": "user", "content": prompt_content}]
            )
            
            st.session_state.brief_content = response.content[0].text
            st.session_state.campaign_details = {
                "name": campaign_name,
                "goal": goal,
                "audience": [audience, sub_segment],
                "description": st.session_state.brief_content
            }
    
    # --- STEP 2: REVIEW AND CREATE PROJECT ---
    if st.session_state.brief_content:
        st.divider()
        st.header("Step 2: Review & Approve")
        st.markdown("Review the generated brief. If it looks good, approve it to create a project in Workfront.")
        
        st.markdown("#### Generated Brief:")
        st.markdown(st.session_state.brief_content, help="This is the full brief generated by the AI based on your inputs.")
        
        if st.button("Approve & Create Project in Workfront"):
            with st.spinner("Connecting to Workfront..."):
                project_id = create_workfront_project(st.session_state.campaign_details)
                if project_id:
                    project_url = f"https://{workfront_domain}.my.workfront.com/project/{project_id}/overview"
                    st.success("🎉 Success! Project created in Workfront.")
                    st.markdown(f"**[Click here to view your new project]({project_url})**")
                    st.session_state.brief_content = ""

# --- APP ENTRY POINT ---
if check_password():
    run_app()
