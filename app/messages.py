"""Fixed, reviewed message templates. Safety advice is never LLM-generated."""
LANGS = {"en": "English", "hi": "हिन्दी", "kn": "ಕನ್ನಡ"}
JOBS = {
    "en": {"delivery": "Delivery rider", "construction": "Construction", "farm": "Farm work", "vendor": "Street vendor"},
    "hi": {"delivery": "डिलीवरी राइडर", "construction": "निर्माण कार्य", "farm": "खेती", "vendor": "फेरीवाला"},
    "kn": {"delivery": "ಡೆಲಿವರಿ ರೈಡರ್", "construction": "ನಿರ್ಮಾಣ ಕೆಲಸ", "farm": "ಕೃಷಿ ಕೆಲಸ", "vendor": "ಬೀದಿ ವ್ಯಾಪಾರಿ"},
}
T = {
    "en": {
        "levels": ["Low", "Moderate", "High", "Extreme"],
        "lang_q": "Choose your language", "job_q": "What work do you do?",
        "loc_q": "Share your work location so I can check the local weather.", "loc_btn": "Share location",
        "done": "All set! You will get a heat plan every morning at 7. Use /plan anytime, /dizzy if you feel unwell, /stop to unsubscribe.",
        "plan": "🌡️ Heat risk today: {level}\nPeak risk: {peak}\nWork {work} min, rest {rest} min in shade.\nDrink a glass of water every 20 minutes.\nSafer hours: {safe}",
        "alert": "⚠️ Heat risk is now {level}. Work {work} min, rest {rest} min in shade. Drink water now.",
        "firstaid": "Dizzy or headache? Move to shade, sip water, loosen clothes, cool your head and neck with a wet cloth.\n🚨 If confused, fainting, or skin is hot and dry with no sweating: call 108 now.",
        "stop": "You are unsubscribed. Send /start to join again.", "nouser": "Send /start first.",
        "disc": "Guidance is based on occupational heat standards. It is not medical advice.",
    },
    "hi": {
        "levels": ["कम", "मध्यम", "ज़्यादा", "बहुत ज़्यादा"],
        "lang_q": "अपनी भाषा चुनें", "job_q": "आप कौन सा काम करते हैं?",
        "loc_q": "स्थानीय मौसम देखने के लिए अपनी काम की जगह साझा करें।", "loc_btn": "लोकेशन भेजें",
        "done": "तैयार! हर सुबह 7 बजे गर्मी की योजना मिलेगी। कभी भी /plan, तबीयत ख़राब हो तो /dizzy, बंद करने के लिए /stop।",
        "plan": "🌡️ आज गर्मी का जोखिम: {level}\nसबसे ज़्यादा जोखिम: {peak}\n{work} मिनट काम करें, {rest} मिनट छाँव में आराम करें।\nहर 20 मिनट में एक गिलास पानी पिएँ।\nकम जोखिम वाले समय: {safe}",
        "alert": "⚠️ गर्मी का जोखिम अब {level} है। {work} मिनट काम करें, {rest} मिनट छाँव में आराम करें। अभी पानी पिएँ।",
        "firstaid": "चक्कर या सिरदर्द? छाँव में जाएँ, पानी के घूँट लें, कपड़े ढीले करें, गीले कपड़े से सिर-गर्दन ठंडा करें।\n🚨 भ्रम, बेहोशी या गर्म सूखी त्वचा (पसीना नहीं) हो तो तुरंत 108 पर कॉल करें।",
        "stop": "आपकी सदस्यता बंद हो गई। दोबारा जुड़ने के लिए /start भेजें।", "nouser": "पहले /start भेजें।",
        "disc": "यह सलाह कार्यस्थल गर्मी मानकों पर आधारित है, चिकित्सा सलाह नहीं।",
    },
    "kn": {
        "levels": ["ಕಡಿಮೆ", "ಮಧ್ಯಮ", "ಹೆಚ್ಚು", "ತೀವ್ರ"],
        "lang_q": "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆರಿಸಿ", "job_q": "ನೀವು ಯಾವ ಕೆಲಸ ಮಾಡುತ್ತೀರಿ?",
        "loc_q": "ಸ್ಥಳೀಯ ಹವಾಮಾನ ನೋಡಲು ನಿಮ್ಮ ಕೆಲಸದ ಸ್ಥಳವನ್ನು ಹಂಚಿಕೊಳ್ಳಿ.", "loc_btn": "ಸ್ಥಳ ಕಳುಹಿಸಿ",
        "done": "ಸಿದ್ಧ! ಪ್ರತಿದಿನ ಬೆಳಿಗ್ಗೆ 7ಕ್ಕೆ ಶಾಖದ ಯೋಜನೆ ಸಿಗುತ್ತದೆ. /plan, ಅಸ್ವಸ್ಥರಾದರೆ /dizzy, ನಿಲ್ಲಿಸಲು /stop.",
        "plan": "🌡️ ಇಂದಿನ ಶಾಖದ ಅಪಾಯ: {level}\nಹೆಚ್ಚು ಅಪಾಯದ ಸಮಯ: {peak}\n{work} ನಿಮಿಷ ಕೆಲಸ ಮಾಡಿ, {rest} ನಿಮಿಷ ನೆರಳಿನಲ್ಲಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ.\nಪ್ರತಿ 20 ನಿಮಿಷಕ್ಕೆ ಒಂದು ಲೋಟ ನೀರು ಕುಡಿಯಿರಿ.\nಕಡಿಮೆ ಅಪಾಯದ ಸಮಯ: {safe}",
        "alert": "⚠️ ಶಾಖದ ಅಪಾಯ ಈಗ {level}. {work} ನಿಮಿಷ ಕೆಲಸ, {rest} ನಿಮಿಷ ನೆರಳಿನಲ್ಲಿ ವಿಶ್ರಾಂತಿ. ಈಗ ನೀರು ಕುಡಿಯಿರಿ.",
        "firstaid": "ತಲೆಸುತ್ತು ಅಥವಾ ತಲೆನೋವು? ನೆರಳಿಗೆ ಹೋಗಿ, ನೀರು ಕುಡಿಯಿರಿ, ಬಟ್ಟೆ ಸಡಿಲಗೊಳಿಸಿ, ಒದ್ದೆ ಬಟ್ಟೆಯಿಂದ ತಲೆ-ಕತ್ತು ತಂಪುಗೊಳಿಸಿ.\n🚨 ಗೊಂದಲ, ಮೂರ್ಛೆ ಅಥವಾ ಬಿಸಿ ಒಣ ಚರ್ಮ (ಬೆವರಿಲ್ಲ) ಇದ್ದರೆ ತಕ್ಷಣ 108 ಕ್ಕೆ ಕರೆ ಮಾಡಿ.",
        "stop": "ನಿಮ್ಮ ಚಂದಾದಾರಿಕೆ ನಿಲ್ಲಿಸಲಾಗಿದೆ. ಮತ್ತೆ ಸೇರಲು /start ಕಳುಹಿಸಿ.", "nouser": "ಮೊದಲು /start ಕಳುಹಿಸಿ.",
        "disc": "ಈ ಮಾರ್ಗದರ್ಶನ ಕೆಲಸದ ಸ್ಥಳದ ಶಾಖ ಮಾನದಂಡಗಳ ಆಧಾರಿತ; ವೈದ್ಯಕೀಯ ಸಲಹೆ ಅಲ್ಲ.",
    },
}


