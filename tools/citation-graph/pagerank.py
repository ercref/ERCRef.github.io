import sys,re,glob,os,collections,json
D,O=sys.argv[1],sys.argv[2]
docs={}
for path in glob.glob(f"{D}/EIPs/EIPS/eip-*.md")+glob.glob(f"{D}/ERCs/ERCS/erc-*.md"):
    t=open(path,encoding="utf-8",errors="ignore").read()
    m=re.match(r"---\n(.*?)\n---\n(.*)",t,re.S)
    if not m: continue
    fm,body=m.groups()
    f={}
    for line in fm.split("\n"):
        if ":" in line:
            k,v=line.split(":",1); f[k.strip().lower()]=v.strip()
    if f.get("status")=="Moved": continue
    n=int(re.search(r"(\d+)\.md$",path).group(1))
    authors=[]
    for a in re.split(r",(?![^()<>]*[)>])",f.get("author","")):
        a=a.strip()
        h=re.search(r"\(@([A-Za-z0-9_-]+)\)",a)
        name=re.sub(r"[<(].*","",a).strip().replace("ß","ss")
        if a: authors.append((h.group(1).lower() if h else None,name))
    refs=set(int(x) for x in re.findall(r"\b(?:EIP|ERC)[- ]?(\d{1,5})\b",body,re.I))
    refs|=set(int(x) for x in re.findall(r"(?:eip|erc)-(\d+)\.md",body))
    refs|=set(int(x) for x in re.findall(r"\d+",f.get("requires","")))
    refs.discard(n)
    kind="ERC" if "/ERCS/" in path else "EIP"
    docs[n]=dict(n=n,kind=kind,title=f.get("title",""),status=f.get("status",""),authors=authors,refs=refs)
nodes=list(docs); idx={n:i for i,n in enumerate(nodes)}
out={n:[r for r in docs[n]["refs"] if r in docs] for n in nodes}
N=len(nodes); d=0.85; pr={n:1/N for n in nodes}
for _ in range(100):
    dang=sum(pr[n] for n in nodes if not out[n])
    new={n:(1-d)/N+d*dang/N for n in nodes}
    for n in nodes:
        for r in out[n]: new[r]+=d*pr[n]/len(out[n])
    pr=new
indeg=collections.Counter(r for n in nodes for r in out[n])
rank=sorted(nodes,key=lambda n:-pr[n])
with open(f"{O}/docs.tsv","w") as w:
    for i,n in enumerate(rank,1):
        x=docs[n]; w.write(f"{i}\t{x['kind']}-{n}\t{pr[n]*N:.2f}\t{indeg[n]}\t{x['status']}\t{x['title']}\n")
name2h={}
for n in nodes:
    for h,name in docs[n]['authors']:
        if h: name2h.setdefault(name.lower(),h)
# author score: sum of PR (normalized so mean doc=1) over Final docs
share={}; sc=collections.defaultdict(float); best={}; names={}; cnt=collections.Counter()
for n in nodes:
    x=docs[n]
    if x["status"]!="Final": continue
    m=len(x["authors"]); tot=m*(m+1)/2
    for i,(h,name) in enumerate(x["authors"]):
        k=h or name2h.get(name.lower()) or ("name:"+name.lower())
        names.setdefault(k,name); sc[k]+=pr[n]*N*(m-i)/tot; cnt[k]+=1
        share[(k,n)]=pr[n]*N*(m-i)/tot
        if k not in best or share[(k,n)]>share[(k,best[k])]: best[k]=n
with open(f"{O}/authors_weighted.tsv","w") as w:
    for i,k in enumerate(sorted(sc,key=lambda k:-sc[k]),1):
        b=best[k]; w.write(f"{i}\t{k}\t{names[k]}\t{sc[k]:.2f}\t{cnt[k]}\t{docs[b]['kind']}-{b}\t{docs[b]['title']}\n")
print("docs",N,"edges",sum(len(v) for v in out.values()),"final authors",len(sc))
