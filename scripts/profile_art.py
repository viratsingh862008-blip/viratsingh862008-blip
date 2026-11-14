#!/usr/bin/env python3
"""Render Aryan Singh's editorial GitHub profile cards from public GitHub data."""
import re, json, urllib.request
from pathlib import Path
from datetime import date, datetime, timedelta
from html import escape
from html.parser import HTMLParser
from collections import defaultdict
from PIL import Image, ImageOps, ImageEnhance
from io import BytesIO

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'cards'; OUT.mkdir(exist_ok=True)
USER='viratsingh862008-blip'
BLUE='#3157F5'; PAPER='#F4F4F1'; INK='#111111'; MUTED='#707078'; RED='#F23B2D'; YELLOW='#FFC51B'
SERIF="'Bodoni 72', 'Didot', 'Georgia', serif"
SANS="Arial, Helvetica, sans-serif"
MONO="'Courier New', monospace"

class Days(HTMLParser):
    def __init__(self): super().__init__(); self.days=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='td' and 'ContributionCalendar-day' in a.get('class','') and a.get('data-date'):
            label=a.get('aria-label','')
            m=re.search(r'(\d[\d,]*) contributions?',label,re.I)
            count=int(m.group(1).replace(',','')) if m else None
            self.days.append({'date':a['data-date'],'level':max(0,min(4,int(a.get('data-level','0')))),'count':count})

def fetch_days():
    req=urllib.request.Request(f'https://github.com/users/{USER}/contributions',headers={'User-Agent':'Mozilla/5.0 AryanProfile/2.0'})
    raw=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
    p=Days(); p.feed(raw)
    unique={x['date']:x for x in p.days}
    days=sorted(unique.values(),key=lambda x:x['date'])[-371:]
    if len(days)<300: raise RuntimeError(f'Expected a full contribution year; got {len(days)} days')
    return {'username':USER,'updated_at':datetime.utcnow().replace(microsecond=0).isoformat()+'Z','days':days}

def load_data():
    try:
        data=fetch_days(); (ROOT/'data').mkdir(exist_ok=True); (ROOT/'data/contributions.json').write_text(json.dumps(data,indent=2))
        return data
    except Exception as e:
        p=ROOT/'data/contributions.json'
        if not p.exists(): raise
        data=json.loads(p.read_text())
        data['days']=sorted({x['date']:x for x in data.get('days',[])}.values(),key=lambda x:x['date'])[-371:]
        data['refresh_warning']=str(e)
        return data

def metrics(days):
    active=defaultdict(int)
    for x in days:
        d=date.fromisoformat(x['date']); active[d.strftime('%b')]+=bool(x['level'])
    dates={date.fromisoformat(x['date']) for x in days if x['level']>0}
    today=date.today(); cur=today if today in dates else today-timedelta(days=1)
    streak=0
    while cur in dates: streak+=1; cur-=timedelta(days=1)
    longest=run=0; prev=None
    for d in sorted(dates):
        run=run+1 if prev and d==prev+timedelta(days=1) else 1
        longest=max(longest,run); prev=d
    best=max((x for x in days if x['level']),key=lambda x:(x['level'],x['date']),default=None)
    return active,len(dates),streak,longest,best

def avatar_ascii():
    try:
        req=urllib.request.Request(f'https://github.com/{USER}.png',headers={'User-Agent':'Mozilla/5.0'})
        im=Image.open(BytesIO(urllib.request.urlopen(req,timeout=20).read())).convert('L')
        im=ImageOps.fit(im,(58,58)); im=ImageEnhance.Contrast(im).enhance(1.8)
        ramp=' .:-=+*#%@'
        return [''.join(ramp[min(9,int(im.getpixel((x,y))/256*10))] for x in range(58)) for y in range(0,58,2)]
    except Exception:
        return ['']*29

