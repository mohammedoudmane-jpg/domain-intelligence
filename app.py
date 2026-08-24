"""
Domain Analyzer Pro - Streamlit Web App
"""

import streamlit as st
import re
import pandas as pd
import io

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Domain Analyzer Pro",
    page_icon="🏆",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🏆 Domain Analyzer Pro")
st.markdown("### تحليل الدومينات الاحترافي | Professional Domain Analysis")
st.markdown("---")

# ============================================================
# FORBIDDEN WORDS
# ============================================================

FORBIDDEN_WORDS = {
    "sex", "porn", "xxx", "escort", "slut", "tube", "cum", "dick",
    "pussy", "ass", "fuck", "shit", "cunt", "whore", "bitch", "naked",
    "horny", "fisting", "prostitute", "transvestite", "transgender",
    "maga", "trump", "biden", "obama", "clinton", "google", "facebook",
    "amazon", "microsoft", "apple", "netflix", "twitter", "instagram",
    "youtube", "tiktok", "snapchat", "whatsapp", "telegram", "zoom"
}

# ============================================================
# HOT KEYWORDS
# ============================================================

HOT_KEYWORDS = {
    "ai": 15, "flow": 12, "token": 12, "protocol": 10,
    "engine": 8, "analytics": 8, "vault": 7, "mate": 7,
    "escrow": 9, "lead": 6, "bio": 6, "pay": 8, "finance": 7,
    "capital": 7, "invest": 6, "cloud": 7, "data": 6,
    "smart": 5, "tech": 5, "pro": 4, "elite": 6
}

# ============================================================
# ANALYSIS FUNCTION
# ============================================================

def analyze_domain(domain):
    domain_clean = domain.lower().strip()
    
    if domain_clean.endswith('.com'):
        sld = domain_clean[:-4]
    else:
        sld = domain_clean.split('.')[0]
    
    length = len(sld)
    has_hyphen = '-' in sld
    has_number = bool(re.search(r'\d', sld))
    words = re.findall(r'[a-z]+', sld.lower())
    word_count = len(words)
    
    # Brand Score
    brand_score = 50
    
    if 6 <= length <= 12:
        brand_score += 20
    elif length <= 8:
        brand_score += 15
    elif length <= 15:
        brand_score += 5
    else:
        brand_score -= 10
    
    if not has_hyphen:
        brand_score += 10
    if not has_number:
        brand_score += 5
    if domain_clean.endswith('.com'):
        brand_score += 20
    if word_count <= 2:
        brand_score += 10
    
    # Keywords
    keyword_score = 0
    found_keywords = []
    for kw, score in HOT_KEYWORDS.items():
        if kw in sld.lower():
            keyword_score += score
            found_keywords.append(kw)
    
    brand_score += keyword_score
    brand_score = min(100, brand_score)
    
    # Commercial Score
    commercial_score = 0
    
    if keyword_score >= 20:
        commercial_score += 30
    elif keyword_score >= 10:
        commercial_score += 20
    elif keyword_score >= 5:
        commercial_score += 10
    
    commercial_words = {"pay", "buy", "sell", "trade", "invest", "fund", 
                        "capital", "asset", "wealth", "money", "cash", "loan", 
                        "credit", "finance", "insurance", "bank", "broker"}
    if any(w in sld.lower() for w in commercial_words):
        commercial_score += 20
    
    if domain_clean.endswith('.com'):
        commercial_score += 10
    
    commercial_score = min(100, commercial_score)
    
    # Buyer Pool
    buyer_score = 0
    
    large_pool = {"ai", "tech", "cloud", "data", "pay", "finance", 
                  "health", "care", "auto", "home", "real", "estate"}
    if any(w in sld.lower() for w in large_pool):
        buyer_score += 20
    
    medium_pool = {"pro", "expert", "master", "elite", "prime", 
                   "core", "max", "ultra", "mega", "hyper", "super"}
    if any(w in sld.lower() for w in medium_pool):
        buyer_score += 10
    
    buyer_score = min(100, buyer_score)
    
    # Legal Risk
    legal_risk = "Low"
    warnings = []
    
    forbidden_found = [w for w in FORBIDDEN_WORDS if w in sld.lower()]
    if forbidden_found:
        legal_risk = "HIGH"
        warnings.append(f"Forbidden: {', '.join(forbidden_found)}")
    
    trademark_words = {"google", "amazon", "microsoft", "apple", "facebook", 
                       "netflix", "twitter", "instagram", "youtube", "tiktok"}
    trademark_found = [w for w in trademark_words if w in sld.lower()]
    if trademark_found:
        legal_risk = "HIGH"
        warnings.append(f"Trademark: {', '.join(trademark_found)}")
    
    # Final Score
    final_score = (brand_score + commercial_score + buyer_score) / 3
    
    if legal_risk == "HIGH":
        final_score -= 40
    elif legal_risk == "Medium":
        final_score -= 15
    
    final_score = max(0, min(100, final_score))
    
    # Tier & Recommendation
    if final_score >= 80:
        tier = "Premium"
        recommendation = "STRONG BUY"
        price = "$2,000 - $8,000"
        color = "🟢"
    elif final_score >= 65:
        tier = "Mid"
        recommendation = "BUY"
        price = "$500 - $2,000"
        color = "🟡"
    elif final_score >= 50:
        tier = "Brandable"
        recommendation = "MAYBE"
        price = "$100 - $500"
        color = "🟠"
    else:
        tier = "Low"
        recommendation = "PASS"
        price = "$0 - $100"
        color = "🔴"
    
    # Buyers
    buyers = []
    if "ai" in sld.lower() or "flow" in sld.lower():
        buyers.append("AI/ML companies")
    if "pay" in sld.lower() or "finance" in sld.lower():
        buyers.append("FinTech")
    if "cloud" in sld.lower() or "data" in sld.lower():
        buyers.append("Cloud/SaaS")
    if "health" in sld.lower() or "care" in sld.lower():
        buyers.append("Healthcare")
    
    return {
        "domain": domain,
        "score": round(final_score, 1),
        "tier": tier,
        "recommendation": recommendation,
        "price": price,
        "color": color,
        "keywords": found_keywords,
        "buyers": buyers,
        "warnings": warnings,
        "length": length,
        "brand_score": brand_score,
        "commercial_score": commercial_score,
        "buyer_score": buyer_score,
        "legal_risk": legal_risk
    }

