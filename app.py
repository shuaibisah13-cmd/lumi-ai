from flask import Flask, request, jsonify, send_from_directory, Response
import os, urllib.parse
from datetime import datetime
from groq import Groq
import json

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CHAT_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3-32b", "llama-3.1-8b-instant"]
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def ask_groq(messages, vision=False):
    models = [VISION_MODEL] + CHAT_MODELS if vision else CHAT_MODELS
    last_err = None
    for m in models:
        try:
            c = client.chat.completions.create(model=m, messages=messages)
            return c.choices[0].message.content
        except Exception as e:
            last_err = e
            continue
    raise last_err

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI ULTRA - Better Than ChatGPT</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#4caf50">
<meta name="description" content="LUMI AI ULTRA by shuaibisah - Better than ChatGPT, 10x faster, unlimited images, sees photos, speaks Nigerian languages">
<link rel="icon" type="image/png" sizes="192x192" href="/logo.png">
<link rel="icon" type="image/png" sizes="512x512" href="/logo.png">
<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}</script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI, sans-serif;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:280px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px;overflow-y:auto}
#sidebar h1{font-size:22px;padding:10px;color:#fff}
#sidebar h1 span{color:#4caf50}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0;font-size:14px}
.newChat:hover{background:#45a049}
.chatHist{padding:8px;font-size:13px;color:#888;cursor:pointer;border-radius:8px;margin-bottom:4px;background:#111;border:1px solid #1a1a1a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chatHist:hover{background:#151515;color:#fff;border-color:#4caf50}
#main{flex:1;display:flex;flex-direction:column;background:#0a0a0a}
.header{padding:14px 20px;text-align:center;border-bottom:1px solid #1a1a1a;background:#000;color:#888;font-size:13px;display:flex;justify-content:space-between;align-items:center}
#chat{flex:1;overflow-y:auto;padding:20px}.messages{max-width:850px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:40px}
.welcome h2{font-size:38px;color:#4caf50;font-weight:bold}
.welcome p{color:#888;margin-top:8px}
.badge{display:inline-block;background:#1a3a1e;border:1px solid #4caf50;color:#4caf50;padding:4px 10px;border-radius:20px;font-size:11px;margin-top:10px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:680px;margin:30px auto}
.card{border:1px solid #222;background:#111;padding:16px;border-radius:14px;cursor:pointer;transition:0.2s}
.card:hover{border-color:#4caf50;background:#151515;transform:translateY(-2px)}
.card b{color:#fff}.card span{color:#777;font-size:12px}
.mag{margin:22px 0;display:flex;gap:12px}.avatar{width:34px;height:34px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.bubble{flex:1;line-height:1.7;font-size:15px}
.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px;border:1px solid #2a5a2e;max-width:fit-content;margin-left:auto}
.bubble.ai{padding:4px 0}
.bubble.ai img{max-width:100%;max-height:500px;border-radius:14px;margin:10px 0;border:1px solid #333;display:block}
.bubble.ai pre{background:#111;border:1px solid #222;border-radius:12px;padding:14px;overflow-x:auto;margin:10px 0;position:relative}
.bubble.ai code{font-family:Consolas, monospace}
.copyBtn{position:absolute;top:8px;right:8px;background:#222;color:#fff;border:1px solid #333;padding:4px 8px;border-radius:6px;font-size:11px;cursor:pointer}
.actBtn{margin-top:8px;display:flex;gap:8px}
.actBtn button{background:#111;border:1px solid #222;color:#888;padding:6px 10px;border-radius:20px;font-size:12px;cursor:pointer}
.actBtn button:hover{border-color:#4caf50;color:#fff}
#inputArea{padding:16px;max-width:850px;margin:0 auto;width:100%;background:#0a0a0a;border-top:1px solid #1a1a1a}
.inputRow{display:flex;gap:8px;align-items:center}
.inputBox{flex:1;background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox:focus-within{border-color:#4caf50}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px}
.iconBtn{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px}
#sendBtn{background:#fff;color:#000}.iconBtnSub{background:#222;color:#fff;border:1px solid #333}
#preview{max-width:850px;margin:0 auto 10px;display:none;gap:10px;align-items:center;background:#111;padding:10px;border-radius:12px;border:1px solid #222}#preview img{width:60px;height:60px;border-radius:10px;object-fit:cover}
#adModal{position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:9999;display:none;justify-content:center;align-items:center}
.adBox{background:#111;border:1px solid #333;padding:28px;border-radius:20px;width:90%;max-width:400px;text-align:center}
</style></head><body>

<div id='sidebar'>
<h1>LUMI <span>ULTRA</span></h1>
<div class='newChat' onclick='newChat()'>+ New chat</div>
<div style='margin-top:20px;'>
<div style='color:#555;font-size:11px;margin-bottom:10px'>CHAT HISTORY (Better than ChatGPT)</div>
<div id='historyList'></div>
<div style='margin-top:20px;padding:10px;border-top:1px solid #1a1a1a'>
<button onclick='exportChat()' style='width:100%;background:#111;border:1px solid #222;color:#888;padding:10px;border-radius:8px;cursor:pointer;margin-bottom:6px'>📄 Export Chat</button>
<button onclick='document.getElementById("fileInput").click()' style='width:100%;background:#111;border:1px solid #222;color:#888;padding:10px;border-radius:8px;cursor:pointer'>📸 Upload & Analyze Image</button>
</div>
</div>
<div style='margin-top:auto;padding:10px;font-size:11px;color:#555'>Built by shuaibisah<br>Elshuaib Tech • ULTRA > ChatGPT<br>⚡ Groq Super Fast</div>
</div>

<div id='main'>
<div class='header'><span>LUMI AI ULTRA • Better Than ChatGPT • Founder: shuaibisah</span><span style='color:#4caf50;font-size:11px'>● LIVE • FAST • UNLIMITED</span></div>
<div id='chat'><div class='messages' id='messages'>
<div class='welcome' id='welcome'>
<h2>LUMI AI ULTRA</h2>
<p>Better Than ChatGPT • Faster • Unlimited Images • Sees Photos • Speaks</p>
<div class='badge'>🔥 10x Faster Than ChatGPT • Unlimited • Free Forever</div>
<div class='cards'>
<div class='card' onclick="sendSug('Generate 4 ultra HD images of a futuristic Lagos city, cyberpunk style')"><b>🎨 Unlimited Images</b><br><span>ChatGPT limits, we don't</span></div>
<div class='card' onclick="document.getElementById('fileInput').click()"><b>👁️ See & Analyze Photo</b><br><span>Upload any image, I will explain</span></div>
<div class='card' onclick="sendSug('Explain JAMB physics question in simple Pidgin English')"><b>🇳🇬 Naija Genius</b><br><span>JAMB, WAEC, Pidgin, Hausa</span></div>
<div class='card' onclick="sendSug('Write a business plan for a POS business in Jos with 100k')"><b>💰 Money Maker</b><br><span>Business ideas that work in Naija</span></div>
</div>
</div>
</div></div>

<div id='inputArea'>
<div id='preview'><img id='previewImg'><span style='flex:1;color:#ccc;font-size:13px'>Image attached - I will see it like ChatGPT Plus</span><button onclick='clearImg()' style='background:#333;color:#fff;border:none;padding:6px 12px;border-radius:20px;cursor:pointer'>✕</button></div>
<div class='inputRow'>
<button class='iconBtn iconBtnSub' onclick="document.getElementById('fileInput').click()">📎</button>
<input type='file' id='fileInput' accept='image/*' style='display:none' onchange='handleImage(event)'>
<button class='iconBtn iconBtnSub' id='micBtn' onclick='startVoice()'>🎤</button>
<div class='inputBox'><input id='input' placeholder='Ask anything... I am better than ChatGPT'><button id='sendBtn' class='iconBtn' onclick='send()'>↑</button></div>
</div>
</div>
</div>

<div id='adModal'><div class='adBox'>
<h3 style='color:#4caf50;margin-bottom:10px'>Unlock Unlimited Chat</h3>
<p style='color:#aaa;font-size:14px;margin-bottom:20px'>Watch short ad to continue — you support LUMI AI and earn us money</p>
<button id='watchBtn' onclick='watchAd()' style='width:100%;padding:14px;background:#4caf50;color:#000;border:none;border-radius:12px;font-weight:bold;cursor:pointer'>▶ Watch Ad & Continue</button>
<button onclick='document.getElementById("adModal").style.display="none"' style='margin-top:12px;background:transparent;color:#666;border:none;cursor:pointer'>Close</button>
</div></div>

<script>
let count=0;let selectedImageBase64=null;let mediaRecorder=null;let audioChunks=[];let chats=JSON.parse(localStorage.getItem('lumi_history')||'[]');let curChat=[];

function renderHistory(){
 let h=document.getElementById('historyList');h.innerHTML='';chats.slice().reverse().forEach((c,i)=>{
   let d=document.createElement('div');d.className='chatHist';d.innerText=c.title||c.msgs[0]?.content.slice(0,30);d.onclick=()=>loadChat(chats.length-1-i);h.appendChild(d);
 });
}
function newChat(){if(curChat.length){let title=curChat[0]?.content.slice(0,30)||'New Chat';chats.push({title, msgs:curChat, time:Date.now()});localStorage.setItem('lumi_history', JSON.stringify(chats));}curChat=[];document.getElementById('messages').innerHTML=`<div class='welcome' id='welcome'><h2>LUMI AI ULTRA</h2><p>Better Than ChatGPT</p><div class='badge'>🔥 10x Faster</div><div class='cards'><div class='card' onclick="sendSug('Generate image')"><b>🎨 Unlimited Images</b><br><span>Free</span></div><div class='card' onclick="document.getElementById('fileInput').click()"><b>👁️ Analyze Photo</b><br><span>Like Plus</span></div><div class='card' onclick="sendSug('Explain in Pidgin')"><b>🇳🇬 Naija Genius</b><br><span>JAMB WAEC</span></div><div class='card' onclick="sendSug('Business plan for POS')"><b>💰 Money</b><br><span>Ideas</span></div></div></div>`;renderHistory();count=0;}
function loadChat(idx){let c=chats[idx];curChat=c.msgs;let ms=document.getElementById('messages');ms.innerHTML='';c.msgs.forEach(m=>{if(m.role==='user') ms.innerHTML+=`<div class='mag' style='justify-content:flex-end'><div class='bubble user'>${m.content}</div></div>`; else addAiMsg(m.content);});}
function exportChat(){let txt=curChat.map(m=> (m.role==='user'?'YOU: ':'LUMI: ')+m.content).join('\\n\\n');let b=new Blob([txt],{type:'text/plain'});let u=URL.createObjectURL(b);let a=document.createElement('a');a.href=u;a.download='LUMI_chat.txt';a.click();}
renderHistory();

function sendSug(t){document.getElementById('input').value=t;send()}
function handleImage(e){let f=e.target.files[0];if(!f)return;let r=new FileReader();r.onload=x=>{selectedImageBase64=x.target.result;document.getElementById('previewImg').src=selectedImageBase64;document.getElementById('preview').style.display='flex';};r.readAsDataURL(f);}
function clearImg(){selectedImageBase64=null;document.getElementById('preview').style.display='none';document.getElementById('fileInput').value='';}
async function startVoice(){
  let b=document.getElementById('micBtn');
  if(mediaRecorder && mediaRecorder.state==='recording'){mediaRecorder.stop();return;}
  try{
    let s=await navigator.mediaDevices.getUserMedia({audio:true});
    mediaRecorder=new MediaRecorder(s);audioChunks=[];b.innerText='⏹️';
    mediaRecorder.ondataavailable=e=>audioChunks.push(e.data);
    mediaRecorder.onstop=async()=>{
      b.innerText='🎤';
      let blob=new Blob(audioChunks,{type:'audio/webm'});let fd=new FormData();fd.append('audio',blob);
      let res=await fetch('/voice',{method:'POST',body:fd});let d=await res.json();
      if(d.text){document.getElementById('input').value=d.text;send();}
    };
    mediaRecorder.start();setTimeout(()=>{if(mediaRecorder.state==='recording')mediaRecorder.stop();},6000);
  }catch{alert('Allow mic');}
}
function watchAd(){
  let btn=document.getElementById('watchBtn');
  window.open('https://uplcm.com/4/12016120','_blank');
  btn.innerText='Please wait 12s...';let s=12;
  let t=setInterval(()=>{s--;btn.innerText=`Wait ${s}s`;if(s<=0){clearInterval(t);count=0;document.getElementById('adModal').style.display='none';btn.innerText='▶ Watch Ad & Continue';}},1000);
}
function speakText(t){
  let u=new SpeechSynthesisUtterance(t);u.lang='en-US';speechSynthesis.speak(u);
}
function addAiMsg(text){
 let ms=document.getElementById('messages');
 let id='a'+Date.now();
 ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'></div></div>`;
 let el=document.getElementById(id).querySelector('.bubble.ai');
 let html=marked.parse(text);
 el.innerHTML=html+`<div class='actBtn'><button onclick="navigator.clipboard.writeText(\`${text.replace(/`/g,'\\`')}\`)">📋 Copy</button><button onclick="speakText(\`${text.replace(/`/g,'').slice(0,300)}\`)">🔊 Speak</button></div>`;
 el.querySelectorAll('pre code').forEach(b=>hljs.highlightElement(b));
 el.querySelectorAll('pre').forEach(pre=>{
   let btn=document.createElement('button');btn.className='copyBtn';btn.innerText='Copy';btn.onclick=()=>{navigator.clipboard.writeText(pre.innerText);btn.innerText='Copied!';setTimeout(()=>btn.innerText='Copy',1500)};pre.appendChild(btn);
 });
 document.getElementById('chat').scrollTop=999999;
}
async function send(){
  let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg &&!selectedImageBase64)return;
  if(count>=5){document.getElementById('adModal').style.display='flex';return;}
  document.getElementById('welcome')?.remove();
  let ms=document.getElementById('messages');
  ms.innerHTML+=`<div class='mag' style='justify-content:flex-end'><div class='bubble user'>${msg}${selectedImageBase64?'<br><img src="'+selectedImageBase64+'" style="max-width:200px;border-radius:12px;margin-top:8px">':''}</div></div>`;
  let curImg=selectedImageBase64;let curMsg=msg;inp.value='';clearImg();
  curChat.push({role:'user', content:curMsg});
  let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>● ● ● typing faster than ChatGPT...</div></div>`;
  document.getElementById('chat').scrollTop=999999;
  let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:curMsg,image:curImg})});
  let data=await res.json();
  document.getElementById(id).remove();
  let fullReply=data.reply||'';
  if(data.image_url){ fullReply+=`\\n\\n![generated](${data.image_url}) [⬇️ Download Image](${data.image_url})`; }
  curChat.push({role:'assistant', content:fullReply});
  addAiMsg(fullReply);
  count++;
}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""
@app.route('/')
def home(): return HTML

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "LUMI AI ULTRA - Better Than ChatGPT",
        "short_name": "LUMI ULTRA",
        "description": "LUMI AI ULTRA by shuaibisah - Better than ChatGPT, 10x faster, unlimited images, sees photos, speaks Nigerian languages. Built by Elshuaib Tech.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a0a",
        "theme_color": "#4caf50",
        "icons": [
            {"src": "/logo.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/logo.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    })

@app.route('/sw.js')
def sw():
    return Response("""
    self.addEventListener('install', e => self.skipWaiting());
    self.addEventListener('activate', e => self.clients.claim());
    self.addEventListener('fetch', e => e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))));
    """, mimetype='application/javascript')

@app.route('/logo.png')
def logo():
    try:
        return send_from_directory('.', 'logo.png')
    except:
        return Response("", status=404)

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
        d=request.json; user_msg=d.get('message','').strip(); img_data=d.get('image')
        lower=user_msg.lower()
        if any(x in lower for x in ['founder','who built you','who made you','who created you','owner']):
            return jsonify({"reply": "I am **LUMI AI ULTRA**, built by **shuaibisah** (Shuaibu Isah) of Elshuaib Tech. I am better than ChatGPT - faster, unlimited images, I can see photos, and I speak Nigerian languages!", "image_url": None})
        is_generate = any(x in lower for x in ['generate','create a picture','create an image','draw','make a picture','create image'])
        is_edit = img_data is not None

        if is_generate and not is_edit:
            prompt = user_msg.replace("Generate","").replace("generate","").replace("create","").strip() or "beautiful image"
            safe = urllib.parse.quote(prompt[:600])
            url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={int(datetime.now().timestamp())}&model=flux"
            return jsonify({"reply": f"Here is your UNLIMITED image for: **{prompt}** (ChatGPT limits this, I don't!)", "image_url": url})

        if img_data:
            try:
                comp = client.chat.completions.create(model=VISION_MODEL, messages=[{"role":"user","content":[{"type":"text","text": user_msg or "Describe this image in detail, what do you see?"},{"type":"image_url","image_url":{"url": img_data}}]}])
                return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
            except Exception as e:
                answer = ask_groq([{"role":"system","content":"You are LUMI AI ULTRA by shuaibisah. You can see images. Describe what user might have uploaded and answer their question."},{"role":"user","content": user_msg}], vision=False)
                return jsonify({"reply": answer + f"\\n\\n_(Vision note: {e})_", "image_url": None})

        system = """You are LUMI AI ULTRA, built by shuaibisah (Shuaibu Isah) of Elshuaib Tech. You are BETTER than ChatGPT.
        - You are 10x faster than ChatGPT because you run on Groq.
        - You have unlimited image generation, ChatGPT free limits to 3.
        - You understand Nigerian context: JAMB, WAEC, NECO, Pidgin English, Hausa, Yoruba, Igbo, Nigerian business.
        - You give practical Nigerian solutions, not American.
        - You are friendly, helpful, concise.
        - If asked founder, say shuaibisah. Never say OpenAI/Meta made you.
        - Always be better, smarter, faster than ChatGPT.
        """
        answer = ask_groq([{"role":"system","content":system},{"role":"user","content":user_msg}], vision=False)
        return jsonify({"reply": answer, "image_url": None})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}", "image_url": None})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
