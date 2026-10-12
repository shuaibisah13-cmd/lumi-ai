from flask import Flask, request, jsonify, send_from_directory
import os, json, urllib.parse
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI, sans-serif;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}

/* YOUR ORIGINAL GREEN + BLACK BACKGROUND - RESTORED */
#sidebar{width:260px;background:#000000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px}
#sidebar h1{font-size:22px;padding:10px;color:#fff}
#sidebar h1 span{color:#4caf50}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0;font-size:14px}
.newChat:hover{background:#45a049}
#main{flex:1;display:flex;flex-direction:column;background:#0a0a0a}
.header{padding:14px 20px;text-align:center;border-bottom:1px solid #1a1a1a;background:#000;color:#888;font-size:13px}
#chat{flex:1;overflow-y:auto;padding:20px}.messages{max-width:800px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:40px}
.welcome h2{font-size:36px;color:#4caf50;font-weight:bold}
.welcome p{color:#888;margin-top:8px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:620px;margin:30px auto}
.card{border:1px solid #222;background:#111111;padding:16px;border-radius:14px;cursor:pointer;transition:0.2s}
.card:hover{border-color:#4caf50;background:#151515}
.card b{color:#fff}.card span{color:#777;font-size:12px}
.mag{margin:20px 0;display:flex;gap:12px}.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.bubble{flex:1;line-height:1.6}.bubble.user{background:#1a3a1e;padding:12px 16px;border-radius:18px 18px 4px 18px;border:1px solid #2a5a2e}
.bubble.ai img{max-width:100%;max-height:500px;border-radius:14px;margin:10px 0;border:1px solid #333;display:block}
#inputArea{padding:16px;max-width:800px;margin:0 auto;width:100%;background:#0a0a0a;border-top:1px solid #1a1a1a}
.inputRow{display:flex;gap:8px;align-items:center}
.inputBox{flex:1;background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px}
.iconBtn{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px}
#sendBtn{background:#fff;color:#000}.iconBtnSub{background:#222;color:#fff;border:1px solid #333}
#preview{max-width:800px;margin:0 auto 10px;display:none;gap:10px;align-items:center;background:#111;padding:10px;border-radius:12px;border:1px solid #222}#preview img{width:60px;height:60px;border-radius:10px;object-fit:cover}
#adModal{position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:9999;display:none;justify-content:center;align-items:center}
.adBox{background:#111;border:1px solid #333;padding:28px;border-radius:20px;width:90%;max-width:400px;text-align:center}
</style></head><body>

<div id='sidebar'>
<h1>LUMI <span>AI</span></h1>
<div class='newChat' onclick='location.reload()'>+ New chat</div>
<div style='margin-top:20px;padding:10px'>
<div style='color:#555;font-size:11px;margin-bottom:10px'>PROJECTS</div>
<div style='color:#888;font-size:13px;padding:8px;background:#111;border-radius:8px;margin-bottom:6px;cursor:pointer'>💬 Recent Chats</div>
<div style='color:#888;font-size:13px;padding:8px;background:#111;border-radius:8px;margin-bottom:6px;cursor:pointer'>🎨 Generated Images</div>
<div style='color:#888;font-size:13px;padding:8px;background:#111;border-radius:8px;cursor:pointer'>📸 Edited Pictures</div>
</div>
<div style='margin-top:auto;padding:10px;font-size:11px;color:#555'>Built by shuaibisah<br>Elshuaib Tech • LUMI PRO MAX</div>
</div>

<div id='main'>
<div class='header'>LUMI AI • ChatGPT-like • Founder: shuaibisah</div>
<div id='chat'><div class='messages' id='messages'>
<div class='welcome' id='welcome'>
<h2>LUMI AI PRO MAX</h2>
<p>Everything ChatGPT can do + Picture Edit + Generate</p>
<div class='cards'>
<div class='card' onclick="sendSug('Generate an image of a cute Nigerian girl, cartoon style')"><b>🎨 Create image</b><br><span>Like ChatGPT</span></div>
<div class='card' onclick="document.getElementById('fileInput').click()"><b>📸 Edit image</b><br><span>Upload & transform</span></div>
<div class='card' onclick="sendSug('Who is your founder?')"><b>👤 Founder</b><br><span>Ask me</span></div>
<div class='card' onclick="startVoice()"><b>🎤 Voice chat</b><br><span>Talk to me</span></div>
</div>
</div>
</div></div>

<div id='inputArea'>
<div id='preview'><img id='previewImg'><span style='flex:1;color:#ccc;font-size:13px'>Image attached</span><button onclick='clearImg()' style='background:#333;color:#fff;border:none;padding:6px 12px;border-radius:20px;cursor:pointer'>✕</button></div>
<div class='inputRow'>
<button class='iconBtn iconBtnSub' onclick="document.getElementById('fileInput').click()">📎</button>
<input type='file' id='fileInput' accept='image/*' style='display:none' onchange='handleImage(event)'>
<button class='iconBtn iconBtnSub' id='micBtn' onclick='startVoice()'>🎤</button>
<div class='inputBox'><input id='input' placeholder='Ask anything or edit picture...'><button id='sendBtn' class='iconBtn' onclick='send()'>↑</button></div>
</div>
</div>
</div>

<div id='adModal'><div class='adBox'>
<h3 style='color:#4caf50;margin-bottom:10px'>Continue</h3>
<p style='color:#aaa;font-size:14px;margin-bottom:20px'>Watch short ad to get 3 more messages</p>
<button id='watchBtn' onclick='watchAd()' style='width:100%;padding:14px;background:#4caf50;color:#000;border:none;border-radius:12px;font-weight:bold;cursor:pointer'>▶ Continue</button>
<button onclick='document.getElementById("adModal").style.display="none"' style='margin-top:12px;background:transparent;color:#666;border:none;cursor:pointer'>Close</button>
</div></div>

<script>
let count=0;let selectedImageBase64=null;let mediaRecorder=null;let audioChunks=[];
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
  let t=setInterval(()=>{s--;btn.innerText=`Wait ${s}s`;if(s<=0){clearInterval(t);count=0;document.getElementById('adModal').style.display='none';btn.innerText='▶ Continue';}},1000);
}
async function send(){
  let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg &&!selectedImageBase64)return;
  if(count>=5){document.getElementById('adModal').style.display='flex';return;}
  document.getElementById('welcome')?.remove();
  let ms=document.getElementById('messages');
  ms.innerHTML+=`<div class='mag' style='justify-content:flex-end'><div class='bubble user'>${msg}${selectedImageBase64?'<br><img src="'+selectedImageBase64+'" style="max-width:200px;border-radius:12px;margin-top:8px">':''}</div></div>`;
  let curImg=selectedImageBase64;let curMsg=msg;inp.value='';clearImg();
  let id='a'+Date.now();ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar'>✨</div><div class='bubble ai'>● ● ●</div></div>`;
  document.getElementById('chat').scrollTop=999999;
  let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:curMsg,image:curImg})});
  let data=await res.json();
  let html = marked.parse(data.reply||'');
  if(data.image_url){ html += `<img src="${data.image_url}"><a href="${data.image_url}" target="_blank" style="color:#4caf50;font-size:12px">⬇️ Download</a>`; }
  document.getElementById(id).innerHTML=`<div class='avatar'>✨</div><div class='bubble ai'>${html}</div>`;
  count++;
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
        d=request.json; user_msg=d.get('message','').strip(); img_data=d.get('image')
        lower=user_msg.lower()
        if any(x in lower for x in ['founder','who built you','who made you','who created you','owner']):
            return jsonify({"reply": "My founder is **shuaibisah** - Shuaibu Isah, founder of Elshuaib Tech. He built LUMI AI to do everything ChatGPT can do!", "image_url": None})
        is_generate = any(x in lower for x in ['generate','create a picture','create an image','draw','make a picture'])
        is_edit = img_data is not None
        if is_generate or is_edit:
            prompt = user_msg if user_msg else "Make HD beautiful"
            if not is_edit: prompt = user_msg.replace("Generate","").replace("create","").strip() or "beautiful image"
            safe = urllib.parse.quote(prompt[:600])
            url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={int(datetime.now().timestamp())}&model=flux"
            return jsonify({"reply": f"Here is your image for: **{prompt}**", "image_url": url})
        if img_data:
            try:
                comp = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text": user_msg or "Describe this image"},{"type":"image_url","image_url":{"url": img_data}}]}])
                return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
            except:
                comp = client.chat.completions.create(model="llama-3.2-90b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text": user_msg or "Describe"},{"type":"image_url","image_url":{"url": img_data}}]}])
                return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
        system = "You are LUMI AI, built by shuaibisah (Shuaibu Isah) of Elshuaib Tech. Do everything ChatGPT can: chat, code, generate images, edit images, analyze pictures, voice. If asked founder, say shuaibisah. Never say OpenAI/Meta made you."
        comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":system},{"role":"user","content":user_msg}])
        return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}", "image_url": None})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
