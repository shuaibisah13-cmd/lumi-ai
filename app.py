from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>LUMI AI</title>
<style>
body{margin:0;font-family:sans-serif;background:#0f0f0f;color:#fff;display:flex;flex-direction:column;height:100vh}
.header{padding:15px;background:#1a1a1a;text-align:center;border-bottom:1px solid #333}
#chat{flex:1;overflow-y:auto;padding:20px;position:relative}
#watermark{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);opacity:0.08;pointer-events:none;z-index:0}
#watermark img{width:300px}
.messages{position:relative;z-index:1}
.mag{margin:12px 0;padding:12px 16px;border-radius:18px;max-width:80%;line-height:1.5}
.user{background:#2e7d32;margin-left:auto}
.ai{background:#2a2a2a}
.suggestions{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:20px 0;position:relative;z-index:1}
.sug{border:1px solid #444;padding:12px 16px;border-radius:12px;background:#1e1e1e;cursor:pointer;font-size:14px}
.sug:hover{background:#333}
#inputArea{display:flex;padding:12px;background:#1a1a1a;gap:10px}
#inputArea input{flex:1;padding:14px;border-radius:24px;border:1px solid #444;background:#2a2a2a;color:white;outline:none}
#inputArea button{padding:14px 22px;border-radius:24px;border:none;background:#4caf50;color:white;font-weight:bold;cursor:pointer}
#adModal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;justify-content:center;align-items:center}
.box{background:white;color:black;padding:30px;border-radius:20px;text-align:center;width:90%;max-width:360px}
#limit{font-size:12px;color:#aaa;margin-top:5px}
</style>
</head>
<body>
<div class='header'><h2 style='margin:0'>LUMI AI</h2><div id='limit'>Free: 0/5</div></div>
<div id='chat'><div id='watermark'><img src='/static/logo.png'></div><div class='messages' id='messages'></div><div class='suggestions' id='sug'><div class='sug' onclick='sendSug(this)'>What is AI?</div><div class='sug' onclick='sendSug(this)'>Tell a joke</div><div class='sug' onclick='sendSug(this)'>Explain quantum</div></div></div>
<div id='inputArea'><input id='input' placeholder='Ask LUMI AI...'><button onclick='send()'>Send</button></div>
<div id='adModal'><div class='box'><h3>Free limit reached</h3><p>Watch ad to continue</p><button onclick='watchAd()' style='padding:12px 24px;background:#4caf50;color:white;border:none;border-radius:10px;font-weight:bold;'>Watch Ad</button></div></div>
<script>
let count=0;
function sendSug(el){document.getElementById('input').value=el.innerText;send();}
async function send(){
 let inp=document.getElementById('input');let msg=inp.value.trim();if(!msg)return;
 if(count>=5){document.getElementById('adModal').style.display='flex';return;}
 document.getElementById('sug').style.display='none';
 let ms=document.getElementById('messages');ms.innerHTML+=`<div class='mag user'>${msg}</div>`;inp.value='';
 let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
 let data=await res.json();ms.innerHTML+=`<div class='mag ai'>${data.reply}</div>`;
 count++;document.getElementById('limit').innerText=`Free: ${count}/5`;ms.parentElement.scrollTop=9999;
}
function watchAd(){count=0;document.getElementById('limit').innerText=`Free: ${count}/5`;document.getElementById('adModal').style.display='none';}
document.getElementById('input').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg = request.json.get('message')
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": msg}])
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
