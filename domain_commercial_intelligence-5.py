import re
import io
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Domain Commercial Intelligence", page_icon="🌐", layout="wide")

# ============================================================
# Domain Commercial Intelligence Engine — V2
# Designed around End-User / Project Value, not generic appraisal.
# No live web calls are made by this local version.
# ============================================================

COMMERCIAL_TERMS = {
    "ai","automation","software","saas","security","cyber","cloud","data","analytics",
    "finance","fintech","insurance","legal","health","medical","property","realestate",
    "roofing","construction","workers","resin","polymer","logistics","payments","leads",
    "capture","workflow","agent","agents","commerce","market","capital","energy",
    "solar","staffing","jobs","payroll","billing","credit","mortgage","freight",
    "shipping","supply","medical","clinic","dental","law","tax","accounting","sales",
    "crm","support","voice","chat","video","media","design","travel","hotel"
}
GENERIC_WORDS = {"the","and","of","for","to","in","on","my","get","go","a","an","pro","hub","tech"}
NEGATIVE_PATTERNS = [
    r"[^a-z0-9-]", r"^\-", r"\-$", r"\d{3,}", r"(.)\1\1"
]

WEIGHTS = {
    "Project Value": 15,
    "Commercial Intent": 12,
    "Buyer Pool": 12,
    "Brandability": 10,
    "Instant Understanding": 10,
    "TLD Quality": 8,
    "Pronunciation": 7,
    "Upgrade Potential": 6,
    "Market Evidence": 5,
    "Comparable Sales": 5,
    "International Fit": 3,
    "Trust Signal": 7,
}
# Total positive = 100. Legal/history are gates rather than cosmetic points.

def clean_domain(raw):
    x = str(raw).strip().lower()
    x = re.sub(r"^https?://", "", x).split("/")[0].strip()
    return x

def parse_domain(raw):
    d = clean_domain(raw)
    if "." not in d:
        return d, d, "", [d]
    sld, tld = d.rsplit(".", 1)
    # hyphen is retained as a separator
    tokens = [x for x in re.split(r"[-_]+", sld) if x]
    return d, sld, tld, tokens

def pronounce_score(sld, tokens, tld):
    if not sld:
        return 0
    score = 45
    n = len(sld)
    if 5 <= n <= 12: score += 22
    elif n <= 16: score += 12
    elif n <= 20: score += 2
    else: score -= 15
    if re.search(r"[^a-z]", sld): score -= 12
    if re.search(r"[bcdfghjklmnpqrstvwxyz]{4,}", sld): score -= 12
    if re.search(r"[aeiou]{4,}", sld): score -= 8
    if len(tokens) <= 2: score += 8
    if tld == "com": score += 5
    return max(0, min(100, score))

def brandability_score(sld, tokens, tld):
    score = 50
    if len(tokens) == 1: score += 22
    elif len(tokens) == 2: score += 15
    elif len(tokens) == 3: score += 2
    else: score -= 15
    if 5 <= len(sld) <= 12: score += 15
    elif len(sld) <= 16: score += 7
    if "-" in sld or "_" in sld: score -= 20
    if any(c.isdigit() for c in sld): score -= 15
    if tld == "com": score += 10
    if re.search(r"(.)\1\1", sld): score -= 12
    return max(0, min(100, score))

def commercial_score(tokens):
    hits = sum(1 for t in tokens if t in COMMERCIAL_TERMS)
    exact = len(tokens) == 2 and all(t in COMMERCIAL_TERMS for t in tokens)
    score = 35 + hits * 18
    if exact: score += 15
    if len(tokens) == 1 and tokens[0] in COMMERCIAL_TERMS: score += 20
    return max(0, min(100, score))

def instant_understanding(tokens):
    if len(tokens) == 1:
        return 72 if tokens[0] in COMMERCIAL_TERMS else 48
    known = sum(t in COMMERCIAL_TERMS or t in GENERIC_WORDS for t in tokens)
    score = 48 + (known / max(1, len(tokens))) * 42
    if len(tokens) == 2: score += 5
    return max(0, min(100, score))

def project_value(tokens, commercial, clarity, brand):
    # Can an entrepreneur immediately imagine a product/service/company?
    if len(tokens) == 2 and commercial >= 60:
        base = 82
    elif commercial >= 70:
        base = 76
    elif clarity >= 75:
        base = 68
    else:
        base = 50
    return round(0.50*base + 0.25*commercial + 0.15*clarity + 0.10*brand)

