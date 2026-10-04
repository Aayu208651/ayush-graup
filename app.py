from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Ayush Pandit - Ultra Premium</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:#07070b;color:#fff;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
.blur{position:fixed;width:600px;height:600px;border-radius:50%;filter:blur(130px);z-index:-1;opacity:.6}
.b1{background:linear-gradient(135deg,#7c3aed,#ec4899);top:-150px;left:-150px}
.b2{background:linear-gradient(135deg,#06b6d4,#3b82f6);bottom:-150px;right:-150px}
.card{width:100%;max-width:800px;background:rgba(255,255,255,0.07);backdrop-filter:blur(30px);border:1px solid rgba(255,255,255,0.12);border-radius:26px;padding:32px;box-shadow:0 30px 80px rgba(0,0,0,.6)}
h1{text-align:center;font-size:32px;font-weight:800;background:linear-gradient(90deg,#a78bfa,#f472b6,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{text-align:center;opacity:.5;letter-spacing:4px;font-size:12px;margin-top:6px;margin-bottom:28px}
input{width:100%;padding:16px;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.15);border-radius:14px;color:#fff;font-size:14px;outline:none}
input:focus{border-color:#a78bfa;box-shadow:0 0 0 4px rgba(167,139,250,.2)}
.btn{width:100%;margin-top:16px;padding:15px;background:linear-gradient(90deg,#7c3aed,#ec4899);border:none;border-radius:14px;color:#fff;font-weight:800;font-size:16px;cursor:pointer;letter-spacing:1px}
.status{margin-top:18px;padding:12px;border-radius:10px;text-align:center;font-weight:700;display:none}
.working{background:rgba(34,197,94,.15);border:1px solid #22c55e;color:#22c55e}
.invalid{background:rgba(239,68,68,.15);border:1px solid #ef4444;color:#ef4444}
.results{margin-top:24px;display:none}
.box{background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:18px;margin-bottom:18px}
.box h3{color:#a78bfa;margin-bottom:12px;font-size:15px}
.item{padding:11px;background:rgba(255,255,255,.06);border-radius:10px;margin-bottom:8px;font-size:13px;word-break:break-all;display:flex;justify-content:space-between;gap:10px;align-items:center}
.cp{padding:6px 12px;background:#fff;color:#000;border-radius:7px;font-weight:800;font-size:11px;border:none;cursor:pointer}
.footer{text-align:center;margin-top:20px;opacity:.3;font-size:11px;letter-spacing:3px}
</style>
</head>
<body>
<div class="blur b1"></div><div class="blur b2"></div>
<div class="card">
<h1>AYUSH PANDIT</h1>
<div class="sub">ULTRA PREMIUM EXTRACTOR - FLASK EDITION</div>
<input id="token" placeholder="Paste Facebook User Access Token Here...">
<button class="btn" onclick="doExtract()">EXTRACT NOW ⚡</button>
<div id="status" class="status"></div>
<div id="results" class="results">
  <div class="box"><h3>📄 PAGES TOKEN (<span id="pc">0</span>)</h3><div id="plist"></div></div>
  <div class="box"><h3>👥 GROUPS UID (<span id="gc">0</span>)</h3><div id="glist"></div></div>
</div>
<div class="footer">MADE BY AYUSH PANDIT</div>
</div>
<script>
async function doExtract(){
 let token = document.getElementById('token').value.trim();
 if(!token) return alert('Token daal bhai!');
 document.getElementById('status').style.display='block';
 document.getElementById('status').innerHTML='Checking...';
 let res = await fetch('/api/extract', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({token})});
 let data = await res.json();
 let st = document.getElementById('status');
 if(data.valid){
   st.className='status working'; st.style.display='block';
   st.innerHTML=`✅ TOKEN WORKING - ID: ${data.user.id} | Name: ${data.user.name}`;
 } else {
   st.className='status invalid'; st.style.display='block';
   st.innerHTML=`❌ TOKEN INVALID / EXPIRED - ${data.error}`;
   return;
 }
 document.getElementById('results').style.display='block';
 document.getElementById('pc').innerText = data.pages.length;
 document.getElementById('gc').innerText = data.groups.length;
 let ph='', gh='';
 data.pages.forEach(p=>{
   ph+=`<div class="item"><span><b>${p.name}</b><br>ID: ${p.id}<br>TOKEN: ${p.access_token.slice(0,70)}...</span><button class="cp" onclick="navigator.clipboard.writeText('${p.access_token}');alert('Copied')">COPY</button></div>`;
 });
 if(data.pages.length==0) ph='<div class="item">Koi Page nahi mila</div>';
 data.groups.forEach(g=>{
   gh+=`<div class="item"><span><b>${g.name}</b><br>GROUP UID: ${g.id}</span><button class="cp" onclick="navigator.clipboard.writeText('${g.id}');alert('Copied')">COPY</button></div>`;
 });
 if(data.groups.length==0) gh='<div class="item">Koi Group nahi mila (Permission chahiye)</div>';
 document.getElementById('plist').innerHTML=ph;
 document.getElementById('glist').innerHTML=gh;
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/extract', methods=['POST'])
def extract():
    token = request.json.get('token','').strip()
    if not token:
        return jsonify({'valid':False,'error':'Token empty'})
    
    # 1. Check Token Valid or Not
    try:
        me = requests.get(f'https://graph.facebook.com/v19.0/me?access_token={token}', timeout=10).json()
        if 'error' in me:
            return jsonify({'valid':False,'error':me['error']['message']})
        user = {'id':me.get('id'), 'name':me.get('name')}
    except Exception as e:
        return jsonify({'valid':False,'error':str(e)})

    pages = []
    groups = []

    # 2. Get All Pages + Tokens
    try:
        # pagination handle
        url = f'https://graph.facebook.com/v19.0/me/accounts?limit=5000&access_token={token}'
        r = requests.get(url, timeout=15).json()
        if 'data' in r:
            for p in r['data']:
                pages.append({'id':p.get('id'),'name':p.get('name'),'access_token':p.get('access_token')})
    except: pass

    # 3. Get All Groups UID - Old Token Logic
    try:
        # Old API still works for old tokens
        url2 = f'https://graph.facebook.com/v19.0/me/groups?limit=5000&access_token={token}'
        r2 = requests.get(url2, timeout=15).json()
        if 'data' in r2:
            for g in r2['data']:
                groups.append({'id':g.get('id'),'name':g.get('name')})
        
        # Extra: try with v12 also for old tokens
        if len(groups)==0:
            url3 = f'https://graph.facebook.com/v12.0/me/groups?limit=5000&access_token={token}'
            r3 = requests.get(url3, timeout=15).json()
            if 'data' in r3:
                for g in r3['data']:
                    groups.append({'id':g.get('id'),'name':g.get('name')})
    except: pass

    return jsonify({'valid':True,'user':user,'pages':pages,'groups':groups})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
