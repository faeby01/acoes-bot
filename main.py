import requests,time
from datetime import datetime
TOKEN="8750903572:AAEGmATCu-GHKvVkFwP88ocuQzFd2cBkg9Y"
CHAT="2055797728"
ATIVOS={"8035.T":"TokyoElectron","7011.T":"Mitsubishi","9984.T":"SoftBank"}
def sinal(p,mn,mx,closes,v):
 amp=((mx-mn)/mn*100)if mn else 0
 media=sum(closes)/len(closes)if closes else p
 pts=sum([amp>2,abs(v)>1,(v>0 and p>media)or(v<0 and p<media)])
 return"BOM PARA TRADE"if pts>=3 else("MODERADO"if pts==2 else"EVITAR")
def get_noticias(ticker):
 try:
  codigo=ticker.replace(".T","")
  r=requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={codigo}&newsCount=5",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  return[n["title"]for n in r.get("news",[])[:5]if n.get("title")]
 except:
  return[]
def analisar(titulos,v):
 positivo=["surge","jumps","rises","gains","up","high","record","buy","strong","growth","beat","rally","profit"]
 negativo=["falls","drops","down","crash","loss","cut","weak","miss","sell","risk","decline","slump"]
 if titulos:
  pos=sum(1 for t in titulos for w in positivo if w in t.lower())
  neg=sum(1 for t in titulos for w in negativo if w in t.lower())
  sent="Notícias positivas"if pos>neg else("Notícias negativas"if neg>pos else"Notícias neutras")
  resumo=titulos[0][:80]if titulos else""
 else:
  sent="Sem notícias";resumo=""
 if v>2:prev="Previsão: ALTA — momentum forte"
 elif v<-2:prev="Previsão: BAIXA — pressão vendedora"
 elif 0<v<=2:prev="Previsão: leve alta"
 elif -2<=v<0:prev="Previsão: leve baixa"
 else:prev="Previsão: neutro"
 return f"📰 {sent}\n📌 {resumo}\n🔮 {prev}"if resumo else f"📰 {sent}\n🔮 {prev}"
def preco(t,modo="anterior"):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  m=r["chart"]["result"][0]["meta"]
  closes=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("close",[])if c]
  highs=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("high",[])if c]
  lows=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("low",[])if c]
  p=m.get("regularMarketPrice",0)
  mx=m.get("regularMarketDayHigh",0);mn=m.get("regularMarketDayLow",0)
  if modo=="anterior"and len(closes)>=2:
   p=closes[-1];ref=closes[-2];v=((p-ref)/ref*100)if ref else 0
   mx=highs[-1]if highs else p;mn=lows[-1]if lows else p
  elif modo=="dia":
   ab=m.get("regularMarketOpen",0);v=((p-ab)/ab*100)if ab else 0
  else:
   ref=m.get("previousClose",0);v=((p-ref)/ref*100)if ref else 0
  e="📈"if v>=0 else"📉"
  tk=t.replace(".T","")
  return f"{tk} ¥{p:,.2f} {e}{v:+.2f}%\nMax¥{mx:,.2f} Min¥{mn:,.2f}\n{sinal(p,mn,mx,closes,v)}",v
 except Exception as ex:
  return f"Erro: {ex}",0
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo(titulo,modo):
 enviar(titulo+" "+datetime.now().strftime("%d/%m %H:%M"))
 for t,n in ATIVOS.items():
  info,v=preco(t,modo)
  analise=analisar(get_noticias(t),v)
  enviar(f"{n}\n{info}\n\n{analise}")
  time.sleep(2)
 enviar("Fim do resumo!")
e1=False;e2=False
while True:
 h=datetime.now().strftime("%H:%M")
 if h=="00:00"and not e1:resumo("📊 ABERTURA 09:00 JST — Ontem:",modo="anterior");e1=True
 if h=="06:00"and not e2:resumo("⏰ FECHAMENTO 15:00 JST — Hoje:",modo="dia");e2=True
 if h=="12:00":e1=False;e2=False
 time.sleep(30)