# ============================================================
# SIDEBAR - INPUT METHODS
# ============================================================

st.sidebar.header("📥 Input Methods")

input_method = st.sidebar.radio(
    "Choose input method:",
    ["✏️ Text Input", "📄 Upload File", "📋 Paste List"]
)

domains = []

if input_method == "✏️ Text Input":
    domain_input = st.sidebar.text_input(
        "Enter domain(s):",
        placeholder="e.g., aiflowmate.com, tokenissuers.com"
    )
    if domain_input:
        if ',' in domain_input:
            domains = [d.strip() for d in domain_input.split(',') if d.strip()]
        else:
            domains = [domain_input.strip()]

elif input_method == "📄 Upload File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload domains file (.txt or .csv)",
        type=["txt", "csv"]
    )
    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content))
            if 'domain' in df.columns:
                domains = df['domain'].tolist()
            else:
                domains = df.iloc[:, 0].tolist()
        else:
            domains = [line.strip() for line in content.split('\n') if line.strip()]

else:  # Paste List
    pasted = st.sidebar.text_area(
        "Paste your domains (one per line):",
        height=200,
        placeholder="aiflowmate.com\ntokenissuers.com\nveritad.com"
    )
    if pasted:
        domains = [d.strip() for d in pasted.split('\n') if d.strip()]

# ============================================================
# MAIN CONTENT
# ============================================================

if domains:
    st.sidebar.success(f"✅ {len(domains)} domains loaded")
    
    # Analyze button
    if st.sidebar.button("🚀 Analyze", use_container_width=True):
        
        with st.spinner("Analyzing domains..."):
            results = [analyze_domain(d) for d in domains]
            results.sort(key=lambda x: x["score"], reverse=True)
        
        # ============================================================
        # RESULTS
        # ============================================================
        
        st.header("📊 Analysis Results")
        st.markdown(f"**Total:** {len(results)} domains analyzed")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            strong_buy = sum(1 for r in results if r["recommendation"] == "STRONG BUY")
            st.metric("🟢 STRONG BUY", strong_buy)
        with col2:
            buy = sum(1 for r in results if r["recommendation"] == "BUY")
            st.metric("🟡 BUY", buy)
        with col3:
            maybe = sum(1 for r in results if r["recommendation"] == "MAYBE")
            st.metric("🟠 MAYBE", maybe)
        with col4:
            pass_ = sum(1 for r in results if r["recommendation"] == "PASS")
            st.metric("🔴 PASS", pass_)
        
        st.markdown("---")
        
        # ============================================================
        # RESULTS TABLE
        # ============================================================
        
        # Create DataFrame for display
        df_results = pd.DataFrame(results)
        df_display = df_results[[
            "domain", "score", "tier", "recommendation", "price",
            "keywords", "buyers", "warnings"
        ]]
        
        # Style the dataframe
        def color_recommendation(val):
            if val == "STRONG BUY":
                return "background-color: #d4edda; color: #155724"
            elif val == "BUY":
                return "background-color: #fff3cd; color: #856404"
            elif val == "MAYBE":
                return "background-color: #ffe5cc; color: #cc7a00"
            else:
                return "background-color: #f8d7da; color: #721c24"
        
        st.dataframe(
            df_display.style.map(
                color_recommendation, subset=["recommendation"]
            ),
            use_container_width=True,
            height=400
        )
        
        # ============================================================
        # DETAILED RESULTS
        # ============================================================
        
        st.markdown("---")
        st.subheader("🔍 Detailed Results")
        
        for i, r in enumerate(results[:10], 1):
            with st.expander(f"{r['color']} {i}. {r['domain']} - Score: {r['score']}/100", expanded=(i <= 3)):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Tier:** {r['tier']}")
                    st.write(f"**Recommendation:** {r['recommendation']}")
                    st.write(f"**Price:** {r['price']}")
                    st.write(f"**Length:** {r['length']} characters")
                with col2:
                    if r['keywords']:
                        st.write(f"**Keywords:** {', '.join(r['keywords'])}")
                    if r['buyers']:
                        st.write(f"**Buyers:** {', '.join(r['buyers'])}")
                    if r['warnings']:
                        st.write(f"⚠️ **Warnings:** {'; '.join(r['warnings'])}")
        
        # ============================================================
        # EXPORT
        # ============================================================
        
        st.markdown("---")
        st.subheader("📤 Export Results")
        
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="domain_analysis_results.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("👈 Enter domains in the sidebar and click **Analyze**")
