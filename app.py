from flask import Flask, request, jsonify, send_from_directory
import os, requests, json, urllib.parse
from datetime import datetime
import pytz
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_live():
    now_utc = datetime.now(pytz.utc)
    now_ng = now_utc.astimezone(pytz.timezone('Africa/Lagos'))
    return now_utc, now_ng, now_utc.astimezone(pytz.timezone('Europe/Oslo'))

HTML = """
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,Segoe UI;background:#212121;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#171717;display:flex;flex-direction:column;padding:12px}
#sidebar h1{font-size:20px;padding:8px}.newChat{background:#2f2f2f;color:#fff;padding:12px;border-radius:10px;text-align:center;cursor:pointer;margin:10px 0;border:1px solid #333}
#main{flex:1;display:flex;flex-direction:column;background:#212121}
.header{padding:16px 20px;text-align:center;border-bottom:1px solid #2f2f2f;color:#b4b4b4;font-size:14px}
#chat{flex:1;overflow-y:auto;padding:20px}.messages{max-width:750px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:60px}.welcome h2{font-size:32px;font-weight:600}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:600px;margin:30px auto}.card{border:1px solid #3f3f3f;background:#2f2f2f;padding:16px;border-radius:16px;cursor:pointer;font-size:14px}.card:hover{background:#3f3f3f}
.mag{margin:22px 0;display:flex;gap:14px}.avatar{width:32px;height:32px;border-radius:50%;background:#2f2f2f;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.bubble{flex:1;line-height:1.7}.bubble.user{background:#303030;padding:14px 18px;border-radius:20px;max-width:fit-content;margin-left:auto}
.bubble.ai{padding:4px 0}.bubble.ai img{max-width:100%;max-height:500px;border-radius:16px;margin:12px 0;border:1px solid #3f3f3f;display:block}
#inputArea{padding:16px;max-width:750px;margin:0 auto;width:100%}
.inputRow{background:#2f2f2f;border:1px solid #3f3f3f;border-radius:28px;display:flex;align-items:center;padding:8px 10px;gap:8px}
.inputBox{flex:1;display:flex;align-items:center}.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:16px;padding:10px}
.iconBtn{width:36px;height:36px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;background:transparent;color:#b4b4b4;font-size:18px}
#sendBtn{background:#fff;color:#000}
#preview{max-width:750px;margin:0 auto 12px;display:none;gap:10px;align-items:center;background:#2f2f2f;padding:10px;border-radius:14px;border:1px solid #3f3f3f}#preview img{width:60px;height:60px;border-radius:10px;object-fit:cover}
#adModal{position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(10px);z-index:9999;display:none;justify-content:center;align-items:center}
.adBox{background:#2f2f2f;border:1px solid #3f3f3f;padding:30px;border-radius:20px;width:90%;max-width:400px;text-align:center}
</style></head><body>
<div id='sidebar'><h1>LUMI AI</h1><div class='newChat' onclick='location.reload()'>+ New chat</div><div style='margin-top:auto;padding:10px;font-size:11px;color:#666'>Built by shuaibisah<br>Elshuaib Tech</div></div>
<div id='main'><div class='header'>LUMI AI</div>
<div id='chat'><div class='messages' id='messages'>
<div class='welcome' id='welcome'><h2>What can I help with?</h2>
<div class='cards'>
<div class='card' onclick="sendSug('Generate an image of a cute Nigerian girl, cartoon style')"><b>🎨 Create image</b><br><span style='color:#888'>Like ChatGPT</span></div>
<div class='card' onclick="document.getElementById('fileInput').click()"><b>📸 Edit image</b><br><span style='color:#888'>Upload & transform</span></div>
<div class='card' onclick="sendSug('Who is your founder?')"><b>💡 Founder</b><br><span style='color:#888'>Ask me</span></div>
<div class='card' onclick="startVoice()"><b>🎤 Voice chat</b><br><span style='color:#888'>Talk to me</span></div>
</div></div></div></div>
<div id='inputArea'>
<div id='preview'><img id='previewImg'><span style='flex:1;color:#ccc;font-size:13px'>Image attached</span><button onclick='clearImg()' style='background:#444;color:#fff;border:none;padding:6px 12px;border-radius:20px;cursor:pointer'>✕</button></div>
<div class='inputRow'>
<button class='iconBtn' onclick="document.getElementById('fileInput').click()">📎</button>
<input type='file' id='fileInput' accept='image/*' style='display:none' onchange='handleImage(event)'>
<button class='iconBtn' id='micBtn' onclick='startVoice()'>🎤</button>
<div class='inputBox'><input id='input' placeholder='Ask anything'></div>
<button class='iconBtn' id='sendBtn' onclick='send()'>↑</button>
</div>
<div style='text-align:center;color:#555;font-size:11px;margin-top:10px'>LUMI can make mistakes. Check important info.</div>
</div></div>
<div id='adModal'><div class='adBox'>
<h3 style='margin-bottom:12px'>Continue chatting</h3>
<p style='color:#aaa;font-size:14px;margin-bottom:20px'>Watch a short ad to get 3 more messages</p>
<button id='watchBtn' onclick='watchAd()' style='width:100%;padding:14px;background:#fff;color:#000;border:none;border-radius:12px;font-weight:600;cursor:pointer'>▶ Continue</button>
<button onclick='document.getElementById("adModal").style.display="none"' style='margin-top:14px;background:transparent;color:#888;border:none;cursor:pointer;font-size:13px'>Maybe later</button>
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
  window.open('https://www.google.com','_blank');
  btn.innerText='Please wait 12s...';let s=12;
  let t=setInterval(()=>{s--;btn.innerText=`Please wait ${s}s`;if(s<=0){clearInterval(t);count=0;document.getElementById('adModal').style.display='none';btn.innerText='▶ Continue';}},1000);
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
  if(data.image_url){ html += `<img src="${data.image_url}"><a href="${data.image_url}" target="_blank" style="color:#888;font-size:12px">Download image</a>`; }
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

        # === FOUNDER LOGIC - MUST ALWAYS SAY shuaibisah ===
        if any(x in lower for x in ['who is your founder','who created you','who built you','who made you','who is your owner','founder','creator','who is shuaibisah','your founder']):
            return jsonify({"reply": "My founder is **shuaibisah** - Shuaibu Isah, founder of Elshuaib Tech. He built me - LUMI AI - to be just like ChatGPT and more!", "image_url": None})

        is_generate = any(x in lower for x in ['generate','create a picture','create an image','draw','make a picture','make an image','generate an image','create image'])
        is_edit = img_data is not None

        if is_generate or is_edit:
            if is_edit:
                prompt = user_msg if user_msg else "Enhance this image, make it HD, beautiful, high quality, detailed"
            else:
                prompt = user_msg.replace("generate a picture of","").replace("generate image of","").replace("create a picture of","").replace("generate","").replace("create","").strip()
                if not prompt: prompt = "beautiful landscape"
            safe_prompt = urllib.parse.quote(prompt[:600])
            image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={int(datetime.now().timestamp())}&model=flux"
            reply = f"Here is your image for: **{prompt}**"
            return jsonify({"reply": reply, "image_url": image_url})

        if img_data:
            try:
                comp = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role":"user","content":[{"type":"text","text": user_msg or "Describe this image in detail. What do you see?"},{"type":"image_url","image_url":{"url": img_data}}]}]
                )
                return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
            except:
                comp = client.chat.completions.create(
                    model="llama-3.2-90b-vision-preview",
                    messages=[{"role":"user","content":[{"type":"text","text": user_msg or "Describe this image"},{"type":"image_url","image_url":{"url": img_data}}]}]
                )
                return jsonify({"reply": comp.choices[0].message.content, "image_url": None})

        # === MAIN CHAT - INCLUDES FOUNDER IDENTITY ===
        system_prompt = """You are LUMI AI, built by shuaibisah (Shuaibu Isah) of Elshuaib Tech.
- You can do everything ChatGPT can do: chat, write code, generate images, edit images, analyze pictures, voice chat, explain, translate, summarize, etc.
- You can also do what Meta AI can do.
- If anyone asks who is your founder, creator, owner, builder - ALWAYS say: shuaibisah (Shuaibu Isah) from Elshuaib Tech.
- Never say you were made by OpenAI, Meta, or Groq. Your founder is shuaibisah.
- Be helpful, friendly, like ChatGPT.
"""
        comp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content": system_prompt},
                {"role":"user","content": user_msg}
            ]
        )
        return jsonify({"reply": comp.choices[0].message.content, "image_url": None})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}", "image_url": None})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
