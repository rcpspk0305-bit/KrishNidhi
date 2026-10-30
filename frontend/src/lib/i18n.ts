export const locales = ["en", "te", "hi"] as const;
export type Locale = (typeof locales)[number];
export const localeNames = { en: "English", te: "తెలుగు", hi: "हिन्दी" };
export const localeTags = { en: "en-IN", te: "te-IN", hi: "hi-IN" };

// English source messages map to Telugu and Hindi. Runtime values and API IDs stay unchanged.
export const messages: Record<string, readonly [string, string]> = {
  "Soil moisture forecast": ["నేల తేమ అంచనా", "मिट्टी की नमी का पूर्वानुमान"],
  "Estimated moisture in 1 hour": ["ఒక గంటలో అంచనా తేమ", "एक घंटे में अनुमानित नमी"],
  "Time to minimum moisture": ["కనిష్ఠ తేమకు సమయం", "न्यूनतम नमी तक समय"],
  "Forecast unavailable": ["అంచనా అందుబాటులో లేదు", "पूर्वानुमान उपलब्ध नहीं है"],
  "Sensor coverage": ["సెన్సార్ సమాచారం లభ్యత", "सेंसर डेटा की उपलब्धता"],
  "USB sensors connected. Pump control is unavailable; relay held OFF.": ["USB సెన్సార్లు అనుసంధానమయ్యాయి. పంపు నియంత్రణ అందుబాటులో లేదు; రిలే ఆఫ్‌లో ఉంది.", "USB सेंसर जुड़े हैं। पंप नियंत्रण उपलब्ध नहीं है; रिले बंद रखा गया है।"],
  "USB relay OFF": ["USB రిలే ఆఫ్", "USB रिले बंद"],
  "Device reported": ["పరికరం నివేదించింది", "डिवाइस द्वारा बताया गया"],
  "Relay held OFF": ["రిలే ఆఫ్‌లో ఉంది", "रिले बंद रखा गया है"],
  "Firmware configured": ["ఫర్మ్‌వేర్‌లో అమర్చబడింది", "फ़र्मवेयर में निर्धारित"],
  "Command {1} applied: Relay = {2}": [
    "ఆదేశం {1} అమలైంది: రిలే = {2}",
    "निर्देश {1} लागू हुआ: रिले = {2}",
  ],
  "The assistant’s request limit has been reached. Please try again later.": [
    "సహాయకుడి ప్రశ్నల పరిమితి పూర్తయింది. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
    "सहायक के अनुरोध की सीमा पूरी हो गई है। कृपया बाद में फिर कोशिश करें।",
  ],
  Language: ["భాష", "भाषा"],
  "Application language": ["అప్లికేషన్ భాష", "ऐप की भाषा"],
  "Ask AI": ["AIని అడగండి", "AI से पूछें"],
  "KrishiNidhi Assistant": ["కృషినిధి సహాయకుడు", "कृषिनिधि सहायक"],
  "Ask anything, in your language.": [
    "మీ భాషలో ఏ ప్రశ్నైనా అడగండి.",
    "अपनी भाषा में कोई भी सवाल पूछें।",
  ],
  "How can I help you today?": [
    "ఈ రోజు మీకు ఎలా సహాయపడగలను?",
    "आज मैं आपकी कैसे मदद कर सकता हूँ?",
  ],
  "Ask about plant care, irrigation, or farmer schemes.": [
    "మొక్కల సంరక్షణ, నీటిపారుదల లేదా రైతు పథకాల గురించి అడగండి.",
    "पौधों की देखभाल, सिंचाई या किसान योजनाओं के बारे में पूछें।",
  ],
  "Type your question…": ["మీ ప్రశ్నను టైప్ చేయండి…", "अपना सवाल लिखें…"],
  "Your question": ["మీ ప్రశ్న", "आपका सवाल"],
  "Send question": ["ప్రశ్న పంపండి", "सवाल भेजें"],
  "Stop response": ["సమాధానాన్ని ఆపండి", "जवाब रोकें"],
  "Close assistant": ["సహాయకుడిని మూసివేయండి", "सहायक बंद करें"],
  "Clear conversation": ["సంభాషణను తొలగించండి", "बातचीत साफ़ करें"],
  "Thinking…": ["ఆలోచిస్తోంది…", "सोच रहा है…"],
  You: ["మీరు", "आप"],
  "AI assistant": ["AI సహాయకుడు", "AI सहायक"],
  Retry: ["మళ్లీ ప్రయత్నించండి", "फिर कोशिश करें"],
  "AI replies are unavailable right now. Please try again later.": [
    "ప్రస్తుతం AI సమాధానాలు అందుబాటులో లేవు. దయచేసి కొంతసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.",
    "अभी AI के जवाब उपलब्ध नहीं हैं। कृपया कुछ देर बाद फिर कोशिश करें।",
  ],
  "The connection was interrupted. Please try again.": [
    "కనెక్షన్‌కు అంతరాయం కలిగింది. మళ్లీ ప్రయత్నించండి.",
    "कनेक्शन टूट गया। कृपया फिर कोशिश करें।",
  ],
  "AI can make mistakes. It cannot control your pump or read live sensors.": [
    "AI పొరపాట్లు చేయవచ్చు. ఇది మీ పంపును నియంత్రించదు; ప్రత్యక్ష సెన్సర్ సమాచారం దీనికి అందుబాటులో లేదు.",
    "AI से गलतियाँ हो सकती हैं। यह पंप नियंत्रित नहीं कर सकता और लाइव सेंसर नहीं पढ़ सकता।",
  ],
  "Explain this plant dashboard": [
    "ఈ మొక్కల డ్యాష్‌బోర్డ్‌ను వివరించండి",
    "इस पौधा डैशबोर्ड को समझाएँ",
  ],
  "Why is my device offline?": [
    "నా పరికరం ఆఫ్‌లైన్‌లో ఎందుకు ఉంది?",
    "मेरा उपकरण ऑफ़लाइन क्यों है?",
  ],
  "How often should I water a plant?": [
    "మొక్కకు ఎంత తరచుగా నీరు పోయాలి?",
    "पौधे को कितनी बार पानी देना चाहिए?",
  ],
  Portal: ["పోర్టల్", "पोर्टल"],
  Home: ["ముఖ్య పేజీ", "मुख्य पृष्ठ"],
  Dashboard: ["డ్యాష్‌బోర్డ్", "डैशबोर्ड"],
  Overview: ["అవలోకనం", "अवलोकन"],
  "KrishiNidhi Botanical IoT Suite": [
    "కృషినిధి మొక్కల IoT వ్యవస్థ",
    "कृषिनिधि पौधों की IoT प्रणाली",
  ],
  "NodeMCU ESP8266 • Server-Sent Events": [
    "NodeMCU ESP8266 • సర్వర్ నుంచి ప్రత్యక్ష నవీకరణలు",
    "NodeMCU ESP8266 • सर्वर से लाइव अपडेट",
  ],
  "Mindful Plant Telemetry & Fail-Safe Automated Irrigation.": [
    "మొక్కల పర్యవేక్షణ మరియు సురక్షిత స్వయంచాలక నీటిపారుదల.",
    "पौधों की निगरानी और सुरक्षित स्वचालित सिंचाई।",
  ],
  "A quieter, higher-fidelity workspace to monitor your plant's microclimate, observe soil hydration dynamics, and issue authoritative irrigation commands backed by hardware fail-safes and agronomic intelligence.":
    [
      "మీ మొక్క చుట్టూ వాతావరణం, నేల తేమను పర్యవేక్షించండి. పరికర భద్రతా నియమాలతో నీటిపారుదల ఆదేశాలను పంపండి.",
      "पौधे के आसपास का वातावरण और मिट्टी की नमी देखें। उपकरण के सुरक्षा नियमों के साथ सिंचाई के निर्देश भेजें।",
    ],
  "Launch Plant Workspace": [
    "మొక్కల కార్యస్థలాన్ని తెరవండి",
    "पौधा कार्यस्थल खोलें",
  ],
  "Agricultural Scheme Finder": ["వ్యవసాయ పథకాల శోధన", "कृषि योजनाएँ खोजें"],
  "Hardware-Authoritative": [
    "పరికరం ధృవీకరించిన స్థితి",
    "उपकरण द्वारा पुष्ट स्थिति",
  ],
  "Firmware acknowledgments represent true relay coil status.": [
    "ఫర్మ్‌వేర్ ధృవీకరణలు రిలే స్థితిని సూచిస్తాయి.",
    "फ़र्मवेयर की पुष्टि रिले की स्थिति बताती है।",
  ],
  "Watchdog Protection": ["రన్‌టైమ్ భద్రత", "रनटाइम सुरक्षा"],
  "15s runtime cutoff and 60s cooldown prevent water damage.": [
    "15 సెకన్ల పని పరిమితి, 60 సెకన్ల విరామం ఉన్నాయి.",
    "15 सेकंड चलने की सीमा और 60 सेकंड का विराम है।",
  ],
  "Live Telemetry Broadcast": [
    "ప్రత్యక్ష సెన్సర్ సమాచారం",
    "लाइव सेंसर जानकारी",
  ],
  "Sub-second SSE updates with graceful polling resilience.": [
    "SSE ద్వారా ప్రత్యక్ష నవీకరణలు, ప్రత్యామ్నాయంగా క్రమానుగత తనిఖీలు.",
    "SSE से लाइव अपडेट और विकल्प के रूप में नियमित जाँच।",
  ],
  "Smart Plant Monitor & Irrigation": [
    "మొక్కల పర్యవేక్షణ మరియు నీటిపారుదల",
    "पौधों की निगरानी और सिंचाई",
  ],
  "Primary Workspace": ["ప్రధాన కార్యస్థలం", "मुख्य कार्यस्थल"],
  "Real-time NodeMCU telemetry (DHT11, calibrated soil moisture, PIR motion), authoritative relay actuator, and AI agronomy insights.":
    [
      "ఉష్ణోగ్రత, నేల తేమ, కదలికల ప్రత్యక్ష సమాచారం, రిలే నియంత్రణ, మొక్కల సంరక్షణ సూచనలు.",
      "तापमान, मिट्टी की नमी और हलचल की लाइव जानकारी, रिले नियंत्रण और पौधों की देखभाल के सुझाव।",
    ],
  "Launch Workspace": ["కార్యస్థలాన్ని తెరవండి", "कार्यस्थल खोलें"],
  "Personal IoT Station": ["వ్యక్తిగత IoT కేంద్రం", "व्यक्तिगत IoT केंद्र"],
  "IoT Telemetry": ["IoT సెన్సర్ సమాచారం", "IoT सेंसर जानकारी"],
  "Dedicated responsive dashboard for continuous environmental tracking and virtual hardware testing.":
    [
      "నిరంతర వాతావరణ పర్యవేక్షణ, వర్చువల్ పరికర పరీక్షల డ్యాష్‌బోర్డ్.",
      "लगातार वातावरण की निगरानी और वर्चुअल उपकरण परीक्षण का डैशबोर्ड।",
    ],
  "Open Station": ["కేంద్రాన్ని తెరవండి", "केंद्र खोलें"],
  "Government Scheme Finder": ["ప్రభుత్వ పథకాల శోధన", "सरकारी योजनाएँ खोजें"],
  "Governance Directory": ["ప్రభుత్వ పథకాల జాబితా", "सरकारी योजनाओं की सूची"],
  "Search farmer and agricultural assistance schemes, subsidies, and eligibility criteria across regions.":
    [
      "రైతుల సహాయ పథకాలు, సబ్సిడీలు, అర్హత వివరాలను వెతకండి.",
      "किसान सहायता योजनाएँ, सब्सिडी और पात्रता की जानकारी खोजें।",
    ],
  "Explore Schemes": ["పథకాలను చూడండి", "योजनाएँ देखें"],
  "KrishiNidhi Botanical Systems • Department of Computer Science & Engineering":
    [
      "కృషినిధి మొక్కల వ్యవస్థలు • కంప్యూటర్ సైన్స్ మరియు ఇంజినీరింగ్ విభాగం",
      "कृषिनिधि पौधा प्रणाली • कंप्यूटर विज्ञान और इंजीनियरिंग विभाग",
    ],
  "NodeMCU ESP8266 ESP-12E Architecture • Next.js 16 • Warm Editorial Botanical Edition":
    [
      "NodeMCU ESP8266 ESP-12E • Next.js 16 • కృషినిధి",
      "NodeMCU ESP8266 ESP-12E • Next.js 16 • कृषिनिधि",
    ],
  "KrishiNidhi Station Login": ["కృషినిధి లాగిన్", "कृषिनिधि लॉगिन"],
  "Enter your credentials to access the plant monitoring console": [
    "మొక్కల పర్యవేక్షణ కోసం మీ లాగిన్ వివరాలు ఇవ్వండి",
    "पौधों की निगरानी के लिए अपना लॉगिन विवरण भरें",
  ],
  "MOBILE NUMBER": ["మొబైల్ నంబర్", "मोबाइल नंबर"],
  PASSWORD: ["పాస్‌వర్డ్", "पासवर्ड"],
  "Sign In to Console": ["లాగిన్ చేయండి", "लॉगिन करें"],
  "Demo credentials:": ["డెమో లాగిన్ వివరాలు:", "डेमो लॉगिन विवरण:"],
  "Invalid credentials. Try 9999999999 / krishi123": [
    "లాగిన్ వివరాలు తప్పు. 9999999999 / krishi123 ఉపయోగించండి",
    "लॉगिन विवरण गलत है। 9999999999 / krishi123 इस्तेमाल करें",
  ],
  "Return to Homepage": [
    "ముఖ్య పేజీకి తిరిగి వెళ్లండి",
    "मुख्य पृष्ठ पर लौटें",
  ],
  "Benefit Directory": ["ప్రయోజనాల జాబితా", "लाभ की सूची"],
  "Official Governance Portal": [
    "ప్రభుత్వ పథకాల సమాచారం",
    "सरकारी योजनाओं की जानकारी",
  ],
  "SCHEME FINDER": ["పథకాల శోధన", "योजनाएँ खोजें"],
  "Discover agricultural subsidies and support programs tailored to your field telemetry and regional classification.":
    [
      "మీ వ్యవసాయ అవసరాలకు అనుగుణంగా సబ్సిడీలు, సహాయ పథకాలను కనుగొనండి.",
      "अपनी कृषि ज़रूरतों के अनुसार सब्सिडी और सहायता योजनाएँ खोजें।",
    ],
  "Search by name or keyword...": [
    "పేరు లేదా పదంతో వెతకండి...",
    "नाम या शब्द से खोजें...",
  ],
  Eligibility: ["అర్హత", "पात्रता"],
  "Benefit Amount": ["ప్రయోజనం", "लाभ"],
  "Access Portal": ["పోర్టల్ తెరవండి", "पोर्टल खोलें"],
  All: ["అన్నీ", "सभी"],
  "Income Support": ["ఆదాయ సహాయం", "आय सहायता"],
  Insurance: ["బీమా", "बीमा"],
  "Soil Health": ["నేల ఆరోగ్యం", "मिट्टी का स्वास्थ्य"],
  Pension: ["పెన్షన్", "पेंशन"],
  Central: ["కేంద్ర", "केंद्र"],
  "Direct Benefit": ["ప్రత్యక్ష ప్రయోజనం", "प्रत्यक्ष लाभ"],
  "Risk Management": ["ప్రమాద నిర్వహణ", "जोखिम प्रबंधन"],
  Testing: ["పరీక్ష", "परीक्षण"],
  Fertility: ["సారవంతత", "उर्वरता"],
  "Old Age": ["వృద్ధాప్యం", "वृद्धावस्था"],
  Security: ["భద్రత", "सुरक्षा"],
  "Agronomic Health Intelligence": [
    "మొక్కల ఆరోగ్య విశ్లేషణ",
    "पौधों के स्वास्थ्य का विश्लेषण",
  ],
  "Deterministic Rule Engine & Natural Language Insights": [
    "నియమాల ఆధారిత విశ్లేషణ మరియు సులభమైన సూచనలు",
    "नियमों पर आधारित विश्लेषण और सरल सुझाव",
  ],
  "Risk:": ["ప్రమాదం:", "जोखिम:"],
  "95% Confidence": ["95% విశ్వాసం", "95% विश्वास"],
  "Agronomist Summary": ["వ్యవసాయ నిపుణుడి సారాంశం", "कृषि विशेषज्ञ का सारांश"],
  Environment: ["వాతావరణం", "वातावरण"],
  "Soil Moisture": ["నేల తేమ", "मिट्टी की नमी"],
  Temperature: ["ఉష్ణోగ్రత", "तापमान"],
  Humidity: ["గాలిలో తేమ", "हवा में नमी"],
  "Telemetry Observations": ["సెన్సర్ పరిశీలనలు", "सेंसर अवलोकन"],
  "Prescribed Next Steps": ["తదుపరి సూచనలు", "अगले सुझाव"],
  "Active System Alerts": ["ప్రస్తుత హెచ్చరికలు", "वर्तमान चेतावनियाँ"],
  "Active Agronomic & Hardware Alerts (": [
    "మొక్కలు మరియు పరికర హెచ్చరికలు (",
    "पौधे और उपकरण की चेतावनियाँ (",
  ],
  "Requires Attention": ["శ్రద్ధ అవసరం", "ध्यान देना ज़रूरी"],
  priority: ["ప్రాధాన్యత", "प्राथमिकता"],
  Acknowledge: ["చూసినట్లు గుర్తించండి", "देख लिया"],
  "ESP8266 Online": ["ESP8266 కనెక్ట్ అయింది", "ESP8266 जुड़ा है"],
  "ESP8266 Offline": ["ESP8266 ఆఫ్‌లైన్‌లో ఉంది", "ESP8266 ऑफ़लाइन है"],
  "Live SSE:": ["ప్రత్యక్ష సమాచారం:", "लाइव जानकारी:"],
  "Last packet:": ["చివరి సమాచారం:", "अंतिम जानकारी:"],
  Connected: ["కనెక్ట్ అయింది", "जुड़ा है"],
  "Syncing...": ["నవీకరిస్తోంది...", "अपडेट हो रहा है..."],
  Sync: ["నవీకరించండి", "अपडेट करें"],
  "just now": ["ఇప్పుడే", "अभी"],
  Offline: ["ఆఫ్‌లైన్", "ऑफ़लाइन"],
  "Hardware Linked": ["పరికరం కనెక్ట్ అయింది", "उपकरण जुड़ा है"],
  "Virtual Hardware Test Bench": [
    "వర్చువల్ పరికర పరీక్ష",
    "वर्चुअल उपकरण परीक्षण",
  ],
  "Simulate ESP8266 sensor packets and relay acknowledgments directly in the browser":
    [
      "బ్రౌజర్‌లో ESP8266 సెన్సర్ సమాచారం, రిలే ధృవీకరణలను పరీక్షించండి",
      "ब्राउज़र में ESP8266 सेंसर जानकारी और रिले की पुष्टि का परीक्षण करें",
    ],
  "Open Test Bench": ["పరీక్షను తెరవండి", "परीक्षण खोलें"],
  "Close Test Bench": ["పరీక్షను మూసివేయండి", "परीक्षण बंद करें"],
  "Temp (DHT11):": ["ఉష్ణోగ్రత (DHT11):", "तापमान (DHT11):"],
  "Humidity (DHT11):": ["తేమ (DHT11):", "नमी (DHT11):"],
  "Soil Moisture (A0):": ["నేల తేమ (A0):", "मिट्टी की नमी (A0):"],
  "PIR Motion:": ["PIR కదలిక:", "PIR हलचल:"],
  "Broadcast Telemetry Packet": [
    "సెన్సర్ సమాచారం పంపండి",
    "सेंसर जानकारी भेजें",
  ],
  "Start Firmware Auto-ACK": [
    "స్వయంచాలక ధృవీకరణ ప్రారంభించండి",
    "स्वचालित पुष्टि शुरू करें",
  ],
  "Stop Firmware Auto-ACK": [
    "స్వయంచాలక ధృవీకరణ ఆపండి",
    "स्वचालित पुष्टि रोकें",
  ],
  "ESP8266 Telemetry Workspace": [
    "ESP8266 పర్యవేక్షణ కార్యస్థలం",
    "ESP8266 निगरानी कार्यस्थल",
  ],
  "Health:": ["ఆరోగ్యం:", "स्वास्थ्य:"],
  "Mode:": ["మోడ్:", "मोड:"],
  "Telemetry Timestamp:": ["సెన్సర్ సమాచారం సమయం:", "सेंसर जानकारी का समय:"],
  "Agronomic Index": ["మొక్క ఆరోగ్య సూచిక", "पौधे का स्वास्थ्य सूचकांक"],
  "Control Mode": ["నియంత్రణ మోడ్", "नियंत्रण मोड"],
  "Return to Portal Homepage": [
    "పోర్టల్ ముఖ్య పేజీకి వెళ్లండి",
    "पोर्टल के मुख्य पृष्ठ पर जाएँ",
  ],
  "KrishiNidhi Botanical Console": [
    "కృషినిధి మొక్కల కేంద్రం",
    "कृषिनिधि पौधा केंद्र",
  ],
  "Smart Plant & Irrigation Station": [
    "మొక్కలు మరియు నీటిపారుదల కేంద్రం",
    "पौधा और सिंचाई केंद्र",
  ],
  "Synchronize plant data": [
    "మొక్క సమాచారాన్ని నవీకరించండి",
    "पौधे की जानकारी अपडेट करें",
  ],
  "Scheme Finder": ["పథకాల శోధన", "योजनाएँ खोजें"],
  "Telemetry is currently stale (>35s without packet). Displaying last known sensor readings.":
    [
      "35 సెకన్లుగా కొత్త సమాచారం రాలేదు. చివరగా అందిన సెన్సర్ విలువలు చూపిస్తున్నాం.",
      "35 सेकंड से नई जानकारी नहीं मिली। अंतिम सेंसर मान दिखाए जा रहे हैं।",
    ],
  "Retry Sync": ["మళ్లీ నవీకరించండి", "फिर अपडेट करें"],
  "“KrishiNidhi — Mindful environmental stewardship and botanical vitality.”": [
    "“కృషినిధి — పర్యావరణ సంరక్షణ మరియు మొక్కల జీవశక్తి.”",
    "“कृषिनिधि — पर्यावरण की देखभाल और पौधों की जीवंतता।”",
  ],
  "ESP8266 NodeMCU ESP-12E Architecture • Computer Science & Engineering Final Project • Warm Editorial Botanical Edition":
    [
      "ESP8266 NodeMCU ESP-12E • కంప్యూటర్ సైన్స్ మరియు ఇంజినీరింగ్ ప్రాజెక్ట్",
      "ESP8266 NodeMCU ESP-12E • कंप्यूटर विज्ञान और इंजीनियरिंग प्रोजेक्ट",
    ],
  "Irrigation Pump Controller": [
    "నీటిపారుదల పంపు నియంత్రణ",
    "सिंचाई पंप नियंत्रण",
  ],
  "Relay IN: GPIO 14 (D5) • Active-LOW Optocoupled": [
    "రిలే: GPIO 14 (D5) • Active-LOW",
    "रिले: GPIO 14 (D5) • Active-LOW",
  ],
  "... Awaiting ESP8266 acknowledgment packet.": [
    "... ESP8266 ధృవీకరణ కోసం వేచి ఉంది.",
    "... ESP8266 की पुष्टि की प्रतीक्षा है।",
  ],
  "OPERATING MODE": ["పనిచేసే మోడ్", "कार्य मोड"],
  "MANUAL RELAY ACTUATION": ["మాన్యువల్ రిలే నియంత్రణ", "मैनुअल रिले नियंत्रण"],
  "Last Watering": ["చివరిసారి నీరు పోసిన సమయం", "अंतिम सिंचाई"],
  "Current Run": ["ప్రస్తుత పని సమయం", "वर्तमान संचालन समय"],
  "State Authority": ["స్థితి ధృవీకరణ", "स्थिति की पुष्टि"],
  "Firmware Verified": ["ఫర్మ్‌వేర్ ధృవీకరించింది", "फ़र्मवेयर द्वारा पुष्ट"],
  "Watchdog:": ["భద్రతా పరిమితి:", "सुरक्षा सीमा:"],
  "15s limit": ["15 సెకన్ల పరిమితి", "15 सेकंड की सीमा"],
  "Cooldown:": ["విరామం:", "विराम:"],
  "60s safety lockout": [
    "60 సెకన్ల భద్రతా విరామం",
    "60 सेकंड का सुरक्षा विराम",
  ],
  "Default:": ["ప్రారంభ స్థితి:", "शुरुआती स्थिति:"],
  "Safe Boot OFF": ["సురక్షిత ప్రారంభం: ఆఫ్", "सुरक्षित शुरुआत: बंद"],
  "Ambient Temp (DHT11)": ["గది ఉష్ణోగ్రత (DHT11)", "कमरे का तापमान (DHT11)"],
  "Target: 18.0°C – 30.0°C": [
    "లక్ష్యం: 18.0°C – 30.0°C",
    "लक्ष्य: 18.0°C – 30.0°C",
  ],
  "Relative Humidity": ["సాపేక్ష ఆర్ద్రత", "सापेक्ष आर्द्रता"],
  "Target: 50% – 75% RH": ["లక్ష్యం: 50% – 75% RH", "लक्ष्य: 50% – 75% RH"],
  "Soil Moisture (LM393)": ["నేల తేమ (LM393)", "मिट्टी की नमी (LM393)"],
  "Raw:": ["మూల విలువ:", "मूल मान:"],
  "Auto-on: <30%": ["స్వయంచాలక ప్రారంభం: <30%", "स्वचालित शुरुआत: <30%"],
  "Target cutoff: 55%": ["ఆపే లక్ష్యం: 55%", "बंद करने का लक्ष्य: 55%"],
  "PIR Motion Sensor": ["PIR కదలిక సెన్సర్", "PIR हलचल सेंसर"],
  "Passive infrared detection around planter perimeter.": [
    "మొక్క చుట్టూ కదలికలను గుర్తిస్తుంది.",
    "पौधे के आसपास हलचल पहचानता है।",
  ],
  "Environmental Telemetry Trends": [
    "వాతావరణ సమాచారం ధోరణులు",
    "वातावरण के आँकड़ों का रुझान",
  ],
  "Chronological Microclimate Log from NodeMCU": [
    "NodeMCU వాతావరణ సమాచారం చరిత్ర",
    "NodeMCU के वातावरण की जानकारी का इतिहास",
  ],
  "No historical telemetry points found. Telemetry will plot here once received from ESP8266.":
    [
      "ఇంకా సెన్సర్ చరిత్ర లేదు. ESP8266 నుంచి సమాచారం అందినప్పుడు ఇక్కడ కనిపిస్తుంది.",
      "अभी सेंसर का इतिहास नहीं है। ESP8266 से जानकारी आने पर यहाँ दिखेगा।",
    ],
  Optimal: ["అనుకూలం", "अनुकूल"],
  "Needs Attention": ["శ్రద్ధ అవసరం", "ध्यान देना ज़रूरी"],
  "Needs Water": ["నీరు అవసరం", "पानी चाहिए"],
  "Over-watered": ["అధికంగా నీరు పోశారు", "ज़रूरत से ज़्यादा पानी"],
  "No Telemetry": ["సెన్సర్ సమాచారం లేదు", "सेंसर जानकारी नहीं है"],
  low: ["తక్కువ", "कम"],
  medium: ["మధ్యస్థం", "मध्यम"],
  high: ["అధికం", "अधिक"],
  critical: ["తీవ్రం", "गंभीर"],
  AUTO: ["స్వయంచాలకం", "स्वचालित"],
  MANUAL: ["మాన్యువల్", "मैनुअल"],
  OFF: ["ఆఫ్", "बंद"],
  ON: ["ఆన్", "चालू"],
  "Pending read": ["సమాచారం కోసం వేచి ఉంది", "जानकारी की प्रतीक्षा"],
  "N/A": ["అందుబాటులో లేదు", "उपलब्ध नहीं"],
  "Optimal Microclimate": ["అనుకూల వాతావరణం", "अनुकूल वातावरण"],
  "Temperature Variance": ["ఉష్ణోగ్రత వ్యత్యాసం", "तापमान में अंतर"],
  "Comfort Zone": ["అనుకూల స్థాయి", "अनुकूल स्तर"],
  "Sub-optimal VPD": ["అనుకూలం కాని VPD", "कम अनुकूल VPD"],
  "Motion Detected": ["కదలిక గుర్తించబడింది", "हलचल मिली"],
  "Motion Active": ["కదలిక ఉంది", "हलचल है"],
  "Field Clear": ["కదలిక లేదు", "हलचल नहीं"],
  "None recorded": ["ఇంకా నమోదు కాలేదు", "अभी दर्ज नहीं"],
  "Active in MANUAL Mode Only": [
    "మాన్యువల్ మోడ్‌లో మాత్రమే అందుబాటులో ఉంటుంది",
    "केवल मैनुअल मोड में उपलब्ध",
  ],
  "Failed to switch mode": ["మోడ్ మార్చలేకపోయాం", "मोड नहीं बदल पाया"],
  "Failed to submit pump command": [
    "పంపు ఆదేశం పంపలేకపోయాం",
    "पंप का निर्देश नहीं भेज पाया",
  ],
  "Attention Recommended": ["శ్రద్ధ సిఫార్సు చేయబడింది", "ध्यान देने की सलाह"],
  "Intervention Required": ["చర్య అవసరం", "कार्रवाई ज़रूरी"],
  "Awaiting sensor broadcast": [
    "సెన్సర్ సమాచారం కోసం వేచి ఉంది",
    "सेंसर जानकारी की प्रतीक्षा",
  ],
  "Indoor Botanical Specimen": ["ఇంటి మొక్క", "घर का पौधा"],
  Soil: ["నేల", "मिट्टी"],
  Temp: ["ఉష్ణోగ్రత", "तापमान"],
  Pump: ["పంపు", "पंप"],
  "All Sensors": ["అన్ని సెన్సర్లు", "सभी सेंसर"],
  "Response stopped.": ["సమాధానం ఆపబడింది.", "जवाब रोक दिया गया।"],
  "Nominal Indoor": ["సాధారణ ఇంటి వాతావరణం", "सामान्य घरेलू वातावरण"],
  "Optimal Zone": ["అనుకూల స్థాయి", "अनुकूल स्तर"],
  "Thermal Comfort": ["అనుకూల ఉష్ణోగ్రత", "अनुकूल तापमान"],
  "Balanced VPD": ["సమతుల్య VPD", "संतुलित VPD"],
  "Telemetry-grounded agronomic rules. LLM operates strictly in advisory capacity.":
    [
      "సెన్సర్ సమాచారం ఆధారంగా సూచనలు. AI సలహా మాత్రమే ఇస్తుంది.",
      "सेंसर जानकारी पर आधारित सुझाव। AI केवल सलाह देता है।",
    ],
  "Relay Closed (Irrigating)": [
    "రిలే మూసివేయబడింది (పంపు ఆన్)",
    "रिले बंद संपर्क (पंप चालू)",
  ],
  "Relay Open (Standby)": [
    "రిలే తెరిచి ఉంది (విశ్రాంతి)",
    "रिले खुला संपर्क (प्रतीक्षा)",
  ],
  "Turn Off Pump (Manual)": [
    "పంపును ఆపండి (మాన్యువల్)",
    "पंप बंद करें (मैनुअल)",
  ],
  "Actuate Pump (Manual)": [
    "పంపును ప్రారంభించండి (మాన్యువల్)",
    "पंप चालू करें (मैनुअल)",
  ],
  "0s (Standby)": ["0 సెకన్లు (విశ్రాంతి)", "0 सेकंड (प्रतीक्षा)"],
  "Manual pump actuation is restricted to MANUAL mode. Please switch modes first.":
    [
      "పంపు నియంత్రణ మాన్యువల్ మోడ్‌లో మాత్రమే అందుబాటులో ఉంటుంది. ముందుగా మోడ్ మార్చండి.",
      "पंप का नियंत्रण केवल मैनुअल मोड में उपलब्ध है। पहले मोड बदलें।",
    ],
  "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)": [
    "పీఎం-కిసాన్ (ప్రధాన మంత్రి కిసాన్ సమ్మాన్ నిధి)",
    "पीएम-किसान (प्रधानमंत्री किसान सम्मान निधि)",
  ],
  "Pradhan Mantri Fasal Bima Yojana (PMFBY)": [
    "ప్రధాన మంత్రి ఫసల్ బీమా యోజన (PMFBY)",
    "प्रधानमंत्री फ़सल बीमा योजना (PMFBY)",
  ],
  "Soil Health Card Scheme": [
    "భూసార పరీక్ష కార్డు పథకం",
    "मृदा स्वास्थ्य कार्ड योजना",
  ],
  "PM-KMY (Pradhan Mantri Kisan Maandhan Yojana)": [
    "పీఎం-కేఎంవై (ప్రధాన మంత్రి కిసాన్ మాన్‌ధన్ యోజన)",
    "पीएम-केएमवाई (प्रधानमंत्री किसान मानधन योजना)",
  ],
  "₹6,000 per year in three installments": [
    "ఏటా మూడు విడతల్లో ₹6,000",
    "हर वर्ष तीन किस्तों में ₹6,000",
  ],
  "All landholding farmer families": [
    "భూమి కలిగిన రైతు కుటుంబాలు",
    "भूमिधारक किसान परिवार",
  ],
  "A central sector scheme providing income support to all landholding farmers' families in the country to supplement their financial needs.":
    [
      "భూమి కలిగిన రైతు కుటుంబాలకు ఆర్థిక అవసరాల కోసం ఆదాయ సహాయం అందించే కేంద్ర ప్రభుత్వ పథకం.",
      "भूमिधारक किसान परिवारों की आर्थिक ज़रूरतों के लिए आय सहायता देने वाली केंद्रीय योजना।",
    ],
  "Financial support to farmers suffering crop loss/damage": [
    "పంట నష్టపోయిన రైతులకు ఆర్థిక సహాయం",
    "फ़सल के नुकसान पर किसानों को आर्थिक सहायता",
  ],
  "All farmers including sharecroppers and tenant farmers": [
    "కౌలు రైతులు సహా రైతులందరూ",
    "बटाईदार और किरायेदार सहित सभी किसान",
  ],
  "Yield-based crop insurance scheme that provides financial support to farmers for crop failure due to natural calamities, pests & diseases.":
    [
      "ప్రకృతి విపత్తులు, చీడపీడలు, వ్యాధుల వల్ల పంట నష్టానికి ఆర్థిక సహాయం అందించే పంట బీమా పథకం.",
      "प्राकृतिक आपदाओं, कीटों और रोगों से फ़सल के नुकसान पर सहायता देने वाली फ़सल बीमा योजना।",
    ],
  "Testing soil and providing nutrition recommendations": [
    "నేలను పరీక్షించి పోషకాల సూచనలు అందించడం",
    "मिट्टी की जाँच और पोषक तत्वों के सुझाव",
  ],
  "All farmers with land holdings": [
    "భూమి కలిగిన రైతులందరూ",
    "भूमिधारक सभी किसान",
  ],
  "Promotes soil test based and balanced use of fertilizers to enable farmers to realize higher yields at lower cost.":
    [
      "నేల పరీక్షల ఆధారంగా ఎరువులను సమతుల్యంగా ఉపయోగించి తక్కువ ఖర్చుతో మంచి దిగుబడి పొందేందుకు ప్రోత్సహిస్తుంది.",
      "मिट्टी की जाँच के आधार पर संतुलित उर्वरक उपयोग से कम लागत में बेहतर पैदावार को बढ़ावा देता है।",
    ],
  "Monthly pension of ₹3,000": [
    "నెలకు ₹3,000 పెన్షన్",
    "हर महीने ₹3,000 पेंशन",
  ],
  "Small and marginal farmers aged 18-40 years": [
    "18–40 ఏళ్ల చిన్న, సన్నకారు రైతులు",
    "18–40 वर्ष के छोटे और सीमांत किसान",
  ],
  "A voluntary and contributory pension scheme for small and marginal farmers to provide social security in their old age.":
    [
      "చిన్న, సన్నకారు రైతులకు వృద్ధాప్యంలో సామాజిక భద్రత అందించే స్వచ్ఛంద చందా పెన్షన్ పథకం.",
      "छोटे और सीमांत किसानों को वृद्धावस्था में सामाजिक सुरक्षा देने वाली स्वैच्छिक अंशदायी पेंशन योजना।",
    ],
  "No matching schemes found.": [
    "సరిపోయే పథకాలు కనిపించలేదు.",
    "कोई मिलती-जुलती योजना नहीं मिली।",
  ],
  "Try another search or category.": [
    "వేరే పదం లేదా విభాగంతో వెతకండి.",
    "दूसरा शब्द या श्रेणी चुनें।",
  ],
  "Soil Moisture (%)": ["నేల తేమ (%)", "मिट्टी की नमी (%)"],
  "Temperature (°C)": ["ఉష్ణోగ్రత (°C)", "तापमान (°C)"],
  "Humidity (% RH)": ["గాలిలో తేమ (% RH)", "हवा में नमी (% RH)"],
  "Pump Relay Active (0/100%)": [
    "పంపు రిలే స్థితి (0/100%)",
    "पंप रिले की स्थिति (0/100%)",
  ],
  "{1}s ago": ["{1} సెకన్ల క్రితం", "{1} सेकंड पहले"],
  "{1}s (Active)": ["{1} సెకన్లు (పనిచేస్తోంది)", "{1} सेकंड (सक्रिय)"],
  "Switching operating mode to {1}": [
    "మోడ్‌ను {1}కు మారుస్తోంది",
    "मोड {1} में बदल रहा है",
  ],
  "Commanding pump relay {1}": [
    "పంపు రిలేకు {1} ఆదేశం పంపుతోంది",
    "पंप रिले को {1} का निर्देश भेज रहा है",
  ],
  "ESP8266 hardware is {1}": ["ESP8266 పరికరం {1}", "ESP8266 उपकरण {1}"],
  "Live telemetry stream is {1}": ["ప్రత్యక్ష సమాచారం {1}", "लाइव जानकारी {1}"],
  connected: ["కనెక్ట్ అయింది", "जुड़ा है"],
  offline: ["ఆఫ్‌లైన్‌లో ఉంది", "ऑफ़लाइन है"],
  active: ["అందుబాటులో ఉంది", "सक्रिय है"],
  reconnecting: ["తిరిగి కనెక్ట్ అవుతోంది", "फिर जुड़ रहा है"],
  "Sensor data pending": [
    "సెన్సర్ సమాచారం కోసం వేచి ఉంది",
    "सेंसर जानकारी की प्रतीक्षा",
  ],
  "Awaiting Telemetry": [
    "సెన్సర్ సమాచారం కోసం వేచి ఉంది",
    "सेंसर जानकारी की प्रतीक्षा",
  ],
  "No sensor data received yet from the device.": [
    "పరికరం నుంచి ఇంకా సెన్సర్ సమాచారం రాలేదు.",
    "उपकरण से अभी सेंसर जानकारी नहीं मिली।",
  ],
  "Check ESP8266 power supply and Wi-Fi connection.": [
    "ESP8266 విద్యుత్ సరఫరా, వై-ఫై కనెక్షన్‌ను తనిఖీ చేయండి.",
    "ESP8266 की बिजली और वाई-फ़ाई कनेक्शन जाँचें।",
  ],
  "Irrigation cycle recommended. In AUTO mode, the ESP8266 will trigger safe watering.":
    [
      "నీరు పోయడం సిఫార్సు చేయబడింది. స్వయంచాలక మోడ్‌లో ESP8266 పరికరం నీటిపారుదలను నియంత్రిస్తుంది.",
      "सिंचाई की सलाह है। स्वचालित मोड में ESP8266 उपकरण सिंचाई नियंत्रित करता है।",
    ],
  "Temporarily pause irrigation. Ensure proper drainage in the planter.": [
    "తాత్కాలికంగా నీటిపారుదలను ఆపి, కుండలో నీరు బయటకు వెళ్లేలా చూడండి.",
    "कुछ समय सिंचाई रोकें और गमले में पानी निकलने की व्यवस्था जाँचें।",
  ],
  "Provide shade or increase ventilation to prevent thermal transpiration shock.":
    [
      "వేడి ప్రభావాన్ని తగ్గించేందుకు నీడ లేదా గాలి ప్రసరణ పెంచండి.",
      "गर्मी का प्रभाव कम करने के लिए छाया या हवा का प्रवाह बढ़ाएँ।",
    ],
  "Move plant away from cold drafts or provide passive thermal insulation.": [
    "మొక్కను చల్లని గాలికి దూరంగా ఉంచండి.",
    "पौधे को ठंडी हवा से दूर रखें।",
  ],
  "Increase air circulation to minimize fungal pathogen risk.": [
    "శిలీంధ్రాల ప్రమాదాన్ని తగ్గించేందుకు గాలి ప్రసరణ పెంచండి.",
    "फफूँद का जोखिम घटाने के लिए हवा का प्रवाह बढ़ाएँ।",
  ],
  "Mist foliage or raise ambient relative humidity.": [
    "ఆకులపై తేలికగా నీరు పిచికారీ చేయండి లేదా గాలిలో తేమ పెంచండి.",
    "पत्तियों पर हल्का पानी छिड़कें या हवा में नमी बढ़ाएँ।",
  ],
  "Current environmental conditions match the profile. Continue routine monitoring.":
    [
      "ప్రస్తుత వాతావరణం మొక్క అవసరాలకు అనుకూలంగా ఉంది. పర్యవేక్షణ కొనసాగించండి.",
      "मौजूदा वातावरण पौधे की ज़रूरतों के अनुकूल है। निगरानी जारी रखें।",
    ],
  "below target": ["లక్ష్యం కంటే తక్కువ", "लक्ष्य से कम"],
  optimal: ["అనుకూలం", "अनुकूल"],
  saturated: ["అధిక తేమ", "अधिक नमी"],
  warm: ["వేడిగా ఉంది", "गर्म"],
  cool: ["చల్లగా ఉంది", "ठंडा"],
  abnormal: ["అనుకూలంగా లేదు", "असामान्य"],
  "Sensor reading in progress": [
    "సెన్సర్ సమాచారం అందుతోంది",
    "सेंसर जानकारी आ रही है",
  ],
  "Awaiting first telemetry packet from physical hardware.": [
    "పరికరం నుంచి మొదటి సెన్సర్ సమాచారం కోసం వేచి ఉంది.",
    "उपकरण से पहली सेंसर जानकारी की प्रतीक्षा है।",
  ],
  "Deterministic assessment based on calibrated soil moisture, DHT11 microclimate data, and botanical reference parameters. Does not replace lab soil testing.":
    [
      "నేల తేమ, DHT11 సెన్సర్ సమాచారం, మొక్క అవసరాల ఆధారంగా సూచనలు. ఇది ప్రయోగశాల నేల పరీక్షకు ప్రత్యామ్నాయం కాదు.",
      "मिट्टी की नमी, DHT11 सेंसर और पौधे की ज़रूरतों पर आधारित सुझाव। यह प्रयोगशाला की मिट्टी जाँच का विकल्प नहीं है।",
    ],
  "No sensor telemetry received yet from the device.": [
    "పరికరం నుంచి ఇంకా సెన్సర్ సమాచారం రాలేదు.",
    "उपकरण से अभी सेंसर जानकारी नहीं मिली।",
  ],
  "Critical Alert": ["తీవ్ర హెచ్చరిక", "गंभीर चेतावनी"],
  Confidence: ["విశ్వాస స్థాయి", "विश्वास स्तर"],
  "Soil moisture is critically low at {1}% (target: {2}%–{3}%).": [
    "నేల తేమ {1}% వద్ద చాలా తక్కువగా ఉంది (లక్ష్యం: {2}%–{3}%).",
    "मिट्टी की नमी {1}% पर बहुत कम है (लक्ष्य: {2}%–{3}%)।",
  ],
  "Soil is saturated at {1}%. High risk of root hypoxia or root rot.": [
    "నేల తేమ {1}% వద్ద అధికంగా ఉంది. వేర్లకు గాలి అందకపోవడం లేదా కుళ్లు వచ్చే ప్రమాదం ఉంది.",
    "मिट्टी में {1}% पर बहुत नमी है। जड़ों को हवा न मिलने या सड़ने का जोखिम है।",
  ],
  "Soil moisture is optimal at {1}% within healthy root zone bounds.": [
    "నేల తేమ {1}% వద్ద అనుకూలంగా ఉంది.",
    "मिट्टी की नमी {1}% पर अनुकूल है।",
  ],
  "Ambient temperature ({1}°C) exceeds preferred upper threshold ({2}°C).": [
    "గది ఉష్ణోగ్రత ({1}°C) గరిష్ఠ లక్ష్యం ({2}°C) కంటే ఎక్కువగా ఉంది.",
    "कमरे का तापमान ({1}°C) ऊपरी लक्ष्य ({2}°C) से अधिक है।",
  ],
  "Ambient temperature ({1}°C) is below minimum threshold ({2}°C).": [
    "గది ఉష్ణోగ్రత ({1}°C) కనిష్ఠ లక్ష్యం ({2}°C) కంటే తక్కువగా ఉంది.",
    "कमरे का तापमान ({1}°C) न्यूनतम लक्ष्य ({2}°C) से कम है।",
  ],
  "Temperature is stable at {1}°C (target {2}–{3}°C).": [
    "ఉష్ణోగ్రత {1}°C వద్ద స్థిరంగా ఉంది (లక్ష్యం {2}–{3}°C).",
    "तापमान {1}°C पर स्थिर है (लक्ष्य {2}–{3}°C)।",
  ],
  "VPD is low ({1} kPa); high humidity limits natural transpiration.": [
    "VPD తక్కువగా ఉంది ({1} kPa); అధిక తేమ వల్ల సహజ నీటి ఆవిరి తగ్గుతుంది.",
    "VPD कम है ({1} kPa); अधिक नमी से प्राकृतिक वाष्पोत्सर्जन घटता है।",
  ],
  "VPD is elevated ({1} kPa); dry air causes accelerated moisture loss.": [
    "VPD ఎక్కువగా ఉంది ({1} kPa); పొడి గాలి వల్ల తేమ త్వరగా తగ్గుతుంది.",
    "VPD अधिक है ({1} kPa); सूखी हवा से नमी जल्दी घटती है।",
  ],
  "Vapor Pressure Deficit is balanced at {1} kPa.": [
    "VPD {1} kPa వద్ద సమతుల్యంగా ఉంది.",
    "VPD {1} kPa पर संतुलित है।",
  ],
  "Soil dry-down rate is ~{1}% moisture loss per hour.": [
    "గంటకు సుమారు {1}% చొప్పున నేల తేమ తగ్గుతోంది.",
    "मिट्टी की नमी हर घंटे लगभग {1}% घट रही है।",
  ],
  "Critically dry soil: {1}% is below minimum threshold ({2}%).": [
    "నేల చాలా పొడిగా ఉంది: {1}% కనిష్ఠ లక్ష్యం ({2}%) కంటే తక్కువ.",
    "मिट्टी बहुत सूखी है: {1}% न्यूनतम लक्ष्य ({2}%) से कम है।",
  ],
  "High ambient temperature: {1}°C exceeds threshold ({2}°C).": [
    "అధిక ఉష్ణోగ్రత: {1}°C లక్ష్యం ({2}°C) కంటే ఎక్కువ.",
    "अधिक तापमान: {1}°C लक्ष्य ({2}°C) से अधिक है।",
  ],
  "PIR sensor detected activity near the plant planter.": [
    "PIR సెన్సర్ మొక్క దగ్గర కదలిక గుర్తించింది.",
    "PIR सेंसर ने पौधे के पास हलचल पहचानी।",
  ],
};

