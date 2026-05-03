import requests,time
from datetime import datetime
TOKEN="8750903572:AAEGmATCu-GHKvVkFwP88ocuQzFd2cBkg9Y"
CHAT="2055797728"
ATIVOS={"9984.T":"SoftBank","6857.T":"Advantest","6920.T":"Lasertec","8035.T":"TokyoElectron","GC=F":"Ouro","^N225":"Nikkei","^IXIC":"Nasdaq","NVDA":"Nvidia"}
USD=["GC=F","^IXIC","NVDA"]
def sinal(p,mn,mx,closes,v):
 amp=((mx-mn)/mn*100)if mn else 0
 media=sum(closes)/len(closes)if closes else p
 pts=sum([amp>2,abs(v)>1,(v>0 and p>media)or(v<0 and p<media)])
 return"🟢 BOM PARA TRADE"if pts>=3 else("🟡 MODERADO"if pts==2 else"🔴 EVITAR")
def preco(t,dia_anterior=False):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  m=r["chart"]["result"][0]["meta"]
  closes=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("close",[])if c]
  highs=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("high",[])if c]
  lows=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("low",[])if c]
  if dia_anterior and len(closes)>=2:
   p=closes[-1];ant=closes[-2]
   mx=highs[-1]if highs else p
   mn=lows[-1]if lows else p
   v=((p-ant)/ant*100)if ant else 0
  else:
   p=m.get("regularMarketPrice",0);a=m.get("previousClose",0)
   mx=m.get("regularMarketDayHigh",0);mn=m.get("regularMarketDayLow",0)
   v=((p-a)/a*100)if a else 0
  e="📈"if v>=0 else"📉"
  moeda="$"if t in USD else"¥"
  tk=t.replace(".T","").replace("=F","").replace("^","")
  return f"{tk} {moeda}{p:,.2f} {e}{v:+.2f}%\nMax{moeda}{mx:,.2f} Min{moeda}{mn:,.2f}\n{sinal(p,mn,mx,closes,v)}"
 except Exception as ex:
  return f"Erro: {ex}"
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo(titulo,dia_anterior=False):
 enviar(titulo+" "+datetime.now().strftime("%d/%m %H:%M")+" UTC")
 [enviar(f"{n}\n{preco(t,dia_anterior)}")or time.sleep(1) for t,n in ATIVOS.items()]
 enviar("Fim do resumo!")
e1=False;e2=False
while True:
 h=datetime.now().strftime("%H:%M")
 if h=="00:00"and not e1:resumo("📊 ABERTURA 09:00 JST — Ontem:",dia_anterior=True);e1=True
 if h=="06:00"and not e2:resumo("⏰ FECHAMENTO 15:00 JST — Hoje:");e2=True
 if h=="12:00":e1=False;e2=False
 time.sleep(30) 
