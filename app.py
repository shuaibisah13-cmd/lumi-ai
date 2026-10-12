from flask import Flask, request, jsonify, send_from_directory
import os, requests, json
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET", "")

EMAILS_FILE = "users.json"
def save_user(email, name, paid=False):
    try:
        users = {}
        if os.path.exists(EMAILS_FILE):
            with open(EMAILS_FILE,'r') as f: users=json.load(f)
        users[email] = {"name":name,"paid":paid,"date":str(datetime.now())}
        with open(EMAILS_FILE,'w') as f: json.dump(users,f)
    except: pass

def get_live():
    now_utc = datetime.now(pytz.utc)
    now_ng = now_utc.astimezone(pytz.timezone('Africa/Lagos'))
    now_oslo = now_utc.astimezone(pytz.timezone('Europe/Oslo'))
    return now_utc, now_ng, now_oslo

def wiki_live(query):
    try:
        q = query.lower().replace("who is","").replace("what is","").strip()
        s = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json", timeout=6).json()
        if s.get('query',{}).get('search'):
            title=s['query']['search'][0]['title']
            sum_r=requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=6).json()
            if sum_r.get('extract'): return f"{sum_r.get('title')}: {sum_r.get('extract')[:700]}"
    except: pass
    return None

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<meta name="theme-color" content="#4caf50"><link rel="manifest" href="/manifest.json">
<title>LUMI PRO MAX</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://js.paystack.co/v1/inline.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0}
#main{flex:1;display:flex;flex-direction:column;background:#0a0a0a}
.header{padding:12px 18px;display:flex;justify-content:space-between;border-bottom:1px solid #1a1a1a;background:#000;align-items:center}
#chat{flex:1;overflow-y:auto;padding:20px;position:relative}#watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.12;pointer-events:none;z-index:0}#watermark img{width:380px}
.messages{position:relative;z-index:2;max-width:800px;margin:0 auto;width:100%}.welcome{text-align:center;margin-top:20px}.welcome h2{font-size:32px;color:#4caf50}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:600px;margin:20px auto}.card{border:1px solid #222;background:#111;padding:14px;border-radius:14px;cursor:pointer}
.mag{margin:18px 0;display:flex;gap:12px}.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center}.avatar.user{background:#4caf50;color:#000}
.bubble{flex:1;line-height:1.6}.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px;border:1px solid #2a5a2e}
.bubble.ai img{max-width:300px;border-radius:12px;margin:8px 0;border:1px solid #333}
#inputArea{padding:12px;max-width:800px;margin:0 auto;width:100%;background:#0a0a0a;border-top:1px solid #1a1a1a}
.inputRow{display:flex;gap:8px;align-items:flex-end}
.inputBox{background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px;flex:1}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
.iconBtn{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px}
#sendBtn{background:#fff;color:#000}#micBtn{background:#222;color:#fff;border:1px solid #333}#imgBtn{background:#222;color:#fff;border:1px solid #333}
#micBtn.recording{background:#ff3333;animation:pulse 1s infinite}@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
.preview{max-width:800px;margin:0 auto 10px;display:none}#previewImg{max-width:120px;border-radius:12px;border:2px solid #4caf50}
#signupModal,#payModal{position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:9999;display:flex;justify-content:center;align-items:center}.box,.signupBox{background:#111;border:1px solid #333;padding:28px;border-radius:20px;width:90%;max-width:400px;text-align:center}
.signupBox input{width:100%;padding:12px;border-radius:10px;border:1px solid #333;background:#1a1a1a;color:#fff;margin-bottom:10px}
</style></head><body>
<div id='sidebar'><h1>LUMI <span style='color:#4caf50'>PRO MAX</span></h1><div class='newChat' onclick='location.reload()'>+ New Chat</div>
<div style='padding:10px;font-size:11px;color:#555'>Free: <span id='limit'>0/5</span><div id='paidBadge' style='display:none;color:#4caf50;font-weight:bold'>✅ UNLIMITED PAID</div>
<div style='margin-top:20px;color:#888'><b>Features:</b><br>📸 Picture Upload<br>🎤 Voice Chat<br>🔊 AI Speaks</div></div></div>
<div id='main'><div class='header'><b>💰 LUMI PRO MAX - Paystack Ready</b><span id='uEmail' style='font-size:11px;color:#666'></span></div>
<div id='chat'><div id='watermark'><img src='/logo.png' onerror="this.style.display='none'"><div style='font-size:60px;color:#4caf50;font-weight:bold;text-align:center'>LUMI AI</div></div>
<div class='messages' id='messages'><div class='welcome' id='welcome'><h2>LUMI PRO MAX</h2><p style='color:#888'>Voice + Picture + Paystack ₦1000</p>
<div class='cards'><div class='card' onclick="sendSug('Who is Bola Ahmed Tinubu?')"><b>🇳🇬 Tinubu Live</b></div><div class='card' onclick="document.getElementById('fileInput').click()"><b>📸 Upload Picture</b></div><div class='card' onclick="startVoice()"><b>🎤 Voice Chat</b></div><div class='card' onclick="sendSug('What is time in Norway now?')"><b>🕐 Live Time</b></div></div></div></div></div>
<div id='inputArea'>
<div id='preview' class='preview'><img id='previewImg'><button onclick='clearImage()' style='background:#333;color:#fff;border:none;padding:4px 8px;border-radius:6px;margin-left:8px;cursor:pointer'>X Remove</button></div>
<div class='inputRow'>
<button class='iconBtn' id='imgBtn' onclick="document.getElementById('fileInput').click()" title='Upload Picture'>📸</button>
<input type='file' id='fileInput' accept='image/*' style='display:none' onchange='handleImage(event)'>
<button class='iconBtn' id='micBtn' onclick='startVoice()' title='Voice'>🎤</button>
<div class='inputBox'><input id='input' placeholder='Ask, upload picture, or use voice...'><button id='sendBtn' class='iconBtn' onclick='send()'>↑</button></div>
</div></div></div>

<div id='signupModal'><div class='signupBox'><h2 style='color:#4caf50'>LUMI PRO MAX ✨</h2><p style='color:#666;font-size:13px'>By Elshuaib Tech</p><input id='emailInput' type='email' placeholder='Your Email'><input id='nameInput' placeholder='Full Name'><button onclick='doSignup()' style='width:100%;padding:12px;background:#fff;color:#000;border:none;border-radius:10px;font-weight:bold;cursor:pointer'>Start - 5 Free Chats</button></div></div>
<div id='payModal' style='display:none'><div class='box'><h2 style='color:#4caf50'>💳 Unlock Unlimited</h2><p style='color:#ccc;margin:15px 0'>You used 5 free.<br>Pay <b>₦1,000</b> for <b>UNLIMITED</b> Forever</p><button onclick='payWithPaystack()' style='width:100%;padding:16px;background:#4caf50;color:#000;border:none;border-radius:12px;font-weight:bold;font-size:16px;cursor:pointer'>💰 Pay ₦1,000 with Paystack</button><button onclick='document.getElementById("payModal").style.display="none"' style='margin-top:12px;background:transparent;color:#666;border:none;cursor:pointer'>Close</button></div></div>

<script>
let count=0;let userEmail=localStorage.getItem('lumi_email');let isPaid=localStorage.getItem('lumi_paid')==='true';let selectedImageBase64=null;let mediaRecorder=null;let audioChunks=[];
window.onload=()=>{if(userEmail){document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=userEmail; if(isPaid){document.getElementById('paidBadge').style.display='block';document.getElementById('limit').style.display='none';}}}
function doSignup(){let e=document.getElementById('emailInput').value.trim(),n=document.getElementById('nameInput').value.trim();if(!e.includes('@'))return alert('Enter email');if(!n)return alert('Enter name');localStorage.setItem('lumi_email',e);document.getElementById('signupModal').style.display='none';document.getElementById('uEmail').innerText=e;fetch('/save-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,name:n})})}
function sendSug(t){document.getElementById('input').value=t;send()}
function handleImage(event){let file=event.target.files[0];if(!file)return;let reader=new FileReader();reader.onload=(e)=>{selectedImageBase64=e.target.result;document.getElementById('previewImg').src=selectedImageBase64;document.getElementById('preview').style.display='block';};reader.readAsDataURL(file);}
function clearImage(){selectedImageBase64=null;document.getElementById('preview').style.display='none';document.getElementById('fileInput').value='';}
async function startVoice(){
  let micBtn=document.getElementById('micBtn');
  if(mediaRecorder && mediaRecorder.state==='recording'){mediaRecorder.stop();return;}
  try{
    let stream=await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder=new MediaRecorder(stream);audioChunks=[];micBtn.classList.add('recording');micBtn.innerText='⏹️';
    mediaRecorder.ondataavailable=e=>audioChunks.push(e.data);
    mediaRecorder.onstop=async()=>{
      micBtn.classList.remove('recording');micBtn.innerText='🎤';
      let audioBlob=new Blob(audioChunks,{type:'audio/webm'});
      let form=new FormData();form.append('audio',audioBlob);
      let ms=document.getElementById('messages');let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>🎤 Transcribing...</div></div>`;
      let res=await fetch('/voice',{method:'POST',body:form});let data=await res.json();
      if(data.text){document.getElementById('input').value=data.text;document.getElementById(id).remove();send();}
      else{document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>❌ Try again</div>`;}
    };
    mediaRecorder.start();setTimeout(()=>{if(mediaRecorder.state==='recording')mediaRecorder.stop();},6000);
  }catch(e){alert('Mic permission needed');}
}
function speakText(text){if('speechSynthesis' in window){let clean=text.replace(/[*#`_]/g,'').substring(0,300);let ut=new SpeechSynthesisUtterance(clean);ut.rate=1;speechSynthesis.speak(ut);}}
async function send(){
  let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg &&!selectedImageBase64)return;
  if(!localStorage.getItem('lumi_email')){document.getElementById('signupModal').style.display='flex';return}
  if(!isPaid && count>=5){document.getElementById('payModal').style.display='flex';return}
  document.getElementById('welcome')?.remove();let ms=document.getElementById('messages');
  let imgHtml=selectedImageBase64?`<br><img src='${selectedImageBase64}'>`:'';
  ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'>${msg}${imgHtml}</div></div>`;
  let curImg=selectedImageBase64;inp.value='';clearImage();
  let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>⏳ Thinking...</div></div>`;document.getElementById('chat').scrollTop=999999;
  let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,email:localStorage.getItem('lumi_email'),image:curImg})});
  let data=await res.json();document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${marked.parse(data.reply)} <br><button onclick="speakText('${data.reply.replace(/'/g,"").substring(0,150)}')" style='background:#222;color:#4caf50;border:1px solid #333;padding:6px 12px;border-radius:20px;cursor:pointer;margin-top:8px'>🔊 Speak</button></div>`;
  if(!isPaid){count++;document.getElementById('limit').innerText=`${count}/5`;}speakText(data.reply);
}
function payWithPaystack(){
  let email=localStorage.getItem('lumi_email');
  let handler=PaystackPop.setup({
    key: 'pk_test_48e66b6f363f0eb10721254b7163128ca99ad360',
    email: email,
    amount: 100000,
    currency: 'NGN',
    ref: 'LUMI_'+Math.floor((Math.random()*1000000000)+1),
    callback:function(r){
      fetch('/verify-pay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,reference:r.reference})})
     .then(x=>x.json()).then(d=>{if(d.ok){localStorage.setItem('lumi_paid','true');isPaid=true;document.getElementById('payModal').style.display='none';document.getElementById('paidBadge').style.display='block';document.getElementById('limit').style.display='none';alert('✅ Payment Success! Unlimited Unlocked!');}})
    },
    onClose:function(){}
  });
  handler.openIframe();
}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route('/')
def home(): return HTML
@app.route('/manifest.json')
def manifest():
    return jsonify({"name":"LUMI PRO MAX","short_name":"LUMI","start_url":"/","display":"standalone","background_color":"#0a0a0a","theme_color":"#4caf50","icons":[{"src":"/logo.png","sizes":"512x512","type":"image/png"}]})
@app.route('/logo.png')
def logo(): return send_from_directory('.', 'logo.png')
@app.route('/save-email', methods=['POST'])
def save_email():
    d=request.json; save_user(d.get('email'), d.get('name')); return jsonify({"ok":True})
@app.route('/verify-pay', methods=['POST'])
def verify_pay():
    data=request.json; email=data.get('email'); ref=data.get('reference')
    if PAYSTACK_SECRET:
        try:
            r=requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers={"Authorization": f"Bearer {PAYSTACK_SECRET}"}, timeout=8).json()
            if r.get('data',{}).get('status')=='success':
                save_user(email, "", paid=True); return jsonify({"ok":True})
        except: pass
    save_user(email, "", paid=True); return jsonify({"ok":True})

@app.route('/voice', methods=['POST'])
def voice():
    try:
        audio=request.files.get('audio')
        if not audio: return jsonify({"text":""})
        audio.save('/tmp/voice.webm')
        with open('/tmp/voice.webm','rb') as f:
            transcription=client.audio.transcriptions.create(model="whisper-large-v3", file=f)
        return jsonify({"text": transcription.text})
    except Exception as e:
        return jsonify({"text":"", "error":str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data=request.json; user_msg=data.get('message',''); img_data=data.get('image')
        now_utc, now_ng, now_oslo=get_live()
        live_wiki=None
        if any(x in user_msg.lower() for x in ['who is','what is','tinubu','president']) and not img_data:
            live_wiki=wiki_live(user_msg)
        system=f"You are LUMI PRO MAX by Elshuaib Tech. Time: Nigeria {now_ng.strftime('%Y-%m-%d %H:%M WAT')}, Norway {now_oslo.strftime('%Y-%m-%d %H:%M CEST')}."
        if live_wiki: system+=f"\nLIVE WIKI: {live_wiki}"
        messages=[{"role":"system","content":system}]
        if img_data:
            messages.append({"role":"user","content":[{"type":"text","text": user_msg or "Describe this image"}, {"type":"image_url","image_url":{"url": img_data}}]})
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        else:
            messages.append({"role":"user","content": user_msg})
            model="openai/gpt-oss-20b"
        comp=client.chat.completions.create(model=model, messages=messages)
        reply=comp.choices[0].message.content
        if live_wiki and not img_data: reply=f"📚 LIVE Wikipedia: {live_wiki}\n\n---\n\n"+reply
        return jsonify({"reply":reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
