import html, os
OUT = "assets"
BG1, BG2 = "#16050A", "#2A0C16"
BURG, BURG2 = "#7A1630", "#A8284F"
GOLD, GOLD2 = "#D4AF7A", "#F0D9B0"
CYAN = GOLD            # accent (kept name so the rest of the script reads the same)
WHITE, GRAY, LINE = "#F8EDE3", "#C2A5A2", "#4A1A28"
CHIP = "#33101C"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Fira Code', 'SFMono-Regular', Consolas, monospace"
e = html.escape

def wrap(w, h, body, rx=18, delay=0, sweep=True):
    clip = f'<clipPath id="c"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
    shimmer = ""
    if sweep:
        shimmer = (f'<rect x="-300" y="-20" width="150" height="{h+40}" fill="url(#sh)" transform="skewX(-20)">'
                   f'<animate attributeName="x" values="-300;{w+300};{w+300}" keyTimes="0;0.55;1" dur="11s" begin="{delay}s" repeatCount="indefinite"/></rect>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<defs>{clip}'
            f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>'
            f'<linearGradient id="a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BURG}"/><stop offset=".6" stop-color="{BURG2}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
            f'<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD2}" stop-opacity="0"/><stop offset=".5" stop-color="{GOLD2}" stop-opacity=".12"/><stop offset="1" stop-color="{GOLD2}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="r" cx="1" cy="0" r="1"><stop offset="0" stop-color="{BURG2}" stop-opacity=".35"/><stop offset="1" stop-color="{BURG}" stop-opacity="0"/></radialGradient>'
            f'</defs>'
            f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#g)"/>'
            f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#r)"/>'
            f'<g clip-path="url(#c)">{shimmer}<rect width="{w}" height="3" fill="url(#a)"/></g>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="none" stroke="{LINE}" stroke-width="2"/>'
            f'{body}</svg>')

def pulse(x, y, i, size=8, rx=2):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}" fill="{GOLD}">'
            f'<animate attributeName="opacity" values="1;.3;1" dur="3.2s" begin="{(i*0.3)%3:.1f}s" repeatCount="indefinite"/></rect>')

def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f: f.write(svg)

