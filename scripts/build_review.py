"""Build an allowlisted review candidate. Does not deploy or revoke existing URLs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import shutil,json

ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'dist'
PAGES=['index.html','404.html','about/index.html','contact/index.html','work/index.html',
       'resume/index.html','cfa/index.html','futurezen/index.html','lab/index.html',
       'counterpunch/index.html',
       'post/nfl-big-data-bowl-2021-2022/index.html','post/nfl-performance/index.html',
       'post/nfl-multivariate-analysis/index.html','post/fifa-world-cup-match-prediction/index.html',
       'post/2020-supplemental-football-match-up-analysis/index.html','post/super-bowl-53-analysis/index.html',
       'archive/nfl-performance/index.html','archive/nfl-multivariate-analysis/index.html',
       'archive/fifa-world-cup-match-prediction/index.html']

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v:self.links.append(v)

def build():
    # Remove only this script's generated build directory.
    if DEST.exists():shutil.rmtree(DEST)
    DEST.mkdir();files=set(PAGES+['robots.txt'])
    for folder in ['assets','ananke']:
        files.update(str(p.relative_to(ROOT)) for p in (ROOT/folder).rglob('*') if p.is_file())
    for name in PAGES:
        parser=Links();parser.feed((ROOT/name).read_text())
        for url in parser.links:
            u=urlparse(url)
            if u.scheme not in ['','http','https'] or (u.netloc and u.netloc.lower()!='emr89.github.io'):continue
            path=unquote(u.path).lstrip('/')
            if path.startswith('images/') and (ROOT/path).is_file():files.add(path)
    assert not any(n.startswith('cfa/review/') or n.startswith('data/') or '..' in Path(n).parts for n in files)
    for n in sorted(files):
        target=DEST/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,target)
    urls=['https://emr89.github.io/'+n.removesuffix('index.html') for n in PAGES if n.endswith('index.html') and not n.startswith('archive/')]
    (DEST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>')
    report={'exported_files':len(files),'excluded_prefix':'cfa/review/','source_files_deleted':0,'deployed':False,
            'warning':'Exclusion does not remove source/history or invalidate existing public review URLs.'}
    (DEST/'review-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

if __name__=='__main__':build()
