#!/usr/bin/env python3
from __future__ import annotations
import json, os, re
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
USERNAME=os.getenv('GITHUB_USERNAME','viratsingh862008-blip')
PAPER,INK,MUTED='#F4F4F1','#111111','#74747A'
BLUE,RED,YELLOW='#3157F5','#F2382B','#FFC51B'
PALETTE=['#E2E2DE','#CAD4FF','#9DB1FF','#6687FF',BLUE]
class DayParser(HTMLParser):
    def __init__(self): super().__init__(); self.days={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); ds=a.get('data-date')
        if not ds: return
        try: date.fromisoformat(ds)
        except ValueError: return
        if tag not in ('td','rect') and 'ContributionCalendar-day' not in a.get('class',''): return
        try: level=max(0,min(4,int(a.get('data-level','0'))))
        except ValueError: level=0
        count=a.get('data-count'); aria=a.get('aria-label','')
        if count is None:
            m=re.search(r'([\d,]+)\s+contributions?',aria,re.I); count=m.group(1).replace(',','') if m else None
        try: count=int(count) if count is not None else None
        except ValueError: count=None
        self.days[ds]={'date':ds,'level':level,'count':count}
def fetch_data():
    req=Request(f'https://github.com/users/{USERNAME}/contributions',headers={'User-Agent':'Mozilla/5.0 AryanProfileArt/2.0'})
    with urlopen(req,timeout=30) as r: html=r.read().decode('utf-8','replace')
    p=DayParser(); p.feed(html)
    days=sorted(p.days.values(),key=lambda x:x['date'])[-371:]
    if len(days)<300: raise RuntimeError(f'Expected at least 300 calendar days; got {len(days)}')
    today=date.today(); days=[x for x in days if date.fromisoformat(x['date'])<=today]
    complete=all(x['count'] is not None for x in days)
    monthly=Counter()
    for x in days:
        value=x['count'] if complete else int(x['level']>0)
        monthly[x['date'][:7]] += value
    daymap={date.fromisoformat(x['date']):x for x in days}
    cursor=today
    if not ((daymap.get(cursor,{}).get('count') or 0) or daymap.get(cursor,{}).get('level',0)): cursor-=timedelta(days=1)
    streak=0
    while cursor in daymap and ((daymap[cursor].get('count') or 0) or daymap[cursor].get('level',0)):
        streak+=1; cursor-=timedelta(days=1)
    active=sum(1 for x in days if (x.get('count') or 0)>0 or x['level']>0)
    return {'username':USERNAME,'updated_at':datetime.utcnow().replace(microsecond=0).isoformat()+'Z','days':days,'total':sum(x['count'] or 0 for x in days) if complete else None,'counts_available':complete,'active_days':active,'current_streak':streak,'monthly':dict(monthly),'best_day':max((x.get('count') or 0 for x in days),default=0)}
def load_data():
    path=ROOT/'data/contributions.json'
    try:
        data=fetch_data(); path.write_text(json.dumps(data,indent=2),encoding='utf-8'); return data
    except Exception as exc:
        if path.exists():
            data=json.loads(path.read_text(encoding='utf-8'))
            if len(data.get('days',[]))>=300: data['refresh_note']=str(exc); return data
        raise
