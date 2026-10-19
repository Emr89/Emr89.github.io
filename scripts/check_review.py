"""Check current primary review pages; retain legacy-page link debt explicitly."""
from pathlib import Path
from urllib.parse import urlparse,unquote
from build_review import ROOT,DEST,PAGES,Links
import json

failures=[];legacy=[]
for name in PAGES:
    if name=='counterpunch/demo.html':continue # embedded app downloads use data URLs
    p=DEST/name;parser=Links();parser.feed(p.read_text())
    for value in parser.links:
        u=urlparse(value)
        if u.scheme not in ['','http','https'] or u.netloc and u.netloc.lower()!='emr89.github.io':continue
        if not u.path:continue
        target=DEST/unquote(u.path).lstrip('/') if u.path.startswith('/') or u.netloc else p.parent/unquote(u.path)
        if target.is_dir():target=target/'index.html'
        if not target.exists():
            item={'page':name,'target':value}
            (legacy if name.startswith('archive/') or name in ['404.html','post/2020-supplemental-football-match-up-analysis/index.html','post/super-bowl-53-analysis/index.html'] else failures).append(item)
assert not list((DEST/'cfa/review').glob('**/*'))
report={'primary_broken_links':failures,'legacy_link_debt':legacy,'private_review_exported':False}
(ROOT/'REVIEW_CHECKS.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'primary_broken_links':len(failures),'legacy_link_debt':len(legacy),'private_review_exported':False}))
if failures:raise SystemExit(1)
