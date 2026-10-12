# Same imports as before...
from flask import Flask, request, jsonify, send_from_directory
import os, requests, json
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

def wiki_live(q):
    try:
        s = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json", timeout=5).json()
        if s.get('query',{}).get('search'):
            t=s['query']['search'][0]['title']
            r=requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{t}", timeout=5).json()
            return r.get('extract','')[:600]
    except: return None
    return None

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI - Watch Ad to Chat</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<!-- MONETAG ADS - REPLACE WITH YOUR ZONE ID -->
<script src="https://alwingulla.com/88/tag.min.js" data-zone="YOUR_MONETAG_ZONE" async data-cfasync="false"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI;background:#0a0a0a;color:#ececec;display:flex;height:100vh}
#sidebar{width:250px;background:#000;border-right:1px solid #222;padding:12px}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer}
#main{flex:1;display:flex;flex-direction:column}
.header{padding:12px 18px;border-bottom:1px solid #1a1a1a;background:#000}
#chat{flex:1;overflow-y:auto;padding:20px}.messages{max-width:750px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:30px}.welcome h2{font-size:32px;color:#4caf50}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:600px;margin:20px auto}.card{border:1px solid #222;background:#111;padding:14px;border-radius:14px;cursor:pointer}
.mag{margin:18px 0;display:flex;gap:12px}.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center}
.bubble{flex:1}.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px}
#inputArea{padding:12px;max-width:750px;margin:0 auto;width:100%;border-top:1px solid #1a1a1a}
.inputRow{display:flex;gap:8px}.inputBox{flex:1;background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;padding:10px 0}
.iconBtn{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;font-size:18px}
#adModal{position:fixed;inset:0;background:rgba(0,0,0,0.95);z-index:9999;display:none;justify-content:center;align-items:center}
.adBox{background:#111;border:2px solid #4caf50;padding:28px;border-radius:20px;width:90%;max-width:420px;text-align:center}
</style></head><body>
<div id='sidebar'><h1>LUMI <span style='color:#4caf50'>AI</span></h1><div class='newChat' onclick='location.reload()'>+ New Chat</div><div style='margin-top:15px;font-size:12px;color:#777'>Free chats: <span id='limit'>0/5</span><br><br>💰 Earn when they watch ads!</div></div>
<div id='main'><div class='header'><b>LUMI AI - Free with Ads</b></div>
<div id='chat'><div class='messages' id='messages'><div class='welcome' id='welcome'><h2>Welcome to LUMI AI</h2><p style='color:#888'>Ask anything - Voice + Picture supported</p>
<div class='cards'><div class='card' onclick="sendSug('Who is Bola Ahmed Tinubu?')"><b>🇳🇬 Tinubu</b></div><div class='card' onclick="document.getElementById('fileInput').click()"><b>📸 Upload Picture</b></div><div class='card' onclick="startVoice()"><b>🎤 Voice</b></div><div class='card' onclick="sendSug('Bitcoin price today')"><b>💰 Crypto</b></div></div></div></div></div>
<div id='inputArea'>
<div class='inputRow'>
<button class='iconBtn' style='background:#222;color:#fff' onclick="document.getElementById('fileInput').click()">📸</button>
<input type='file' id='fileInput' accept='image/*' style='display:none' onchange='handleImage(event)'>
<button class='iconBtn' style='background:#222;color:#fff' id='micBtn' onclick='startVoice()'>🎤</button>
<div class='inputBox'><input id='input' placeholder='Ask LUMI...'><button id='sendBtn' class='iconBtn' style='background:#fff;color:#000' onclick='send()'>↑</button></div>
</div></div></div>

<div id='adModal'><div class='adBox'>
<h2 style='color:#4caf50'>🔓 Unlock More Chats!</h2>
<p style='color:#ccc;margin:15px 0'>You used 5 free chats.<br><b>Watch a short ad to get 3 more chats FREE!</b></p>
<div style='background:#000;padding:12px;border-radius:10px;margin:15px 0;border:1px dashed #333'>
<p style='color:#888;font-size:13px'>Ad will open in new tab.<br>Wait 15 seconds, then come back!</p>
</div>
<button id='watchBtn' onclick='watchAd()' style='width:100%;padding:16px;background:#4caf50;color:#000;border:none;border-radius:12px;font-weight:bold;font-size:16px;cursor:pointer'>▶️ Watch Ad (15s) - Get 3 Chats</button>
<p style='color:#666;font-size:11px;margin-top:12px'>Powered by Monetag - You earn $ when they watch</p>
<button onclick='document.getElementById("adModal").style.display="none"' style='margin-top:12px;background:transparent;color:#666;border:none;cursor:pointer'>Close</button>
</div></div>

<script>
let count=0;let selectedImageBase64=null;let mediaRecorder=null;let audioChunks=[];
function sendSug(t){document.getElementById('input').value=t;send()}
function handleImage(e){let f=e.target.files[0];if(!f)return;let r=new FileReader();r.onload=x=>{selectedImageBase64=x.target.result;};r.readAsDataURL(f);alert('📸 Picture attached! Now type your question and send');}
async function startVoice(){
  let b=document.getElementById('micBtn');
  if(mediaRecorder && mediaRecorder.state==='recording'){mediaRecorder.stop();return;}
  try{
    let s=await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder=new MediaRecorder(s);audioChunks=[];b.innerText='⏹️';b.style.background='#ff3333';
    mediaRecorder.ondataavailable=e=>audioChunks.push(e.data);
    mediaRecorder.onstop=async()=>{
      b.innerText='🎤';b.style.background='#222';
      let blob=new Blob(audioChunks,{type:'audio/webm'});let fd=new FormData();fd.append('audio',blob);
      let ms=document.getElementById('messages');let id='a'+Date.now();ms.innerHTML+=`<div class='mag'><div class='avatar'>✨</div><div class='bubble'>🎤 Transcribing...</div></div>`;
      let res=await fetch('/voice',{method:'POST',body:fd});let d=await res.json();
      if(d.text){document.getElementById('input').value=d.text;send();}
    };
    mediaRecorder.start();setTimeout(()=>{if(mediaRecorder.state==='recording')mediaRecorder.stop();},5000);
  }catch{alert('Allow mic');}
}
function watchAd(){
  let btn=document.getElementById('watchBtn');
  // OPEN YOUR MONETAG AD LINK HERE - This is where you earn!
  window.open('https://alwingulla.com/4/YOUR_MONETAG_LINK', '_blank');
  btn.innerText='⏳ Watching... 15s';btn.disabled=true;
  let sec=15;
  let timer=setInterval(()=>{
    sec--;btn.innerText=`⏳ Wait ${sec}s...`;
    if(sec<=0){
      clearInterval(timer);
      count=0;
      document.getElementById('limit').innerText=`${count}/5`;
      document.getElementById('adModal').style.display='none';
      btn.innerText='▶️ Watch Ad (15s) - Get 3 Chats';btn.disabled=false;
      alert('✅ You got 3 more chats! (You earned money from ad)');
    }
  },1000);
}
async function send(){
  let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg &&!selectedImageBase64)return;
  if(count>=5){document.getElementById('adModal').style.display='flex';return;}
  document.getElementById('welcome')?.remove();
  let ms=document.getElementById('messages');ms.innerHTML+=`<div class='mag'><div class='avatar' style='background:#4caf50;color:#000'>You</div><div class='bubble user'>${msg}${selectedImageBase64?'<br><img src="'+selectedImageBase64+'" style="max-width:200px;border-radius:10px;margin-top:8px">':''}</div></div>`;
  let curImg=selectedImageBase64;inp.value='';selectedImageBase64=null;
  let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble'>⏳ Thinking...</div></div>`;
  document.getElementById('chat').scrollTop=999999;
  let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,image:curImg})});
  let data=await res.json();document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble'>${marked.parse(data.reply)}</div>`;
  count++;document.getElementById('limit').innerText=`${count}/5`;
}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""
@app.route('/')
def home(): return HTML
@app.route('/logo.png')
def logo(): return send_from_directory('.', 'logo.png')
@app.route('/voice', methods=['POST'])
def voice():
    try:
        audio=request.files.get('audio');audio.save('/tmp/v.webm')
        with open('/tmp/v.webm','rb') as f:
            t=client.audio.transcriptions.create(model="whisper-large-v3", file=f)
        return jsonify({"text": t.text})
    except: return jsonify({"text":""})
@app.route('/chat', methods=['POST'])
def chat():
    try:
        d=request.json; msg=d.get('message',''); img=d.get('image')
        now_utc, now_ng, now_oslo=get_live()
        wiki=None
        if any(x in msg.lower() for x in ['who is','what is','tinubu']) and not img:
            wiki=wiki_live(msg)
        sys=f"You are LUMI AI. Time Nigeria {now_ng.strftime('%H:%M WAT')}."
        if wiki: sys+=f" WIKI: {wiki}"
        msgs=[{"role":"system","content":sys}]
        if img:
            msgs.append({"role":"user","content":[{"type":"text","text":msg or "What is this?"},{"type":"image_url","image_url":{"url":img}}]})
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        else:
            msgs.append({"role":"user","content":msg});model="openai/gpt-oss-20b"
        comp=client.chat.completions.create(model=model, messages=msgs)
        reply=comp.choices[0].message.content
        return jsonify({"reply":reply})
    except Exception as e: return jsonify({"reply":str(e)})
if __name__=='__main__': app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
