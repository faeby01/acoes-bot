import requests,time
from datetime import datetime,date
TOKEN="8750903572:AAEGmATCu-GHKvVkFwP88ocuQzFd2cBkg9Y"
CHAT="2055797728"
ATIVOS={"8035.T":"Tokyo Electron","7011.T":"Mitsubishi","9984.T":"SoftBank","6857.T":"Advantest","6920.T":"Lasertec"}
enviado={}
def sinal_compra(p,mn,mx,v):
 if mx==mn:return"🟡 AGUARDAR"
 pos_range=((p-mn)/(mx-mn))*100
 if v<-1 and pos_range<35:return"🟢 OPORTUNIDADE — caiu, perto da mínima"
 elif pos_range>70:return"🔴 NÃO COMPRAR — perto da máxima"
 else:return"🟡 AGUARDAR — sem sinal claro"
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
def get_noticias(ticker):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker.replace('.T','')}&newsCount=5",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  return[n["title"]for n in r.get("news",[])[:5]if n.get("title")]
 except:
  return[]
def preco(t,dias_atras=1):
 try:
  r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
  res=r["chart"]["result"][0]
  q=res["indicators"]["quote"][0]
  closes=[c for c in q.get("close",[])if c]
  highs=[c for c in q.get("high",[])if c]
  lows=[c for c in q.get("low",[])if c]
  if len(closes)<2:return"Dados insuficientes",0
  p=closes[-1];ref=closes[-2]
  mx=highs[-1]if highs else p
  mn=lows[-1]if lows else p
  v=((p-ref)/ref*100)if ref else 0
  e="📈 POSITIVO"if v>=0 else"📉 NEGATIVO"
  sinal=sinal_compra(p,mn,mx,v)
  return f"¥{p:,.2f} — {e} {v:+.2f}%\nMáx ¥{mx:,.2f} | Mín ¥{mn:,.2f}\n{sinal}",v
 except Exception as ex:
  return f"Erro: {ex}",0
def enviar(txt):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":txt},timeout=10)
def resumo(chave,titulo):
 chave_dia=f"{chave}_{date.today()}"
 if enviado.get(chave_dia):return
 enviado[chave_dia]=True
 enviar(f"{titulo} {datetime.now().strftime('%d/%m')}")
 for t,n in ATIVOS.items():
  info,v=preco(t)
  analise=analisar(get_noticias(t),v)
  enviar(f"━━━━━━━━━━━━\n{n} ({t.replace('.T','')})\n{info}\n\n{analise}")
  time.sleep(3)
 enviar("✅ Fim do resumo!")
ultima_hora=""
while True:
 h=datetime.now().strftime("%H:%M")
 if h!=ultima_hora:
  ultima_hora=h
  if h=="00:00":resumo("manha","📊 ABERTURA 09:00 JST")
  if h=="07:00":resumo("fechamento","📊 FECHAMENTO 16:00 JST")
 time.sleep(55)
