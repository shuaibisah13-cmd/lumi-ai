from flask import Flask, request, jsonify, send_from_directory
import os, requests
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_live():
    now_utc = datetime.now(pytz.utc)
    now_ng = now_utc.astimezone(pytz.timezone('Africa/Lagos'))
    now_oslo = now_utc.astimezone(pytz.timezone('Europe/Oslo'))
    return now_utc, now_ng, now_oslo

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>LUMI AI LIVE</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0}
#main{flex:1;display:flex;flex-direction:column;position:relative;background:#0a0a0a}
.header{padding:16px 24px;display:flex;justify-content:space-between;border-bottom:1px solid #1a1a1a;background:#000}
#chat{flex:1;overflow-y:auto;padding:30px;position:relative}#watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.18;pointer-events:none;z-index:0}#watermark img{width:360px;filter:none}
.messages{position:relative;z-index:2;max-width:800px;margin:0 auto;width:100%}.welcome{text-align:center;margin-top:60px}.welcome h2{font-size:36px;color:#4caf50}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:600px;margin:20px auto}.card{border:1px solid #222;background:rgba(255,255,255,0.03);padding:14px;border-radius:14px;cursor:pointer;text-align:left}
.mag{margin:20px 0;display:flex;gap:12px}.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center}.avatar.user{background:#4caf50;color:#000}
.bubble{flex:1;line-height:1.6}.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px;border:1px solid #2a5a2e}
#inputArea{padding:18px;max-width:800px;margin:0 auto;width:100%}.inputBox{background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}#sendBtn{background:#fff;color:#000;width:36px;height:36px;border-radius:50%;border:none;cursor:pointer}
#adModal,#signupModal{position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:9999;display:flex;justify-content:center;align-items:center}.box,.signupBox{background:#111;border:1px solid #333;padding:28px;border-radius:20px;width:90%;max-width:380px;text-align:center}
.signupBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #333;background:#1a1a1a;color:#fff;margin-bottom:10px}
</style></head><body>
<div id='sidebar'><h1>LUMI <span style='color:#4caf50'>AI</span> LIVE</h1><div class='newChat' onclick='location.reload()'>+ New Chat</div><div style='padding:10px;font-size:11px;color:#555'>Free: <span id='limit'>0/5</span></div></div>
<div id='main'><div class='header'><b>LUMI LIVE 🔴</b><span id='uEmail' style='font-size:11px;color:#666'></span></div>
<div id='chat'><div id='watermark'><img src='/logo.png' onerror="this.style.display='none'"><div style='font-size:70px;color:#4caf50;font-weight:bold'>LUMI AI</div></div>
<div class='messages' id='messages'><div class='welcome' id='welcome'><h2>Hello, I'm LUMI LIVE</h2><p style='color:#888'>Ask me time, scores, weather, crypto - all LIVE</p>
<div class='cards'><div class='card' onclick="sendSug('Live football scores today')"><b>⚽ Live Scores</b><br><small>Premier League</small></div><div class='card' onclick="sendSug('What is time in Norway now?')"><b>🕐 Norway Time</b><br><small>Current Oslo time</small></div><div class='card' onclick="sendSug('Weather in Jos today')"><b>🌤️ Weather</b><br><small>Live weather</small></div><div class='card' onclick="sendSug('Bitcoin price now')"><b>💰 Crypto</b><br><small>BTC live</small></div></div></div></div></div>
<div id='inputArea'><div class='inputBox'><input id='input' placeholder='Ask LUMI anything LIVE...'><button id='sendBtn' onclick='send()'>↑</button></div></div></div>
<div id='signupModal'><div class='signupBox'><h2 style='color:#4caf50'>Welcome to LUMI LIVE</h2><input id='emailInput' type='email' placeholder='Email'><input id='nameInput' placeholder='Name'><button onclick='doSignup()' style='width:100%;padding:12px;background:#fff;color:#000;border:none;border-radius:10px;font-weight:bold;cursor:pointer'>Continue</button></div></div>
<div id='adModal' style='display:none'><div class='box'><h3>Free limit reached</h3><button onclick='watchAd()' style='padding:10px 20px;background:#4caf50;border:none;border-radius:8px;font-weight:bold;margin-top:12px;width:100%'>Watch Ad - Continue</button></div></div>
<script>
let count=0;let userEmail=localStorage.getItem('lumi_email');
window.onload=()=>{if(userEmail){document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=userEmail}}
function doSignup(){let e=document.getElementById('emailInput').value.trim(),n=document.getElementById('nameInput').value.trim();if(!e.includes('@'))return alert('email');if(!n)return alert('name');localStorage.setItem('lumi_email',e);document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=e;fetch('/save-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,name:n})})}
function sendSug(t){document.getElementById('input').value=t;send()}
async function send(){let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg)return;if(!localStorage.getItem('lumi_email')){document.getElementById('signupModal').style.display='flex';return}if(count>=5){document.getElementById('adModal').style.display='flex';return}document.getElementById('welcome')?.remove();let ms=document.getElementById('messages');ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'>${msg}</div></div>`;inp.value='';let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>⏳ LIVE searching...</div></div>`;document.getElementById('chat').scrollTop=99999;let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});let data=await res.json();document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${marked.parse(data.reply)}</div>`;count++;document.getElementById('limit').innerText=`${count}/5`;}
function watchAd(){count=0;document.getElementById('limit').innerText='0/5';document.getElementById('adModal').style.display='none'}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route('/')
def home(): return HTML

@app.route('/logo.png')
def logo(): return send_from_directory('.', 'logo.png')

@app.route('/save-email', methods=['POST'])
def save_email(): return jsonify({"ok":True})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message','')
        ml = user_msg.lower()
        now_utc, now_ng, now_oslo = get_live()

        if 'time' in ml:
            if 'norway' in ml or 'oslo' in ml:
                return jsonify({"reply": f"🕐 **LIVE - NORWAY TIME NOW**\n\n**{now_oslo.strftime('%I:%M:%S %p')}**\n{now_oslo.strftime('%A, %B %d, %Y')}\nCEST (UTC+2)\n\nYour time Jos: {now_ng.strftime('%I:%M %p')} WAT"})
            return jsonify({"reply": f"🕐 **LIVE TIME NOW**\n\n🇳🇬 **Jos Nigeria:** {now_ng.strftime('%I:%M:%S %p - %A, %B %d, %Y')} (WAT)\n🇳🇴 **Norway Oslo:** {now_oslo.strftime('%I:%M:%S %p - %A, %B %d, %Y')} (CEST)\n🇬🇧 **London:** {now_utc.astimezone(pytz.timezone('Europe/London')).strftime('%I:%M %p %A')}\n🇺🇸 **New York:** {now_utc.astimezone(pytz.timezone('America/New_York')).strftime('%I:%M %p %A')}\n🌍 **UTC:** {now_utc.strftime('%H:%M:%S')}"})

        if any(x in ml for x in ['score','football','premier','sport','match today']):
            try:
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", timeout=6).json()
                games=[]
                for ev in r.get('events',[])[:5]:
                    comp=ev.get('competitions',[{}])[0]
                    teams=comp.get('competitors',[])
                    if len(teams)>=2:
                        games.append(f"{teams[0]['team']['displayName']} {teams[0].get('score','0')} - {teams[1].get('score','0')} {teams[1]['team']['displayName']} ({comp.get('status',{}).get('type',{}).get('detail','Live')})")
                if games:
                    return jsonify({"reply": "⚽ **LIVE FOOTBALL SCORES TODAY (Premier League):**\n\n" + "\n".join(games) + f"\n\nUpdated {now_ng.strftime('%I:%M %p')} WAT"})
            except: pass

        if 'weather' in ml:
            try:
                city="Oslo" if "norway" in ml or "oslo" in ml else "London" if "london" in ml else "Jos"
                wt=requests.get(f"https://wttr.in/{city}?format=%C+%t+%h", timeout=5).text
                return jsonify({"reply": f"🌤️ **LIVE WEATHER {city.upper()} NOW:**\n{wt}\n\nUpdated: {now_ng.strftime('%I:%M %p')} WAT"})
            except: pass

        if any(x in ml for x in ['bitcoin','btc','crypto','dollar']):
            try:
                pr=requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd", timeout=5).json()
                return jsonify({"reply": f"💰 **LIVE CRYPTO NOW:**\nBitcoin: ${pr['bitcoin']['usd']}\nEthereum: ${pr['ethereum']['usd']}\n\nUpdated: {now_ng.strftime('%I:%M %p')} WAT"})
            except: pass

        system = f"You are LUMI AI LIVE by Elshuaib Tech. Current LIVE datetime: Nigeria {now_ng.strftime('%Y-%m-%d %H:%M:%S WAT')}, Norway {now_oslo.strftime('%Y-%m-%d %H:%M:%S CEST')}. You DO have live time. NEVER say you don't have real-time data. Use provided time. Be concise premium."

        comp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":system},{"role":"user","content":user_msg}])
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
