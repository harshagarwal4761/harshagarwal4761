"""Render a chess profile from public GitHub data; no external image services."""
import json
import html
import re
import math
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

BG = '#0d1916'
PANEL = BG
LINE = '#294138'
MINT = '#a6ddbe'
WHITE = '#f0f0e5'
MUTED = '#9aafa3'
LEVELS = ['#14342a', '#1e6448', '#299664', '#55ca8b', '#a3ffd3']
LEVEL_NAMES = ['NONE', 'FIRST_QUARTILE', 'SECOND_QUARTILE', 'THIRD_QUARTILE', 'FOURTH_QUARTILE']

def font(size):
    for candidate in ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                      '/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf']:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)

FONTS = {s: font(s) for s in [12, 14, 16, 18, 20, 22, 24, 28, 32, 38, 44]}

def text(d, xy, value, size=16, color=WHITE):
    d.text(xy, str(value), font=FONTS[size], fill=color)

def panel(height):
    im = Image.new('RGB', (1200, height), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, 1198, height-2), radius=20, outline=LINE, width=2)
    return im

def save_animation(frames, name, duration):
    # One stable palette prevents flickering across frames.
    palette = frames[0].quantize(colors=256)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/name, save_all=True, append_images=frames[1:], loop=0,
                   duration=duration, disposal=1, optimize=True)

def hero(user, updated):
    calendar = user['contributionsCollection']['contributionCalendar']
    base = panel(432)
    d = ImageDraw.Draw(base)
    text(d, (40, 30), 'ENDGAME / 01', 16, MINT)
    text(d, (997, 30), 'CHESS × CODE', 16, MUTED)
    d.line((40, 68, 1160, 68), fill=LINE)
    d.line((376, 102, 376, 370), fill=LINE)
    title_font = next((ImageFont.truetype(path, 48) for path in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf'
    ] if Path(path).exists()), ImageFont.load_default(size=48))
    d.text((426, 106), 'Harsh Agarwal', font=title_font, fill=WHITE)
    text(d, (430, 170), '@'+USER, 18, MINT)
    text(d, (430, 218), 'Think ahead. Build with intent.', 22, WHITE)
    text(d, (430, 255), 'Java / Web / Shell / Kotlin', 18, MUTED)
    for x, val, label in [(430, user['allRepos']['totalCount'], 'PUBLIC REPOS'),
                          (667, calendar['totalContributions'], 'CONTRIBUTIONS / YEAR'),
                          (987, user['followers']['totalCount'], 'FOLLOWERS')]:
        text(d, (x, 315), f'{val:02}', 32, MINT)
        text(d, (x, 359), label, 14, MUTED)
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
    for frame in range(24):
        im=base.copy(); d=ImageDraw.Draw(im)
        scan = 120 - 150 * math.cos(frame * 2 * math.pi / 24)
        for r, y in enumerate(range(0,256,10)):
            for c, x in enumerate(range(0,180,5)):
                if mask.getpixel((x,y)):
                    char='01/+#'[ (r*3+c*7)%5 ]
                    yy=96+r*10
                    distance=abs((yy-96)-scan)
                    col=MINT if distance<22 else '#6eb590' if distance<55 else '#3d735b'
                    text(d,(62+c*8,yy),char,12,col)
        text(d,(112,370),'Nf3 / YOUR MOVE',14,MUTED)
        frames.append(im)
    frames[0].save(ASSETS/'player-card.png')
    save_animation(frames,'player-card.gif',140)

def activity(user, updated):
    cal=user['contributionsCollection']['contributionCalendar']
    weeks=cal['weeks']; count=cal['totalContributions']
    base=panel(310)
    d=ImageDraw.Draw(base)
    text(d,(40,25),f'{count} contributions',24,WHITE)
    text(d,(882,31),'THE LAST 12 MONTHS',16,MUTED)
    startx=89; starty=101; step=20; cell=14
    previous=None
    valid=set()
    for col,week in enumerate(weeks):
        days=week['contributionDays']
        first=date.fromisoformat(days[0]['date'])
        month=first.strftime('%b')
        if month != previous and col < len(weeks)-2:
            text(d,(startx+col*step,73),month,12,MUTED); previous=month
        for day in days:
            row=(date.fromisoformat(day['date']).weekday()+1)%7
            level=LEVEL_NAMES.index(day['contributionLevel'])
            x=startx+col*step; y=starty+row*step
            d.rounded_rectangle((x,y,x+cell,y+cell),radius=3,fill=LEVELS[level])
            valid.add((col,row))
    for row,day in [(1,'M'),(3,'W'),(5,'F')]:text(d,(48,starty+row*step),day,12,MUTED)
    d.line((40,248,1160,248),fill=LINE)
    text(d,(40,267),'ONE MOVE AT A TIME.',14,MUTED)
    text(d,(873,269),'LESS',12,MUTED)
    for i,c in enumerate(LEVELS):d.rounded_rectangle((916+i*21,270,930+i*21,283),radius=2,fill=c)
    text(d,(1033,269),'MORE',12,MUTED)
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
        for phase in [0]:
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
    save_animation(frames,'contribution-board.gif',360)

def update_projects():
    config = json.loads((ROOT/'profile.json').read_text())
    projects = config['projects']
    if len(projects) != 3:
        raise ValueError('Choose exactly three repositories in profile.json.')
    entries = []
    for index, project in enumerate(projects, 1):
        repo = project['repo']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('Use owner/repository format: '+repo)
        data = json.loads(subprocess.check_output(['gh','api','repos/'+repo], text=True))
        if data['private']:
            raise ValueError('Featured repositories must be public: '+repo)
        title = html.escape(project.get('title') or data['name'])
        description = html.escape(project.get('description') or data.get('description') or 'Explore the code and follow the project on GitHub.')
        language = html.escape(data.get('language') or 'Code')
        url = 'https://github.com/'+repo
        entries.append(f'<h3>{index:02} / <a href="{url}">{title}</a></h3>\n\n'
                       f'<p>{description}<br /><sub>{language} &nbsp; · &nbsp; '
                       f'<a href="{url}">Explore repository ↗</a></sub></p>')
    readme = ROOT/'README.md'
    start, end = '<!-- PROJECTS:START -->', '<!-- PROJECTS:END -->'
    content = readme.read_text()
    if content.count(start) != 1 or content.count(end) != 1:
        raise ValueError('README needs exactly one pair of project markers.')
    before, rest = content.split(start)
    _, after = rest.split(end)
    readme.write_text(before+start+'\n\n'+'\n\n'.join(entries)+'\n\n'+end+after)

def main():
    raw=subprocess.check_output(['gh','api','graphql','-f','query='+QUERY],text=True)
    payload=json.loads(raw)
    if payload.get('errors'):raise RuntimeError(payload['errors'])
    user=payload['data']['user']
    today=date.today().isoformat()
    hero(user,today)
    activity(user,today)
    update_projects()
    print('Rendered player card and contribution board from live public GitHub data.')

if __name__=='__main__':main()