def tld_quality(tld):
    if tld == "com": return 100
    if tld in {"ai","io","co"}: return 75
    if tld in {"net","org"}: return 60
    return 40

def score_domain(raw, manual=None):
    d,sld,tld,tokens = parse_domain(raw)
    manual = manual or {}
    commercial = commercial_score(tokens)
    clarity = instant_understanding(tokens)
    brand = brandability_score(sld, tokens, tld)
    pron = pronounce_score(sld, tokens, tld)
    tldq = tld_quality(tld)
    project = project_value(tokens, commercial, clarity, brand)

    # Pre-research heuristics: intentionally conservative.
    buyer = min(100, 35 + commercial*0.55 + (12 if len(tokens)==2 else 0))
    trust = round(0.45*tldq + 0.30*clarity + 0.25*pron)
    upgrade = min(100, round(40 + commercial*0.40 + clarity*0.25))
    market = manual.get("Market Evidence", 35)
    comps = manual.get("Comparable Sales", 35)
    intl = manual.get("International Fit", 65)

    vals = {
        "Project Value": project, "Commercial Intent": round(commercial),
        "Buyer Pool": round(buyer), "Brandability": brand,
        "Instant Understanding": clarity, "TLD Quality": tldq,
        "Pronunciation": pron, "Upgrade Potential": upgrade,
        "Market Evidence": market, "Comparable Sales": comps,
        "International Fit": intl, "Trust Signal": trust
    }
    total = round(sum(vals[k] * WEIGHTS[k] / 100 for k in WEIGHTS))
    legal = manual.get("Trademark Risk", "Unknown")
    history = manual.get("History Risk", "Unknown")
    if legal == "High": verdict = "🔴 STOP — trademark/legal review"
    elif history == "High": verdict = "🔴 STOP — history/spam review"
    elif total >= 82: verdict = "🟢 STRONG END-USER CANDIDATE"
    elif total >= 68: verdict = "🟡 RESEARCH FURTHER"
    else: verdict = "🔴 LOW PRIORITY"

    return {
        "Domain": d, "Score": total, "Verdict": verdict,
        **vals, "Trademark Risk": legal, "History Risk": history,
        "Niche": niche(tokens), "Tokens": " · ".join(tokens)
    }

def niche(tokens):
    hits = [t.upper() for t in tokens if t in COMMERCIAL_TERMS]
    return " / ".join(hits) if hits else "Brandable / General"

def project_ideas(row):
    t = row["Tokens"].replace(" · "," ")
    if row["Commercial Intent"] >= 75:
        return [
            f"Specialized SaaS or software product around {t}",
            f"Marketplace / service platform for {t}",
            f"B2B brand or vertical solution using {t}"
        ]
    return [
        "Brand-led startup or digital product",
        "Agency / service company",
        "Niche content or commerce brand"
    ]

def research_queries(domain, niche_text):
    return [
        f'"{domain}"',
        f'"{niche_text}" startup',
        f'"{niche_text}" software company',
        f'"{niche_text}" SaaS',
        f'"{niche_text}" platform',
        f'"{niche_text}" LinkedIn founder'
    ]

# ---------------- UI ----------------
st.title("🌐 Domain Commercial Intelligence Engine")
st.markdown("### End-User / Project Value Edition")
st.write("يفحص الدومين بمنطق: **هل يصلح كاسم مشروع حقيقي؟ هل له قيمة تجارية؟ وهل يمكن بناء Buyer Pool حوله؟**")

with st.sidebar:
    st.header("⚙️ Research controls")
    st.caption("V2 يعمل محليًا. درجات Market Evidence وComps وTrademark/History يمكن إدخالها يدويًا بعد البحث الخارجي.")
    market = st.slider("Market Evidence", 0, 100, 35)
    comps = st.slider("Comparable Sales", 0, 100, 35)
    intl = st.slider("International Fit", 0, 100, 65)
    legal = st.selectbox("Trademark Risk", ["Unknown","Low","Medium","High"])
    history = st.selectbox("History/Spam Risk", ["Unknown","Low","Medium","High"])

