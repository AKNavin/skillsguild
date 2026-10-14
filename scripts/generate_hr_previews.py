"""Maintain the catalogue's text-free, code-native HR illustrations."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INK='#596160'; BLUE='#79a8c6'; CORAL='#cf8875'; GOLD='#d8b46a'; GREEN='#93ad93'; PAPER='#fff9e9'

def path(d,fill='none',stroke=INK,width=3):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'
def rect(x,y,w,h,fill=PAPER,r=5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{INK}" stroke-width="2.4"/>'
def circle(x,y,r,fill=PAPER):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="2.4"/>'
def group(x,y,scale,content,angle=0):
    return f'<g transform="translate({x} {y}) scale({scale}) rotate({angle})">{content}</g>'
def line(x,y,a,b,color=INK,width=3):
    return path(f'M{x} {y} L{a} {b}',stroke=color,width=width)
def doc(x,y,s=1,color=PAPER):
    return group(x,y,s,rect(0,0,100,135,color)+rect(17,22,22,22,BLUE)+rect(52,22,28,22,GOLD)+rect(17,62,63,10,'#e0dfd3',2)+rect(17,88,45,10,'#e0dfd3',2))
def folder(x,y,s=1,color=GOLD):
    return group(x,y,s,path('M0 23 L0 5 L47 5 L63 22 L130 22 L130 103 L0 103 Z',color)+path('M0 43 L141 43 L128 112 L-9 112 Z',PAPER))
def book(x,y,s=1):
    return group(x,y,s,path('M0 12 Q40 0 83 20 Q123 0 166 12 L166 126 Q122 113 83 134 Q40 114 0 126 Z',PAPER)+line(83,20,83,134)+path('M11 24 Q44 14 70 29',stroke=BLUE,width=6)+path('M98 29 Q127 14 155 24',stroke=GOLD,width=6))
def peg(x,y,s=1,color=BLUE):
    return group(x,y,s,circle(0,0,20,color)+path('M-14 22 Q-31 47 -27 77 Q0 88 27 77 Q30 47 14 22 Z',color))
def team(x,y,s=1):
    return group(x,y,s,peg(-48,15,.8,GREEN)+peg(48,15,.8,CORAL)+peg(0,0,1,BLUE))
def calendar(x,y,s=1):
    return group(x,y,s,rect(0,0,110,115)+rect(0,0,110,25,CORAL)+line(25,-8,25,10,INK,5)+line(85,-8,85,10,INK,5)+''.join(rect(18+c*28,43+r*28,15,15,[BLUE,GOLD,GREEN][(r+c)%3],2) for r in range(2) for c in range(3)))
def clock(x,y,s=1):
    return group(x,y,s,circle(0,0,44,GOLD)+circle(0,0,36)+path('M0 -24 L0 0 L20 12',width=4)+circle(0,0,3,INK))
def magnify(x,y,s=1):
    return group(x,y,s,path('M30 32 L64 69',stroke=GOLD,width=16)+circle(0,0,45,BLUE)+circle(0,0,35,'#ecf5ee')+path('M-21 -12 Q-19 -24 -6 -26',stroke='#ffffff',width=5))
def envelope(x,y,s=1,color=PAPER):
    return group(x,y,s,rect(0,0,130,85,color)+path('M0 0 L65 48 L130 0')+path('M0 85 L43 41 M130 85 L87 41'))
def laptop(x,y,s=1):
    return group(x,y,s,rect(0,0,135,90,BLUE)+rect(9,9,117,72,'#e3eee9')+path('M0 90 L-18 108 L153 108 L135 90 Z',PAPER)+line(42,99,93,99))
def tray(x,y,s=1,color=BLUE):
    return group(x,y,s,path('M8 0 L112 0 L135 55 L-12 55 Z',PAPER)+path('M-12 55 L135 55 L135 80 L-12 80 Z',color))
def coins(x,y,s=1):
    return group(x,y,s,''.join(f'<ellipse cx="0" cy="{-i*13}" rx="28" ry="10" fill="{GOLD}" stroke="{INK}" stroke-width="2.3"/>' for i in range(4)))
def pen(x,y,s=1):
    return group(x,y,s,path('M0 0 L23 0 L23 102 L11 134 L0 102 Z',BLUE)+path('M0 102 L23 102 L11 134 Z',GOLD)+line(11,115,11,130),angle=30)
def lock(x,y,s=1):
    return group(x,y,s,path('M-22 0 L-22 -20 Q0 -58 22 -20 L22 0',stroke=INK,width=9)+rect(-34,0,68,55,GOLD)+circle(0,23,6,INK)+line(0,23,0,36,INK,5))
def target(x,y,s=1):
    return group(x,y,s,circle(0,0,60,CORAL)+circle(0,0,42,PAPER)+circle(0,0,24,BLUE)+circle(0,0,7,GOLD))
def building(x,y,s=1):
    return group(x,y,s,rect(0,0,110,150,PAPER)+''.join(rect(16+c*31,18+r*32,17,18,BLUE,2) for r in range(3) for c in range(3))+rect(43,117,27,33,GOLD,1))
def key(x,y,s=1):
    return group(x,y,s,circle(0,0,22,GOLD)+circle(0,0,9,PAPER)+path('M20 0 L95 0 L95 17 M73 0 L73 15',stroke=GOLD,width=11))
def speech(x,y,s=1,color=BLUE):
    return group(x,y,s,path('M0 0 Q0 -10 12 -10 L95 -10 Q110 -10 110 5 L110 55 Q110 65 96 65 L38 65 L16 87 L20 65 L10 65 Q0 65 0 55 Z',color))
def balance(x,y,s=1):
    return group(x,y,s,path('M0 -90 L0 80 M-52 80 L52 80 M-105 -75 L105 -75',stroke=INK,width=6)+circle(0,-75,8,GOLD)+path('M-105 -75 L-140 18 L-70 18 Z M105 -75 L70 18 L140 18 Z',PAPER)+path('M-142 18 Q-106 62 -68 18 M68 18 Q104 62 142 18',GOLD))
def gear(x,y,s=1,color=BLUE):
    points=[]
    for i in range(40):
        radius=50 if i%4 in [0,1] else 39
        a=2*math.pi*i/40
        points.append(f'{radius*math.cos(a):.2f},{radius*math.sin(a):.2f}')
    return group(x,y,s,f'<polygon points="{" ".join(points)}" fill="{color}" stroke="{INK}" stroke-width="2.3"/>'+circle(0,0,17,PAPER))
def plant(x,y,s=1):
    return group(x,y,s,path('M-35 0 L35 0 L25 53 L-25 53 Z',CORAL)+path('M0 0 Q-5 -55 9 -114',stroke=INK,width=5)+path('M0 -47 Q-66 -94 -54 -106 Q-4 -108 0 -47',GREEN)+path('M5 -77 Q55 -138 61 -109 Q61 -78 5 -77',GREEN))
def chair(x,y,s=1,color=BLUE):
    return group(x,y,s,rect(-35,-70,70,75,color)+rect(-41,5,82,19,PAPER)+path('M-29 24 L-35 80 M29 24 L35 80',width=6))
def bridge(x,y,s=1):
    return group(x,y,s,path('M-130 50 Q0 -55 130 50 L130 75 Q0 -20 -130 75 Z',PAPER)+path('M-130 28 Q0 -77 130 28',stroke=BLUE,width=7)+''.join(line(v,17+abs(v)*.15,v,49+abs(v)*.12,BLUE,4) for v in [-110,-65,0,65,110]))
def globe(x,y,s=1):
    return group(x,y,s,circle(0,0,70,BLUE)+f'<ellipse cx="0" cy="0" rx="29" ry="70" fill="none" stroke="{INK}" stroke-width="2.4"/>'+path('M-66 -25 Q0 2 66 -25 M-66 25 Q0 -2 66 25')+line(-70,0,70,0))
def bell(x,y,s=1):
    return group(x,y,s,path('M-55 35 L-42 10 Q-45 -65 0 -65 Q45 -65 42 10 L55 35 Z',GOLD)+circle(0,45,10,CORAL)+circle(0,-72,7,INK))
def funnel(x,y,s=1):
    return group(x,y,s,path('M-100 -70 L100 -70 L25 15 L25 68 L-25 82 L-25 15 Z',GOLD)+line(-75,-40,75,-40))
def ruler(x,y,s=1):
    return group(x,y,s,rect(0,0,160,24,GOLD,2)+''.join(line(i,0,i,12 if i%40 else 18) for i in range(10,155,10)))
def stairs(x,y,s=1):
    return group(x,y,s,path('M0 100 L0 70 L50 70 L50 35 L100 35 L100 0 L150 0 L150 100 Z',PAPER))
def star(x,y,s=1):
    return group(x,y,s,path('M0 -45 L14 -15 L46 -12 L22 10 L28 42 L0 26 L-28 42 L-22 10 L-46 -12 L-14 -15 Z',GOLD))

scenes={
'hr-context-profile':book(225,145,1.15)+building(95,145,.85)+peg(490,192,.9)+key(468,315,.75),
'hr-style-guide':book(130,165,1.45)+pen(475,113,1.3)+''.join(path(f'M255 {y} Q282 {y-24} 309 {y} T365 {y}',stroke=BLUE,width=5) for y in [211,235,259])+circle(453,315,23,CORAL)+circle(506,321,20,GOLD),
'hr-role-context':line(320,215,135,155,BLUE)+line(320,215,500,145,BLUE)+line(320,215,470,315,BLUE)+rect(264,150,112,145)+peg(320,194,.75)+target(500,145,.65)+team(463,300,.65)+gear(135,155,.9),
'hr-workflow-router':path('M160 220 L260 220 L260 125 L395 125 M260 220 L400 220 M260 220 L260 320 L400 320',stroke=BLUE,width=8)+tray(80,200,.9)+calendar(410,75,.65)+doc(423,185,.5)+tray(400,300,.7,GREEN),
'hr-workflow-automation':gear(190,165,1.3)+gear(295,215,1,GOLD)+gear(390,155,.9,GREEN)+path('M165 302 Q310 385 455 295 M449 276 L455 295 L431 301',stroke=BLUE,width=7)+doc(460,220,.7)+tray(450,313,.7,GREEN),
'hr-data-quality':doc(160,90,1.8)+rect(206,245,85,18,CORAL)+magnify(385,232,1.35)+pen(488,212,.7),
'hr-people-dashboard':rect(85,95,470,235)+''.join(rect(120+i*33,251-h,22,h,[BLUE,GOLD,CORAL][i%3]) for i,h in enumerate([55,90,72]))+path('M270 234 L301 192 L337 208 L374 144',stroke=BLUE,width=6)+team(460,155,.65)+lock(454,268,.65),
'hr-workforce-cost':balance(320,220,1.2)+team(194,155,.6)+coins(445,211,.9)+calendar(89,270,.6)+doc(477,267,.55),
'hr-privacy-retention':rect(130,95,240,240,BLUE)+folder(160,120,1.2)+folder(160,220,1.2,GREEN)+lock(376,230,.9)+clock(481,143,1)+tray(453,300,.75),
'hr-change-communications':bell(320,186,1.3)+line(250,215,150,280,BLUE,5)+line(390,215,491,280,BLUE,5)+envelope(84,265,.8)+envelope(267,287,.8)+envelope(454,265,.8)+team(320,330,.5),
'hr-workforce-plan':balance(320,215,1.2)+tray(130,190,.65)+tray(135,166,.65)+team(446,150,.6)+peg(533,284,.7,GREEN),
'hr-hiring-intake':rect(126,150,378,194,GOLD)+path('M250 150 L250 117 L375 117 L375 150',width=8)+doc(160,185,.95)+target(355,230,.65)+ruler(340,300,.8),
'hr-role-scorecard':doc(201,88,1.8)+rect(251,222,18,18,GREEN)+rect(290,222,18,18,GOLD)+rect(329,222,18,18,CORAL)+ruler(405,285,.8),
'hr-job-description':rect(155,78,330,245,GOLD)+doc(250,110,1.2)+circle(308,108,8,CORAL)+path('M197 323 L181 365 M443 323 L461 365',width=8)+folder(431,274,.65),
'hr-sourcing-plan':path('M145 225 L280 225 L280 125 L440 125 M280 225 L440 225 M280 225 L280 325 L440 325',stroke=BLUE,width=7)+folder(433,89,.55)+folder(433,190,.55)+folder(433,288,.55)+magnify(173,198,1.2),
'hr-candidate-outreach':bridge(325,265,1.2)+folder(100,134,1.1)+envelope(404,152,1.05)+peg(325,228,.6),
'hr-application-evidence':folder(175,190,1.7)+doc(210,140,.9)+doc(253,123,.9)+doc(300,153,.9)+magnify(411,232,1.3),
'hr-work-sample':rect(110,245,420,29,GOLD)+path('M146 274 L146 356 M492 274 L492 356',width=11)+gear(257,202,.85)+doc(388,128,.8)+pen(172,130,.7),
'hr-interview-scheduling':calendar(92,145,1.2)+calendar(416,145,1.2)+line(234,210,416,210,BLUE,6)+clock(322,187,1.15)+globe(329,310,.55),
'hr-interview-debrief':f'<ellipse cx="320" cy="224" rx="180" ry="99" fill="{GOLD}" stroke="{INK}" stroke-width="3"/>'+doc(175,135,.6)+doc(270,107,.6)+doc(392,145,.6)+rect(290,237,45,40,'#e7e6df')+chair(116,270,.6)+chair(516,270,.6),
'hr-offer-preparation':doc(154,90,1.6)+envelope(301,228,1.4)+coins(497,307,1.1)+circle(390,291,16,CORAL),
'hr-candidate-communications':tray(92,241,1)+tray(427,241,1,GREEN)+path('M200 215 Q320 92 440 215',stroke=BLUE,width=5)+envelope(202,165,.58)+envelope(302,127,.58)+envelope(393,177,.58),
'hr-recruiting-funnel':funnel(320,170,1.3)+''.join(circle(x,y,10,c) for x,y,c in [(215,91,BLUE),(270,77,GREEN),(334,82,CORAL),(402,88,BLUE),(315,174,GREEN),(338,198,CORAL)])+tray(114,308,.75)+tray(280,308,.75)+tray(446,308,.75),
'hr-preboarding':rect(100,198,440,150,GOLD)+laptop(134,116,1)+calendar(361,151,.9)+rect(282,213,64,90,BLUE)+peg(314,240,.4)+line(265,211,265,337)+line(352,211,352,337),
'hr-employee-records':folder(140,157,2)+rect(177,144,38,34,BLUE)+rect(229,144,38,34,CORAL)+rect(281,144,38,34,GREEN)+magnify(429,242,1.2),
'hr-hris-import':tray(85,235,1.1)+tray(421,235,1.1,GREEN)+bridge(321,243,.75)+folder(118,163,.75)+folder(277,202,.65)+folder(447,163,.75),
'hr-hr-helpdesk':bell(320,162,1.1)+tray(78,285,1)+tray(258,285,1,GREEN)+tray(438,285,1,CORAL)+doc(111,231,.45)+doc(289,232,.45)+doc(470,231,.45),
'hr-policy-answer':book(174,177,1.6)+path('M117 320 L117 133 L194 98',stroke=INK,width=8)+path('M155 84 L223 123 L250 77 Z',GOLD)+magnify(475,260,.75),
'hr-leave-coordination':calendar(104,154,1.4)+path('M326 189 Q402 56 478 189 Z',BLUE)+path('M388 167 Q463 44 539 167 Z',GREEN)+line(403,189,403,296)+line(464,167,464,292)+team(434,273,.65),
'hr-attendance-exceptions':doc(279,98,1.6)+rect(308,232,32,29,'#e9ece4')+clock(156,212,1.5)+magnify(427,254,.75),
'hr-payroll-handoff':folder(84,191,1)+envelope(248,170,1)+rect(455,154,90,138,BLUE)+''.join(circle(476+c*25,210+r*24,6,PAPER) for c in range(2) for r in range(3))+path('M210 246 L238 246 M388 246 L432 246',stroke=GOLD,width=7)+balance(320,323,.48),
'hr-payroll-reconciliation':balance(320,230,1.3)+doc(128,105,.95)+doc(402,105,.95)+coins(293,328,.65)+magnify(439,283,.75),
'hr-benefits-coordination':path('M115 175 Q320 -5 525 175 Z',BLUE)+line(320,175,320,301)+team(326,232,1)+folder(126,246,.9)+coins(486,320,1),
'hr-employee-letters':doc(183,85,1.8)+pen(432,125,1.35)+circle(450,313,27,CORAL)+path('M436 334 L432 370 L450 358 L469 370 L464 334',GOLD),
'hr-internal-transfer':bridge(320,245,1.05)+laptop(85,142,.9)+laptop(437,142,.9)+folder(277,225,.75)+peg(320,193,.65),
'hr-offboarding':tray(123,249,2.7)+laptop(163,127,1)+folder(350,172,1)+key(381,297,.9),
'hr-exit-insights':funnel(320,180,1)+speech(117,107,.6,BLUE)+speech(272,66,.6,CORAL)+speech(432,107,.6,GREEN)+''.join(rect(x,285,70,75,'#e3ece4',12)+circle(x+35,323,12,c) for x,c in [(167,BLUE),(285,CORAL),(403,GREEN)]),
'hr-compliance-calendar':calendar(106,122,1.8)+folder(387,220,1.1)+clock(480,143,1)+path('M257 128 L257 70 L311 85 L257 100',CORAL),
'hr-goal-setting':stairs(116,234,1.4)+target(447,160,1.15)+ruler(92,346,1.1),
'hr-manager-one-to-one':chair(170,214,1.2)+chair(470,214,1.2,GREEN)+rect(264,251,112,20,GOLD)+path('M282 270 L282 333 M360 270 L360 333',width=7)+book(281,215,.45)+clock(335,176,.58),
'hr-feedback-synthesis':speech(93,94,.8,BLUE)+speech(395,93,.8,CORAL)+speech(259,61,.8,GREEN)+rect(237,224,170,128,'#e1ebe4',20)+''.join(circle(x,y,13,c) for x,y,c in [(265,320,BLUE),(300,320,BLUE),(344,320,CORAL),(380,320,CORAL),(295,281,GREEN),(345,281,GREEN)]),
'hr-review-cycle':calendar(264,151,1)+path('M200 122 Q330 25 454 151 M454 151 L451 120 M454 151 L421 154 M437 295 Q297 390 174 256 M174 256 L173 289 M174 256 L207 258',stroke=BLUE,width=10)+doc(108,142,.65)+doc(460,214,.65),
'hr-calibration-preparation':balance(320,215,1.2)+folder(131,153,.8)+folder(383,153,.8)+magnify(484,300,.7),
'hr-development-plan':book(153,271,1.7)+book(183,245,1.35)+book(216,218,1)+plant(320,210,1.1)+path('M458 264 L510 264 L510 314 L458 314 Z M510 278 L554 252 L556 268 L510 297',BLUE),
'hr-learning-needs':''.join(rect(143+c*73,102+r*73,58,58,[BLUE,GOLD,GREEN][(r+c)%3]) for r in range(3) for c in range(4) if (r,c)!=(1,2))+magnify(333,202,.85),
'hr-learning-program':book(77,233,.95)+rect(277,262,120,20,GOLD)+path('M292 282 L292 337 M382 282 L382 337',width=7)+gear(336,229,.6)+path('M493 132 L493 334 M493 132 L565 151 L493 187',GREEN)+path('M208 293 L260 293 M408 293 L470 293',stroke=BLUE,width=6),
'hr-career-framework':stairs(90,225,1.3)+f'<g transform="translate(552 225) scale(-1.3 1.3)">{stairs(0,0,1)}</g>'+rect(279,214,83,24,GOLD)+folder(151,245,.4)+folder(426,245,.4)+target(320,135,.7),
'hr-succession-planning':chair(320,156,1.2,GOLD)+chair(140,290,.9)+chair(500,290,.9,GREEN)+path('M166 225 L320 176 L476 225',stroke=BLUE,width=7),
'hr-engagement-survey':rect(204,224,235,127,GOLD)+path('M204 224 L245 186 L470 186 L439 224 Z',PAPER)+line(290,203,387,203,INK,6)+speech(263,80,.8,BLUE)+speech(111,138,.6,GREEN)+clock(500,260,.75),
'hr-engagement-actions':tray(77,250,1.1)+speech(113,171,.6)+doc(278,136,.65)+doc(349,177,.65)+doc(278,252,.65)+plant(497,285,.9)+line(213,270,260,234,GOLD,6),
'hr-recognition':star(320,163,1.3)+path('M92 287 Q160 222 245 234 L306 257 Q320 282 289 287 L235 272 L316 314 L414 247 Q466 222 543 263 L557 308 L411 360 L243 352 L96 325 Z',PAPER)+gear(489,164,.65,GREEN),
'hr-compensation-review':rect(103,132,120,180,BLUE)+rect(118,148,90,35,PAPER)+''.join(circle(132+c*28,211+r*28,8,PAPER) for r in range(3) for c in range(3))+ruler(274,152,1.5)+ruler(274,217,1.5)+ruler(274,282,1.5)+coins(512,338,.85),
'hr-relations-intake':folder(300,168,1.8)+lock(432,261,.8)+envelope(95,128,1.1)+path('M213 297 L264 297 L264 235 M264 297 L264 335',stroke=BLUE,width=7),
'hr-investigation-plan':rect(111,90,413,242,GOLD)+path('M179 172 L309 256 L441 157 M179 172 L441 157',stroke=CORAL,width=4)+doc(146,113,.6)+doc(282,213,.6)+doc(412,111,.6)+magnify(470,289,.8),
'hr-performance-support':bridge(320,223,1.5)+rect(120,313,103,58,BLUE)+path('M144 313 L144 296 L195 296 L195 313',width=6)+peg(320,129,.8,GREEN),
'hr-policy-update':book(84,170,1.2)+book(367,170,1.2)+rect(482,218,50,25,GOLD)+pen(327,128,.9)+path('M290 298 L343 298',stroke=BLUE,width=6),
'hr-accommodation-coordination':rect(379,84,140,245,BLUE)+rect(395,99,108,230,PAPER)+path('M100 344 L399 267 L399 344 Z',GOLD)+rect(106,144,165,18,PAPER)+path('M129 162 L129 269 M247 162 L247 269',stroke=BLUE,width=8)+path('M184 183 L184 229 M174 193 L184 183 L194 193',stroke=CORAL,width=4),
'hr-global-mobility':globe(320,197,1.35)+building(92,205,.75)+building(470,205,.75)+path('M147 172 Q320 26 512 172',stroke=GOLD,width=7)+rect(263,283,116,73,CORAL)+path('M295 283 L295 269 L346 269 L346 283',width=5),
'hr-contingent-workforce':tray(116,279,1.3)+tray(370,279,1.3,GREEN)+rect(146,141,90,120,BLUE)+peg(192,174,.55)+rect(404,139,90,120,CORAL,20)+peg(450,174,.55,GREEN)+folder(280,210,.65),
'hr-organisation-design':circle(320,218,55,GOLD)+path('M270 192 L185 148 M368 192 L461 148 M320 272 L320 326',stroke=BLUE,width=8)+team(159,111,.8)+team(481,111,.8)+team(320,305,.65),
'hr-employee-consultation':f'<ellipse cx="320" cy="275" rx="189" ry="73" fill="{GOLD}" stroke="{INK}" stroke-width="3"/>'+speech(115,115,.75,BLUE)+speech(416,115,.75,GREEN)+folder(250,227,1)+speech(270,73,.75,CORAL),
'hr-wellbeing-program':path('M91 130 L320 49 L549 130',stroke=GREEN,width=14)+path('M119 135 L119 341 M521 135 L521 341',width=7)+plant(203,260,1)+chair(429,251,.85,GREEN)+rect(272,243,91,22,GOLD)+line(291,265,291,331,INK,6)+line(345,265,345,331,INK,6)
}

palettes=['#e2eddf','#e1e9ee','#efe9db','#e9e5ef','#f2edcf']
for i,(slug,scene) in enumerate(scenes.items()):
    folderpath=ROOT/'skills/hr'/slug
    meta=json.loads((folderpath/'metadata.json').read_text(encoding='utf-8'))
    if meta.get('image')!='preview.svg':
        raise ValueError(f'Unexpected image for {slug}')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="426" viewBox="0 0 640 426"><defs><filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".055"/></feComponentTransfer><feBlend in="SourceGraphic" mode="multiply"/></filter></defs><rect width="640" height="426" fill="{palettes[i%len(palettes)]}"/><g filter="url(#paper)"><ellipse cx="320" cy="363" rx="234" ry="18" fill="#5a675e" opacity=".10"/>{scene}</g></svg>'''
    (folderpath/'preview.svg').write_text(svg+'\n',encoding='utf-8')
print(f'Generated {len(scenes)} distinct text-free HR previews; existing illustrated cards preserved.')
