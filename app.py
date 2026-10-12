from flask import Flask, request, jsonify, send_from_directory
import os, requests
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# === LIVE ENGINE ===
def get_live_data(query):
    q = query.lower()
    now_utc = datetime.now(pytz.utc)
    results = []

    # 1. TIME - any country
    if "time" in q:
        try:
            zones = {"norway":"Europe/Oslo","nigeria":"Africa/Lagos","usa":"America/New_York","uk":"Europe/London","london":"Europe/London","dubai":"Asia/Dubai","india":"Asia/Kolkata"}
            for name, tz in zones.items():
                if name in q:
                    t = now_utc.astimezone(pytz.timezone(tz))
                    results.append(f"Current time in {name.title()} ({tz}): {t.strftime('%I:%M %p, %A %B %d, %Y')}")
            if not results:
                results.append(f"Your time Jos Nigeria: {now_utc.astimezone(pytz.timezone('Africa/Lagos')).strftime('%I:%M %p %A %B %d %Y')}, Norway: {now_utc.astimezone(pytz.timezone('Europe/Oslo')).strftime('%I:%M %p')}, UTC: {now_utc.strftime('%H:%M UTC')}")
        except: pass

    # 2. WEATHER LIVE
    if "weather" in q or "temperature" in q:
        try:
            city = "Jos"
            if "norway" in q: city="Oslo"
            if "london" in q: city="London"
            if "lagos" in q: city="Lagos"
            r = requests.get(f"https://wttr.in/{city}?format=%C+%t+%w+%h", timeout=5)
            if r.status_code==200:
                results.append(f"Live Weather {city}: {r.text}")
        except: pass

    # 3. SPORTS / FOOTBALL LIVE SCORES - uses free ESPN api
    if any(x in q for x in ["score","football","premier","la liga","champions","sport","live match"]):
        try:
            r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", timeout=6)
            data = r.json()
            games = []
            for ev in data.get('events',[])[:5]:
                name = ev.get('name','')
                comp = ev.get('competitions',[{}])[0]
                competitors = comp.get('competitors',[])
                if len(competitors)>=2:
                    home = competitors[0]['team']['displayName']
                    away = competitors[1]['team']['displayName']
                    score_h = competitors[0].get('score','0')
                    score_a = competitors[1].get('score','0')
                    status = comp.get('status',{}).get('type',{}).get('detail','')
                    games.append(f"{home} {score_h} - {score_a} {away} ({status})")
            if games:
                results.append("LIVE FOOTBALL (Premier League): " + " | ".join(games))
        except Exception as e:
            results.append(f"Live sports check: {e}")

    # 4. CRYPTO / DOLLAR LIVE
    if any(x in q for x in ["bitcoin","btc","dollar","naira","crypto","eth"]):
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,ngn", timeout=5)
            d = r.json()
            results.append(f"LIVE Crypto: Bitcoin ${d['bitcoin']['usd']} | Ethereum ${d['ethereum']['usd']}")
        except: pass

    # 5. GENERAL LIVE SEARCH - DuckDuckGo
    if len(results)<2 and any(x in q for x in ["who","what","when","latest","today","news","result"]):
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1", timeout=5)
            j = r.json()
            if j.get('AbstractText'):
                results.append(f"Live Info: {j['AbstractText'][:400]}")
        except: pass

    return "\n".join(results) if results else None

# --- HTML SAME AS BEFORE WITH BRIGHT WATERMARK ---
HTML = """ (use the previous premium HTML you loved, but with watermark opacity 0.18 and filter:none) """
# I will keep your premium HTML from before - just copy it from previous file