tabs = st.tabs(["🔎 Batch Scanner", "🎯 Deep Analysis", "🧠 Research Plan", "📥 CSV"])

with tabs[0]:
    domains = st.text_area(
        "الصق قائمة الدومينات — واحد في كل سطر",
        value="AIFlowMate.com\nRoofingWorkers.com\nVinylResin.com\nZenveta.com\nLeadCaptureEngine.com",
        height=190
    )
    if st.button("🚀 RUN COMMERCIAL SCAN", type="primary"):
        manual = {
            "Market Evidence": market, "Comparable Sales": comps,
            "International Fit": intl, "Trademark Risk": legal, "History Risk": history
        }
        rows = [score_domain(x, manual) for x in domains.splitlines() if x.strip()]
        df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
        st.session_state["df"] = df

    if "df" in st.session_state:
        df = st.session_state["df"]
        st.dataframe(
            df[["Domain","Score","Verdict","Project Value","Commercial Intent","Buyer Pool",
                "Brandability","Instant Understanding","TLD Quality","Pronunciation",
                "Upgrade Potential","Market Evidence","Comparable Sales",
                "Trademark Risk","History Risk","Niche"]],
            use_container_width=True, hide_index=True
        )

with tabs[1]:
    if "df" not in st.session_state:
        st.info("شغّل Batch Scanner أولًا.")
    else:
        df = st.session_state["df"]
        selected = st.selectbox("اختر الدومين", df["Domain"].tolist())
        r = df[df.Domain == selected].iloc[0]

        c = st.columns(5)
        for col, label in zip(c, ["Score","Project Value","Commercial Intent","Buyer Pool","Brandability"]):
            col.metric(label, f'{int(r[label])}/100')

        st.subheader("🏢 Business / Project Thesis")
        for idea in project_ideas(r):
            st.write("•", idea)

        st.subheader("🧲 Why an End User could care")
        if r["Project Value"] >= 80:
            st.success("الاسم يحمل فكرة مشروع واضحة ويمكن شرحه في جملة واحدة.")
        elif r["Project Value"] >= 65:
            st.warning("يوجد مشروع محتمل، لكن يجب إثبات السوق والـbuyer pool بالبحث.")
        else:
            st.error("القيمة التجارية المباشرة ضعيفة؛ لا تعتمد على brandability وحدها.")

        st.subheader("📊 Score breakdown")
        bd = pd.DataFrame({"Criterion": list(WEIGHTS.keys()),
                           "Weight": list(WEIGHTS.values()),
                           "Score": [int(r[k]) for k in WEIGHTS]})
        bd["Contribution"] = (bd.Score * bd.Weight / 100).round(2)
        st.dataframe(bd, use_container_width=True, hide_index=True)

        st.caption("⚠️ هذا Screening Engine وليس appraisal احترافيًا، ولا يثبت وجود مشترٍ أو قيمة بيع.")

with tabs[2]:
    domain = st.text_input("Domain for research plan", "AIFlowMate.com")
    _,_,_,tokens = parse_domain(domain)
    niche_text = " ".join(tokens)
    st.subheader("🔍 Search plan")
    st.write("استخدم هذه الاستعلامات في Google/Perplexity/LinkedIn/Crunchbase/NameBio/Trademark databases:")
    for q in research_queries(domain, niche_text):
        st.code(q)
    st.subheader("🎯 المطلوب إثباته قبل قرار الشراء")
    for x in [
        "وجود سوق تجاري واضح للكلمات/المفهوم.",
        "وجود عدة End Users حقيقيين، وليس شركة واحدة فقط.",
        "وجود شركات تستخدم أسماء/دومينات أضعف يمكن Upgrade إليها.",
        "وجود منتجات أو شركات يمكن أن تجعل الدومين Product/Brand جديدًا.",
        "عدم وجود trademark conflict واضح في نفس المجال/الاختصاص.",
        "وجود comparable sales منطقية، لا مجرد تقديرات AI.",
        "سجل نظيف إذا كان الدومين expired."
    ]:
        st.write("☑️", x)

with tabs[3]:
    if "df" in st.session_state:
        csv = st.session_state["df"].to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Download domain_report.csv", csv, "domain_report.csv", "text/csv")
    else:
        st.info("لا توجد نتائج بعد.")
