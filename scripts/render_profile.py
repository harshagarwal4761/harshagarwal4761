"""Render a chess profile from public GitHub data; no external image services."""
import json
import math
import os
from pathlib import Path
import subprocess
from datetime import date

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
USER = 'harshagarwal4761'
QUERY = '''query { user(login: "harshagarwal4761") {
  login followers { totalCount }
  allRepos: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
  repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100, isFork: false) {
    totalCount pageInfo { hasNextPage } nodes { name stargazerCount }
  }
  contributionsCollection { contributionCalendar {
    totalContributions weeks { contributionDays { contributionCount contributionLevel date } }
  } }
} }'''

BG = '#071311'
PANEL = '#0b211b'
LINE = '#285c49'
MINT = '#a3ffd3'
WHITE = '#edf9f2'
MUTED = '#88ad9c'
LEVELS = ['#14342a', '#1e6448', '#299664', '#55ca8b', '#a3ffd3']
LEVEL_NAMES = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']

def font(size):
    for candidate in ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                      '/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf']:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)

FONTS = {s: font(s) for s in [12, 14, 16, 18, 20, 24, 28, 38, 44]}

def text(d, xy, value, size=16, color=WHITE):
    d.text(xy, str(value), font=FONTS[size], fill=color)

def panel(height, label, right):
    im = Image.new('RGB', (1200, height), BG)
    d = ImageDraw.Draw(im)
    for inset in range(12):
        g = int(28 + inset * 2)
        d.rounded_rectangle((inset, inset, 1199-inset, height-1-inset), radius=22-inset,
                            outline=(14, g, int(g*.72)))
    d.rounded_rectangle((15, 15, 1184, height-16), radius=10, fill=PANEL, outline=LINE)
    for x, color in [(36, '#8effbc'), (56, '#62b68b'), (76, '#315f4d')]:
        d.ellipse((x, 34, x+7, 41), fill=color)
    text(d, (105, 28), label, 14, MINT)
    text(d, (1160-d.textlength(right, font=FONTS[12]), 30), right, 12, MUTED)
    d.line((32, 62, 1167, 62), fill=LINE)
    return im

def save_animation(frames, name, duration):
    # One stable palette prevents flickering across frames.
    palette = frames[0].quantize(colors=256)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/name, save_all=True, append_images=frames[1:], loop=0,
                   duration=duration, disposal=2, optimize=True)

def hero(user, updated):
    calendar = user['contributionsCollection']['contributionCalendar']
    base = panel(530, 'ENDGAME.EXE / PLAYER PROFILE', 'CHESS × CODE')
    d = ImageDraw.Draw(base)
    d.line((453, 88, 453, 452), fill=LINE)
    text(d, (498, 91), 'HARSH AGARWAL', 38)
    text(d, (500, 145), '@'+USER, 18, MINT)
    text(d, (500, 190), 'Think ahead. Build with intent.', 18, MUTED)
    text(d, (500, 238), 'CLASS', 14, MUTED)
    text(d, (684, 234), 'Developer / chess enthusiast', 16)
    text(d, (500, 277), 'LOADOUT', 14, MUTED)
    text(d, (684, 273), 'Java · Web · Shell · Kotlin', 16)
    text(d, (500, 316), 'PLAYSTYLE', 14, MUTED)
    text(d, (684, 312), 'Curiosity, then the next move.', 16)
    for x, val, label in [(500, user['allRepos']['totalCount'], 'PUBLIC REPOS'),
                          (722, calendar['totalContributions'], 'CONTRIBUTIONS / YEAR'),
                          (1000, user['followers']['totalCount'], 'FOLLOWERS')]:
        text(d, (x, 375), f'{val:02}', 38, MINT)
        text(d, (x, 425), label, 12, MUTED)
    d.line((33, 473, 1167, 473), fill=LINE)
    text(d, (42, 489), '01 / THE KNIGHT     THINK IN POSSIBILITIES.', 14, MINT)
    text(d, (882, 489), 'SYNC '+updated, 14, MUTED)
    # Original knight silhouette, sampled into a field of terminal characters.
    mask=Image.new('L',(180,260))
    md=ImageDraw.Draw(mask)
    md.polygon([(20,221),(25,190),(47,164),(66,143),(76,126),(48,134),(29,126),
                (8,129),(0,111),(23,79),(33,52),(57,39),(63,9),(83,29),(101,14),
                (109,46),(135,64),(157,96),(167,124),(166,150),(155,185),(154,221)],fill=255)
    md.ellipse((48,66,58,76),fill=0)
    md.rectangle((12,222,162,233),fill=255)
    md.polygon([(17,236),(157,236),(171,250),(3,250)],fill=255)
    frames=[]
    for frame in range(28):
        im=base.copy(); d=ImageDraw.Draw(im)
        scan = frame*12
        for r, y in enumerate(range(0,256,8)):
            for c, x in enumerate(range(0,180,5)):
                if mask.getpixel((x,y)):
                    char='01/+#'[ (r*3+c*7)%5 ]
                    yy=91+r*11
                    distance=abs((yy-91)-scan)
                    col=MINT if distance<25 else '#5bc69a' if distance<70 else '#358768'
                    text(d,(62+c*10,yy),char,12,col)
        text(d,(96,445),'Nf3  /  READY FOR THE NEXT MOVE',12,MUTED)
        frames.append(im)
    frames[0].save(ASSETS/'player-card.png')
    save_animation(frames,'player-card.gif',100)

