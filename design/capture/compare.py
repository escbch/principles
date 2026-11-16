"""Print the measurements of several captures side by side, one block per app.

    python3 compare.py <out folder of app 1> <out folder of app 2> ...

Each folder holds the measure.json that shoot.cjs wrote. For every app: body
font, heading sizes, page width, header, navigation, the different button and
field styles with their counts, overflow, small tap targets, axe rules,
requests to other origins, console errors, missing focus indicators.
"""
import json,sys,collections,os
for folder in sys.argv[1:]:
    app=os.path.basename(os.path.normpath(folder))
    d=json.load(open(os.path.join(folder,'measure.json')))
    print(f'\n===== {app}: {len(d)} screens')
    agg={k:collections.Counter() for k in ['body','h1','h2','h3','main412','main1280','header412','header1280','lang','focus']}
    btn=collections.defaultdict(lambda:[0,set(),set()]); fld=collections.defaultdict(lambda:[0,set()])
    navs=collections.Counter(); over=[]; small=collections.Counter(); axe=collections.Counter(); ext=collections.Counter(); con=0; fmiss=0; dialogs=collections.Counter(); tables=collections.Counter()
    for name,e in d.items():
        for w in ['412','1280']:
            m=e.get('measure',{}).get(w)
            if not m: continue
            if m['overflowX']: over.append(f"{name}@{w}({m['scrollWidth']})")
            agg['main'+w][f"max {m['main']['maxWidth']} pad {m['main']['paddingInline']}"]+=1
            h=m.get('header'); agg['header'+w][f"{h['h']}px {h['position']}" if h else 'none']+=1
            for n in m['navs']:
                navs[f"@{w} {n['where']} {n['w']}x{n['h']} top{n['top']} [{n.get('label')}] {'|'.join(n['items'][:8])}"]+=1
            if w=='412':
                agg['lang'][m['lang']]+=1
                b=m['body']; agg['body'][f"{b['fontFamily'][:40]} {b['fontSize']}/{b['lineHeight']}"]+=1
                for h in m['headings']: agg[h['tag']][f"{h['font']} mt{h['marginTop']} mb{h['marginBottom']}"]+=1
                for b in m['buttons']:
                    k=f"h{b['h']} {b['font']} r{b['radius']} pad[{b['padding']}] bg{b['bg']} c{b['color']} bd[{b['border']}]"
                    btn[k][0]+=b['count']; btn[k][1].update(x for x in b['examples'] if x); btn[k][2].add(str(b.get('cls'))[:30])
                for f in m['fields']:
                    k=f"h{f['h']} {f['font']} r{f['radius']} pad[{f['padding']}] bg{f['bg']} bd[{f['border']}]"
                    fld[k][0]+=f['count']; fld[k][1].add(str(f.get('cls'))[:30])
                for s in m['smallTargets']: small[f"{s['tag']} {s['w']}x{s['h']} '{s['text'][:22]}'"]+=1
                for dl in m['dialogs']: dialogs[f"{dl['tag']} r{dl['radius']} labelled={dl['labelled']}"]+=1
                for t in m['tables']: tables[f"cols{t['cols']} scrollBox={t['scrollBox']} w{t['w']}"]+=1
        for sch in ['light','dark']:
            for v in e.get('axe',{}).get(sch,[]): axe[f"{sch}:{v['id']}"]+=v.get('count',1)
        for x in e.get('externalRequests',[]): ext[x.split(' ')[1].split('/')[2] if '//' in x else x]+=1
        con+=len(e.get('console',[]))
        f=e.get('focus')
        if f:
            fmiss+=len(f['missing']); agg['focus'][str(f['sampleOutline'])]+=1
    for k,c in agg.items(): print(f' {k}:', '; '.join(f'{v}× {x}' for x,v in c.most_common(4)))
    print(' NAV:'); [print('   ',v,'×',x[:170]) for x,v in navs.most_common(7)]
    print(f' BUTTON styles: {len(btn)}'); [print('   ',v[0],'×',k,'|',list(v[1])[:4],list(v[2])[:2]) for k,v in sorted(btn.items(),key=lambda kv:-kv[1][0])[:12]]
    print(f' FIELD styles: {len(fld)}'); [print('   ',v[0],'×',k,list(v[1])[:2]) for k,v in sorted(fld.items(),key=lambda kv:-kv[1][0])[:6]]
    print(' overflow:',over[:12]); print(' small targets (distinct):',len(small),small.most_common(10))
    print(' axe:',dict(axe)); print(' external:',dict(ext)); print(' console errors:',con,' focus missing:',fmiss)
    print(' dialogs:',dict(dialogs)); print(' tables:',tables.most_common(5))
