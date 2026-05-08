import requests,time
from datetime import datetime,date
TOKEN="8750903572:AAEGmATCu-GHKvVkFwP88ocuQzFd2cBkg9Y"
CHAT="2055797728"
ATIVOS={"8035.T":"Tokyo Electron","7011.T":"Mitsubishi","9984.T":"SoftBank","6857.T":"Advantest","6920.T":"Lasertec"}
enviado={}
def get_noticias(ticker):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker.replace('.T','')}&newsCount=5",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  return[n["title"]for n in r.get("news",[])[:5]if n.get("title")]
 except:
  return[]
def analisar(titulos,v):
 pos_words=["surge","jumps","rises","gains","up","high","record","buy","strong","beat","rally","profit"]
 neg_words=["falls","drops","down","crash","loss","cut","weak","miss","sell","risk","decline","slump"]
 if titulos:
  pos=sum(1 for t in titulos for w in pos_words if w in t.lower())
  neg=sum(1 for t in titulos for w in neg_words if w in t.lower())
  sent="Notícias positivas"if pos>neg else("Notícias negativas"if neg>pos else"Notícias neutras")
  resumo=titulos[0][:80]
 else:
  sent="Sem notícias";resumo=""
 if v<-3:prev="🔮 Caiu forte — possível reversão amanhã"
 elif v<-1:prev="🔮 Leve queda — monitorar entrada"
 elif v>3:prev="🔮 Subiu forte — aguardar correção"
 elif v>1:prev="🔮 Leve alta — não é momento de compra"
 else:prev="🔮 Neutro — aguardar movimento"
 txt=f"📰 {sent}\n{prev}"
 if resumo:txt+=f"\n📌 {resumo}"
 return txt
def sinal_compra(p,mn,mx,v):
 if mx==mn:return"🟡 AGUARDAR"
 pos_range=((p-mn)/(mx-mn))*100
 if v<-1 and pos_range<35:return"🟢 OPORTUNIDADE — caiu, perto da mínima"
 elif pos_range>70:return"🔴 NÃO COMPRAR — perto da máxima"
 else:return"🟡 AGUARDAR — sem sinal claro"
def preco_manha(t):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  q=r["chart"]["result"][0]["indicators"]["quote"][0]
  closes=[c for c in q.get("close",[])if c]
  highs=[c for c in q.get("high",[])if c]
  lows=[c for c in q.get("low",[])if c]
  if len(closes)<2:return"Dados insuficientes",0
  p=closes[-1];ref=closes[-2]
  mx=highs[-1]if highs else p;mn=lows[-1]if lows else p
  v=((p-ref)/ref*100)if ref else 0
  e="📈 POSITIVO"if v>=0 else"📉 NEGATIVO"
  sinal=sinal_compra(p,mn,mx,v)
  return f"¥{p:,.2f} — {e} {v:+.2f}%\nMáx ¥{mx:,.2f} | Mín ¥{mn:,.2f}\n{sinal}",v
 except Exception as ex:
  return f"Erro: {ex}",0
def preco_fechamento(t):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1d&interval=5m",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  m=r["chart"]["result"][0]["meta"]
  q=r["chart"]["result"][0]["indicators"]["quote"][0]
  precos=[c for c in q.get("close",[])if c]
  highs=[c for c in q.get("high",[])if c]
  lows=[c for c in q.get("low",[])if c]
  p=precos[-1]if precos else m.get("regularMarketPrice",0)
  mx=max(highs)if highs else p
  mn=min(lows)if lows else p
  tk=t.replace(".T","")
  return f"¥{p:,.2f}\n📈 Máx do dia ¥{mx:,.2f}\n📉 Mín do dia ¥{mn:,.2f}"
 except Exception as ex:
  return f"Erro: {ex}"
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo_manha():
 chave=f"manha_{date.today()}"
 if enviado.get(chave):return
 enviado[chave]=True
 enviar(f"📊 08:45 JST — Ontem: {datetime.now().strftime('%d/%m')}")
 for t,n in ATIVOS.items():
  info,v=preco_manha(t)
  analise=analisar(get_noticias(t),v)
  enviar(f"━━━━━━━━━━━━\n{n} ({t.replace('.T','')})\n{info}\n\n{analise}")
  time.sleep(3)
 enviar("✅ Fim do resumo!")
def resumo_fechamento():
 chave=f"fechamento_{date.today()}"
 if enviado.get(chave):return
 enviado[chave]=True
 enviar(f"⏰ 15:45 JST — Máx/Mín do dia: {datetime.now().strftime('%d/%m')}")
 for t,n in ATIVOS.items():
  info=preco_fechamento(t)
  enviar(f"━━━━━━━━━━━━\n{n} ({t.replace('.T','')})\n{info}")
  time.sleep(2)
 enviar("✅ Mercado fecha em 15 min!")
ultima_hora=""
while True:
 h=datetime.now().strftime("%H:%M")
 if h!=ultima_hora:
  ultima_hora=h
  if h=="23:45":resumo_manha()
  if h=="06:45":resumo_fechamento()
 time.sleep(55)
