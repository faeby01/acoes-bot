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
def get_noticias(ticker):
 try:
  codigo=ticker.replace(".T","").replace("=F","").replace("^","")
  r=requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={codigo}&newsCount=5",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  return[n["title"]for n in r.get("news",[])[:5]if n.get("title")]
 except:
  return[]
def analisar(nome,titulos,v):
 positivo=["surge","jumps","rises","gains","up","high","record","buy","strong","growth","beat","rally","profit"]
 negativo=["falls","drops","down","crash","loss","cut","weak","miss","sell","risk","decline","slump","concern"]
 if not titulos:
  sent="📰 Sem notícias"
 else:
  pos=sum(1 for t in titulos for w in positivo if w in t.lower())
  neg=sum(1 for t in titulos for w in negativo if w in t.lower())
  if pos>neg:sent="📰 Notícias: POSITIVAS 🟢"
  elif neg>pos:sent="📰 Notícias: NEGATIVAS 🔴"
  else:sent="📰 Notícias: NEUTRAS 🟡"
 if v>2:prev="🔮 Previsão: ALTA — momentum forte"
 elif v<-2:prev="🔮 Previsão: BAIXA — pressão vendedora"
 elif 0<v<=2:prev="🔮 Previsão: LEVE ALTA — movimento moderado"
 elif -2<=v<0:prev="🔮 Previsão: LEVE BAIXA — movimento moderado"
 else:prev="🔮 Previsão: NEUTRO — aguardar sinal"
 return f"{sent}\n{prev}"
def preco(t,modo="anterior"):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  m=r["chart"]["result"][0]["meta"]
  closes=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("close",[])if c]
  highs=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("high",[])if c]
  lows=[c for c in r["chart"]["result"][0]["indicators"]["quote"][0].get("low",[])if c]
  p=m.get("regularMarketPrice",0)
  mx=m.get("regularMarketDayHigh",0)
  mn=m.get("regularMarketDayLow",0)
  if modo=="anterior" and len(closes)>=2:
   ref=closes[-2];v=((closes[-1]-ref)/ref*100)if ref else 0;p=closes[-1]
   mx=highs[-1]if highs else p;mn=lows[-1]if lows else p
  elif modo=="dia":
   abertura=m.get("regularMarketOpen",0)
   ref=abertura;v=((p-abertura)/abertura*100)if abertura else 0
  else:
   ref=m.get("previousClose",0);v=((p-ref)/ref*100)if ref else 0
  e="📈"if v>=0 else"📉"
  moeda="$"if t in USD else"¥"
  tk=t.replace(".T","").replace("=F","").replace("^","")
  return f"{tk} {moeda}{p:,.2f} {e}{v:+.2f}%\nMax{moeda}{mx:,.2f} Min{moeda}{mn:,.2f}\n{sinal(p,mn,mx,closes,v)}",v
 except Exception as ex:
  return f"Erro: {ex}",0
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo(titulo,modo="anterior"):
 enviar(titulo+" "+datetime.now().strftime("%d/%m %H:%M")+" UTC")
 for t,n in ATIVOS.items():
  info,v=preco(t,modo)
  noticias=get_noticias(t)
  analise=analisar(n,noticias,v)
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