def svg(w,h,body,title,desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc><style>@keyframes rise{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}@keyframes print{{from{{opacity:0;transform:translateX(-12px)}}to{{opacity:1;transform:translateX(0)}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;transform:none!important}}}}</style>{body}</svg>'''
def hero():
    rows=['      .:+*##*+:.      ','   .-*%%%%%%%%%%*-.   ','  :#%%#*++++*#%%#:  ',' =%%*:        :*%%= ',' #%%:   A R   :%%# ',' #%%:   Y A N :%%# ',' =%%*:        :*%%= ','  :#%%#*++++*#%%#:  ','   .-*%%%%%%%%%%*-.   ','      .:+*##*+:.      ']
    art=''.join(f'<text x="0" y="{36+i*17}" font-family="monospace" font-size="10" fill="{INK}" opacity="0" style="animation:print .5s {i*.09:.2f}s forwards">{escape(line)}</text>' for i,line in enumerate(rows))
    body=f'''<rect width="1200" height="430" rx="26" fill="{PAPER}"/><rect x="54" y="46" width="11" height="11" rx="3" fill="{BLUE}"/><text x="82" y="58" fill="{MUTED}" font-family="monospace" font-size="17" letter-spacing="2">BUILDER / FOUNDER / DEVELOPER</text><text x="52" y="190" fill="{INK}" font-family="Georgia,serif" font-size="106" font-style="italic" opacity="0" style="animation:rise .8s .2s forwards">Aryan</text><text x="52" y="290" fill="{INK}" font-family="Georgia,serif" font-size="106" font-style="italic" opacity="0" style="animation:rise .8s .4s forwards">Singh</text><text x="56" y="350" fill="#393939" font-family="Arial,sans-serif" font-size="26">I build digital products, AI workflows,</text><text x="56" y="386" fill="#393939" font-family="Arial,sans-serif" font-size="26">and brand experiences that move businesses forward.</text><text x="56" y="414" fill="{INK}" font-family="monospace" font-size="17">webteaconnect.vercel.app  ↗</text><g transform="translate(815 72)">{art}</g><text x="1180" y="405" text-anchor="end" fill="{MUTED}" font-family="monospace" font-size="12" letter-spacing="2">BETTIAH / BIHAR / INDIA</text>'''
    return svg(1200,430,body,'Aryan Singh — profile hero','Typographic hero with an original ASCII monogram, role, focus and website.')
def tile(label,headline,copy,color,dark=False):
    fg=INK if dark else '#FFFFFF'
    body=f'''<rect width="380" height="270" rx="22" fill="{color}"/><text x="30" y="48" fill="{fg}" font-family="monospace" font-size="17" letter-spacing="3">{label}</text><text x="348" y="48" text-anchor="end" fill="{fg}" font-size="22">↗</text><text x="30" y="142" fill="{fg}" font-family="Georgia,serif" font-size="45" font-style="italic">{escape(headline)}</text><text x="30" y="190" fill="{fg}" font-family="Arial,sans-serif" font-size="17">{escape(copy)}</text><text x="30" y="232" fill="{fg}" font-family="monospace" font-size="11" letter-spacing="2">EXPLORE  ↗</text>'''
    return svg(380,270,body,f'{label}: {headline}',copy)
def activity(data):
    months=sorted(data.get('monthly',{}).items())[-12:] or [('—',0)]; maxv=max([v for _,v in months]+[1]); total=data.get('total'); total_txt=f'{total:,} contributions' if total is not None else f'{data.get("active_days",0):,} active days'; bars=[]
    for i,(m,v) in enumerate(months):
        h=150*v/maxv if maxv else 0; x=62+i*78; color=BLUE if v==maxv else INK
        bars.append(f'<rect x="{x}" y="{245-h}" width="56" height="{h}" rx="7" fill="{color}" opacity="0" style="animation:rise .55s {i*.06:.2f}s forwards"/>')
        label=datetime.strptime(m, '%Y-%m').strftime('%b') if len(m)==7 else m
        bars.append(f'<text x="{x+28}" y="273" text-anchor="middle" fill="{MUTED}" font-family="monospace" font-size="12">{escape(label)}</text>')
        if v: bars.append(f'<text x="{x+28}" y="{235-h}" text-anchor="middle" fill="{BLUE}" font-family="monospace" font-size="11">{v:,}</text>')
    streak=data.get('current_streak',0); active=data.get('active_days',0); best=data.get('best_day',0)
    body=f'''<rect width="1200" height="360" rx="24" fill="{PAPER}"/><text x="48" y="48" fill="{MUTED}" font-family="monospace" font-size="16" letter-spacing="2">THE LAST 12 MONTHS ON GITHUB</text><text x="48" y="112" fill="{INK}" font-family="Georgia,serif" font-size="58" font-style="italic">{total_txt}</text><g>{''.join(bars)}</g><text x="1000" y="105" fill="{INK}" font-family="Georgia,serif" font-size="54" font-style="italic">{streak} days</text><text x="1000" y="133" fill="{MUTED}" font-family="Arial,sans-serif" font-size="17">current streak</text><path d="M1000 158H1150" stroke="#D8D8D2"/><text x="1000" y="220" fill="{INK}" font-family="Georgia,serif" font-size="46" font-style="italic">{active}</text><text x="1000" y="248" fill="{MUTED}" font-family="Arial,sans-serif" font-size="16">active days</text><path d="M1000 270H1150" stroke="#D8D8D2"/><text x="1000" y="320" fill="{INK}" font-family="Georgia,serif" font-size="34" font-style="italic">{best or '—'}</text><text x="1060" y="319" fill="{MUTED}" font-family="Arial,sans-serif" font-size="14">best day</text>'''
    return svg(1200,360,body,'GitHub activity by month','Monthly contribution activity, current streak, active days and busiest day from public GitHub calendar data.')
def heatmap(data):
    days=sorted(data.get('days',[]),key=lambda x:x['date'])[-371:]; cells=[]
    if days:
        offset=(date.fromisoformat(days[0]['date']).weekday()+1)%7
        for i,d in enumerate(days):
            col,row=divmod(i+offset,7); x,y=55+col*17,110+row*17; level=max(0,min(4,int(d.get('level',0)))); delay=col*.018+row*.025
            cells.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{PALETTE[level]}" opacity="0" style="animation:fade .25s {delay:.3f}s forwards"><title>{escape(d["date"])} · level {level}</title></rect>')
    updated=escape(data.get('updated_at','').replace('T',' ').replace('Z',' UTC'))
    legend=''.join(f'<rect x="{100+i*17}" y="237" width="12" height="12" rx="3" fill="{c}"/>' for i,c in enumerate(PALETTE))
    body=f'''<rect width="1200" height="270" rx="24" fill="{PAPER}"/><text x="48" y="58" fill="{INK}" font-family="Georgia,serif" font-size="42">Every day, <tspan fill="{BLUE}" font-style="italic">in blue</tspan></text><text x="1150" y="55" text-anchor="end" fill="{MUTED}" font-family="monospace" font-size="14" letter-spacing="2">REFRESHED DAILY</text>{''.join(cells)}<text x="55" y="248" fill="{MUTED}" font-family="monospace" font-size="12">LESS</text>{legend}<text x="195" y="248" fill="{MUTED}" font-family="monospace" font-size="12">MORE</text><text x="1150" y="248" text-anchor="end" fill="{MUTED}" font-family="monospace" font-size="11">{updated}</text>'''
    return svg(1200,270,body,"Aryan Singh's GitHub contribution graph",'Self-hosted animated contribution calendar refreshed daily from GitHub.')
def project(title,description,stack,color):
    body=f'''<rect width="560" height="190" rx="20" fill="{PAPER}" stroke="#E2E2DE"/><text x="28" y="38" fill="{color}" font-family="monospace" font-size="14">SELECTED BUILD</text><text x="28" y="88" fill="{INK}" font-family="Georgia,serif" font-size="36" font-style="italic">{escape(title)}</text><text x="28" y="124" fill="#444" font-family="Arial,sans-serif" font-size="16">{escape(description)}</text><text x="28" y="164" fill="{MUTED}" font-family="monospace" font-size="12">{escape(stack)}</text>'''
    return svg(560,190,body,title,description)
def main():
    data=load_data(); out=ROOT/'cards'; out.mkdir(exist_ok=True)
    cards={'hero.svg':hero(),'build.svg':tile('BUILD','Products & code','Web apps, AI workflows and useful software.',BLUE),'brand.svg':tile('BRAND','WebTea','Digital experiences, identity and business growth.',RED),'learn.svg':tile('LEARN','Aaruufication','Ideas, lessons and creative work in public.',YELLOW,True),'activity.svg':activity(data),'heatmap.svg':heatmap(data),'project-wingmenbook.svg':project('Wingmenbook','Interactive, editorial-style brand experience.','REACT / TYPESCRIPT / VITE',BLUE),'project-webtea.svg':project('WebTea Connect','Digital presence and growth systems for businesses.','WEB / BRAND / AUTOMATION',RED),'project-hq.svg':project('WebTea HQ','AI employee and workflow orchestration workspace.','MCP / AGENTS / WORKFLOWS',BLUE)}
    for name,content in cards.items(): (out/name).write_text(content,encoding='utf-8')
if __name__=='__main__': main()
