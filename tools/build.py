"""Build the public static site from the live Claude artifact data.
Inputs: /home/claude/nine-kingdoms.html, /home/claude/live/{entries,texts,img}
Output: /home/claude/site
"""
import json,glob,os,re,shutil
from PIL import Image
SRC='/home/claude/nine-kingdoms.html'; LIVE='/home/claude/live'; OUT='/home/claude/anna-magical-world/public'
os.makedirs(OUT+'/data/texts',exist_ok=True); os.makedirs(OUT+'/img',exist_ok=True)
# entries
E=[]
for f in sorted(glob.glob(LIVE+'/entries/*.json')):
    d=json.load(open(f)); d['id']=os.path.basename(f)[:-5]; E.append(d)
json.dump(E,open(OUT+'/data/entries.json','w'),ensure_ascii=False,separators=(',',':'))
# texts
for f in glob.glob(OUT+'/data/texts/*.json'): os.remove(f)
for f in glob.glob(LIVE+'/texts/*.json'):
    d=json.load(open(f)); json.dump({'title':d.get('title',''),'body':d.get('body','')},open(OUT+'/data/texts/'+os.path.basename(f),'w'),ensure_ascii=False,separators=(',',':'))
# images -> resized jpg
used={e.get('image') for e in E}-{None,''}
for f in glob.glob(OUT+'/img/*'): 
    if os.path.basename(f)[:-4] not in used: os.remove(f)
for i in used:
    dst=f'{OUT}/img/{i}.jpg'
    if os.path.exists(dst): continue
    src=(glob.glob(f'{LIVE}/img/{i}.*') or [None])[0]
    if not src: print('MISSING IMAGE',i); continue
    im=Image.open(src).convert('RGB'); im.thumbnail((1800,1800)); im.save(dst,'JPEG',quality=82,optimize=True,progressive=True)
# page
s=open(SRC).read()
def rep(a,b):
    global s
    assert s.count(a)==1,a[:80]; s=s.replace(a,b)
rep('function imgUrl(id){return id?"/_blob/"+encodeURIComponent(id):"";}','function imgUrl(id){return id?"img/"+encodeURIComponent(id)+".jpg":"";}')
rep('S.db.collection("texts").doc(id).get().then(s=>{S.texts.set(id,s.exists?s.data():false);','fetch("data/texts/"+encodeURIComponent(id)+".json").then(r=>r.ok?r.json():false).then(s=>{S.texts.set(id,s||false);')
i=s.index('  const c=window.claude;if(!c||!c.use)'); j=s.index('})();\n})();',i)
s=s[:i]+'''  try{const r=await fetch("data/entries.json",{cache:"no-cache"});const list=await r.json();
    const m=new Map();list.forEach(v=>{if(v&&v.id)m.set(v.id,v);});S.entries=m;S.loaded=true;S.dbOk=true;}
  catch(e){S.dbOk=false;}
  route();
'''+s[j:]
s='<!doctype html>\n<html lang="el">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta property="og:title" content="Ο Μαγικός Κόσμος της Άννας">\n<meta property="og:description" content="Βασίλεια, ήρωες, πλάσματα, ιστορίες, τραγούδια και χάρτες, για μικρούς και μεγάλους.">\n<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ccircle cx=%2250%22 cy=%2250%22 r=%2246%22 fill=%22%231b1d3a%22/%3E%3Cpath d=%22M50 12L58 42L88 50L58 58L50 88L42 58L12 50L42 42Z%22 fill=%22%23c9973a%22/%3E%3C/svg%3E">\n'+s
rep('<title>','<meta name="description" content="Η εγκυκλοπαίδεια του κόσμου της Άννας: βασίλεια, ήρωες, πλάσματα, ιστορίες, τραγούδια και χάρτες. Anna\'s Magical World, a bilingual encyclopedia.">\n<title>')
open(OUT+'/index.html','w').write(s)
open(OUT+'/../netlify.toml','w').write('[build]\n  publish = "public"\n\n[[headers]]\n  for = "/data/*"\n  [headers.values]\n    Cache-Control = "public, max-age=0, must-revalidate"\n')
os.makedirs(OUT+'/../tools',exist_ok=True); shutil.copy(__file__,OUT+'/../tools/build.py')
print('entries',len(E),'texts',len(glob.glob(OUT+'/data/texts/*.json')),'images',len(used))
