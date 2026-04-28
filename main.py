stock_alert_telegram.py
import requests,time
from datetime import datetime
TOKEN="8750903572:AAEGmATCu-GHKvVkFwP88ocuQzFd2cBkg9Y"
CHAT="2055797728"
ATIVOS={"9984.T":"SoftBank🟣","6857.T":"Advantest🔵","6920.T":"Lasertec🟢","8035.T":"TokyoElectron🟠","GC=F":"Ouro🥇","^N225":"Nikkei🗾","^IXIC":"Nasdaq🇺🇸","NVDA":"Nvidia🤖"}
USD=["GC=F","^IXIC","NVDA"]
def sinal(p,mn,mx,closes,v):
 amp=((mx-mn)/mn*100)if mn else 0
 media=sum(closes)/len(closes)if closes else p
 pts=0
 if amp>2:pts+=1
 if abs(v)>1:pts+=1
 if(v>0 and p>media)or(v<0 and p<media):pts+=1
 return"🟢 BOM PARA TRADE"if pts>=3 else("🟡 MODERADO"if pts==2 else"🔴 EVITAR")
def preco(t):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  m=r["chart"]["result"][0]["meta"]
  p=m.get("regularMarketPrice",0);a=m.get("previousClose",0)
  mx=m.get("regularMarketDayHigh",0);mn=m.get("regularMarketDayLow",0)
  v=((p-a)/a*100)if a else 0
  closes=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("close",[])if c]
  e="📈"if v>=0 else"📉"
  moeda="$"if t in USD else"¥"
  tk=t.replace(".T","").replace("=F","").replace("^","")
  return f"{tk} 💰{moeda}{p:,.2f} {e}{v:+.2f}%\nMáx{moeda}{mx:,.2f} Mín{moeda}{mn:,.2f}\n{sinal(p,mn,mx,closes,v)}"
 except Exception as ex:
  return f"Erro: {ex}"
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo():
 enviar("📊 RESUMO — "+datetime.now().strftime("%d/%m %H:%M"))
 [enviar(f"{n}\n{preco(t)}")or time.sleep(1) for t,n in ATIVOS.items()]
 enviar("✅ Fim do resumo!")
e=False
print("Aguardando 09:00 JST...")
while True:
 h=datetime.now().strftime("%H:%M")
 if h=="09:00"and not e:resumo();e=True
 if h=="00:01":e=False
 time.sleep(30)
