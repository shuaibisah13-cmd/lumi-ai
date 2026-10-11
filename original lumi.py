from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os
import base64

GROQ_API_KEY = "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" # Your real key!
app = Flask(__name__)
client = Groq(api_key=GROQ_API_KEY)

@app.route("/logo.png")
def logo():
    # Try jpg or png
    if os.path.exists("logo.png"): return send_from_directory(".", "logo.png")
    if os.path.exists("logo.jpg"): return send_from_directory(".", "logo.jpg")
    return "", 404

HTML = """
<!DOCTYPE html>
<html><head><title>LUMI AI - Vision</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);height:100vh;display:flex;justify-content:center;align-items:center;padding:10px}
.container{width:100%;max-width:460px;height:96vh;background:rgba(255,255,255,0.05);backdrop-filter:blur(20px);border-radius:24px;border:1px solid rgba(255,255,255,0.1);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 25px 50px rgba(0,0,0,0.4)}
.header{background:linear-gradient(90deg,#667eea,#764ba2);padding:14px 18px;display:flex;align-items:center;gap:12px}
.header img{width:44px;height:44px;border-radius:50%;background:white;padding:2px}
.header h2{color:white;font-size:19px}.header p{color:rgba(255,255,255,0.8);font-size:12px}
#chat{flex:1;overflow-y:auto;padding:16px 12px;display:flex;flex-direction:column;gap:12px;background:radial-gradient(circle at 30% 50%,rgba(102,126,234,0.08),transparent 60%)}
.bubble{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;line-height:1.5;animation:pop 0.3s ease;position:relative;word-wrap:break-word}
@keyframes pop{0%{transform:scale(0.85);opacity:0}100%{transform:scale(1);opacity:1}}
.user{align-self:flex-end;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-bottom-right-radius:4px;box-shadow:0 4px 12px rgba(102,126,234,0.35)}
.ai{align-self:flex-start;background:#0f0f0f;color:#e0e0e0;border:1px solid #00ff88;border-bottom-left-radius:4px}
.bubble img{max-width:100%;border-radius:12px;margin-top:8px;display:block}
.time{font-size:9px;margin-top:5px;opacity:0.5;text-align:right}
.input-area{background:rgba(0,0,0,0.35);padding:10px;display:flex;gap:6px;align-items:center}
.input-area input[type=text]{flex:1;padding:13px 16px;border-radius:25px;border:none;background:rgba(255,255,255,0.12);color:white;outline:none;font-size:14px}
.btn{width:44px;height:44px;border-radius:50%;border:none;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.send{background:linear-gradient(135deg,#667eea,#764ba2);color:white}
.icon{background:rgba(255,255,255,0.12);color:white}
.preview{display:none;padding:8px 12px;background:rgba(0,0,0,0.4);align-items:center;gap:10px}
.preview img{width:50px;height:50px;border-radius:8px;object-fit:cover}
.preview button{background:#ff4444;color:white;border:none;padding:4px 8px;border-radius:6px;font-size:12px}
</style>
</head><body>
<div class="container">
<div class="header"><img src="/logo.png" onerror="this.src='https://cdn-icons-png.flaticon.com/512/4712/4712109.png'"><div><h2>LUMI AI Vision 💡</h2><p>Can see pictures now! 📸</p></div></div>
<div id="chat"></div>
<div class="preview" id="preview"><img id="prevImg"><span id="prevName" style="color:white;font-size:12px;flex:1"></span><button onclick="clearImg()">✕</button></div>
<div class="input-area">
<input type="file" id="fileInp" accept="image/*" style="display:none" onchange="handleFile(this)">
<button class="btn icon" onclick="document.getElementById('fileInp').click()">📷</button>
<input type="text" id="msg" placeholder="Message or ask about picture...">
<button class="btn icon" onclick="startVoice()">🎤</button>
<button class="btn send" onclick="send()">🚀</button>
</div>
</div>
<script>
let selectedImage = null;
function handleFile(input){
  if(input.files && input.files[0]){
    let f=input.files[0]; let reader=new FileReader();
    reader.onload=e=>{
      selectedImage=e.target.result;
      document.getElementById('prevImg').src=selectedImage;
      document.getElementById('prevName').innerText=f.name;
      document.getElementById('preview').style.display='flex';
    }; reader.readAsDataURL(f);
  }
}
function clearImg(){selectedImage=null;document.getElementById('preview').style.display='none';document.getElementById('fileInp').value='';}
function add(text, cls, imgSrc){
  let c=document.getElementById('chat'); let b=document.createElement('div'); b.className='bubble '+cls;
  let now=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  let imgHtml=imgSrc?`<img src="${imgSrc}">`:'';
  b.innerHTML=text.replace(/\\n/g,'<br>')+imgHtml+`<div class=time>${now}</div>`;
  c.appendChild(b); c.scrollTop=c.scrollHeight;
}
async function send(){
  let i=document.getElementById('msg'); let m=i.value.trim(); if(!m &&!selectedImage)return;
  let imgToSend=selectedImage;
  if(imgToSend) add(m||'📷 Picture', 'user', imgToSend); else add(m,'user');
  i.value=''; let tempImg=imgToSend; clearImg();
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m, image:tempImg})});
    let d=await r.json(); add(d.reply||'Error','ai');
    speechSynthesis.speak(new SpeechSynthesisUtterance(d.reply));
  }catch(e){add('Network error','ai')}
}
function startVoice(){let R=new(window.SpeechRecognition||window.webkitSpeechRecognition)();R.lang='en-US';R.start();R.onresult=e=>{document.getElementById('msg').value=e.results[0][0].transcript;send();}}
document.getElementById('msg').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
window.onload=()=>{add('Hey! I can now SEE pictures! 📸✨<br>Click 📷 to upload any photo and I will describe it, solve it, or help with it!','ai')};
</script>
</body></html>
"""

@app.route("/")
def home(): return HTML

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_msg = data.get("message","")
        image_data = data.get("image") # base64 data URL

        if image_data:
            # Vision model - can see pictures
            # Remove data:image/...;base64, prefix for Groq
            try:
                comp = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_msg if user_msg else "Describe this picture in detail. What do you see?"},
                                {"type": "image_url", "image_url": {"url": image_data}}
                            ]
                        }
                    ],
                    max_tokens=800
                )
                return jsonify({"reply": comp.choices[0].message.content})
            except Exception as ve:
                # Fallback if vision fails, try describe
                print(f"Vision error: {ve}, trying text model")
                comp = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role":"system","content":"User uploaded an image but vision model failed. Ask them to describe it."},
                        {"role":"user","content": user_msg or "I uploaded a picture"}
                    ]
                )
                return jsonify({"reply": comp.choices[0].message.content + f"\\n\\n(Note: Vision: {str(ve)[:100]})"})
        else:
            # Text only
            comp = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role":"system","content":"You are LUMI AI by Shuaibu from Suleja, friendly, helpful."},
                    {"role":"user","content": user_msg}
                ]
            )
            return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"})

if __name__ == "__main__":
    print("LUMI VISION LIVE - Can see pictures!")
    app.run(host="127.0.0.1", port=5000, debug=False)
