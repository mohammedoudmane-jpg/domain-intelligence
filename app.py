import streamlit as st
import pandas as pd
import tldextract
import re
import os
import json
from openai import OpenAI

# ==========================================
# ⚙️ إعدادات النظام والمفاتيح
# ==========================================
st.set_page_config(page_title="DomainSniper Pro", layout="wide", page_icon="🎯")
st.title("🎯 DomainSniper Pro: Big Brother Edition")
st.markdown("**المحرك الهجين:** فلترة خوارزمية صارمة + تحليل نية تجارية + تقييم AI عميق.")

# إدخل مفتاح API
api_key = st.sidebar.text_input("🔑 OpenAI API Key (اختياري)", type="password")
client = None
if api_key:
    client = OpenAI(api_key=api_key)
else:
    st.sidebar.info("💡 يمكن استخدام الفلترة الخوارزمية المجانية بدون أدنى تكلفة وبدون مفتاح API.")

# ==========================================
# 🧠 محرك الفلترة الخوارزمية (The Ruthless Filter)
# ==========================================
def algorithmic_filter(domain):
    """فلتر الأخ الأكبر: يرفض الدومينات الضعيفة فوراً بدون صرف أموال"""
    try:
        ext = tldextract.extract(domain)
        sld = ext.domain.lower()
        tld = ext.suffix.lower()
        
        # 1. فحص الامتداد (فقط .com)
        if tld != 'com':
            return False, "❌ ليس .COM"
            
        # 2. فحص الطول (أكثر من 16 حرف = مرفوض)
        if len(sld) > 16:
            return False, "❌ طويل جداً (>16 حرف)"
            
        # 3. فحص الشرطة والأرقام
        if '-' in domain or any(char.isdigit() for char in sld):
            return False, "❌ يحتوي شرطة/أرقام"
            
        # 4. فحص عدد الكلمات التقريبي
        words = re.findall(r'[a-z]+', sld)
        if len(words) > 3:
            return False, "❌ أكثر من 3 كلمات"
            
        return True, "✅ اجتاز الفلتر الأولي"
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"

# ==========================================
# 💼 محرك النية التجارية (Commercial Intent Engine)
# ==========================================
COMMERCIAL_KEYWORDS = {
    'ai': 15, 'tech': 10, 'soft': 10, 'data': 12, 'cloud': 10,
    'lead': 12, 'sales': 10, 'market': 10, 'seo': 12, 'ads': 8,
    'roof': 15, 'plumb': 15, 'build': 12, 'home': 8, 'law': 15,
    'med': 12, 'dent': 12, 'health': 10, 'care': 8, 'fit': 8,
    'shop': 8, 'store': 8, 'buy': 10, 'sell': 10, 'trade': 10,
    'crypto': 12, 'coin': 10, 'token': 10, 'nft': 8, 'web3': 10,
    'auto': 10, 'car': 8, 'motor': 10, 'gear': 8, 'tool': 10,
    'pay': 12, 'flow': 12, 'vault': 10, 'mate': 8
}

def analyze_commercial_intent(sld):
    """يبحث عن كلمات تجارية داخل الدومين ويعطيه درجة"""
    score = 0
    found_keywords = []
    for kw, weight in COMMERCIAL_KEYWORDS.items():
        if kw in sld.lower():
            score += weight
            found_keywords.append(kw)
    return score, found_keywords

