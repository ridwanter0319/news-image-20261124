"""Compose 'The World in One Day — Tuesday 24 November 2026'.

Draws a one-page cream broadsheet, exactly 1024x1024, with PIL:
masthead, standfirst, a numbers strip tied to the leads, a region bar,
a UTC timeline strip, three illustrated lead cards, twelve illustrated
story cards, 21 short briefs in two columns, a dotted world map with
numbered pins for stories 1-15, and an honest DATE CHECK box.
Everything is drawn in code; no external assets, no network.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # content width = 996

CREAM = (247, 241, 227)
PAPER = (251, 247, 236)
INK = (26, 24, 20)
SOFT = (74, 68, 58)
RED = (164, 22, 26)
DARKRED = (122, 14, 18)
RULE = (120, 110, 92)
CARDBG = (253, 250, 241)
CHIP = (255, 252, 244)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIFI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, maxw):
    """Greedy word wrap against pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, font, fill, maxw, lh, max_lines=None):
    """Draw wrapped text; returns y after the last line."""
    x, y = xy
    lines = wrap(draw, text, font, maxw)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def centered(draw, y, text, font, fill):
    w_ = draw.textlength(text, font=font)
    draw.text(((W - w_) / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- data

TOP_LEFT = "THE WORLD IN ONE DAY"
TOP_RIGHT = "36 STORIES · 8 REGIONS · EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
MASTHEAD = "Tuesday 24 November 2026"
STANDFIRST = ("Huang returns to a hero's welcome at Nvidia · UN demands a probe as the "
              "Ukraine war reaches Libya · Iran says three tankers hit mines in Hormuz")

NUMBERS = [
    ("3", "tankers hit mines in Hormuz — Iran's claim"),
    ("26", "dead in Cikande — toll updated Tuesday"),
    ("+3.91%", "Nikkei — Tuesday's close in Tokyo"),
    ("2 / 22", "killed / wounded in Zaporizhzhia"),
    ("700,000+", "Russian soldiers dead — leaked data"),
    ("7.3M", "more people risk losing food aid"),
]

REGION_BAR = ("EUROPE 8 · MIDDLE EAST 8 · ASIA-PACIFIC 7 · AMERICAS 6 · "
              "AFRICA 4 · WORLD 1 · SCIENCE 1 · SPORT 1")

UTC_ANCHORS = [
    "01:47 GMT — Brent at $88.97 as Hormuz risk persists",
    "06:00 UTC — Tokyo closes, Nikkei +3.91%",
    "12:03 UTC — UK designates the Houthis under Yemen sanctions",
    "16:30 UTC — Frankfurt closes, DAX +2.15%",
]

LEADS = [
    {
        "scene": "nvidia",
        "img_title": "THE HERO'S WELCOME",
        "img_sub": "HUANG AT HQ",
        "kicker": "1 · SANTA CLARA · TECH — REPORTED",
        "headline": "Huang returns to a hero's welcome at Nvidia as Trump hails his intervention",
        "body": ("A day after Nvidia reinstated Jensen Huang as CEO under pressure from "
                 "President Trump, Huang returns to a hero's welcome at Nvidia HQ and Trump "
                 "hails his own intervention. US lawmakers criticise the reinstatement. The "
                 "Commerce Department blacklists Alibaba's Singapore subsidiary Apex "
                 "Enterprise Solutions and Megaspeed, the neocloud at the centre of the "
                 "Nvidia scandal. Nvidia stock had nearly halved in the six weeks to Friday, "
                 "then surged 31% on Monday. (Reuters)"),
    },
    {
        "scene": "libya",
        "img_title": "PROBE DEMANDED",
        "img_sub": "WAR REACHES LIBYA",
        "kicker": "2 · BENGHAZI / TRIPOLI · WAR — REPORTED",
        "headline": "UN demands an independent probe as the Ukraine war reaches Libya",
        "body": ("The UN mission in Libya (UNSMIL) calls for an immediate, independent and "
                 "transparent investigation into Sunday's attacks at Benghazi port, where "
                 "Ukrainian naval drones sank the Russian corvette Merkury and hit the "
                 "weapons freighter MV Angara — Kyiv's first acknowledged strike in Libya. "
                 "Tripoli's UN-backed government condemns the strikes; the eastern "
                 "government asks the UN to investigate and opens a joint probe with "
                 "Russia. (UNSMIL, The Times, CNN, WSJ)"),
    },
    {
        "scene": "hormuz",
        "img_title": "MINES IN THE STRAIT?",
        "img_sub": "3 TANKERS",
        "kicker": "3 · STRAIT OF HORMUZ · IRAN — CLAIM vs REPORTED",
        "headline": "Iran says three tankers hit mines in Hormuz under US escort",
        "body": ("Iran's Revolutionary Guards say three oil tankers struck naval mines and "
                 "caught fire in the Strait of Hormuz while sailing under US escort — a "
                 "claim US Central Command has not confirmed and no operator has verified. "
                 "The Joint Maritime Information Center keeps the strait's threat level at "
                 "\"severe\" after seven tanker attacks on 16–21 Nov. Brent crude eases "
                 "0.45% to $88.97 regardless. (Reuters, IRNA/Press TV, JMIC)"),
    },
]

# scene key, number, place · beat, red label line 1, red label line 2, body
CARDS = [
    ("zaporizhzhia", 4, "ZAPORIZHZHIA, UKRAINE · WAR", "2 DEAD", "22 WOUNDED",
     "A Russian attack overnight kills 2 people and wounds 22, including 2 children, "
     "in Zaporizhzhia, the regional defence council says. (Reuters)"),
    ("beijing", 5, "BEIJING · POLITICS", "POLITBURO PROBE", "CHEN JINING",
     "Shanghai party chief Chen Jining, a member of China's Politburo, is placed under "
     "investigation, Xinhua says — the fourth member of the top leadership body probed "
     "since 2025. (Reuters/Xinhua)"),
    ("baghdad", 6, "BAGHDAD · IRAQ", "OILFIELDS ORDER", "KURDISTAN",
     "Iraq's PM Ali al-Zaidi orders the federal oil ministry to manage oilfields under "
     "Kurdish security control in four provinces and the border crossings authority to "
     "take over Kurdistan's crossings, after an oil smuggling probe. (Reuters)"),
    ("gaza", 7, "GAZA · WAR", "6 KILLED", "AIRSTRIKES",
     "Israeli airstrikes kill at least six Palestinians, including two police officers, "
     "in the Gaza Strip on Tuesday, local health and police officials say. (Reuters)"),
    ("cikande", 8, "CIKANDE, INDONESIA · FIRE", "TOLL AT 26", "DOZENS MISSING",
     "The toll from the Cikande candy-factory fire is updated to 26 dead on Tuesday, "
     "with dozens still missing as rescuers search. (Wires)"),
    ("berlin", 9, "BERLIN · DEFENCE", "DELTA ACCESS", "FIRST COUNTRY",
     "Germany becomes the first country granted access to Ukraine's Delta battlefield "
     "management system, under a letter of intent signed by both defence ministers in "
     "Berlin; a preliminary deal adds interceptor missiles for Ukraine. (Kyiv Independent)"),
    ("nuclear", 10, "MOSCOW / TALLINN · RUSSIA", "NUCLEAR WARNINGS", "SPACE THREAT",
     "Medvedev warns Russia could carry out a \"preventive nuclear attack\"; Moscow "
     "accuses Estonia of actions \"on the verge of triggering open war\"; NATO chief "
     "Rutte vows to defend against space threats after reports Russia is preparing a "
     "nuclear-armed satellite. (Wires, BBC)"),
    ("warsaw", 11, "WARSAW · POLAND", "DRONE INCURSION", "NATO AIRCRAFT",
     "A Russian drone enters Polish airspace days after cruise missiles fell in Poland; "
     "NATO deploys advanced detection aircraft in Poland in response. (Wires)"),
    ("iowa", 12, "IOWA · US", "COURT CLEARS BLAST", "TOXIC EXPLOSIVES",
     "A US court clears the Army to detonate toxic explosives in Iowa despite a "
     "last-minute order from Trump to stop it. (Reuters)"),
    ("grok", 13, "OREGON / VIRGINIA · TECH LAW", "STATES SUE", "GROK IMAGES",
     "Oregon and Virginia sue SpaceX and Musk's firms over alleged Grok-generated "
     "child abuse images. (Wires)"),
    ("gazipur", 14, "GAZIPUR, BANGLADESH · UNREST", "GARMENT CLASHES", "TEAR GAS",
     "Garment workers block roads and clash with police in Gazipur as pay protests shut "
     "dozens of factories; police fire tear gas and sound grenades. (Reuters)"),
    ("lahj", 15, "LAHJ, YEMEN · WAR", "25 KILLED", "UK SANCTIONS",
     "Strikes on buses and trucks in Lahj kill about 25; Britain designates the Houthis "
     "under its Yemen sanctions regime and targets four senior figures. (Wires, Reuters)"),
]

BRIEFS = [
    "16 Europe: EU proposes a 22nd sanctions package on Russia, including a sports ban (Wires)",
    "17 Europe: Seven countries urge the EU to limit Russian visas for tourists and sports events (Kyiv Independent)",
    "18 Europe: Spain's Supreme Court amnesties Catalan leader Carles Puigdemont (Wires)",
    "19 Europe: Leaked data reveals the scale of Russian military deaths — more than 700,000 soldiers (Wires)",
    "20 Middle East: Netanyahu pushes Trump to resume strikes on Iran (Wires)",
    "21 Middle East: Qatar's prime minister seeks to revive US–Iran talks in Doha (Wires)",
    "22 Middle East: Iran rules out any negotiation until Washington meets its seven conditions (Wires)",
    "23 Middle East: US eyes Iran as the culprit in cyberattacks against up to 50 ships, WSJ reports (WSJ)",
    "24 Africa: Heavy fighting in Ituri traps DR Congo Ebola responders; WHO says teams took cover for over 24 hours (UN News/WHO)",
    "25 Africa: DR Congo says a military aircraft is missing as rebels claim a shootdown near Minembwe (Wires)",
    "26 Africa: Somalia and Uganda agree to intensify operations against al-Shabaab as withdrawal begins (Wires)",
    "27 Asia-Pacific: A 5.6 magnitude earthquake strikes Nepal's Koshi province near the Chinese border (Wires)",
    "28 Asia-Pacific: China opens its Tiangong station to a first foreign astronaut — Pakistan's Zeeshan Ali, on Shenzhou-24 (Straits Times)",
    "29 Asia-Pacific: Solomon Islands moves to end its security pact with China (Wires)",
    "30 Asia-Pacific: Sheikh Hasina plans to return to Bangladesh on 16 December (Wires)",
    "31 Americas: Mexico will try alleged drug lord 'El Chapo Isidro' in Mexico despite a US extradition request (Reuters)",
    "32 Americas: A car bomb hits the governor's office in Villavicencio, Colombia (Wires)",
    "33 Americas: The United States loses its measles elimination status after more than 25 years; Pennsylvania records a ninth death (Wires)",
    "34 World: Wars threaten food aid for another 7.3 million people, agencies warn (Wires)",
    "35 Science: Astronomers find the most distant glowing black hole yet — a quasar formed within 630 million years of the Big Bang (Wires)",
    "36 Sport: PGL Major Singapore opens — Wildcard stun FaZe 13–9, FlyQuest beat Eternal Fire 13–7, NIP beat M80 13–10 (HLTV)",
]

DATE_CHECK = ("Left out as other days' news: Nvidia's reinstatement announcement and Monday's "
              "+31.5% close (Mon 23 Nov — Tuesday's story is the HQ welcome and the fallout) · "
              "the Merkury sinking itself and Zelensky's claim of it (Sun/Mon — Tuesday's is the "
              "UN probe call and Libya's reaction) · COP31's collapse (the weekend) · the missiles "
              "that fell in Poland (last week — Tuesday's is the drone incursion and NATO's "
              "deployment) · the Cikande fire itself (Sun — Tuesday's is the toll at 26). Dated "
              "where it appears: the IRGC mine claim (the incidents are dated Monday in Tehran's "
              "own statement; unconfirmed by CENTCOM).")

SOURCES = ("Sources: Reuters, The Times, Le Monde, CNN, WSJ, Kyiv Independent, UNSMIL, JMIC, "
           "wires. Pictures and map: original, drawn in code.")
CERTAINTY = "CERTAINTY — REPORTED = carried by the day's wires · CLAIM = one side's account, labelled as such"

# story number -> (lon, lat) for map pins
PINS = {
    1: (-122, 37), 2: (20, 32), 3: (56, 26), 4: (35, 48), 5: (116, 40),
    6: (44, 33), 7: (34, 31), 8: (106, -6), 9: (13, 52), 10: (37, 56),
    11: (21, 52), 12: (-93, 42), 13: (-121, 44), 14: (90, 24), 15: (45, 13),
}


# ---------------------------------------------------------------- scenes
# Each scene paints a small flat vector illustration into box (0,0,w,h)
# of its own image; the caller pastes it and overlays the red label.

SKY = (188, 206, 226)
SEA = (84, 128, 168)
SANDC = (226, 205, 160)


def _person(d, x, y, s, col):
    d.ellipse([x - s * 0.32, y - s, x + s * 0.32, y - s * 0.36], fill=col)
    d.line([x, y - s * 0.3, x, y + s * 0.5], fill=col, width=max(2, int(s * 0.16)))
    d.line([x, y, x - s * 0.45, y + s * 0.28], fill=col, width=max(2, int(s * 0.13)))
    d.line([x, y, x + s * 0.45, y + s * 0.28], fill=col, width=max(2, int(s * 0.13)))


def _flame(d, x, y, s, col=(232, 110, 30)):
    d.polygon([(x, y), (x - s * 0.42, y + s * 0.8), (x - s * 0.12, y + s * 0.62),
               (x - s * 0.2, y + s * 1.05), (x + s * 0.2, y + s * 1.05),
               (x + s * 0.12, y + s * 0.62), (x + s * 0.42, y + s * 0.8)], fill=col)
    d.polygon([(x, y + s * 0.34), (x - s * 0.18, y + s * 0.82), (x + s * 0.18, y + s * 0.82)],
              fill=(246, 178, 60))


def _burst(d, x, y, s, col=(230, 90, 30)):
    import math
    pts = []
    for i in range(16):
        r = s if i % 2 == 0 else s * 0.42
        a = math.pi * i / 8
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    d.polygon(pts, fill=col)


def sc_nvidia(d, w, h):
    d.rectangle([0, 0, w, h], fill=(30, 44, 38))
    d.rectangle([w * 0.30, h * 0.10, w * 0.72, h * 0.78], fill=(118, 184, 60))
    d.rectangle([w * 0.34, h * 0.16, w * 0.68, h * 0.72], fill=(24, 30, 26))
    d.polygon([(w * 0.51, h * 0.24), (w * 0.63, h * 0.60), (w * 0.39, h * 0.60)],
              outline=(160, 230, 90), width=3)
    d.ellipse([w * 0.465, h * 0.40, w * 0.555, h * 0.52], outline=(160, 230, 90), width=3)
    for i, fx in enumerate((0.08, 0.18, 0.82, 0.90)):
        _person(d, w * fx, h * 0.66, h * 0.20, (240, 235, 210))
    d.rectangle([0, h * 0.80, w, h], fill=(52, 66, 50))


def sc_libya(d, w, h):
    d.rectangle([0, 0, w, h * 0.58], fill=SKY)
    d.rectangle([0, h * 0.58, w, h], fill=SEA)
    d.rectangle([w * 0.04, h * 0.30, w * 0.30, h * 0.58], fill=(150, 140, 120))
    d.line([w * 0.10, h * 0.30, w * 0.10, h * 0.08], fill=INK, width=3)
    d.line([w * 0.10, h * 0.10, w * 0.26, h * 0.10], fill=INK, width=3)
    d.polygon([(w * 0.42, h * 0.62), (w * 0.72, h * 0.62), (w * 0.68, h * 0.74),
               (w * 0.46, h * 0.74)], fill=(90, 96, 104))
    d.rectangle([w * 0.52, h * 0.52, w * 0.62, h * 0.62], fill=(70, 76, 84))
    d.polygon([(w * 0.78, h * 0.66), (w * 0.97, h * 0.60), (w * 0.96, h * 0.78),
               (w * 0.80, h * 0.80)], fill=(120, 60, 50))
    d.line([w * 0.80, h * 0.64, w * 0.95, h * 0.76], fill=(60, 40, 36), width=3)
    dx, dy = w * 0.82, h * 0.16
    d.polygon([(dx, dy), (dx + w * 0.09, dy + h * 0.05), (dx, dy + h * 0.10),
               (dx - w * 0.09, dy + h * 0.05)], fill=(40, 42, 48))
    _burst(d, w * 0.60, h * 0.44, h * 0.13, (240, 160, 60))


def sc_hormuz(d, w, h):
    d.rectangle([0, 0, w, h * 0.34], fill=(214, 196, 168))
    d.rectangle([0, h * 0.34, w, h], fill=SEA)
    for i, fx in enumerate((0.16, 0.48, 0.80)):
        y0 = h * (0.44 + 0.10 * (i % 2))
        d.polygon([(w * fx - w * 0.11, y0), (w * fx + w * 0.11, y0),
                   (w * fx + w * 0.08, y0 + h * 0.13), (w * fx - w * 0.08, y0 + h * 0.13)],
                  fill=(52, 54, 60))
        d.rectangle([w * fx - w * 0.07, y0 - h * 0.09, w * fx + w * 0.07, y0], fill=(96, 100, 108))
        _flame(d, w * fx, y0 - h * 0.26, h * 0.15)
    for fx in (0.32, 0.64):
        cx, cy = w * fx, h * 0.86
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(30, 30, 34))
        for a in range(0, 360, 45):
            import math
            d.line([cx, cy, cx + 10 * math.cos(math.radians(a)), cy + 10 * math.sin(math.radians(a))],
                   fill=(30, 30, 34), width=2)


def sc_zaporizhzhia(d, w, h):
    d.rectangle([0, 0, w, h], fill=(196, 190, 178))
    for i, fx in enumerate((0.06, 0.30, 0.62, 0.84)):
        bw, bh = w * 0.17, h * (0.52 + 0.10 * (i % 2))
        d.rectangle([w * fx, h - bh, w * fx + bw, h], fill=(110, 104, 96))
        for r in range(3):
            for c in range(2):
                d.rectangle([w * fx + 4 + c * w * 0.07, h - bh + 5 + r * h * 0.15,
                             w * fx + 9 + c * w * 0.07, h - bh + 11 + r * h * 0.15],
                            fill=(240, 220, 150))
    _burst(d, w * 0.55, h * 0.30, h * 0.20)
    d.ellipse([w * 0.50, h * 0.02, w * 0.72, h * 0.22], fill=(90, 86, 80))


def sc_beijing(d, w, h):
    d.rectangle([0, 0, w, h], fill=(206, 196, 178))
    d.rectangle([w * 0.16, h * 0.30, w * 0.72, h * 0.86], fill=(168, 44, 40))
    d.rectangle([w * 0.12, h * 0.22, w * 0.76, h * 0.32], fill=(120, 30, 28))
    for i in range(5):
        x = w * (0.22 + i * 0.12)
        d.rectangle([x, h * 0.36, x + w * 0.045, h * 0.82], fill=(238, 228, 205))
    d.ellipse([w * 0.60, h * 0.34, w * 0.94, h * 0.86], outline=INK, width=4)
    d.line([w * 0.90, h * 0.78, w * 1.0, h * 0.98], fill=INK, width=5)


def sc_baghdad(d, w, h):
    d.rectangle([0, 0, w, h], fill=(232, 208, 156))
    d.ellipse([w * 0.78, h * 0.06, w * 0.94, h * 0.34], fill=(244, 190, 80))
    d.polygon([(w * 0.10, h * 0.86), (w * 0.20, h * 0.30), (w * 0.30, h * 0.86)], outline=INK, width=3)
    d.line([w * 0.13, h * 0.62, w * 0.28, h * 0.62], fill=INK, width=2)
    d.line([w * 0.16, h * 0.44, w * 0.25, h * 0.44], fill=INK, width=2)
    d.polygon([(w * 0.48, h * 0.52), (w * 0.80, h * 0.40), (w * 0.84, h * 0.50),
               (w * 0.54, h * 0.60)], fill=(60, 58, 54))
    d.line([w * 0.52, h * 0.58, w * 0.60, h * 0.86], fill=(60, 58, 54), width=4)
    d.line([w * 0.80, h * 0.47, w * 0.82, h * 0.86], fill=(60, 58, 54), width=4)
    d.rectangle([0, h * 0.86, w, h], fill=(196, 164, 110))


def sc_gaza(d, w, h):
    d.rectangle([0, 0, w, h], fill=(200, 192, 180))
    for i, fx in enumerate((0.04, 0.30, 0.55, 0.78)):
        bh = h * (0.44 + 0.12 * ((i + 1) % 3) / 2)
        d.rectangle([w * fx, h - bh, w * fx + w * 0.19, h], fill=(122, 114, 104))
    for fx in (0.36, 0.66):
        d.ellipse([w * fx, h * 0.04, w * fx + w * 0.17, h * 0.30], fill=(88, 84, 78))
        d.rectangle([w * fx + w * 0.05, h * 0.24, w * fx + w * 0.12, h * 0.52], fill=(96, 92, 86))
    d.line([w * 0.06, h * 0.10, w * 0.30, h * 0.42], fill=(200, 60, 40), width=3)
    d.line([w * 0.16, h * 0.06, w * 0.38, h * 0.40], fill=(200, 60, 40), width=3)


def sc_cikande(d, w, h):
    d.rectangle([0, 0, w, h], fill=(216, 200, 184))
    d.rectangle([w * 0.10, h * 0.44, w * 0.78, h * 0.90], fill=(140, 132, 120))
    d.rectangle([w * 0.16, h * 0.22, w * 0.24, h * 0.44], fill=(110, 102, 92))
    d.rectangle([w * 0.62, h * 0.18, w * 0.70, h * 0.44], fill=(110, 102, 92))
    _flame(d, w * 0.30, h * 0.16, h * 0.30)
    _flame(d, w * 0.52, h * 0.24, h * 0.24)
    _flame(d, w * 0.70, h * 0.30, h * 0.18)
    d.ellipse([w * 0.24, h * 0.0, w * 0.52, h * 0.16], fill=(80, 76, 70))


def sc_berlin(d, w, h):
    d.rectangle([0, 0, w, h], fill=(36, 48, 60))
    d.rectangle([w * 0.08, h * 0.10, w * 0.66, h * 0.84], outline=(110, 200, 160), width=3)
    for i in range(1, 4):
        d.line([w * 0.08 + i * w * 0.145, h * 0.10, w * 0.08 + i * w * 0.145, h * 0.84],
               fill=(70, 110, 96), width=1)
        d.line([w * 0.08, h * 0.10 + i * h * 0.185, w * 0.66, h * 0.10 + i * h * 0.185],
               fill=(70, 110, 96), width=1)
    pts = [(0.16, 0.66), (0.30, 0.48), (0.44, 0.54), (0.58, 0.30)]
    for i in range(len(pts) - 1):
        d.line([w * pts[i][0], h * pts[i][1], w * pts[i + 1][0], h * pts[i + 1][1]],
               fill=(240, 210, 90), width=3)
    for px, py in pts:
        d.ellipse([w * px - 4, h * py - 4, w * px + 4, h * py + 4], fill=(240, 90, 80))
    d.polygon([(w * 0.84, h * 0.16), (w * 0.94, h * 0.22), (w * 0.94, h * 0.48),
               (w * 0.84, h * 0.60), (w * 0.74, h * 0.48), (w * 0.74, h * 0.22)],
              outline=(240, 235, 210), width=3)


def sc_nuclear(d, w, h):
    d.rectangle([0, 0, w, h], fill=(52, 50, 58))
    cx, cy, r = w * 0.34, h * 0.52, h * 0.30
    import math
    for a0 in (-90, 30, 150):
        pts = [(cx, cy)]
        for a in range(a0 - 28, a0 + 29, 7):
            pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
        d.polygon(pts, fill=(244, 196, 40))
    d.ellipse([cx - r * 0.20, cy - r * 0.20, cx + r * 0.20, cy + r * 0.20], fill=(244, 196, 40))
    sx, sy = w * 0.78, h * 0.30
    d.rectangle([sx - w * 0.10, sy - h * 0.07, sx + w * 0.10, sy + h * 0.07], fill=(170, 176, 186))
    d.polygon([(sx - w * 0.10, sy), (sx - w * 0.20, sy - h * 0.13), (sx - w * 0.10, sy + h * 0.02)],
              fill=(140, 146, 158))
    d.polygon([(sx + w * 0.10, sy), (sx + w * 0.20, sy - h * 0.13), (sx + w * 0.10, sy + h * 0.02)],
              fill=(140, 146, 158))


def sc_warsaw(d, w, h):
    d.rectangle([0, 0, w, h], fill=SKY)
    for r in (0.16, 0.30, 0.44):
        d.arc([w * 0.06, h * 0.98 - 2 * r * h * 0.9, w * 0.06 + 2 * r * w, h * 0.98],
              start=270, end=350, fill=(60, 90, 140), width=3)
    dx, dy = w * 0.58, h * 0.34
    d.rectangle([dx - w * 0.09, dy - h * 0.07, dx + w * 0.09, dy + h * 0.07], fill=(38, 40, 46))
    for ox, oy in ((-0.13, -0.13), (0.13, -0.13), (-0.13, 0.13), (0.13, 0.13)):
        ex, ey = dx + w * ox, dy + h * oy
        d.ellipse([ex - w * 0.055, ey - h * 0.045, ex + w * 0.055, ey + h * 0.045],
                  outline=(38, 40, 46), width=3)
        d.line([dx, dy, ex, ey], fill=(38, 40, 46), width=2)
    d.rectangle([0, h * 0.90, w, h], fill=(120, 140, 110))


def sc_iowa(d, w, h):
    d.rectangle([0, 0, w, h], fill=(206, 198, 182))
    _burst(d, w * 0.34, h * 0.52, h * 0.34)
    _burst(d, w * 0.34, h * 0.52, h * 0.18, (246, 178, 60))
    d.rectangle([w * 0.62, h * 0.16, w * 0.94, h * 0.30], fill=(120, 84, 50))
    d.polygon([(w * 0.60, h * 0.30), (w * 0.68, h * 0.30), (w * 0.76, h * 0.52),
               (w * 0.68, h * 0.52)], fill=(150, 108, 64))
    d.rectangle([w * 0.60, h * 0.78, w * 0.96, h * 0.88], fill=(120, 84, 50))


def sc_grok(d, w, h):
    d.rectangle([0, 0, w, h], fill=(196, 204, 216))
    d.rounded_rectangle([w * 0.10, h * 0.08, w * 0.36, h * 0.92], radius=8,
                        fill=(30, 32, 38))
    d.rectangle([w * 0.14, h * 0.16, w * 0.32, h * 0.78], fill=(120, 160, 200))
    d.text((w * 0.175, h * 0.36), "X", font=F(SANSB, int(h * 0.30)), fill=(240, 244, 248))
    cx = w * 0.68
    d.line([cx, h * 0.14, cx, h * 0.66], fill=INK, width=4)
    d.line([cx - w * 0.17, h * 0.22, cx + w * 0.17, h * 0.22], fill=INK, width=4)
    for sgn in (-1, 1):
        px = cx + sgn * w * 0.17
        d.line([px, h * 0.22, px - w * 0.07, h * 0.48], fill=INK, width=2)
        d.line([px, h * 0.22, px + w * 0.07, h * 0.48], fill=INK, width=2)
        d.arc([px - w * 0.075, h * 0.40, px + w * 0.075, h * 0.58], start=0, end=180,
              fill=INK, width=3)
    d.rectangle([cx - w * 0.10, h * 0.68, cx + w * 0.10, h * 0.76], fill=INK)


def sc_gazipur(d, w, h):
    d.rectangle([0, 0, w, h], fill=(208, 200, 188))
    d.rectangle([w * 0.55, h * 0.16, w * 0.96, h * 0.80], fill=(146, 138, 126))
    for r in range(3):
        for c in range(3):
            d.rectangle([w * (0.59 + c * 0.11), h * (0.24 + r * 0.17),
                         w * (0.65 + c * 0.11), h * (0.34 + r * 0.17)], fill=(238, 226, 170))
    for i in range(6):
        _person(d, w * (0.08 + i * 0.075), h * 0.60, h * 0.17, (60, 56, 50))
    d.ellipse([w * 0.28, h * 0.30, w * 0.55, h * 0.55], fill=(228, 228, 224))


def sc_lahj(d, w, h):
    d.rectangle([0, 0, w, h], fill=(228, 210, 168))
    d.rectangle([0, h * 0.72, w, h], fill=(196, 172, 128))
    d.rectangle([w * 0.06, h * 0.40, w * 0.44, h * 0.70], fill=(70, 110, 160))
    d.rectangle([w * 0.10, h * 0.46, w * 0.20, h * 0.58], fill=(210, 228, 240))
    d.rectangle([w * 0.24, h * 0.46, w * 0.34, h * 0.58], fill=(210, 228, 240))
    d.rectangle([w * 0.54, h * 0.44, w * 0.82, h * 0.70], fill=(150, 90, 60))
    d.rectangle([w * 0.82, h * 0.52, w * 0.94, h * 0.70], fill=(110, 100, 92))
    for fx in (0.14, 0.36, 0.62, 0.88):
        d.ellipse([w * fx - 6, h * 0.68, w * fx + 6, h * 0.68 + 12], fill=(30, 30, 32))
    _burst(d, w * 0.50, h * 0.22, h * 0.16, (220, 80, 40))


SCENES = {
    "nvidia": sc_nvidia, "libya": sc_libya, "hormuz": sc_hormuz,
    "zaporizhzhia": sc_zaporizhzhia, "beijing": sc_beijing, "baghdad": sc_baghdad,
    "gaza": sc_gaza, "cikande": sc_cikande, "berlin": sc_berlin,
    "nuclear": sc_nuclear, "warsaw": sc_warsaw, "iowa": sc_iowa,
    "grok": sc_grok, "gazipur": sc_gazipur, "lahj": sc_lahj,
}


def scene_image(key, w, h):
    img = Image.new("RGB", (w, h), SKY)
    SCENES[key](ImageDraw.Draw(img), w, h)
    return img


# ---------------------------------------------------------------- map

LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-80, 73),
     (-75, 62), (-65, 60), (-55, 52), (-65, 45), (-70, 42), (-75, 38), (-76, 35),
     (-80, 32), (-80, 26), (-84, 22), (-90, 20), (-97, 16), (-105, 20), (-110, 24),
     (-114, 29), (-120, 34), (-124, 40), (-124, 47), (-130, 55), (-150, 60), (-165, 60)],
    [(-105, 20), (-97, 16), (-90, 14), (-86, 13), (-83, 9), (-79, 9), (-80, 7),
     (-86, 12), (-95, 16), (-102, 18)],
    [(-79, 9), (-75, 11), (-71, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -22), (-48, -27), (-52, -33), (-58, -39),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -46),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-81, -4),
     (-80, 1), (-77, 4)],
    [(-10, 37), (-9, 44), (-1, 46), (-4, 48), (1, 50), (5, 53), (8, 54), (8, 57),
     (10, 59), (5, 60), (5, 62), (10, 64), (18, 69), (25, 71), (31, 70), (35, 68),
     (40, 66), (45, 68), (50, 69), (45, 64), (40, 60), (35, 55), (40, 52), (48, 50),
     (40, 46), (35, 45), (30, 46), (28, 41), (23, 40), (23, 36), (19, 40), (15, 38),
     (12, 42), (7, 44), (3, 43), (-2, 37)],
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (35, 28),
     (38, 22), (43, 12), (51, 12), (50, 15), (44, 11), (40, -5), (40, -15),
     (38, -20), (35, -24), (32, -29), (28, -33), (20, -35), (17, -32), (15, -27),
     (13, -18), (12, -10), (9, -5), (9, 0), (6, 4), (-3, 5), (-8, 5), (-13, 8),
     (-17, 12), (-17, 15), (-16, 20), (-15, 25), (-13, 28), (-9, 31)],
    [(28, 41), (30, 46), (35, 50), (40, 52), (48, 50), (55, 51), (65, 50), (75, 52),
     (85, 50), (95, 50), (105, 50), (110, 52), (120, 53), (127, 50), (135, 48),
     (140, 48), (142, 45), (140, 40), (135, 35), (130, 33), (127, 40), (122, 38),
     (120, 32), (122, 30), (120, 25), (115, 23), (108, 20), (105, 15), (103, 8),
     (100, 8), (98, 12), (95, 16), (92, 16), (90, 22), (88, 22), (86, 20),
     (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25), (61, 25),
     (57, 26), (52, 26), (50, 29), (48, 30), (43, 35), (39, 36), (33, 36), (30, 36)],
    [(35, 28), (38, 22), (43, 12), (45, 12), (50, 15), (52, 24), (55, 24),
     (57, 26), (52, 26), (50, 29), (48, 30), (43, 35), (39, 36), (36, 36)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -36), (140, -38), (145, -38), (147, -38),
     (150, -37), (153, -32), (153, -27), (151, -24), (146, -19), (142, -15),
     (142, -11), (140, -17), (136, -15), (135, -12), (132, -11), (130, -12),
     (126, -14), (122, -17), (118, -20)],
]
ISLANDS = [  # (lon, lat, radius in degrees)
    (-2, 53, 3.2), (-19, 65, 3.0), (138, 37, 5.0), (122, 13, 4.0), (95, 4, 4.0),
    (102, -1, 6.0), (110, -1, 5.0), (119, -2, 5.0), (131, -3, 5.0), (47, -19, 4.0),
    (172, -42, 3.4), (79, 21, 2.6), (121, 24, 2.2),
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def is_land(lon, lat):
    if any(_in_poly(lon, lat, p) for p in LAND):
        return True
    return any((lon - lo) ** 2 + (lat - la) ** 2 <= r * r for lo, la, r in ISLANDS)


def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 231, 210), outline=RULE)
    lon0, lon1, lat0, lat1 = -170, 190, 78, -58

    def px(lon):
        return x0 + (lon - lon0) / (lon1 - lon0) * w

    def py(lat):
        return y0 + (lat0 - lat) / (lat0 - lat1) * h

    step = 5
    gy = y0 + 3
    while gy < y0 + h - 2:
        gx = x0 + 3
        while gx < x0 + w - 2:
            lon = lon0 + (gx - x0) / w * (lon1 - lon0)
            lat = lat0 - (gy - y0) / h * (lat0 - lat1)
            if is_land(lon, lat):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(146, 132, 102))
            gx += step
        gy += step
    pf = F(SANSB, 8)
    offsets = {9: (-4, 3), 11: (4, 2), 10: (4, 3), 4: (-3, -2), 2: (-3, -3),
               7: (2, -4), 6: (3, -1)}
    for num, (lon, lat) in PINS.items():
        olon, olat = offsets.get(num, (0, 0))
        cx, cy = px(lon + olon), py(lat + olat)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=CHIP, width=1)
        t = str(num)
        tw = d.textlength(t, font=pf)
        d.text((cx - tw / 2, cy - 5), t, font=pf, fill=(255, 255, 255))