def text(x, y, s, size=15, fill=WHITE, weight=400, font=FONT, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{e(s)}</text>'

def chips(x, y, items, maxw, size=13):
    out, cx, cy = [], x, y
    for it in items:
        w = int(len(it) * size * 0.62 + 24)
        if cx + w > x + maxw:
            cx, cy = x, cy + 36
        out.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="28" rx="14" fill="{CHIP}" stroke="{GOLD}" stroke-opacity=".5"/>')
        out.append(text(cx + w/2, cy + 19, it, size, WHITE, 500, MONO, "middle"))
        cx += w + 10
    return "".join(out), cy + 28

# ---------- hero ----------
phrases = ["Building things with code", "Exploring AI & Data Science", "Turning ideas into real applications", "Always learning, always building"]
anim = ""
for i, p in enumerate(phrases):
    a, b = i/4, (i+1)/4
    kt = f"0;{a};{min(a+0.02,1)};{max(b-0.02,0)};{b};1"
    anim += (f'<text x="60" y="250" font-family="{MONO}" font-size="22" fill="{GOLD}" opacity="0">{e(p)}'
             f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="12s" repeatCount="indefinite"/></text>')
orbs = (f'<circle cx="790" cy="90" r="80" fill="{BURG2}" opacity=".18"><animate attributeName="cy" values="90;120;90" dur="7s" repeatCount="indefinite"/></circle>'
        f'<circle cx="850" cy="240" r="120" fill="{BURG}" opacity=".25"><animate attributeName="cy" values="240;210;240" dur="9s" repeatCount="indefinite"/></circle>'
        f'<circle cx="700" cy="250" r="40" fill="none" stroke="{GOLD}" stroke-opacity=".35" stroke-width="2"><animate attributeName="r" values="40;55;40" dur="5s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".35;.05;.35" dur="5s" repeatCount="indefinite"/></circle>')
hero = (orbs
        + text(60, 100, "HI, I'M", 16, GOLD, 700, MONO, extra='letter-spacing="4"')
        + text(60, 175, "Berwin CR", 72, WHITE, 800)
        + text(60, 214, "B.Tech IT @ CEG  ·  Software Developer  ·  AI/ML Enthusiast", 17, GRAY)
        + anim
        + f'<rect x="60" y="270" width="120" height="4" rx="2" fill="url(#a)"><animate attributeName="width" values="120;260;120" dur="6s" repeatCount="indefinite"/></rect>')
save("hero.svg", wrap(900, 310, hero, 24))

# ---------- section titles ----------
def title(fn, num, name, sub):
    b = (text(28, 60, num, 44, GOLD, 800, MONO)
         + text(110, 44, name, 28, WHITE, 800)
         + text(110, 68, sub, 14, GRAY)
         + f'<rect x="110" y="78" width="740" height="2" fill="{GOLD}" opacity=".2"/>'
         + f'<rect x="110" y="78" width="70" height="2" fill="url(#a)"><animate attributeName="x" values="110;780;110" dur="6s" repeatCount="indefinite"/></rect>')
    save(fn, wrap(900, 96, b, 16, sweep=False))
title("title-about.svg", "01", "About", "Who I am and what I'm into.")
title("title-work.svg", "02", "Featured work", "Products, not assignments.")
title("title-other.svg", "03", "Other projects", "Smaller builds and practice.")
title("title-toolkit.svg", "04", "Toolkit", "The tools I reach for.")
title("title-practice.svg", "05", "Problem solving", "Sharpening fundamentals daily.")
title("title-commits.svg", "06", "Commit log", "Building in public.")
title("title-goals.svg", "07", "Working towards", "Where I'm headed.")
title("title-connect.svg", "08", "Connect", "Let's build something worth explaining.")

# ---------- about card ----------
rows = ["B.Tech Information Technology at College of Engineering Guindy (CEG), Anna University.",
        "Interested in full-stack development and software engineering.",
        "Exploring artificial intelligence, machine learning and data science.",
        "Building projects to strengthen programming and problem-solving skills.",
        "I like turning ideas into practical applications and learning by building."]
b = text(36, 46, "ABOUT ME", 14, CYAN, 700, MONO, extra='letter-spacing="3"')
for i, r in enumerate(rows):
    y = 86 + i*34
    b += pulse(38, y-9, i, 8, 4) + text(60, y, r, 16, WHITE)
save("about.svg", wrap(900, 86+len(rows)*34+10, b))

# ---------- project cards ----------
def project(fn, emoji_free_title, tagline, highlights, stacks):
    h = text(36, 56, emoji_free_title, 28, WHITE, 800)
    y = 84
    for ln in tagline:
        h += text(36, y, ln, 15, GRAY); y += 22
    y += 14
    h += text(36, y, "HIGHLIGHTS", 12, CYAN, 700, MONO, extra='letter-spacing="3"'); y += 26
    half = (len(highlights)+1)//2
    for i, t in enumerate(highlights):
        col, row = divmod(i, half)
        x = 36 + col*420
        yy = y + row*28
        h += pulse(x, yy-10, i) + text(x+20, yy, t, 14.5, WHITE)
    y += half*28 + 16
    for label, items in stacks:
        h += text(36, y+16, label.upper(), 11, GRAY, 700, MONO, extra='letter-spacing="2"')
        c, ny = chips(36, y+26, items, 828)
        h += c; y = ny + 14
    save(fn, wrap(900, y + 14, h))

project("project-mediguide.svg", "MediGuide AI",
        ["AI-powered healthcare education platform that makes", "medicine-related information easier to understand."],
        ["Medicine strip & prescription OCR", "AI-generated medicine explanations", "English & Tamil support", "Voice interaction",
         "Medication reminders", "Drug interaction awareness", "Symptom-based educational guidance"],
        [("Stack", ["React", "Python", "MongoDB Atlas", "Gemini API", "Tesseract OCR", "JWT"])])

project("project-ledger.svg", "Ledger  ·  Personal Finance Manager",
        ["Full-stack finance app for tracking income, expenses", "and spending patterns."],
        ["User registration & JWT auth", "Income & expense tracking", "Transaction categorization", "Search & advanced filtering",
         "Interactive financial reports", "Income vs expense analytics", "Category-wise spending charts", "Responsive dashboard",
         "Pagination & transaction management"],
        [("Frontend", ["React", "Vite", "Tailwind CSS", "Axios", "React Router", "Chart.js"]),
         ("Backend", ["Node.js", "Express.js", "MongoDB Atlas", "Mongoose", "JWT", "bcrypt", "Express Validator"]),
         ("Deployment", ["Vercel", "Render", "MongoDB Atlas"])])

project("project-pharmalens.svg", "PharmaLens  ·  AI Medicine & Pharmacy Agent",
        ["Medicine information and pharmacy discovery agent built on the", "ReAct architecture, with tool use and persistent long-term memory."],
        ["ReAct agent that picks the right tool per request", "Medical info via RxNorm + MedlinePlus", "Pharmacy discovery via Tavily search",
         "Medication reminders with APScheduler", "Persistent long-term memory (JSON)", "LLM > Tool > Observation > Answer loop",
         "Remembers user preferences across sessions"],
        [("Backend", ["Python", "FastAPI"]),
         ("AI & agent", ["OpenRouter", "GPT-5 Nano", "ReAct", "RxNorm", "MedlinePlus", "Tavily", "APScheduler"])])

project("project-showtime.svg", "ShowTime  ·  Movie Ticket Booking",
        ["Web-based booking system: browse movies, pick seats and pay with", "Razorpay test checkout. Two Spring Boot services, each with its own MySQL DB."],
        ["Movie catalogue with title search (TMDB)", "Theatre, date and showtime selection", "Interactive seat map, booked seats blocked",
         "Token-based auth with password hashing", "Bookings, history and cancel unpaid", "Razorpay orders + backend payment verification",
         "Separate show-management service", "Booking confirmation after payment"],
        [("Frontend", ["React", "JavaScript", "Vite", "React Router", "CSS3"]),
         ("Backend", ["Java", "Spring Boot", "REST APIs", "Maven", "MySQL"]),
         ("Integrations", ["TMDB API", "Razorpay (test mode)"])])

# ---------- other projects ----------
others = [("Vidhai  ·  Seed Bank Management", "DBMS project: inventory, ordering, search, relational DB.", "React · Flask · MySQL"),
          ("Campus Event Management", "Department-specific events with student registration.", "Web app"),
          ("Machine Learning Repository", "ML fundamentals implemented and practiced in Python.", "Python"),
          ("LeetCode Solutions", "Data structures and algorithms practice.", "C++"),
          ("Personal Portfolio", "My skills and projects in one place.", "Web")]
b = ""
for i, (t, d, s) in enumerate(others):
    y = 40 + i*74
    b += f'<rect x="28" y="{y-22}" width="4" height="52" rx="2" fill="url(#a)"><animate attributeName="opacity" values="1;.35;1" dur="3.6s" begin="{i*0.5}s" repeatCount="indefinite"/></rect>'
    b += text(48, y, t, 18, WHITE, 700) + text(48, y+24, d, 14, GRAY) + text(864, y, s, 13, CYAN, 500, MONO, "end")
save("other-projects.svg", wrap(900, 40+len(others)*74, b))

# ---------- toolkit ----------
groups = [("Languages", ["C++", "C", "Python", "Java", "JavaScript"]),
          ("Frontend", ["HTML", "CSS", "React", "Tailwind"]),
          ("Backend", ["Node.js", "Express"]),
          ("Databases", ["MySQL", "MongoDB", "PostgreSQL"]),
          ("Cloud & tools", ["GCP", "Git", "GitHub", "VS Code", "Postman"]),
          ("AI / data", ["NumPy", "Pandas", "Scikit-learn", "Matplotlib"])]
b, y = "", 30
for g, items in groups:
    b += text(36, y+19, g.upper(), 12, GRAY, 700, MONO, extra='letter-spacing="2"')
    c, ny = chips(200, y, items, 660)
    b += c; y = ny + 22
save("toolkit.svg", wrap(900, y + 6, b))

# ---------- goals ----------
goals = ["Strong software engineering fundamentals", "Building better full-stack applications",
         "Exploring artificial intelligence & machine learning", "Improving data structures & problem solving",
         "Turning ideas into useful products"]
b = ""
for i, g in enumerate(goals):
    y = 48 + i*40
    b += (f'<text x="36" y="{y}" font-family="{MONO}" font-size="16" font-weight="700" fill="{GOLD}">0{i+1}<animate attributeName="opacity" values="1;.35;1" dur="3.6s" begin="{i*0.5}s" repeatCount="indefinite"/></text>' + text(80, y, g, 18, WHITE, 500))
save("goals.svg", wrap(900, 48+len(goals)*40-10, b))

# ---------- footer ----------
f = (text(450, 62, "Build something worth remembering.", 30, WHITE, 800, anchor="middle")
     + text(450, 94, "Berwin CR  ·  CEG  ·  Software Developer", 15, GRAY, anchor="middle")
     + f'<rect x="390" y="108" width="120" height="4" rx="2" fill="url(#a)"><animate attributeName="x" values="390;330;390" dur="6s" repeatCount="indefinite"/><animate attributeName="width" values="120;240;120" dur="6s" repeatCount="indefinite"/></rect>')
save("footer.svg", wrap(900, 140, f, 24))
print("ok", sorted(os.listdir(OUT)))