# ==========================================
# 🤖 محرك التقييم العميق (AI Deep Valuation)
# ==========================================
def ai_deep_valuation(domain, algo_status, comm_score, keywords):
    if not client:
        return {"Verdict": "PASSED_FILTER", "Reason": "مجاني (بدون API)"}
        
    prompt = f"""
    أنت مستثمر دومينات محترف وصارم للغاية (Big Brother Persona).
    قم بتحليل الدومين: {domain}
    
    البيانات الأولية:
    - حالة الفلتر الخوارزمي: {algo_status}
    - درجة النية التجارية: {comm_score}/100
    - الكلمات المفتاحية المكتشفة: {', '.join(keywords) if keywords else 'لا يوجد'}
    
    بناءً على هذه البيانات، أجب بصيغة JSON ONLY بالمعايير التالية:
    1. "Project_Value": (1-10) هل يصلح كاسم لمشروع حقيقي؟
    2. "Buyer_Pool": (Very Low / Low / Medium / High / Very High)
    3. "End_Users": قائمة بـ 3 أنواع شركات قد تشتريه.
    4. "Trademark_Risk": (Low / Medium / High)
    5. "Est_Price_Wholesale": سعر الجملة المتوقع (مثال: $50-$150)
    6. "Est_Price_EndUser": سعر المستخدم النهائي (مثال: $800-$2500)
    7. "Verdict": (STRONG BUY / BUY / MAYBE / PASS) - كن قاسياً.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"Verdict": "ERROR", "Reason": str(e)}

# ==========================================
# 🖥️ واجهة المستخدم (The UI)
# ==========================================
input_method = st.sidebar.radio("📥 طريقة الإدخال", ["Text Input", "Paste List"])

domains_text = ""
if input_method == "Text Input":
    domains_text = st.sidebar.text_area("أدخل الدومينات (مفصولة بفواصل)", "aiflowmate.com, roofingworkers.com")
else:
    domains_text = st.sidebar.text_area("الصق القائمة (كل دومين في سطر)", "aiflowmate.com\nroofingworkers.com\nvinylresin.com")

if st.sidebar.button("🚀 RUN RUTHLESS SCAN", use_container_width=True):
    raw_domains = re.split(r'[,\n]', domains_text)
    domains = [d.strip().lower() for d in raw_domains if d.strip()]
    
    if not domains:
        st.error("⚠️ يرجى إدخال دومينات للتحليل.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, domain in enumerate(domains):
            status_text.text(f"🔍 جاري تحليل: {domain}...")
            
            # 1. الفلتر الخوارزمي
            passed, algo_status = algorithmic_filter(domain)
            
            # 2. تحليل النية التجارية
            ext = tldextract.extract(domain)
            comm_score, keywords = analyze_commercial_intent(ext.domain)
            
            # 3. التقييم بالـ AI (إن وجد)
            ai_result = {}
            if passed or comm_score > 20:
                if client:
                    ai_result = ai_deep_valuation(domain, algo_status, comm_score, keywords)
                else:
                    verdict_status = "STRONG BUY" if comm_score >= 25 else ("BUY" if comm_score >= 12 else "MAYBE")
                    ai_result = {"Verdict": verdict_status, "Reason": "Algorithmic Match"}
            else:
                ai_result = {"Verdict": "PASS", "Reason": "Rejected by Algorithmic Filter"}
                
            results.append({
                "Domain": domain,
                "Algo Status": algo_status,
                "Comm Score": comm_score,
                "Keywords": ", ".join(keywords),
                "Project Value": ai_result.get("Project_Value", "N/A"),
                "Buyer Pool": ai_result.get("Buyer_Pool", "N/A"),
                "End Users": str(ai_result.get("End_Users", "N/A")),
                "TM Risk": ai_result.get("Trademark_Risk", "N/A"),
                "Wholesale": ai_result.get("Est_Price_Wholesale", "N/A"),
                "End User": ai_result.get("Est_Price_EndUser", "N/A"),
                "Verdict": ai_result.get("Verdict", "PASS")
            })
            
            progress_bar.progress((i + 1) / len(domains))
            
        status_text.text("✅ اكتمل التحليل!")
        
        df = pd.DataFrame(results)
        
        def color_verdict(val):
            if val == 'STRONG BUY': return 'background-color: #28a745; color: white'
            elif val == 'BUY': return 'background-color: #17a2b8; color: white'
            elif val == 'MAYBE': return 'background-color: #ffc107; color: black'
            elif val == 'PASS': return 'background-color: #dc3545; color: white'
            return ''
            
        st.dataframe(df.style.map(color_verdict, subset=['Verdict']), use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report (CSV)", csv, "domain_sniper_report.csv", "text/csv", use_container_width=True)
