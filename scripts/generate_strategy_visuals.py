"""Original text-free diagrams of the frozen selection rules, not performance charts."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BLUE, TEAL, GRAY, PALE, RED = '#2866b2', '#368d83', '#a5b3c6', '#dce5ef', '#bb7868'


def line(points, colour=BLUE, width=3, dash=''):
    return '<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+f'" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'


def circle(x,y,r=4,colour=BLUE):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{colour}"/>'


def rect(x,y,w,h,colour=PALE,r=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{colour}"/>'


def waves(x,y,w,h,cycles=3,trend=0,colour=BLUE):
    return line([(x+i*w/40,y+math.sin(i/40*cycles*math.pi*2)*h-trend*i/40) for i in range(41)],colour)


def basket(n, grouped=False):
    out=rect(502,35,105,87,'#f0f5fb',8)
    columns=5 if n in [10,20] else 6
    for i in range(n):
        c=[BLUE,TEAL,'#7b87b6'][i%3] if grouped else BLUE
        out+=rect(513+(i%columns)*14,49+(i//columns)*13,9,8,c,2)
    return out


def bars(heights, ascending=False, palette=None):
    out=line([(302,114),(445,114)],PALE,1.5)
    for i,h in enumerate(heights):
        out+=rect(311+i*25,114-h,15,h,(palette[i] if palette else TEAL if i<2 else GRAY),3)
    return out


def frame(content, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 156" role="img"><title>{title}</title><desc>Conceptual selection-rule illustration. Shapes are illustrative, not observed prices or simulated returns.</desc><rect width="640" height="156" rx="8" fill="#f6f8fc"/>
<rect x="20" y="20" width="226" height="116" rx="8" fill="white"/><rect x="286" y="20" width="174" height="116" rx="8" fill="white"/>
<path d="M257 78h17m-5-5 5 5-5 5M472 78h17m-5-5 5 5-5 5" fill="none" stroke="#9aabc0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>{content}</svg>'''


def visuals():
    result={}
    x=[35,60,85,110,135,160,185,222]
    result['high52']=line([(35,42),(222,42)],GRAY,2,'4 5')+line(list(zip(x,[111,91,98,68,84,48,70,48])),BLUE)+circle(222,48,5,BLUE)+line(list(zip(x,[117,101,112,96,91,106,90,85])),GRAY,2)+line([(222,42),(222,48)],TEAL,2)+bars([65,61,43,25,17])+basket(10)
    result['residual']=line(list(zip(x,[105,98,73,86,60,75,48,61])),GRAY,2)+line(list(zip(x,[111,95,83,83,65,58,52,35])),BLUE)+line([(303,84),(443,84)],PALE,2,'4 4')+waves(307,85,132,11,3,22,TEAL)+basket(30)
    result['absolute']=line([(34,90),(225,90)],GRAY,1.5,'4 4')+line(list(zip(x,[90,82,86,68,75,53,60,39])),BLUE)+line(list(zip(x,[90,97,91,103,95,113,108,118])),GRAY,2)+bars([68,51,29,12,5])+basket(30)
    result['lowvol']=waves(35,46,184,3,4,0,TEAL)+waves(35,79,184,8,4,0,GRAY)+waves(35,111,184,15,4,0,GRAY)+bars([13,23,34,49,69])+basket(20)
    result['riskmom']=waves(35,106,184,7,4,54,BLUE)+line([(35,120),(221,120)],PALE,1.5)+waves(35,126,184,3,8,0,TEAL)+bars([69,54,36,27,13])+basket(10)
    out=''
    for k,c in enumerate([BLUE,TEAL,'#7b87b6']):
        out+=rect(36+k*64,35,51,84,'#f0f5fb',7)
        for i in range(6):out+=circle(49+k*64+(i%2)*23,51+(i//2)*24,5,c)
    result['industry']=out+bars([64,47,30,13,7],palette=[BLUE,TEAL,'#7b87b6',GRAY,GRAY])+basket(20,True)
    result['fip']=line(list(zip(x,[113,104,91,83,74,61,51,38])),BLUE)+line(list(zip(x,[117,115,114,112,110,42,39,38])),GRAY,2)+''.join(rect(306+(i%8)*17,50+(i//8)*17,10,10,TEAL if i not in [2,10,19] else RED,2) for i in range(24))+basket(10)
    result['reversal']=line(list(zip(x,[57,59,54,60,64,61,59,65])),GRAY,2)+line(list(zip(x,[57,63,61,72,78,94,91,111])),BLUE)+line([(304,50),(443,50)],GRAY,1.5,'4 4')+''.join(rect(311+i*25,51,15,h,BLUE if i<2 else GRAY) for i,h in enumerate([61,47,33,20,9]))+basket(10)
    result['lowbeta']=waves(35,80,184,26,2,0,GRAY)+waves(35,80,184,7,2,0,BLUE)+line([(304,115),(445,115)],PALE,1.5)+line([(304,115),(304,36)],PALE,1.5)+line([(309,95),(439,62)],BLUE,2)+''.join(circle(312+i*13,95-i*3.3+math.sin(i*2)*5,3,TEAL) for i in range(10))+basket(20)
    result['lowmax']=line([(35,53),(54,50),(61,30),(65,53),(90,53),(96,19),(101,52),(132,50),(137,28),(143,52),(175,49),(180,22),(186,51),(211,20),(220,49)],GRAY,2)+waves(35,104,184,4,7,0,TEAL)+bars([15,24,38,56,70])+basket(30)
    result['mad']=line([(35,111),(62,102),(90,92),(118,79),(146,64),(175,50),(221,38)],BLUE)+line([(35,113),(62,110),(90,105),(118,100),(146,92),(175,84),(221,73)],GRAY)+line([(221,38),(221,73)],TEAL,2,'3 4')+bars([68,55,43,30,15])+basket(30)
    result['smad']=line([(35,72),(66,70),(96,68),(126,70),(156,69),(186,73),(221,76)],GRAY,3)+line(list(zip(x,[65,74,62,77,71,84,91,117])),BLUE)+circle(222,117,5,BLUE)+line([(222,76),(222,117)],TEAL,2,'3 4')+bars([18,29,40,55,65])+basket(10)
    return result


def main():
    titles={'high52':'Rank closeness to the 252-session high, select ten stocks', 'residual':'Remove the market component, rank residual momentum, select thirty stocks', 'absolute':'Filter positive formation returns, rank momentum, select thirty stocks', 'lowvol':'Measure return variability, prefer lower volatility, select twenty stocks', 'riskmom':'Divide formation momentum by volatility, rank scores, select ten stocks', 'industry':'Rank industry groups, alternate stock selections across three groups', 'fip':'Prefer frequent positive days within positive top momentum stocks', 'reversal':'Compare returns within each industry and select relative laggards', 'lowbeta':'Measure sensitivity to market returns, rank lowest beta first', 'lowmax':'Average the five largest recent daily returns, prefer smaller jumps', 'mad':'Rank the fifty-session mean divided by the two-hundred-session mean', 'smad':'Rank current close divided by ten-session mean, lowest first'}
    diagrams=visuals()
    for sid,content in diagrams.items():
        svg=frame(content,titles[sid]); ET.fromstring(svg)
        (ROOT/'src'/f'visual-{sid}.svg').write_text(svg,encoding='utf-8')
    print(f'Generated {len(diagrams)} original, text-free strategy-rule diagrams.')


if __name__=='__main__':main()