def wrap(w,h,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><style>
    .serif{{font-family:{SERIF}}}.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}.ink{{fill:{INK}}}.muted{{fill:{MUTED}}}
    @keyframes rise{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}
    @keyframes print{{from{{opacity:0}}to{{opacity:1}}}}
    .rise{{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}}
    @media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}
    </style>{body}</svg>'''

def hero():
    lines=[]
    for i,line in enumerate(avatar_ascii()):
        lines.append(f'<text x="755" y="{90+i*11}" class="mono" fill="#555" font-size="10" xml:space="preserve" opacity="0" style="animation:print .2s {i*.025:.3f}s forwards">{escape(line)}</text>')
    body=f'''<rect width="1200" height="500" rx="24" fill="{PAPER}"/>
    <rect x="54" y="45" width="11" height="11" rx="3" fill="{BLUE}"/><text x="82" y="57" class="mono muted" font-size="17" letter-spacing="2">BUILDER · FOUNDER · DEVELOPER</text>
    <text x="55" y="215" class="serif ink rise" font-size="140">Aryan</text><text x="55" y="340" class="serif ink rise" font-size="140" font-style="italic" style="animation-delay:.12s">Singh</text>
    <text x="60" y="405" class="sans" fill="#393939" font-size="27">I build digital products, shape brand experiences,</text><text x="60" y="443" class="sans" fill="#393939" font-size="27">and explore AI-powered systems.</text>
    <text x="60" y="480" class="mono ink" font-size="17">webteaconnect.vercel.app  ↗</text>
    <g>{''.join(lines)}</g><text x="755" y="455" class="mono muted" font-size="13" letter-spacing="2">GITHUB AVATAR / ASCII RENDER</text>'''
    (OUT/'hero.svg').write_text(wrap(1200,500,body),encoding='utf8')

def tiles():
    specs=[('BUILD','Digital products','Web apps · AI workflows · Tools',BLUE,'#FFFFFF'),('BRAND','WebTea + 4Wingmen','Identity · Experiences · Growth',RED,'#FFFFFF'),('LEARN','Build in public','Experiments · Notes · Reels',YELLOW,INK)]
    for name,title,desc,bg,fg in specs:
        body=f'''<rect width="380" height="280" rx="22" fill="{bg}"/><text x="30" y="48" class="mono" fill="{fg}" font-size="17" letter-spacing="3">{name}</text><text x="342" y="48" class="sans" fill="{fg}" font-size="25" text-anchor="end">↗</text><text x="30" y="145" class="serif" fill="{fg}" font-size="43" font-style="italic">{title}</text><text x="30" y="194" class="sans" fill="{fg}" font-size="18">{desc}</text><text x="30" y="248" class="mono" fill="{fg}" opacity=".8" font-size="13">EXPLORE / {name}</text>'''
        (OUT/f'tile-{name.lower()}.svg').write_text(wrap(380,280,body),encoding='utf8')

def activity(data):
    days=data['days']; active,active_n,streak,longest,best=metrics(days)
    months=[]
    for i in range(11,-1,-1):
        y=date.today().year; m=date.today().month-i
        while m<=0: y-=1; m+=12
        key=date(y,m,1).strftime('%b'); months.append((key,active.get(key,0)))
    maxv=max([v for _,v in months]+[1]); bars=[]
    for i,(m,v) in enumerate(months):
        x=55+i*70; h=190*v/maxv if v else 5; y=300-h; col=BLUE if v==maxv and v else INK
        bars.append(f'<rect x="{x}" y="{y:.1f}" width="48" height="{h:.1f}" rx="8" fill="{col}" opacity="0" style="animation:rise .55s {i*.045:.2f}s forwards"/><text x="{x+24}" y="328" text-anchor="middle" class="mono muted" font-size="12">{m}</text>')
    best_label=best['date'] if best else '—'
    body=f'''<rect width="1200" height="420" rx="24" fill="{PAPER}"/><text x="55" y="58" class="mono muted" font-size="17" letter-spacing="2">THE LAST 12 MONTHS ON GITHUB</text><text x="55" y="145" class="serif ink" font-size="74">{active_n} active days</text><text x="55" y="185" class="sans muted" font-size="18">Days with at least one public contribution</text>{''.join(bars)}
    <path d="M930 85V355" stroke="#D7D7D2" stroke-width="2"/><text x="975" y="130" class="serif ink" font-size="62">{streak} days</text><text x="978" y="162" class="sans muted" font-size="17">current streak</text><path d="M975 195H1150" stroke="#D7D7D2"/><text x="975" y="260" class="serif ink" font-size="56">{longest} days</text><text x="978" y="292" class="sans muted" font-size="17">longest streak</text><path d="M975 320H1150" stroke="#D7D7D2"/><text x="975" y="365" class="mono muted" font-size="14">MOST RECENT ACTIVE: {best_label}</text>'''
    (OUT/'activity.svg').write_text(wrap(1200,420,body),encoding='utf8')

def graph(data):
    days=data['days']; palette=['#E3E4E8','#CCD6FF','#9DB2FF','#6687FF',BLUE]; cells=[]
    first=date.fromisoformat(days[0]['date'])
    for d in days:
        day=date.fromisoformat(d['date']); col=(day-first).days//7; row=day.weekday(); x=55+col*20; y=105+row*18
        cells.append(f'<rect x="{x}" y="{y}" width="11" height="12" rx="3" fill="{palette[d["level"]]}" opacity="0" style="animation:print .25s {col*.018+row*.012:.3f}s forwards"><title>{d["date"]} · level {d["level"]}</title></rect>')
    body=f'''<rect width="1200" height="260" rx="24" fill="{PAPER}"/><text x="55" y="58" class="serif ink" font-size="48">Every day, <tspan fill="{BLUE}" font-style="italic">in blue.</tspan></text><text x="1140" y="55" text-anchor="end" class="mono muted" font-size="15" letter-spacing="2">REFRESHED DAILY</text>{''.join(cells)}<text x="55" y="238" class="mono muted" font-size="13">LESS</text>'''
    for i,c in enumerate(palette): body+=f'<rect x="{100+i*17}" y="224" width="13" height="13" rx="3" fill="{c}"/>'
    body+='<text x="1145" y="238" text-anchor="end" class="mono muted" font-size="13">MORE</text>'
    (OUT/'contributions.svg').write_text(wrap(1200,260,body),encoding='utf8')

def projects():
    items=[('WINGMENBOOK','Interactive brand experience',BLUE),('WEBTEA CONNECT','Digital presence & growth',RED),('WEBTEA AR','QR-led augmented reality',YELLOW)]
    for i,(name,desc,color) in enumerate(items,1):
        body=f'''<rect width="380" height="220" rx="22" fill="{PAPER}" stroke="#DEDED9"/><rect width="380" height="9" rx="4" fill="{color}"/><text x="28" y="60" class="mono muted" font-size="13" letter-spacing="2">SELECTED WORK / 0{i}</text><text x="28" y="112" class="serif ink" font-size="35">{name}</text><text x="28" y="153" class="sans muted" font-size="17">{desc}</text><text x="28" y="192" class="mono" fill="{BLUE}" font-size="14">OPEN PROJECT ↗</text>'''
        (OUT/f'project-{i}.svg').write_text(wrap(380,220,body),encoding='utf8')

def main():
    data=load_data(); hero(); tiles(); activity(data); graph(data); projects()
if __name__=='__main__': main()
