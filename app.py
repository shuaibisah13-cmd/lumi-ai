import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LUMI AI</title>
<style>
body{margin:0;background:#000;color:#fff;font-family:sans-serif;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:15px}
.msg{margin:10px 0;padding:10px 15px;border-radius:15px;max-width:80%}
.user{background:#444;margin-left:auto}
.ai{background:#222}
#box{display:flex;padding:10px;border-top:1px solid #333}
input{flex:1;padding:12px;border-radius:20px;border:none;background:#222;color:#fff;outline:none}
button{margin-left:10px;padding:12px 20px;border-radius:20px;border:none;background:#FFD700;font-weight:bold}
.dots span{animation:bounce 1.4s infinite}
.dots span:nth-child(2){animation-delay:.2s}
.dots span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{opacity:0}40%{opacity:1}}
</style>
</head>
<body>
<div id="chat"></div>
<div id="box"><input id="inp" placeholder="Ask LUMI..."><button onclick="send()">Send</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let c=document.getElementById('chat');
 if(!i.value)return;
 c.innerHTML+=`<div class="msg user">${i.value}</div>`;
 let q=i.value; i.value='';
 let d=document.createElement('div'); d.className='msg ai dots'; d.innerHTML='<span>.</span><span>.</span><span>.</span>'; c.appendChild(d); c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q})});
 let j=await r.json(); d.innerHTML=j.reply;
}
</script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message','')
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":msg}]
    )
    return jsonify({"reply": res.choices[0].message.content})

if __name__ == '__main__':
    app.run()
