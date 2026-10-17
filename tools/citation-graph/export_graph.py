"""Build the graph JSON for the homepage and inline it into template.html.

Usage: python3 export_graph.py <dir with EIPs/ and ERCs/ clones> <work dir> <avatar dir> <output html> <snapshot date>
"""
import base64, contextlib, io, json, os, runpy, sys

src, work, avatars, out_html, date = sys.argv[1:6]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(work, exist_ok=True)

sys.argv = ["pagerank.py", src, work]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(here, "pagerank.py"), run_name="__main__")
docs, pr, N, out = g["docs"], g["pr"], g["N"], g["out"]
sc, names, name2h, share = g["sc"], g["names"], g["name2h"], g["share"]

final = {n for n in docs if docs[n]["status"] == "Final"}
nodes, links = [], []
for n in final:
    x = docs[n]
    nodes.append(dict(id=f"d{n}", t=x["kind"], n=n, title=x["title"].strip('"'), s=round(pr[n] * N, 3)))
    links += [dict(s=f"d{n}", t=f"d{r}", k="c") for r in out[n] if r in final]
for k in sc:
    node = dict(id="a:" + k, t="A", h=None if k.startswith("name:") else k, name=names[k], s=round(sc[k], 3))
    p = os.path.join(avatars, f"{node['h']}.jpg")
    if node["h"] and os.path.exists(p):
        node["av"] = "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()
    nodes.append(node)
for n in final:
    for h, name in docs[n]["authors"]:
        k = h or name2h.get(name.lower()) or ("name:" + name.lower())
        links.append(dict(s="a:" + k, t=f"d{n}", k="a", w=round(share.get((k, n), 0), 3)))

with open(os.path.join(work, "handles.txt"), "w") as f:
    f.write("\n".join(x["h"] for x in nodes if x["t"] == "A" and x["h"]))
data = json.dumps(dict(nodes=nodes, links=links), separators=(",", ":")).replace("</", "<\\/")
tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
open(out_html, "w", encoding="utf-8").write(tpl.replace("__DATE__", date).replace("__DATA__", data))
print(f"{len(final)} documents, {len(sc)} authors, {len(links)} links -> {out_html}")
