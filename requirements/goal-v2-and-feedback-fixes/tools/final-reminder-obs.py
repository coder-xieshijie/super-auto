import json,sys,os,glob,base64
d=sys.argv[1]
insp=sorted(glob.glob(os.path.join(d,'*-inspector')))[-1]
rev=sorted(glob.glob(os.path.join(d,'*-runtime-events.jsonl')))[-1]
bound=set()
for l in open(rev):
    try: e=json.loads(l)
    except: continue
    s=json.dumps(e)
    if 'turn_bound' in s:
        for k in ('turnId','turn_id'):
            def walk(o):
                if isinstance(o,dict):
                    for kk,v in o.items():
                        if kk in('turnId','turn_id') and isinstance(v,str): bound.add(v)
                        walk(v)
                elif isinstance(o,list):
                    for v in o: walk(v)
            walk(e)
rows=[]
for l in open(os.path.join(insp,'events.jsonl')):
    e=json.loads(l)
    if e.get('type')!='call.captured': continue
    cid=e['callId']; p=os.path.join(insp,'payloads',base64.b64encode(cid.encode()).decode()+'.request.json')
    has=None; lastuser=''
    if os.path.exists(p):
        req=json.load(open(p))
        body=req.get('body',req)
        msgs=body.get('messages') or []
        users=[m for m in msgs if m.get('role')=='user']
        if users:
            c=users[-1].get('content')
            txt=c if isinstance(c,str) else ' '.join(x.get('text','') for x in c if isinstance(x,dict))
            lastuser=txt
        has='goal is not running' in json.dumps(body)
        firstpos=json.dumps(body).find("This session's goal is not running")
    rows.append({'callId':cid[:8],'turnId':e.get('turnId'),'startedAtMs':e.get('startedAtMs'),'goalBound':e.get('turnId') in bound,'reminderInRequest':has,'lastUserHead':lastuser[:120]})
print(json.dumps({'inspector':os.path.basename(insp),'boundTurns':sorted(bound),'calls':rows},ensure_ascii=False,indent=1))