# ---------------------------------------------------------------- layout

def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # top strip
    d.rectangle([0, 0, W, 20], fill=INK)
    d.text((MARGIN, 4), TOP_LEFT, font=F(SANSB, 10), fill=CREAM)
    tw = d.textlength(TOP_RIGHT, font=F(SANS, 9))
    d.text((W - MARGIN - tw, 5), TOP_RIGHT, font=F(SANS, 9), fill=CREAM)

    # masthead
    centered(d, 25, MASTHEAD, F(SERIFB, 36), INK)
    d.line([MARGIN, 66, W - MARGIN, 66], fill=INK, width=2)
    d.line([MARGIN, 69, W - MARGIN, 69], fill=INK, width=1)

    # standfirst
    sf = F(SERIFI, 13)
    lines = wrap(d, STANDFIRST, sf, CW - 30)
    y = 73
    for ln in lines:
        w_ = d.textlength(ln, font=sf)
        d.text(((W - w_) / 2, y), ln, font=sf, fill=RED)
        y += 14

    # numbers strip
    ny = 103
    d.line([MARGIN, ny, W - MARGIN, ny], fill=RULE, width=1)
    cellw = CW / 6
    nf, cf = F(SERIFB, 15), F(SANS, 8)
    for i, (num, cap) in enumerate(NUMBERS):
        x = MARGIN + i * cellw
        if i:
            d.line([x, ny + 3, x, ny + 31], fill=RULE, width=1)
        d.text((x + 7, ny + 3), num, font=nf, fill=DARKRED)
        text_block(d, (x + 7, ny + 20), cap, cf, SOFT, cellw - 12, 8.5, max_lines=2)
    d.line([MARGIN, ny + 36, W - MARGIN, ny + 36], fill=RULE, width=1)

    # region bar + UTC strip
    centered(d, 143, REGION_BAR, F(SANSB, 10), INK)
    centered(d, 160, " · ".join(UTC_ANCHORS), F(SANS, 8), SOFT)
    d.line([MARGIN, 176, W - MARGIN, 176], fill=RULE, width=1)

    # leads
    ly, lh_ = 179, 240
    leadw = (CW - 24) / 3
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (leadw + 12)
        d.rectangle([x, ly, x + leadw, ly + lh_], fill=CARDBG, outline=RULE)
        img_area = scene_image(lead["scene"], int(leadw), 76)
        img.paste(img_area, (int(x), ly))
        d.rectangle([x, ly + 56, x + leadw, ly + 76], fill=INK)
        d.text((x + 8, ly + 60), lead["img_title"], font=F(SANSB, 11), fill=CREAM)
        sub = lead["img_sub"]
        sw = d.textlength(sub, font=F(SANSB, 10))
        d.text((x + leadw - 8 - sw, ly + 61), sub, font=F(SANSB, 10), fill=(255, 170, 150))
        d.text((x + 8, ly + 80), lead["kicker"], font=F(SANSB, 8), fill=SOFT)
        hy = text_block(d, (x + 8, ly + 91), lead["headline"], F(SERIFB, 13), INK,
                        leadw - 16, 15, max_lines=3)
        text_block(d, (x + 8, hy + 2), lead["body"], F(SANS, 9), (40, 37, 31),
                   leadw - 16, 10)

    # story cards 4-15
    cy = 425
    cardw = (CW - 24) / 4
    cardh = 84
    bf, pf, tf = F(SANS, 8), F(SANSB, 8), F(SANSB, 8)
    for r in range(3):
        for c in range(4):
            scene, num, place, lab1, lab2, body = CARDS[r * 4 + c]
            x = MARGIN + c * (cardw + 8)
            y = cy + r * (cardh + 2)
            d.rectangle([x, y, x + cardw, y + cardh], fill=CARDBG, outline=RULE)
            img.paste(scene_image(scene, int(cardw), 24), (int(x), y))
            labw = max(d.textlength(lab1, font=tf), d.textlength(lab2, font=tf)) + 10
            d.rectangle([x, y, x + labw, y + 24], fill=CHIP)
            d.text((x + 5, y + 2), lab1, font=tf, fill=RED)
            d.text((x + 5, y + 12), lab2, font=tf, fill=RED)
            d.text((x + 5, y + 26), f"{num} · {place}", font=F(SANSB, 8), fill=INK)
            text_block(d, (x + 5, y + 37), body, bf, (40, 37, 31), cardw - 10, 9.0,
                       max_lines=5)

    # briefs 16-36
    by = 687
    d.text((MARGIN, by), "ALSO ON TUESDAY — 21 MORE STORIES", font=F(SANSB, 10), fill=RED)
    d.line([MARGIN, by + 14, W - MARGIN, by + 14], fill=RULE, width=1)
    brf = F(SANS, 8)
    colw = (CW - 12) / 2
    yy = by + 18
    for i in range(0, len(BRIEFS), 2):
        heights = []
        for j, item in enumerate(BRIEFS[i:i + 2]):
            x = MARGIN + j * (colw + 12)
            endy = text_block(d, (x, yy), item, brf, (40, 37, 31), colw, 9.6)
            heights.append(endy - yy)
        yy += max(heights) + 1

    # map + date check band
    my = 898
    d.text((MARGIN, my), "WHERE IT HAPPENED — pins match story numbers",
           font=F(SANSB, 9), fill=INK)
    draw_map(d, MARGIN, my + 13, 540, 72)
    dx = MARGIN + 552
    dw = W - MARGIN - dx
    d.rectangle([dx, my, W - MARGIN, my + 85], fill=(250, 240, 224), outline=RED, width=2)
    d.text((dx + 8, my + 5), "DATE CHECK — WHAT WE LEFT OUT, AND WHY", font=F(SANSB, 9),
           fill=RED)
    text_block(d, (dx + 8, my + 18), DATE_CHECK, F(SANS, 8), (52, 40, 34), dw - 16, 9.4)

    # sources + certainty
    d.text((MARGIN, 989), SOURCES, font=F(SANS, 8), fill=SOFT)
    d.text((MARGIN, 1000), CERTAINTY, font=F(SANSB, 8), fill=SOFT)

    # bottom strip
    d.rectangle([0, 1012, W, H], fill=INK)
    d.text((MARGIN, 1015), "THE WORLD IN ONE DAY", font=F(SANSB, 9), fill=CREAM)
    tail = "TUESDAY 24 NOVEMBER 2026 · ONE PAGE"
    tw = d.textlength(tail, font=F(SANS, 9))
    d.text((W - MARGIN - tw, 1015), tail, font=F(SANS, 9), fill=CREAM)
    return img


if __name__ == "__main__":
    render().save("entry.png")
    print("wrote entry.png")
