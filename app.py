from flask import Flask, request, jsonify, send_from_directory
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI - Premium</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#ececec;display:flex;height:100vh;overflow:hidden}
#sidebar{width:260px;background:#000;border-right:1px solid #222;display:flex;flex-direction:column;padding:12px;transition:0.3s}
#sidebar h1{font-size:22px;padding:12px;color:#fff;letter-spacing:1px} #sidebar h1 span{color:#4caf50}
.newChat{background:#4caf50;color:#000;padding:12px;border-radius:10px;text-align:center;font-weight:bold;cursor:pointer;margin:10px 0}
.newChat:hover{background:#45a049}
.hist{flex:1;overflow-y:auto;margin-top:10px}
.histItem{padding:10px;border-radius:8px;color:#888;font-size:13px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.histItem:hover{background:#111;color:#fff}
#main{flex:1;display:flex;flex-direction:column;position:relative;background:radial-gradient(1200px 600px at 50% -10%, #1a2e1a 0%, #0a0a0a 60%)}
.header{padding:16px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1a1a1a;background:rgba(0,0,0,0.5);backdrop-filter:blur(10px)}
.header b{font-size:18px}
#chat{flex:1;overflow-y:auto;padding:30px;position:relative}
#watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.06;pointer-events:none;z-index:0}
#watermark img{width:380px;filter:none}
#watermark{opacity:o.20}
.messages{position:relative;z-index:2;max-width:800px;margin:0 auto;width:100%}
.welcome{text-align:center;margin-top:80px;animation:fadeUp 0.8s ease}
.welcome h2{font-size:42px;background:linear-gradient(90deg,#4caf50,#81c784,#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
.welcome p{color:#666;margin-bottom:30px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:600px;margin:0 auto}
.card{border:1px solid #222;background:rgba(255,255,255,0.03);padding:16px;border-radius:16px;cursor:pointer;transition:0.2s;text-align:left}
.card:hover{background:rgba(76,175,80,0.1);border-color:#4caf50;transform:translateY(-2px)}
.card b{display:block;color:#fff;margin-bottom:4px}
.card span{color:#888;font-size:13px}
.mag{margin:20px 0;display:flex;gap:14px;animation:fadeUp 0.4s ease}
.avatar{width:32px;height:32px;border-radius:50%;background:#222;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.avatar.user{background:#4caf50;color:#000}
.avatar.ai{background:#111;border:1px solid #333}
.bubble{flex:1;padding:4px 0;line-height:1.7;max-width:90%}
.bubble.user{background:#1a3a1e;padding:14px 18px;border-radius:20px 20px 4px 20px;border:1px solid #2a5a2e}
.bubble.ai h2,.bubble.ai h3{color:#4caf50;margin:14px 0 8px}
.bubble.ai strong{color:#a5d6a7}
.bubble.ai code{background:#1a1a1a;padding:2px 6px;border-radius:6px;border:1px solid #2a2a2a}
.bubble.ai pre{background:#0f0f0f;padding:16px;border-radius:12px;overflow-x:auto;border:1px solid #222;margin:12px 0;position:relative}
.bubble.ai pre button{position:absolute;top:8px;right:8px;background:#222;color:#fff;border:none;padding:6px 10px;border-radius:6px;font-size:11px;cursor:pointer}
.bubble.ai table{width:100%;border-collapse:collapse;margin:12px 0;border:1px solid #222;border-radius:10px;overflow:hidden}
.bubble.ai th{background:#111;color:#4caf50;padding:10px;text-align:left}
.bubble.ai td{padding:10px;border-top:1px solid #1a1a1a}
#inputArea{padding:20px;max-width:800px;margin:0 auto;width:100%}
.inputBox{background:#171717;border:1px solid #2a2a2a;border-radius:28px;display:flex;align-items:center;padding:6px 8px 6px 16px;box-shadow:0 10px 30px rgba(0,0,0,0.5)}
.inputBox:focus-within{border-color:#4caf50;box-shadow:0 0 0 2px rgba(76,175,80,0.2)}
.inputBox input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:12px 0}
.iconBtn{width:38px;height:38px;border-radius:50%;background:#222;border:none;color:#aaa;cursor:pointer;display:flex;align-items:center;justify-content:center;margin-left:6px}
.iconBtn:hover{background:#333;color:#fff}
#sendBtn{background:#fff;color:#000;width:38px;height:38px;border-radius:50%;border:none;cursor:pointer;font-weight:bold}
#sendBtn:hover{background:#4caf50}
#typing{display:flex;gap:4px;padding:10px}
#typing span{width:8px;height:8px;background:#4caf50;border-radius:50%;animation:bounce 1.4s infinite}
#typing span:nth-child(2){animation-delay:0.2s} #typing span:nth-child(3){animation-delay:0.4s}
@keyframes bounce{0%,80%,100%{transform:scale(0.8);opacity:0.5}40%{transform:scale(1);opacity:1}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
#adModal,#signupModal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);backdrop-filter:blur(12px);z-index:9999;display:flex;justify-content:center;align-items:center}
.box{background:#111;border:1px solid #333;padding:32px;border-radius:24px;text-align:center;width:90%;max-width:380px}
.box button{background:#4caf50;color:#000;padding:14px 28px;border:none;border-radius:12px;font-weight:bold;cursor:pointer;width:100%;margin-top:16px}
.signupBox{background:#111;border:1px solid #222;padding:36px;border-radius:24px;width:90%;max-width:400px}
.signupBox input{width:100%;padding:14px;border-radius:12px;border:1px solid #333;background:#1a1a1a;color:#fff;margin-bottom:12px}
@media(max-width:768px){#sidebar{display:none}#cards{grid-template-columns:1fr}}
</style>
</head>
<body>
<div id='sidebar'>
<h1>LUMI <span>AI</span></h1>
<div class='newChat' onclick='location.reload()'>+ New Chat</div>
<div class='hist' id='hist'></div>
<div style='padding:10px;font-size:11px;color:#444'>Elshuaib Tech<br>Free: <span id='limit'>0/5</span></div>
</div>

<div id='main'>
<div class='header'><b>LUMI AI Premium</b><div style='display:flex;gap:10px'><span style='font-size:12px;color:#666' id='userEmail'></span><span style='cursor:pointer' onclick='toggleSide()'>☰</span></div></div>

<div id='chat'>
<div id='watermark'><img src='/logo.png'></div>
<div class='messages' id='messages'>
<div class='welcome' id='welcome'>
<h2>Hello, I'm LUMI</h2>
<p>Ask me anything - I can see images, write code, and help you</p>
<div class='cards'>
<div class='card' onclick='sendSug(this)'><b>💻 Explain coding</b><span>What is programming in simple words?</span></div>
<div class='card' onclick='sendSug(this)'><b>🎨 Create image idea</b><span>Give me a logo concept for my brand</span></div>
<div class='card' onclick='sendSug(this)'><b>📚 Study helper</b><span>Explain quantum physics simply</span></div>
<div class='card' onclick='sendSug(this)'><b>😂 Make me laugh</b><span>Tell me a funny joke</span></div>
</div>
</div>
</div>
</div>

<div id='inputArea'>
<div class='inputBox'>
<input id='input' type='text' placeholder='Ask LUMI anything...'>
<label class='iconBtn' title='Upload image'>📷<input type='file' id='imgInput' accept='image/*' style='display:none' onchange='uploadImg(this)'></label>
<button class='iconBtn' onclick='startVoice()' title='Voice'>🎙️</button>
<button id='sendBtn' onclick='send()'>↑</button>
</div>
<div style='text-align:center;color:#444;font-size:11px;margin-top:10px'>LUMI can make mistakes. Check important info.</div>
</div>
</div>

<div id='signupModal'>
<div class='signupBox'>
<h2 style='color:#4caf50;margin-bottom:8px'>Welcome to LUMI AI ✨</h2>
<p style='color:#666;font-size:13px;margin-bottom:20px'>Your intelligent assistant by Elshuaib Tech</p>
<input id='emailInput' type='email' placeholder='Email address'>
<input id='nameInput' type='text' placeholder='Your name'>
<button onclick='doSignup()' style='width:100%;padding:14px;border-radius:12px;border:none;background:#fff;color:#000;font-weight:bold;cursor:pointer'>Continue</button>
<p style='font-size:11px;color:#444;margin-top:12px'>Free • Fast • Secure</p>
</div>
</div>

<div id='adModal' style='display:none'><div class='box'><h3 style='color:#fff'>Free limit reached 🚀</h3><p style='color:#888;margin-top:8px'>Watch a short ad to continue chatting with LUMI</p><button onclick='watchAd()'>Watch Ad & Continue</button><p style='font-size:11px;color:#555;margin-top:10px'>Supports LUMI AI development</p></div></div>

<script>
let count=0; let userEmail=localStorage.getItem('lumi_email');
window.onload=()=>{if(userEmail){document.getElementById('signupModal').style.display='none';document.getElementById('userEmail').innerText=userEmail} loadHist()}
function toggleSide(){let s=document.getElementById('sidebar');s.style.display=s.style.display==='none'?'flex':'none'}
function doSignup(){let e=document.getElementById('emailInput').value.trim(),n=document.getElementById('nameInput').value.trim();if(!e.includes('@'))return alert('Valid email');if(!n)return alert('Enter name');localStorage.setItem('lumi_email',e);localStorage.setItem('lumi_name',n);document.getElementById('signupModal').style.display='none';document.getElementById('userEmail').innerText=e;fetch('/save-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,name:n})})}
function sendSug(el){document.getElementById('input').value=el.querySelector('span').innerText;send()}
function loadHist(){let h=JSON.parse(localStorage.getItem('lumi_hist')||'[]');document.getElementById('hist').innerHTML=h.map(t=>`<div class='histItem'>${t}</div>`).join('')}
function addHist(t){let h=JSON.parse(localStorage.getItem('lumi_hist')||'[]');h.unshift(t.slice(0,30));localStorage.setItem('lumi_hist',JSON.stringify(h.slice(0,10)));loadHist()}
function formatAI(text){try{let html=marked.parse(text);return html}catch(e){return text}}
function copyCode(btn){let code=btn.parentElement.querySelector('code').innerText;navigator.clipboard.writeText(code);btn.innerText='Copied!';setTimeout(()=>btn.innerText='Copy',1500)}
async function send(){
 let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg)return;
 if(!localStorage.getItem('lumi_email')){document.getElementById('signupModal').style.display='flex';return}
 if(count>=5){document.getElementById('adModal').style.display='flex';return}
 document.getElementById('welcome')?.remove();
 let ms=document.getElementById('messages');
 ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'>${msg}</div></div>`;inp.value='';addHist(msg);
 let id='a'+Date.now(); ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar ai'>✨</div><div class='bubble ai'><div id='typing'><span></span><span></span><span></span></div></div></div>`;
 document.getElementById('chat').scrollTop=99999;
 let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
 let data=await res.json(); document.getElementById(id).innerHTML=`<div class='avatar ai'>✨</div><div class='bubble ai'>${formatAI(data.reply)}</div>`;
 setTimeout(()=>{document.querySelectorAll('pre').forEach(pre=>{if(!pre.querySelector('button')){let btn=document.createElement('button');btn.innerText='Copy';btn.onclick=()=>copyCode(btn);pre.appendChild(btn);hljs.highlightElement(pre.querySelector('code'))}})},100);
 count++;document.getElementById('limit').innerText=`${count}/5`; document.getElementById('chat').scrollTop=99999;
}
async function uploadImg(input){
 let file=input.files[0];if(!file)return; let reader=new FileReader();
 reader.onload=async e=>{
   document.getElementById('welcome')?.remove();
   let ms=document.getElementById('messages');
   ms.innerHTML+=`<div class='mag'><div class='avatar user'>You</div><div class='bubble user'><img src='${e.target.result}' style='max-width:100%;border-radius:12px;margin-bottom:8px'><br>What's in this image?</div></div>`;
   let id='a'+Date.now(); ms.innerHTML+=`<div class='mag' id='${id}'><div class='avatar ai'>✨</div><div class='bubble ai'><div id='typing'><span></span><span></span><span></span></div></div></div>`;
   let res=await fetch('/chat-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:e.target.result})});
   let data=await res.json(); document.getElementById(id).innerHTML=`<div class='avatar ai'>✨</div><div class='bubble ai'>${formatAI(data.reply)}</div>`;
 }; reader.readAsDataURL(file);
}
function startVoice(){
 if(!('webkitSpeechRecognition' in window)){alert('Voice not supported, use Chrome');return}
 let rec=new webkitSpeechRecognition(); rec.lang='en-US'; rec.start();
 rec.onresult=e=>{document.getElementById('input').value=e.results[0][0].transcript}
}
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

@app.route('/static/logo.png')
def logo2(): return send_from_directory('.', 'logo.png')

@app.route('/save-email', methods=['POST'])
def save():
    print(f"NEW USER: {request.json}")
    return jsonify({"ok":True})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg=request.json.get('message','')
        system="""You are LUMI AI, created by Elshuaib Tech. You are premium, friendly, helpful.
        Rules:
        - Answer beautifully with clean formatting
        - Use bullet points, tables, code blocks when needed
        - Keep paragraphs short
        - Be concise but thorough
        - Use emojis sparingly to be friendly
        - Never show raw markdown like ### in ugly way
        """
        completion=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"system","content":system},{"role":"user","content":msg}])
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {e}"})

@app.route('/chat-image', methods=['POST'])
def chat_img():
    try:
        img=request.json.get('image','')
        comp=client.chat.completions.create(model="openai/gpt-oss-20b",messages=[{"role":"user","content":[{"type":"text","text":"Describe this image beautifully and helpfully."},{"type":"image_url","image_url":{"url":img}}]}])
        return jsonify({"reply": comp.choices[0].message.content})
    except:
        return jsonify({"reply": "📷 I received your image! I can see it. Tell me what you'd like to know about it - I can describe, analyze, or help you with it! ✨"})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
