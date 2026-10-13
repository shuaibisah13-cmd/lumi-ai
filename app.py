import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>LUMI AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:white;font-family:system-ui;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#chat{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:12px}
.msg{padding:12px 16px;border-radius:18px;max-width:85%;word-wrap:break-word;line-height:1.4}
.user{background:#3a3a3a;align-self:flex-end;border-bottom-right-radius:4px}
.ai{background:#1e1e1e;align-self:flex-start;border-bottom-left-radius:4px;border:1px solid #333}
#inputBar{display:flex;gap:10px;padding:12px;background:#111;border-top:1px solid #222;position:sticky;bottom:0}
#inp{flex:1;padding:14px 18px;border-radius:25px;border:1px solid #333;background:#1e1e1e;color:white;outline:none;font-size:16px}
#sendBtn{padding:14px 22px;border-radius:25px;border:none;background:#FFD700;color:black;font-weight:bold;cursor:pointer}
.dots span{display:inline-block;width:6px;height:6px;background:white;border-radius:50%;margin:0 2px;animation:bounce 1.4s infinite}
.dots span:nth-child(2){animation-delay:.2s}.dots span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{opacity:.3;transform:translateY(0)}40%{opacity:1;transform:translateY(-6px)}}
h1{text-align:center;padding:20px 10px 0;margin:0;font-size:22px;color:#FFD700}
</style>
</head>
<body>
<h1>✨ LUMI AI</h1>
<div id="chat"><div class="msg ai">Hello! I'm LUMI. How can I help you today?</div></div>
<div id="inputBar"><input id="inp" placeholder="Ask LUMI anything..." onkeypress="if(event.key==='Enter')send()"><button id="sendBtn" onclick="send()">Send</button></div>
<script>
async function send(){
 let inp=document.getElementById('inp'); let chat=document.getElementById('chat');
 let text=inp.value.trim(); if(!text)return;
 chat.innerHTML+=`<div class="msg user">${text}</div>`; inp.value='';
 let bot=document.createElement('div'); bot.className='msg ai dots'; bot.innerHTML='<span></span><span></span><span></span>'; chat.appendChild(bot); chat.scrollTop=chat.scrollHeight;
 try{
  let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
  let data=await res.json(); bot.classList.remove('dots'); bot.innerHTML=data.reply;
 }catch(e){bot.innerHTML='Error - check GROQ_API_KEY on Render';}
 chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message','')
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":user_msg}]
    )
    return jsonify({"reply": completion.choices[0].message.content})

if __name__ == '__main__':
    app.run()