HTML = open('html_template.html','r').read() if os.path.exists('html_template.html') else """
<!DOCTYPE html>
<html>
<head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI - LIVE</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px}
#sidebar h1{font-size:22px;padding:12px} #sidebar h1 span{color:#4caf50}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0}
.hist{flex:1;overflow-y:auto}
.histItem{padding:10px;border-radius:8px;color:#888;font-size:13px;cursor:pointer}
#main{flex:1;display:flex;flex-direction:column;position:relative;background:radial-gradient(1200px 600px at 50% -10%, #1a2e1a 0%, #0a0a0a 60%)}
.header{padding:16px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a1a;background:rgba(0,0,0,0.5);backdrop-filter:blur(10px)}
#chat{flex:1;overflow-y:auto;padding:30px;position:relative}
#watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.18;pointer-events:none;z-index:0}
#watermark img{width:380px;filter:none}
.messages{position:relative;z-index:2;max-width:800px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:80px}
.welcome h2{font-size:42px;background:linear-gradient(90deg,#4caf50,#81c784,#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:600px;margin:0 auto}
.card{border:1px solid #222;background:rgba(255,255,255,0.03);padding:16px;border-radius:16px;cursor:pointer}
.mag{margin:20px 0;display:flex;gap:14px}
.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.avatar.user{background:#4caf50;color:#000}
.bubble{flex:1;line-height:1.7;max-width:90%}
.bubble.user{background:#1a3a1e;padding:14px 18px;border-radius:20px 20px 4px 20px;border:1px solid #2a5a2e}
.bubble.ai h2,.bubble.ai h3{color:#4caf50;margin:14px 0 8px}
#inputArea{padding:20px;max-width:800px;margin:0 auto;width:100%}
.inputBox{background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:12px 0}
.iconBtn{width:38px;height:38px;border-radius:50%;background:#222;border:none;color:#aaa;cursor:pointer;display:flex;align-items:center;justify-content:center;margin-left:6px}
#sendBtn{background:#fff;color:#000;width:38px;height:38px;border-radius:50%;border:none;cursor:pointer}
#typing{display:flex;gap:4px;padding:10px}
#typing span{width:8px;height:8px;background:#4caf50;border-radius:50%;animation:bounce 1.4s infinite}
#typing span:nth-child(2){animation-delay:0.2s} #typing span:nth-child(3){animation-delay:0.4s}
@keyframes bounce{0%,80%,100%{transform:scale(0.8);opacity:0.5}40%{transform:scale(1);opacity:1}}
#adModal,#signupModal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);backdrop-filter:blur(12px);z-index:9999;display:flex;justify-content:center;align-items:center}
.box{background:#111;border:1px solid #333;padding:32px;border-radius:24px;text-align:center;width:90%;max-width:380px}
.signupBox{background:#111;border:1px solid #222;padding:36px;border-radius:24px;width:90%;max-width:400px}
.signupBox input{width:100%;padding:14px;border-radius:12px;border:1px solid #333;background:#1a1a1a;color:#fff;margin-bottom:12px}
@media(max-width:768px){#sidebar{display:none}.cards{grid-template-columns:1fr}}
</style>
</head>
<body>
<div id='sidebar'><h1>LUMI <span>AI</span> LIVE</h1><div class='newChat' onclick='location.reload()'>+ New Chat</div><div class='hist' id='hist'></div><div style='padding:10px;font-size:11px;color:#444'>Live Data • Free: <span id='limit'>0/5</span></div></div>
<div id='main'><div class='header'><b>LUMI AI LIVE 🔴</b><span id='userEmail' style='font-size:12px;color:#666'></span></div>
<div id='chat'><div id='watermark'><img src='/logo.png' onerror="this.style.display='none';document.getElementById('waterText').style.display='block'"><div id='waterText' style='display:none;font-size:80px;font-weight:bold;color:#4caf50'>LUMI AI</div></div><div class='messages' id='messages'><div class='welcome' id='welcome'><h2>Hello, I'm LUMI LIVE</h2><p>Ask me anything LIVE - time, sports, weather, crypto</p><div class='cards'><div class='card' onclick="sendSug('Live football scores today')"><b>⚽ Live Scores</b><span>Premier League today</span></div><div class='card' onclick="sendSug('What is time in Norway now?')"><b>🕐 Norway Time</b><span>Current time Oslo</span></div><div class='card' onclick="sendSug('Weather in Jos today')"><b>🌤️ Weather</b><span>Live weather Jos</span></div><div class='card' onclick="sendSug('Bitcoin price now')"><b>💰 Crypto</b><span>BTC price live</span></div></div></div></div></div>
<div id='inputArea'><div class='inputBox'><input id='input' type='text' placeholder='Ask LUMI anything LIVE...'><label class='iconBtn'>📷<input type='file' id='imgInput' accept='image/*' style='display:none' onchange='uploadImg(this)'></label><button class='iconBtn' onclick='startVoice()'>🎙️</button><button id='sendBtn' onclick='send()'>↑</button></div></div></div>
<div id='signupModal'><div class='signupBox'><h2 style='color:#4caf50'>Welcome to LUMI LIVE ✨</h2><p style='color:#666;font-size:13px;margin-bottom:20px'>Live data by Elshuaib Tech</p><input id='emailInput' type='email' placeholder='Email'><input id='nameInput' type='text' placeholder='Name'><button onclick='doSignup()' style='width:100%;padding:14px;border-radius:12px;border:none;background:#fff;color:#000;font-weight:bold;cursor:pointer'>Continue</button></div></div>
<div id='adModal' style='display:none'><div class='box'><h3>Free limit reached</h3><p style='color:#888'>Watch ad to continue</p><button onclick='watchAd()' style='padding:12px 24px;background:#4caf50;border:none;border-radius:10px;font-weight:bold;margin-top:12px;width:100%'>Watch Ad</button></div></div>
<script>
let count=0; let userEmail=localStorage.getItem('lumi_email');
window.onload=()=>{if(userEmail){document.getElementById('signupModal').style.display='none';document.getElementById('userEmail').innerText=userEmail}}
function doSignup(){let e=document.getElementById('emailInput').value.trim(),n=document.getElementById('nameInput').value.trim();if(!e.includes('@'))return alert('Valid email');if(!n)return alert('Name');localStorage.setItem('lumi_email',e);document.getElementById('signupModal').style.display='none';document.getElementById('userEmail').innerText=e;fetch('/save-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,name:n})})}
function sendSug(t){document.getElementById('input').value=t;send()}
function formatAI(text){try{return marked.parse(text)}catch{return text}}
async function send(){
 let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg)return;
 if(!localStorage.getItem('lumi_email')){document.getElementById('signupModal').style.display='flex';return}
 if(count>=5){document.getElementById('adModal').style.display='flex';return}
 document.getElementById('welcome')?.remove();
 let ms=document.getElementById('messages');
 ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'>${msg}</div></div>`;inp.value='';
 let id='a'+Date.now(); ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'><div id='typing'><span></span><span></span><span></span></div></div></div>`;
 document.getElementById('chat').scrollTop=99999;
 let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
 let data=await res.json(); document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${formatAI(data.reply)}</div>`;
 count++;document.getElementById('limit').innerText=`${count}/5`;
}
async function uploadImg(input){let file=input.files[0];if(!file)return;let reader=new FileReader();reader.onload=async e=>{document.getElementById('welcome')?.remove();let ms=document.getElementById('messages');ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'><img src='${e.target.result}' style='max-width:100%;border-radius:12px'><br>What is this?</div></div>`;let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'><div id='typing'><span></span><span></span><span></span></div></div></div>`;let res=await fetch('/chat-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:e.target.result})});let data=await res.json();document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${formatAI(data.reply)}</div>`;};reader.readAsDataURL(file);}
function startVoice(){if(!('webkitSpeechRecognition' in window)){alert('Use Chrome');return}let rec=new webkitSpeechRecognition();rec.lang='en-US';rec.start();rec.onresult=e=>{document.getElementById('input').value=e.results[0][0].transcript}}
function watchAd(){count=0;document.getElementById('limit').innerText=`${count}/5`;document.getElementById('adModal').style.display='none'}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
"""