const entities: Record<string, string> = {
  amp: "&",
  apos: "'",
  quot: '"',
  bull: "•",
  gt: ">",
  lt: "<",
  ldquo: "“",
  rdquo: "”",
  nbsp: " ",
};
export function normalizeMessage(value: string): string {
  return value
    .replace(
      /&([a-z]+);/g,
      (original, name: string) => entities[name] || original,
    )
    .replace(/\s+/g, " ")
    .trim();
}

export function translate(
  value: string | number | null | undefined,
  locale: Locale,
): string {
  const source = String(value ?? "");
  if (locale === "en") return source;
  const translated = messages[normalizeMessage(source)];
  if (translated) return translated[locale === "te" ? 0 : 1];
  const patterns: readonly [RegExp, string][] = [
    [
      /^Command (.+) applied: Relay = (ON|OFF)$/,
      "Command {1} applied: Relay = {2}",
    ],
    [/^(\d+(?:\.\d+)?)s ago$/, "{1}s ago"],
    [/^(\d+)s \(Active\)$/, "{1}s (Active)"],
    [
      /^Switching operating mode to (AUTO|MANUAL|OFF)$/,
      "Switching operating mode to {1}",
    ],
    [/^Commanding pump relay (ON|OFF)$/, "Commanding pump relay {1}"],
    [/^ESP8266 hardware is (connected|offline)$/, "ESP8266 hardware is {1}"],
    [
      /^Live telemetry stream is (active|reconnecting)$/,
      "Live telemetry stream is {1}",
    ],
    [
      /^Soil moisture is critically low at ([\d.]+)% \(target: ([\d.]+)%[–-]([\d.]+)%\)\.$/,
      "Soil moisture is critically low at {1}% (target: {2}%–{3}%).",
    ],
    [
      /^Soil is saturated at ([\d.]+)%\. High risk of root hypoxia or root rot\.$/,
      "Soil is saturated at {1}%. High risk of root hypoxia or root rot.",
    ],
    [
      /^Soil moisture is optimal at ([\d.]+)% within healthy root zone bounds\.$/,
      "Soil moisture is optimal at {1}% within healthy root zone bounds.",
    ],
    [
      /^Ambient temperature \(([\d.-]+)°C\) exceeds preferred upper threshold \(([\d.-]+)°C\)\.$/,
      "Ambient temperature ({1}°C) exceeds preferred upper threshold ({2}°C).",
    ],
    [
      /^Ambient temperature \(([\d.-]+)°C\) is below minimum threshold \(([\d.-]+)°C\)\.$/,
      "Ambient temperature ({1}°C) is below minimum threshold ({2}°C).",
    ],
    [
      /^Temperature is stable at ([\d.-]+)°C \(target ([\d.-]+)[–-]([\d.-]+)°C\)\.$/,
      "Temperature is stable at {1}°C (target {2}–{3}°C).",
    ],
    [
      /^VPD is low \(([\d.]+) kPa\); high humidity limits natural transpiration\.$/,
      "VPD is low ({1} kPa); high humidity limits natural transpiration.",
    ],
    [
      /^VPD is elevated \(([\d.]+) kPa\); dry air causes accelerated moisture loss\.$/,
      "VPD is elevated ({1} kPa); dry air causes accelerated moisture loss.",
    ],
    [
      /^Vapor Pressure Deficit is balanced at ([\d.]+) kPa\.$/,
      "Vapor Pressure Deficit is balanced at {1} kPa.",
    ],
    [
      /^Soil dry-down rate is ~([\d.]+)% moisture loss per hour\.$/,
      "Soil dry-down rate is ~{1}% moisture loss per hour.",
    ],
    [
      /^Critically dry soil: ([\d.]+)% is below minimum threshold \(([\d.]+)%\)\.$/,
      "Critically dry soil: {1}% is below minimum threshold ({2}%).",
    ],
    [
      /^High ambient temperature: ([\d.-]+)°C exceeds threshold \(([\d.-]+)°C\)\.$/,
      "High ambient temperature: {1}°C exceeds threshold ({2}°C).",
    ],
  ];
  for (const [pattern, key] of patterns) {
    const match = source.match(pattern);
    if (match)
      return translate(key, locale).replace(/\{(\d+)\}/g, (_, index: string) =>
        translate(match[Number(index)], locale),
      );
  }
  return source.replace(
    /\((below target|optimal|saturated|warm|cool|abnormal)\)/g,
    (_, word: string) => `(${translate(word, locale)})`,
  );
}

export function isLocale(value: unknown): value is Locale {
  return typeof value === "string" && locales.includes(value as Locale);
}