def activity(user, updated):
    cal=user['contributionsCollection']['contributionCalendar']
    weeks=cal['weeks']; count=cal['totalContributions']
    base=panel(380,'THE LONG GAME / CONTRIBUTION ACTIVITY', 'REAL GITHUB DATA')
    d=ImageDraw.Draw(base)
    text(d,(42,83),f'{count} contributions',28,MINT)
    text(d,(42,121),'Over the last year. Every move counts.',14,MUTED)
    startx=83; starty=178; step=20; cell=15
    previous=None
    valid=set()
    for col,week in enumerate(weeks):
        days=week['contributionDays']
        first=date.fromisoformat(days[0]['date'])
        month=first.strftime('%b')
        if month != previous and col < len(weeks)-2:
            text(d,(startx+col*step,152),month,12,MUTED); previous=month
        for day in days:
            row=(date.fromisoformat(day['date']).weekday()+1)%7
            level=LEVEL_NAMES.index(day['contributionLevel'])
            x=startx+col*step; y=starty+row*step
            d.rounded_rectangle((x,y,x+cell,y+cell),radius=3,fill=LEVELS[level])
            valid.add((col,row))
    for row,day in [(1,'M'),(3,'W'),(5,'F')]:text(d,(48,starty+row*step),day,12,MUTED)
    text(d,(42,343),'A KNIGHT TAKES THE SCENIC ROUTE.',12,MINT)
    text(d,(873,343),'LESS',12,MUTED)
    for i,c in enumerate(LEVELS):d.rounded_rectangle((916+i*21,344,930+i*21,357),radius=2,fill=c)
    text(d,(1033,343),'MORE',12,MUTED)
    # A legal sequence of knight moves across the seven-row calendar.
    route=[next((p for p in [(0,3),(0,4),(0,5),(0,6)] if p in valid), min(valid))]
    direction=1
    while route[-1][0]+2<len(weeks):
        col,row=route[-1]
        if not 1<=row+direction<=5:direction*=-1
        dest=(col+2,row+direction)
        if dest not in valid:break
        route.append(dest)
    assert all(sorted((abs(a[0]-b[0]),abs(a[1]-b[1])))==[1,2] for a,b in zip(route,route[1:]))
    assert sum(day['contributionCount'] for w in weeks for day in w['contributionDays']) == count
    # Small custom knight token, drawn as a silhouette instead of relying on emoji fonts.
    token=[(0,19),(3,13),(8,9),(3,11),(0,8),(4,3),(8,3),(9,0),(12,3),(15,2),(18,7),(18,12),(16,19)]
    frames=[]
    for idx,(col,row) in enumerate(route):
        for phase in [0,1]:
            im=base.copy(); d=ImageDraw.Draw(im)
            x=startx+col*step+7; y=starty+row*step+7
            # The board remains intact; only the decorative knight moves.
            radius=15+phase*2
            d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=BG,outline=MINT,width=1)
            points=[(x+px-9,y+py-10) for px,py in token]
            d.polygon(points,fill=WHITE)
            d.rectangle((x-10,y+10,x+10,y+12),fill=MINT)
            d.point((x-2,y-5),fill=BG)
            frames.append(im)
    base.save(ASSETS/'contribution-board.png')
    save_animation(frames,'contribution-board.gif',180)

def main():
    raw=subprocess.check_output(['gh','api','graphql','-f','query='+QUERY],text=True)
    payload=json.loads(raw)
    if payload.get('errors'):raise RuntimeError(payload['errors'])
    user=payload['data']['user']
    today=date.today().isoformat()
    hero(user,today)
    activity(user,today)
    projects=[('01 / ROOK', 'AI LIBRARY TOOLS', 'Java web app / tool discovery, dashboard & authentication', 'ai-tools'),
              ('02 / BISHOP', 'FILE SCANNER', 'Java / directory scanning, pattern matching & reports', 'file-scanner'),
              ('03 / PAWN', 'SPS PROJECT', 'Shell / build, package, archive & deploy a C project', 'sps-project')]
    for label,title,subtitle,slug in projects:
        im=panel(180,label,'PIECES IN PLAY')
        d=ImageDraw.Draw(im)
        text(d,(42,81),title,28,MINT)
        text(d,(42,128),subtitle,16,MUTED)
        text(d,(984,95),'VIEW REPO >',16,WHITE)
        im.save(ASSETS/(slug+'.png'))
    print('Rendered player card and contribution board from live public GitHub data.')

if __name__=='__main__':main()
