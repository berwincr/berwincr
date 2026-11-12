#!/usr/bin/env python3
"""Generates burgundy-themed GitHub stats, top-languages and activity SVGs.

Full mode (GitHub Actions, needs GH_TOKEN): GraphQL -> commits, PRs, issues, reviews, stars, languages, calendar.
Public mode (no token): REST + public contributions page -> contributions, repos, stars, followers, languages, calendar.
Demo mode (--demo): random sample data, only for checking the layout. Never commit demo output.
"""
import os, sys, json, re, html, random, datetime, urllib.request

USER = next((a for a in sys.argv[1:] if not a.startswith("--")), os.environ.get("PROFILE_USER", "berwincr"))
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = "profile"

BG1, BG2 = "#16050A", "#2A0C16"
BURG, BURG2, GOLD, GOLD2 = "#7A1630", "#A8284F", "#D4AF7A", "#F0D9B0"
WHITE, GRAY, LINE, CHIP = "#F8EDE3", "#C2A5A2", "#4A1A28", "#33101C"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Fira Code', 'SFMono-Regular', Consolas, monospace"
e = html.escape

# ------------------------------------------------------------------ data
def http(url, data=None, headers=None):
    h = {"User-Agent": "profile-cards"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def fetch_graphql():
    q = """query($u:String!){ user(login:$u){ followers{totalCount}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100,orderBy:{field:PUSHED_AT,direction:DESC}){ totalCount
        nodes{ stargazerCount languages(first:8,orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name } } } } }
      contributionsCollection{ totalCommitContributions totalPullRequestContributions totalIssueContributions
        totalPullRequestReviewContributions
        contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""
    body = json.dumps({"query": q, "variables": {"u": USER}}).encode()
    d = json.loads(http("https://api.github.com/graphql", body,
                        {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}))["data"]["user"]
    cc = d["contributionsCollection"]
    langs = {}
    stars = 0
    for r in d["repositories"]["nodes"]:
        stars += r["stargazerCount"]
        for ed in r["languages"]["edges"]:
            langs[ed["node"]["name"]] = langs.get(ed["node"]["name"], 0) + ed["size"]
    weeks = [[(x["date"], x["contributionCount"]) for x in w["contributionDays"]]
             for w in cc["contributionCalendar"]["weeks"]]
    tiles = [("Commits", cc["totalCommitContributions"]), ("Pull requests", cc["totalPullRequestContributions"]),
             ("Issues", cc["totalIssueContributions"]), ("Code reviews", cc["totalPullRequestReviewContributions"]),
             ("Stars earned", stars), ("Followers", d["followers"]["totalCount"])]
    return tiles, langs, weeks, cc["contributionCalendar"]["totalContributions"]

def fetch_public():
    u = json.loads(http(f"https://api.github.com/users/{USER}"))
    repos = json.loads(http(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = {}
    for r in own[:25]:
        try:
            for k, v in json.loads(http(r["languages_url"])).items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
    page = http(f"https://github.com/users/{USER}/contributions")
    ids = {}
    for m in re.finditer(r'<td[^>]*?data-date="(\d{4}-\d\d-\d\d)"[^>]*?id="([^"]+)"', page):
        ids[m.group(2)] = m.group(1)
    for m in re.finditer(r'<td[^>]*?id="([^"]+)"[^>]*?data-date="(\d{4}-\d\d-\d\d)"', page):
        ids[m.group(1)] = m.group(2)
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*?for="([^"]+)"[^>]*>\s*(No|\d+)\s+contribution', page):
        if m.group(1) in ids:
            counts[ids[m.group(1)]] = 0 if m.group(2) == "No" else int(m.group(2))
    if not counts:
        raise RuntimeError("could not read the contributions page")
    days = sorted(counts.items())
    weeks, cur = [], []
    for dstr, c in days:
        wd = datetime.date.fromisoformat(dstr).isoweekday() % 7   # Sunday = 0
        if wd == 0 and cur:
            weeks.append(cur); cur = []
        cur.append((dstr, c))
    if cur: weeks.append(cur)
    total = sum(counts.values())
    tiles = [("Contributions", total), ("Public repos", u["public_repos"]), ("Stars earned", stars),
             ("Followers", u["followers"]), ("Following", u["following"]), ("Gists", u["public_gists"])]
    return tiles, langs, weeks, total

def demo():
    random.seed(7)
    start = datetime.date.today() - datetime.timedelta(days=364)
    weeks, cur = [], []
    for i in range(365):
        d = start + datetime.timedelta(days=i)
        if d.isoweekday() % 7 == 0 and cur:
            weeks.append(cur); cur = []
        cur.append((d.isoformat(), max(0, int(random.gauss(2, 3)))))
    weeks.append(cur)
    tiles = [("Commits", 0), ("Pull requests", 0), ("Issues", 0), ("Code reviews", 0), ("Stars earned", 0), ("Followers", 0)]
    langs = {"JavaScript": 40, "Java": 25, "Python": 20, "CSS": 10, "HTML": 5}
    return tiles, langs, weeks, sum(c for w in weeks for _, c in w)

# ------------------------------------------------------------------ svg helpers
def card(w, h, body, delay=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
        f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="18"/></clipPath>'
        f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>'
        f'<linearGradient id="a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BURG}"/><stop offset=".6" stop-color="{BURG2}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
        f'<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD2}" stop-opacity="0"/><stop offset=".5" stop-color="{GOLD2}" stop-opacity=".12"/><stop offset="1" stop-color="{GOLD2}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="r" cx="1" cy="0" r="1"><stop offset="0" stop-color="{BURG2}" stop-opacity=".35"/><stop offset="1" stop-color="{BURG}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BURG2}" stop-opacity=".55"/><stop offset="1" stop-color="{BURG}" stop-opacity="0"/></linearGradient>'
        f'</defs><rect width="{w}" height="{h}" rx="18" fill="url(#g)"/><rect width="{w}" height="{h}" rx="18" fill="url(#r)"/>'
        f'<g clip-path="url(#c)"><rect x="-300" y="-20" width="150" height="{h+40}" fill="url(#sh)" transform="skewX(-20)">'
        f'<animate attributeName="x" values="-300;{w+300};{w+300}" keyTimes="0;0.55;1" dur="11s" begin="{delay}s" repeatCount="indefinite"/></rect>'
        f'<rect width="{w}" height="3" fill="url(#a)"/></g>'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>{body}</svg>')

def t(x, y, s, size=14, fill=WHITE, weight=400, font=FONT, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{e(str(s))}</text>'

def header(label, right, w):
    return t(24, 38, label, 12, GOLD, 700, MONO, extra='letter-spacing="3"') + t(w-24, 38, right, 12, GRAY, 400, MONO, "end")

def fmt(n):
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"

# ------------------------------------------------------------------ cards
def stats_svg(tiles):
    w, h = 440, 240
    b = header("GITHUB STATS", f"@{USER}", w)
    tw, th, gap = 124, 70, 10
    for i, (label, val) in enumerate(tiles[:6]):
        c, r = i % 3, i // 3
        x, y = 24 + c * (tw + gap), 62 + r * (th + gap)
        b += (f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{CHIP}" stroke="{GOLD}" stroke-opacity=".3">'
              f'<animate attributeName="stroke-opacity" values=".3;.8;.3" dur="4s" begin="{i*0.5}s" repeatCount="indefinite"/></rect>')
        b += t(x + 14, y + 28, label.upper(), 10, GRAY, 700, MONO, extra='letter-spacing="1"')
        b += t(x + 14, y + 56, fmt(val), 26, WHITE, 800)
    return card(w, h, b)

def langs_svg(langs):
    w, h = 440, 240
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    b = header("TOP LANGUAGES", "by code size", w)
    bw = 392
    for i, (name, size) in enumerate(top):
        y = 74 + i * 32
        pct = size / total * 100
        fw = max(6, bw * pct / 100)
        b += t(24, y, name, 13, WHITE, 600) + t(w - 24, y, f"{pct:.1f}%", 12, GOLD, 500, MONO, "end")
        b += f'<rect x="24" y="{y+8}" width="{bw}" height="8" rx="4" fill="{CHIP}"/>'
        b += f'<rect x="24" y="{y+8}" width="{fw:.1f}" height="8" rx="4" fill="url(#a)"/>'
        b += (f'<circle cx="{24+fw:.1f}" cy="{y+12}" r="4" fill="{GOLD2}"><animate attributeName="opacity" values="1;.25;1" dur="3s" begin="{i*0.4}s" repeatCount="indefinite"/></circle>')
    return card(w, h, b, delay=3)

def smooth(pts, ymin=None, ymax=None):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i-1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i+1]
        p3 = pts[i+2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0]-p0[0])/6, p1[1] + (p2[1]-p0[1])/6)
        c2 = (p2[0] - (p3[0]-p1[0])/6, p2[1] - (p3[1]-p1[1])/6)
        if ymin is not None:
            c1 = (c1[0], min(max(c1[1], ymin), ymax)); c2 = (c2[0], min(max(c2[1], ymin), ymax))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

def activity_svg(weeks, total):
    """Daily contributions for the last 30 days."""
    days = [d for wk in weeks for d in wk][-30:]
    vals = [c for _, c in days]
    dates = [datetime.date.fromisoformat(d) for d, _ in days]
    w, h = 900, 300
    left, right, top, bottom = 56, 28, 70, 56
    pw, ph = w - left - right, h - top - bottom
    mx = max(max(vals), 4)
    step = -(-mx // 4)
    mx = step * 4
    xs = [left + i * pw / max(len(vals) - 1, 1) for i in range(len(vals))]
    ys = [top + ph - v / mx * ph for v in vals]
    pts = list(zip(xs, ys))
    line = smooth(pts, top, top + ph)
    area = line + f" L{xs[-1]:.1f},{top+ph} L{xs[0]:.1f},{top+ph} Z"
    b = header("CONTRIBUTION ACTIVITY", f"{sum(vals):,} contributions in the last 30 days", w)
    for k in range(5):
        gy = top + ph - k * ph / 4
        b += f'<line x1="{left}" y1="{gy:.1f}" x2="{w-right}" y2="{gy:.1f}" stroke="{LINE}" stroke-width="1" stroke-dasharray="3 5"/>'
        b += t(left - 10, gy + 4, k * step, 10, GRAY, 400, MONO, "end")
    prev_month = None
    for x, d in zip(xs, dates):
        b += t(x, h - 30, d.day, 10, GRAY, 400, MONO, "middle")
        if d.month != prev_month:
            b += t(x, h - 14, d.strftime("%b"), 10, GOLD, 600, MONO, "middle")
            prev_month = d.month
    b += f'<path d="{area}" fill="url(#area)"/>'
    b += f'<path d="{line}" fill="none" stroke="url(#a)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    for x, y in pts:
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{GOLD2}" opacity=".85"/>'
    pk = vals.index(max(vals))
    b += f'<circle cx="{xs[pk]:.1f}" cy="{ys[pk]:.1f}" r="5" fill="{GOLD2}"/>' + t(xs[pk], ys[pk] - 12, f"peak {vals[pk]}", 10, GOLD2, 500, MONO, "middle")
    b += (f'<circle r="10" fill="{GOLD}" opacity=".25"><animateMotion dur="10s" repeatCount="indefinite" path="{line}"/></circle>'
          f'<circle r="4.5" fill="{GOLD2}"><animateMotion dur="10s" repeatCount="indefinite" path="{line}"/></circle>')
    return card(w, h, b, delay=6)

def main():
    mode = "demo" if "--demo" in sys.argv else ("full" if TOKEN else "public")
    if mode == "full":
        data = fetch_graphql()
    elif mode == "public":
        data = fetch_public()
    else:
        data = demo()
    tiles, langs, weeks, total = data
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("stats.svg", stats_svg(tiles)), ("top-langs.svg", langs_svg(langs)), ("activity.svg", activity_svg(weeks, total))):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"mode={mode} user={USER} tiles={tiles} langs={dict(sorted(langs.items(), key=lambda kv:-kv[1])[:5])} total={total}")

if __name__ == "__main__":
    main()