def tr(lang: str) -> dict:
    return T.get(lang, T["en"])


def plan_text(lang: str, plan: dict, key: str = "plan") -> str:
    t = tr(lang)
    return t[key].format(level=t["levels"][plan["level"]], peak=plan["peak"],
                         safe=plan["safe"], work=plan["work"], rest=plan["rest"])

_EXTRA = {
    "en": {"acc_q": "Are you new to working in this heat (or back after 2+ weeks off)?",
           "risk_q": "Are you 45+ or do you have heart, BP or diabetes problems?", "yes": "Yes", "no": "No",
           "fb_hot": "🥵 Too hot", "fb_ok": "👍 Fine", "fb_thx": "Thanks, noted."},
    "hi": {"acc_q": "क्या आप इस गर्मी में काम करने में नए हैं (या 2+ हफ़्ते की छुट्टी के बाद लौटे हैं)?",
           "risk_q": "क्या आपकी उम्र 45+ है या दिल, बीपी या शुगर की समस्या है?", "yes": "हाँ", "no": "नहीं",
           "fb_hot": "🥵 बहुत गर्मी", "fb_ok": "👍 ठीक है", "fb_thx": "धन्यवाद।"},
    "kn": {"acc_q": "ನೀವು ಈ ಬಿಸಿಲಿನಲ್ಲಿ ಕೆಲಸಕ್ಕೆ ಹೊಸಬರೇ (ಅಥವಾ 2+ ವಾರ ರಜೆಯ ನಂತರ ಮರಳಿದ್ದೀರಾ)?",
           "risk_q": "ನಿಮಗೆ 45+ ವಯಸ್ಸೇ ಅಥವಾ ಹೃದಯ, ಬಿಪಿ ಅಥವಾ ಸಕ್ಕರೆ ಕಾಯಿಲೆ ಇದೆಯೇ?", "yes": "ಹೌದು", "no": "ಇಲ್ಲ",
           "fb_hot": "🥵 ತುಂಬಾ ಬಿಸಿ", "fb_ok": "👍 ಸರಿ", "fb_thx": "ಧನ್ಯವಾದ."},
}
for _l, _d in _EXTRA.items():
    T[_l].update(_d)