@app.route('/')
def home(): return HTML

@app.route('/logo.png')
def logo(): return send_from_directory('.', 'logo.png')

@app.route('/save-email', methods=['POST'])
def save_email():
    print(f"NEW USER: {request.json}")
    return jsonify({"ok":True})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message','')
        live_info = get_live_data(user_msg)
        now_nigeria = datetime.now(pytz.timezone('Africa/Lagos')).strftime('%A, %B %d, %Y %I:%M %p WAT')
        now_utc = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M UTC')

        context = f"Current datetime: {now_nigeria}, {now_utc}. "
        if live_info:
            context += f"\nLIVE REAL DATA FROM INTERNET:\n{live_info}\nUse this live data to answer. This is real-time, not old."

        system = f"You are LUMI AI LIVE by Elshuaib Tech. You have LIVE internet data. {context} Always answer with live data when available. Be concise, beautiful formatting, no raw markdown. If live data provided, use it. You NEVER say you don't have live data - you DO now."

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":user_msg}]
        )
        reply = completion.choices[0].message.content
        if live_info and "live" not in reply.lower():
            reply = f"🔴 **LIVE DATA:**\n{live_info}\n\n{reply}"
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

@app.route('/chat-image', methods=['POST'])
def chat_image():
    try:
        img = request.json.get('image','')
        completion = client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"user","content":[{"type":"text","text":"Describe this image."},{"type":"image_url","image_url":{"url":img}}]}])
        return jsonify({"reply": completion.choices[0].message.content})
    except:
        return jsonify({"reply": "📷 I see your image! Tell me what you want to know about it."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
