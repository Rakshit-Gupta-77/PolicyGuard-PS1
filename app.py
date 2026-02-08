import streamlit as st
import pdfplumber

from gap_detector import find_gaps
from llm_rewriter import rewrite_policy

st.set_page_config(page_title="PolicyGuard", layout="wide")

# -------------------------------------------------
# Title + Offline Badge
# -------------------------------------------------
st.title("🔐 PolicyGuard - Offline Policy Gap Analyzer (PS1)")
st.write("Upload a cybersecurity policy document and get gap analysis + improved policy draft.")

# ✅ Upgrade 2: Offline Verified Badge
st.success("✅ Fully Offline System (No External APIs Used)")
st.info("Local LLM: Phi-3 running via Ollama on localhost")

st.markdown("---")


# -------------------------------------------------
# ✅ Upgrade 1: PDF Text Extraction Function
# -------------------------------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# -------------------------------------------------
# ✅ Upgrade 3: Risk Levels + NIST Function Mapping
# -------------------------------------------------
SECTION_PRIORITY = {
    "Incident Response": "HIGH",
    "Access Control": "HIGH",
    "Risk Management": "MEDIUM",
    "Logging and Monitoring": "MEDIUM",
    "Compliance": "LOW",
    "Roles and Responsibilities": "LOW"
}

NIST_MAP = {
    "Access Control": "PROTECT",
    "Incident Response": "RESPOND",
    "Logging and Monitoring": "DETECT",
    "Risk Management": "IDENTIFY",
    "Compliance": "GOVERN",
    "Roles and Responsibilities": "GOVERN"
}


# -------------------------------------------------
# Upload Policy File (TXT + PDF)
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "📄 Upload Policy File (TXT or PDF)",
    type=["txt", "pdf"]
)

if uploaded_file is not None:

    # Read file content based on file type
    if uploaded_file.name.endswith(".pdf"):
        policy_text = extract_text_from_pdf(uploaded_file)
    else:
        policy_text = uploaded_file.read().decode("utf-8")

    # Display Uploaded Policy
    st.subheader("✅ Uploaded Policy Content")
    st.text_area("Policy Text", policy_text, height=200)

    # -------------------------------------------------
    # Step 1: Gap Detection
    # -------------------------------------------------
    st.markdown("---")
    st.subheader("🔍 Step 1: Gap Detection")

    gaps = find_gaps(policy_text)

    if len(gaps) == 0:
        st.success("🎉 No major gaps found. Policy is well aligned!")
    else:
        st.warning("Missing Sections Found (Risk + NIST Mapping):")

        for g in gaps:
            risk = SECTION_PRIORITY.get(g, "MEDIUM")
            nist_func = NIST_MAP.get(g, "N/A")

            st.write(f"❌ {g}  → Risk: **{risk}**  → NIST Function: **{nist_func}**")

        # ✅ Upgrade 2: Download Gap Report Button
        gap_text = "\n".join([f"- {g}" for g in gaps])

        st.download_button(
            label="⬇ Download Gap Report",
            data=gap_text,
            file_name="gaps_report.txt",
            mime="text/plain"
        )

    # -------------------------------------------------
    # Compliance Score
    # -------------------------------------------------
    total_sections = 8
    found_sections = total_sections - len(gaps)
    score = (found_sections / total_sections) * 100

    st.info(f"📊 Compliance Score: **{score:.2f}%**")

    # -------------------------------------------------
    # Step 2: Improved Policy Generation
    # -------------------------------------------------
    st.markdown("---")
    st.subheader("🛠 Step 2: Generate Improved Policy")

    if st.button("Generate Improved Policy using Offline LLM"):
        with st.spinner("Generating improved policy... Please wait..."):
            improved_policy = rewrite_policy(policy_text, gaps)

        st.success("✅ Improved Policy Generated!")

        st.text_area("Improved Policy Output", improved_policy, height=300)

        # Download Improved Policy
        st.download_button(
            label="⬇ Download Improved Policy",
            data=improved_policy,
            file_name="improved_policy.txt",
            mime="text/plain"
        )
