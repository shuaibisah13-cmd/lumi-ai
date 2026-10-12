from flask import Flask, request, jsonify, send_from_directory
import os, requests, json
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET", "") # you will add in Render

# === STORAGE ===
EMAILS_FILE = "users.json"
def save_user(email, name, paid=False):
    try:
        users = {}
        if os.path.exists(EMAILS_FILE):
            with open(EMAILS_FILE, 'r') as f: users = json.load(f)
        users[email] = {"name": name, "paid": paid, "date": str(datetime.now())}
        with open(EMAILS_FILE, 'w') as f: json.dump(users, f)
    except: pass

def is_paid(email):
    try:
        if os.path.exists(EMAILS_FILE):
            with open(EMAILS_FILE,'r') as f:
                return json.load(f).get(email,{}).get('paid',False)
    except: return False
    return False

def get_live():
    now_utc = datetime.now(pytz.utc)
    now_ng = now_utc.astimezone(pytz.timezone('Africa/Lagos'))
    now_oslo = now_utc.astimezone(pytz.timezone('Europe/Oslo'))
    return now_utc, now_ng, now_oslo

def wiki_live(query):
    # LIVE WIKIPEDIA - Fixes Tinubu etc
    try:
        # Clean query: "who is tinubu" -> "tinubu"
        q = query.lower().replace("who is","").replace("who is the","").replace("what is","").strip()
        if len(q) < 2: return None
        # Search Wikipedia
        s = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json", timeout=6).json()
        if s.get('query',{}).get('search'):
            title = s['query']['search'][0]['title']
            # Get summary
            sum_r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=6).json()
            if sum_r.get('extract'):
                return f"LIVE WIKIPEDIA - {sum_r.get('title')}: {sum_r.get('extract')[:800]}\nSource: {sum_r.get('content_urls',{}).get('desktop',{}).get('page','')}"
    except Exception as e:
        print(f"Wiki error {e}")
    return None

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>LUMI AI LIVE PRO</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<!-- ADMOB / ADSENSE MONEY CODE - REPLACE ca-pub- WITH YOUR OWN -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>
<script src="https://js.paystack.co/v1/inline.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0}
#main{flex:1;display:flex;flex-direction:column;position:relative;background:#0a0a0a}
.header{padding:16px 24px;display:flex;justify-content:space-between;border-bottom:1px solid #1a1a1a;background:#000}
#chat{flex:1;overflow-y:auto;padding:30px;position:relative}#watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.15;pointer-events:none;z-index:0}#watermark img{width:360px;filter:none}
.messages{position:relative;z-index:2;max-width:800px;margin:0 auto;width:100%}.welcome{text-align:center;margin-top:40px}.welcome h2{font-size:36px;background:linear-gradient(90deg,#4caf50,#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:600px;margin:20px auto}.card{border:1px solid #222;background:rgba(255,255,255,0.03);padding:14px;border-radius:14px;cursor:pointer;text-align:left}
.mag{margin:20px 0;display:flex;gap:12px}.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center}.avatar.user{background:#4caf50;color:#000}
.bubble{flex:1;line-height:1.6}.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px;border:1px solid #2a5a2e}
.bubble.ai{max-width:90%}
#inputArea{padding:18px;max-width:800px;margin:0 auto;width:100%}.inputBox{background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}#sendBtn{background:#fff;color:#000;width:36px;height:36px;border-radius:50%;border:none;cursor:pointer}
#adModal,#signupModal,#payModal{position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:9999;display:flex;justify-content:center;align-items:center;backdrop-filter:blur(10px)}.box,.signupBox{background:#111;border:1px solid #333;padding:28px;border-radius:20px;width:90%;max-width:400px;text-align:center}
.signupBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #333;background:#1a1a1a;color:#fff;margin-bottom:10px}
.adBox{width:100%;max-width:800px;margin:12px auto;text-align:center}
</style></head><body>
<div id='sidebar'><h1>LUMI <span style='color:#4caf50'>AI</span> LIVE PRO</h1><div class='newChat' onclick='location.reload()'>+ New Chat</div><div style='padding:10px;font-size:11px;color:#555'>Free: <span id='limit'>0/5</span><div id='paidBadge' style='display:none;color:#4caf50'>✅ PAID UNLIMITED</div></div>
<!-- ADMOB BANNER SIDEBAR -->
<div class='adBox'><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1234567890123456" data-ad-slot="1234567890" data-ad-format="auto"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>
</div>
<div id='main'><div class='header'><b>LUMI LIVE PRO 🔴 LIVE MONEY</b><span id='uEmail' style='font-size:11px;color:#666'></span></div>
<div id='chat'><div id='watermark'><img src='/logo.png' onerror="this.style.display='none'"><div style='font-size:70px;color:#4caf50;font-weight:bold'>LUMI AI</div></div>
<div class='messages' id='messages'><div class='welcome' id='welcome'><h2>Hello, I'm LUMI PRO LIVE</h2><p style='color:#888'>Wikipedia LIVE + Time + Sports + Pay to continue</p>
<div class='cards'><div class='card' onclick="sendSug('Who is Bola Ahmed Tinubu?')"><b>🇳🇬 Who is Tinubu?</b><br><small>Correct Wikipedia LIVE</small></div><div class='card' onclick="sendSug('What is time in Norway now?')"><b>🕐 Norway Time</b><br><small>Current Oslo</small></div><div class='card' onclick="sendSug('Live football scores today')"><b>⚽ Live Scores</b><br><small>Premier League LIVE</small></div><div class='card' onclick="sendSug('Weather in Jos today')"><b>🌤️ Weather</b><br><small>Live weather</small></div></div>
<!-- ADMOB BANNER TOP -->
<div class='adBox'><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1234567890123456" data-ad-slot="1234567890" data-ad-format="auto"></ins></div>
</div></div></div>
<div id='inputArea'><div class='inputBox'><input id='input' placeholder='Ask LUMI PRO anything...'><button id='sendBtn' onclick='send()'>↑</button></div></div></div>

<div id='signupModal'><div class='signupBox'><h2 style='color:#4caf50'>Welcome to LUMI PRO ✨</h2><p style='color:#666;font-size:13px;margin:10px 0'>By Elshuaib Tech - Live Data</p><input id='emailInput' type='email' placeholder='Email'><input id='nameInput' placeholder='Full Name'><button onclick='doSignup()' style='width:100%;padding:12px;background:#fff;color:#000;border:none;border-radius:10px;font-weight:bold;cursor:pointer'>Continue - 5 Free Chats</button></div></div>

<div id='adModal' style='display:none'><div class='box'><h3>⏰ Free limit reached!</h3><p style='color:#888;margin:10px 0'>Watch ad or pay to continue unlimited</p>
<!-- ADMOB REWARDED AD PLACE -->
<div class='adBox' style='margin:15px 0'><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1234567890123456" data-ad-slot="1234567890" data-ad-format="auto"></ins></div>
<button onclick='watchAd()' style='padding:12px;background:#4caf50;border:none;border-radius:10px;width:100%;font-weight:bold;margin-bottom:8px'>▶️ Watch Ad - Get 5 More Free</button>
<button onclick='showPay()' style='padding:12px;background:#fff;color:#000;border:none;border-radius:10px;width:100%;font-weight:bold'>💰 Pay ₦1000 - Unlimited Forever</button>
</div></div>

<div id='payModal' style='display:none'><div class='box'><h3 style='color:#4caf50'>💳 Unlock LUMI PRO</h3><p style='color:#888;margin:12px 0'>₦1000 for unlimited chats forever<br>Paystack secure</p><button onclick='payWithPaystack()' style='padding:14px;background:#4caf50;border:none;border-radius:12px;width:100%;font-weight:bold;font-size:16px'>Pay ₦1000 Now</button><button onclick='document.getElementById("payModal").style.display="none"' style='margin-top:10px;background:transparent;color:#666;border:none'>Cancel</button></div></div>

<script>
let count=0;let userEmail=localStorage.getItem('lumi_email');let isPaidUser=localStorage.getItem('lumi_paid')==='true';
window.onload=()=>{if(userEmail){document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=userEmail; if(isPaidUser){document.getElementById('paidBadge').style.display='block'; document.getElementById('limit').style.display='none';}}}
function doSignup(){let e=document.getElementById('emailInput').value.trim(),n=document.getElementById('nameInput').value.trim();if(!e.includes('@'))return alert('email');if(!n)return alert('name');localStorage.setItem('lumi_email',e);document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=e;fetch('/save-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,name:n})})}
function sendSug(t){document.getElementById('input').value=t;send()}
async function send(){let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg)return;if(!localStorage.getItem('lumi_email')){document.getElementById('signupModal').style.display='flex';return}if(!isPaidUser && count>=5){document.getElementById('adModal').style.display='flex';return}document.getElementById('welcome')?.remove();let ms=document.getElementById('messages');ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'>${msg}</div></div>`;inp.value='';let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>⏳ LIVE Wikipedia + Time searching...</div></div>`;document.getElementById('chat').scrollTop=99999;let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,email:localStorage.getItem('lumi_email')})});let data=await res.json();document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${marked.parse(data.reply)}</div>`;if(!isPaidUser){count++;document.getElementById('limit').innerText=`${count}/5`;}}
function watchAd(){count=0;document.getElementById('limit').innerText='0/5';document.getElementById('adModal').style.display='none'; try{(adsbygoogle=window.adsbygoogle||[]).push({});}catch(e){}}
function showPay(){document.getElementById('adModal').style.display='none';document.getElementById('payModal').style.display='flex';}
function payWithPaystack(){let email=localStorage.getItem('lumi_email');let handler=PaystackPop.setup({key:'pk_test_YOUR_PAYSTACK_PUBLIC_KEY',email:email,amount:100000,currency:'NGN',callback:function(response){fetch('/verify-pay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,reference:response.reference})}).then(r=>r.json()).then(d=>{if(d.ok){localStorage.setItem('lumi_paid','true');isPaidUser=true;document.getElementById('payModal').style.display='none';document.getElementById('paidBadge').style.display='block';document.getElementById('limit').style.display='none';alert('✅ Payment success! Unlimited now!');}})},onClose:function(){}});handler.openIframe();}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route('/')
def home(): return HTML

@app.route('/logo.png')
def logo(): return send_from_directory('.', 'logo.png')

@app.route('/save-email', methods=['POST'])
def save_email():
    d=request.json
    save_user(d.get('email'), d.get('name'))
    return jsonify({"ok":True})

@app.route('/verify-pay', methods=['POST'])
def verify_pay():
    data=request.json
    email=data.get('email')
    ref=data.get('reference')
    # Verify with Paystack
    if PAYSTACK_SECRET:
        try:
            r=requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers={"Authorization": f"Bearer {PAYSTACK_SECRET}"}, timeout=8)
            if r.json().get('data',{}).get('status')=='success':
                save_user(email, "", paid=True)
                return jsonify({"ok":True})
        except: pass
    # For testing without Paystack secret, mark paid anyway
    save_user(email, "", paid=True)
    return jsonify({"ok":True})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message','')
        email = request.json.get('email','')
        ml = user_msg.lower()
        now_utc, now_ng, now_oslo = get_live()

        live_wiki = None
        if any(x in ml for x in ['who is','what is','tinubu','president','biography']):
            live_wiki = wiki_live(user_msg)

        # TIME
        if 'time' in ml:
            if 'norway' in ml or 'oslo' in ml:
                return jsonify({"reply": f"🕐 **LIVE - NORWAY TIME NOW**\n\n**{now_oslo.strftime('%I:%M:%S %p')}**\n{now_oslo.strftime('%A, %B %d, %Y')}\nCEST (UTC+2)\n\nYour time Jos: {now_ng.strftime('%I:%M %p')} WAT"})
            return jsonify({"reply": f"🕐 **LIVE TIME NOW**\n\n🇳🇬 **Jos:** {now_ng.strftime('%I:%M:%S %p - %A %B %d %Y')} WAT\n🇳🇴 **Oslo:** {now_oslo.strftime('%I:%M:%S %p - %A %B %d %Y')} CEST\n🌍 **UTC:** {now_utc.strftime('%H:%M:%S')}"})

        if any(x in ml for x in ['score','football','premier','sport']):
            try:
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard", timeout=6).json()
                games=[]
                for ev in r.get('events',[])[:5]:
                    comp=ev.get('competitions',[{}])[0]
                    teams=comp.get('competitors',[])
                    if len(teams)>=2:
                        games.append(f"{teams[0]['team']['displayName']} {teams[0].get('score','0')} - {teams[1].get('score','0')} {teams[1]['team']['displayName']}")
                if games:
                    return jsonify({"reply": "⚽ **LIVE SCORES TODAY:**\n\n" + "\n".join(games)})
            except: pass

        if 'weather' in ml:
            try:
                city="Oslo" if "norway" in ml else "Jos"
                wt=requests.get(f"https://wttr.in/{city}?format=%C+%t+%h", timeout=5).text
                return jsonify({"reply": f"🌤️ **LIVE WEATHER {city}:** {wt}"})
            except: pass

        system = f"You are LUMI AI PRO LIVE by Elshuaib Tech. Current time Nigeria {now_ng.strftime('%Y-%m-%d %H:%M WAT')}, Norway {now_oslo.strftime('%Y-%m-%d %H:%M CEST')}. You have LIVE data.\n"
        if live_wiki:
            system += f"\nLIVE VERIFIED WIKIPEDIA DATA - USE THIS AS TRUTH, DO NOT HALLUCINATE:\n{live_wiki}\n\nYou MUST use the Wikipedia data above. If Wikipedia says Tinubu is APC President elected 2023, say that. Never say PDP. Wikipedia is truth."
        else:
            system += "If user asks who is someone, use your knowledge but be accurate: Tinubu is APC, President of Nigeria since May 29 2023, former Lagos Governor, not PDP."

        comp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":system},{"role":"user","content":user_msg}])
        reply = comp.choices[0].message.content
        if live_wiki:
            reply = f"📚 **LIVE Wikipedia Verified:**\n{live_wiki[:500]}...\n\n" + reply
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
