import json

data = json.load(open("scan-ergebnis.json"))
payload = json.dumps(data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>S&P 500 - Bullische RSI-Divergenzen</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#0f1623;--card:#182233;--line:#26344a;--txt:#e8edf5;--mut:#8fa0b8;
--green:#34c98e;--blue:#4ea3ff;--amber:#ffb454;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;padding:28px}
h1{font-size:22px;margin-bottom:4px}
.sub{color:var(--mut);margin-bottom:20px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 20px}
.kpi b{font-size:22px;display:block}
.kpi span{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.5px}
.filter{display:flex;gap:8px;margin-bottom:22px;flex-wrap:wrap}
.filter button{background:var(--card);border:1px solid var(--line);color:var(--txt);
padding:7px 16px;border-radius:8px;cursor:pointer;font-size:14px}
.filter button.on{background:var(--blue);border-color:var(--blue);color:#08111e;font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.tick{font-size:19px;font-weight:700}
.badge{font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:.5px}
.badge.regulaer{background:rgba(52,201,142,.15);color:var(--green)}
.badge.versteckt{background:rgba(255,180,84,.15);color:var(--amber)}
.badge.fruehsignal{background:rgba(78,163,255,.15);color:var(--blue)}
.badge.bestaetigt{background:rgba(143,160,184,.15);color:var(--mut)}
.meta{color:var(--mut);font-size:12.5px;margin-bottom:10px}
.meta b{color:var(--txt)}
.cv{position:relative;height:190px}.cv.rsi{height:110px;margin-top:4px}
.foot{color:var(--mut);font-size:12px;margin-top:26px;max-width:900px}
</style>
</head>
<body>
<h1>S&amp;P 500 - Bullische RSI(14)-Divergenzen, Tageschart</h1>
<div class="sub" id="sub"></div>
<div class="kpis">
 <div class="kpi"><b id="k-all">0</b><span>Treffer gesamt</span></div>
 <div class="kpi"><b id="k-reg" style="color:var(--green)">0</b><span>Regul&auml;r (Umkehr)</span></div>
 <div class="kpi"><b id="k-hid" style="color:var(--amber)">0</b><span>Versteckt (Fortsetzung)</span></div>
 <div class="kpi"><b id="k-fru" style="color:var(--blue)">0</b><span>Fr&uuml;hsignale</span></div>
</div>
<div class="filter">
 <button data-f="alle" class="on">Alle</button>
 <button data-f="regulaer">Regul&auml;re</button>
 <button data-f="versteckt">Versteckte</button>
 <button data-f="fruehsignal">Nur Fr&uuml;hsignale</button>
</div>
<div class="grid" id="grid"></div>
<div class="foot">Methodik: Fr&uuml;hsignal = das zweite Tief stammt vom HEUTIGEN Handelstag
(tiefster Punkt der letzten 12 Bars, RSI auf Basis des Schlusskurses) &ndash; noch unbest&auml;tigt,
es kann an den Folgetagen unterschritten werden. Best&auml;tigt = das Tief war gestern und heute folgte
ein h&ouml;heres Tief (1-Tages-Best&auml;tigung) &ndash; schw&auml;cher als die klassische Pivot-Best&auml;tigung,
daf&uuml;r ohne Verz&ouml;gerung. Regul&auml;r = tieferes Preistief bei h&ouml;herem RSI-Tief (mind. ein
RSI-Tief unter 45). Versteckt = h&ouml;heres Preistief bei tieferem RSI-Tief, nur bei Kurs &uuml;ber
SMA50. St&auml;rke-Filter: &Delta;RSI &ge; 3 Punkte, &Delta;Tief &ge; 0,5&nbsp;%. Datenquelle: Yahoo
Finance, adjustierte Tagesschlusskurse. Eine Divergenz ist ein Hinweis, kein Signal f&uuml;r sich
allein - und das Ganze ist nat&uuml;rlich keine Anlageberatung.</div>
<script>
const DATA = __PAYLOAD__;
document.getElementById('sub').textContent =
 `Scan vom ${DATA.scan_datum} (Datenstand: letzter US-Handelsschluss) · ${DATA.anzahl_ticker} Aktien gescannt`;
const hits = DATA.treffer.sort((a,b)=>(a.status||'').localeCompare(b.status||'')||a.ticker.localeCompare(b.ticker));
document.getElementById('k-all').textContent = hits.length;
document.getElementById('k-reg').textContent = hits.filter(h=>h.typ==='regulaer').length;
document.getElementById('k-hid').textContent = hits.filter(h=>h.typ==='versteckt').length;
document.getElementById('k-fru').textContent = hits.filter(h=>h.status==='fruehsignal').length;
Chart.defaults.color='#8fa0b8';Chart.defaults.borderColor='#26344a';
Chart.defaults.font.size=10;
const grid=document.getElementById('grid');const charts=[];
function divLine(n,i1,i2,v1,v2){const a=Array(n).fill(null);a[i1]=v1;a[i2]=v2;return a;}
function card(h){
 const el=document.createElement('div');el.className='card';
 el.dataset.typ=h.typ;el.dataset.status=h.status||'bestaetigt';
 const lbl=h.typ==='regulaer'?'Regulär':'Versteckt';
 const st=(h.status==='fruehsignal')
   ?`<span class="badge fruehsignal">Frühsignal</span>`
   :`<span class="badge bestaetigt">bestätigt</span>`;
 el.innerHTML=`<div class="head"><span class="tick">${h.ticker}</span>
  <span>${st} <span class="badge ${h.typ}">${lbl}</span></span></div>
  <div class="meta">Tief 1: <b>${h.low_p1}</b> (${h.datum_p1}, RSI ${h.rsi_p1}) &rarr;
  Tief 2: <b>${h.low_p2}</b> (${h.datum_p2}, RSI ${h.rsi_p2}, vor ${h.tage_seit_tief??'?'} Tag(en)) ·
  Close <b>${h.close}</b> · RSI <b>${h.rsi_aktuell}</b></div>
  <div class="cv"><canvas></canvas></div><div class="cv rsi"><canvas></canvas></div>`;
 grid.appendChild(el);
 const c=h.chart,n=c.dates.length;
 const pCol=h.typ==='regulaer'?'#34c98e':'#ffb454';
 charts.push(new Chart(el.querySelectorAll('canvas')[0],{type:'line',data:{labels:c.dates,
  datasets:[
   {data:c.close,borderColor:'#4ea3ff',borderWidth:1.5,pointRadius:0,tension:.2},
   {data:c.low,borderColor:'rgba(78,163,255,.35)',borderWidth:1,pointRadius:0,tension:.2},
   {data:divLine(n,c.p1,c.p2,h.low_p1,h.low_p2),borderColor:pCol,borderWidth:2,borderDash:[6,4],
    pointRadius:4,pointBackgroundColor:pCol,spanGaps:true}]},
  options:{responsive:true,maintainAspectRatio:false,animation:false,
   plugins:{legend:{display:false},tooltip:{mode:'index',intersect:false}},
   scales:{x:{ticks:{maxTicksLimit:6}},y:{position:'right'}}}}));
 charts.push(new Chart(el.querySelectorAll('canvas')[1],{type:'line',data:{labels:c.dates,
  datasets:[
   {data:c.rsi,borderColor:'#b48cff',borderWidth:1.5,pointRadius:0,tension:.2},
   {data:divLine(n,c.p1,c.p2,h.rsi_p1,h.rsi_p2),borderColor:pCol,borderWidth:2,borderDash:[6,4],
    pointRadius:4,pointBackgroundColor:pCol,spanGaps:true}]},
  options:{responsive:true,maintainAspectRatio:false,animation:false,
   plugins:{legend:{display:false}},
   scales:{x:{display:false},y:{position:'right',min:0,max:100,ticks:{stepSize:25}}}}}));
}
hits.forEach(card);
document.querySelectorAll('.filter button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('.filter button').forEach(x=>x.classList.remove('on'));
 b.classList.add('on');
 document.querySelectorAll('.card').forEach(c=>{
  const f=b.dataset.f;
  c.style.display=(f==='alle'||c.dataset.typ===f||c.dataset.status===f)?'':'none';});
});
</script>
</body>
</html>"""

html = html.replace("__PAYLOAD__", payload)
import os
os.makedirs("public", exist_ok=True)
open("public/index.html", "w", encoding="utf-8").write(html)
print("ok,", len(html)//1024, "KB")
