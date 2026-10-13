<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>LUMI AI ULTRA - Founder: shuwaibaah</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⭐</text></svg>">

<!-- PASTE YOUR MONETAG CODE HERE -->
<!-- Example: <script src="https://...monetag..."></script> -->

<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,Segoe UI,Roboto,sans-serif}
body{background:#000;color:#fff;height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{padding:12px 16px;background:#0a0a0a;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:16px;color:#FFD700;letter-spacing:1px}
header span{font-size:11px;color:#888}
#chat-box{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;font-size:14px;line-height:1.5;word-wrap:break-word}
.user{align-self:flex-end;background:#FFD700;color:#000;border-bottom-right-radius:4px}
.ai{align-self:flex-start;background:#1a1a1a;border:1px solid #222;border-bottom-left-radius:4px}
.lumi-typing-bubble{display:flex;gap:5px;padding:12px 16px;background:#1a1a1a;border:1px solid #222;border-radius:18px;width:fit-content}
.lumi-typing-bubble span{width:7px;height:7px;background:#FFD700;border-radius:50%;animation:lumiBounce 1.2s infinite}
.lumi-typing-bubble span:nth-child(2){animation-delay:0.2s}
.lumi-typing-bubble span:nth-child(3){animation-delay:0.4s}
@keyframes lumiBounce{0%,80%,100%{transform:scale(0.6);opacity:0.5}40%{transform:scale(1);opacity:1}}
#input-area{padding:12px;background:#0a0a0a;border-top:1px solid #222;display:flex;gap:8px;align-items:center}
#user-input{flex:1;background:#1a1a1a;border:1px solid #333;color:#fff;padding:12px 16px;border-radius:25px;outline:none;font-size:14px}
#send-btn, #mic-btn, #upload-btn{background:#FFD700;color:#000;border:none;width:42px;height:42px;border-radius:50%;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center}
#send-btn:active{transform:scale(0.9)}
@media (max-width:600px){.msg{font-size:13px;max-width:90%} header h1{font-size:14px}}
</style>
</head>
<body>

<header>
<h1>⭐ LUMI AI ULTRA</h1>
<span>Founder: shuwaibaah • LIVE • FAST • UNLIMITED</span>
</header>

<div id="chat-box">
<div class="msg ai">Hey! I'm LUMI AI ULTRA ⭐ Your super-fast assistant. Ask me anything, send voice or image!</div>
</div>

<div id="input-area">
<label id="upload-btn">📎<input type="file" id="fileInput" hidden accept="image/*,audio/*,.pdf,.txt"></label>
<button id="mic-btn">🎤</button>
<input type="text" id="user-input" placeholder="Ask anything... I am LUMI AI ULTRA">
<button id="send-btn">➤</button>
</div>

<script>
// === CONFIG - PUT YOUR API KEY IF YOU USE ONE ===
const AI_API_URL = "https://text.pollinations.ai/";

// === CORE ELEMENTS ===
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const fileInput = document.getElementById("fileInput");

// === PREMIUM TYPING - NO TEXT, ONLY DOTS, FASTER THAN CHATGPT ===
function showLumiTyping(){
  const div = document.createElement("div");
  div.id = "lumi-typing";
  div.className = "lumi-typing-bubble";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
function hideLumiTyping(){
  const t = document.getElementById("lumi-typing");
  if(t) t.remove();
}
function typeLumiText(el, text){
  let i=0; el.innerHTML="";
  function type(){
    if(i < text.length){
      el.innerHTML += text.charAt(i);
      i++;
      chatBox.scrollTop = chatBox.scrollHeight;
      setTimeout(type, 12); // 12ms = faster than ChatGPT
    }
  }
  type();
}

// === SEND MESSAGE ===
async function sendMessage(){
  const text = userInput.value.trim();
  if(!text) return;
  
  // Add user message
  const userDiv = document.createElement("div");
  userDiv.className = "msg user";
  userDiv.textContent = text;
  chatBox.appendChild(userDiv);
  userInput.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  // Show premium typing
  showLumiTyping();

  try {
    // Call AI - LUMI identity
    const prompt = `You are LUMI AI ULTRA, created by Founder shuwaibaah. You are fast, helpful, unlimited. Never mention ChatGPT, OpenAI, or any other AI name. Only say you are LUMI AI ULTRA. User: ${text}`;
    const res = await fetch(AI_API_URL + encodeURIComponent(prompt));
    let aiText = await res.text();
    
    // Safety: remove any chatgpt word if model says it
    aiText = aiText.replace(/chatgpt/gi, "LUMI AI ULTRA").replace(/openai/gi, "LUMI Labs").replace(/chat gpt/gi, "LUMI AI ULTRA");

    hideLumiTyping();
    const aiDiv = document.createElement("div");
    aiDiv.className = "msg ai";
    chatBox.appendChild(aiDiv);
    typeLumiText(aiDiv, aiText);

  } catch(e){
    hideLumiTyping();
    const aiDiv = document.createElement("div");
    aiDiv.className = "msg ai";
    aiDiv.textContent = "LUMI is thinking too fast! Check your internet and try again ⭐";
    chatBox.appendChild(aiDiv);
  }
}

sendBtn.onclick = sendMessage;
userInput.addEventListener("keydown", (e)=>{ if(e.key==="Enter") sendMessage(); });

// === VOICE INPUT ===
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "en-US";
  micBtn.onclick = ()=> recognition.start();
  recognition.onresult = (e)=>{ userInput.value = e.results[0][0].transcript; sendMessage(); }
}

// === FILE UPLOAD PREVIEW ===
fileInput.onchange = ()=>{
  const file = fileInput.files[0];
  if(file){
    const div = document.createElement("div");
    div.className = "msg user";
    div.textContent = `📎 Uploaded: ${file.name}`;
    chatBox.appendChild(div);
    // You can add your image generation / analysis logic here - keeping same as before
  }
}

// === GLOBAL CLEANER - No ChatGPT ever ===
setInterval(()=>{
  document.body.innerHTML = document.body.innerHTML.replace(/Better Than ChatGPT/gi, "LIVE • FAST • UNLIMITED");
}, 2000);
</script>

<!-- PASTE YOUR MONETAG BANNER / POP CODE BELOW -->
<!-- Keep your old monetag code here exactly as it was -->

</body>
</html>
