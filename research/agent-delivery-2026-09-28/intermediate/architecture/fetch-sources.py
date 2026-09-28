from pathlib import Path
import urllib.request,concurrent.futures,json,hashlib,datetime
root=Path('/Users/minimax/code/github/xieshijie/super-auto/research/agent-delivery-2026-09-28')
sources=[
('A01','cursor-scaling','Scaling long-running autonomous coding','2026-01-14','https://cursor.com/blog/scaling-agents'),
('A02','cursor-self-driving','Towards self-driving codebases','2026-02-05','https://cursor.com/blog/self-driving-codebases'),
('A03','openai-harness','Harness engineering: leveraging Codex in an agent-first world','2026-02-11','https://openai.com/index/harness-engineering/'),
('A04','openai-symphony','An open-source spec for Codex orchestration: Symphony','2026-04-27','https://openai.com/index/open-source-codex-orchestration-symphony/'),
('A05','symphony-spec','Symphony specification',None,'https://raw.githubusercontent.com/openai/symphony/8001b52e3062495a16e520e4ceaf8f9de868c4d0/SPEC.md'),
('A06','anthropic-long-running','Effective harnesses for long-running agents','2025-11-26','https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents'),
('A07','anthropic-compiler','Building a C compiler with a team of parallel Claudes','2026-02-05','https://www.anthropic.com/engineering/building-c-compiler'),
('A08','anthropic-app-harness','Harness design for long-running application development','2026-03-24','https://www.anthropic.com/engineering/harness-design-long-running-apps'),
('A09','anthropic-managed','Scaling Managed Agents: Decoupling the brain from the hands','2026-04-08','https://www.anthropic.com/engineering/managed-agents'),
('A10','strongdm-factory','Software Factories And The Agentic Moment','2026-02-06','https://factory.strongdm.ai/'),
('A11','strongdm-principles','The Principles',None,'https://factory.strongdm.ai/principles'),
('A12','strongdm-dtu','Digital Twin Universe',None,'https://factory.strongdm.ai/techniques/dtu')]
def fetch(row):
 i,slug,title,date,url=row
 method='direct HTTPS raw source' if 'raw.githubusercontent' in url else 'Jina Reader of primary source'
 fetchurl=url if 'raw.githubusercontent' in url else 'https://r.jina.ai/'+url
 try:
  req=urllib.request.Request(fetchurl,headers={'User-Agent':'research-archive/1.0'})
  with urllib.request.urlopen(req,timeout=90) as r: data=r.read()
  path=root/'raw/architecture'/f'{i}-{slug}.md';path.write_bytes(data)
  return dict(id=i,title=title,date=date,url=url,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(path.relative_to(root)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),method=method,fetch_url=fetchurl)
 except Exception as e:return dict(id=i,url=url,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:out=list(ex.map(fetch,sources))
(root/'intermediate/architecture/source-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for s in out:print(s['id'],s.get('bytes'),s.get('error','ok'))
