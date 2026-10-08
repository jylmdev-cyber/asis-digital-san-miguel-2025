import json, re, hashlib, difflib, urllib.request, urllib.parse
from pathlib import Path
import os
import pymupdf as fitz

ROOT = Path(os.environ.get('ASIS_SOURCE_DIR', str(Path(__file__).resolve().parents[2]))).resolve()
AUDIT = ROOT / 'audit'
pdf = fitz.open(ROOT / 'ASIS_RIS_SAN_MIGUEL_2025.pdf')
pages = json.loads((AUDIT / 'pdf-pages.json').read_text(encoding='utf8'))
word = (AUDIT / 'word-2026-utf8.txt').read_text(encoding='utf8')
def norm(s):
    s = re.sub(r'ANÁLISIS DE LA SITUACIÓN DE SALUD\s*[–-]\s*PROVINCIA DE SAN MIGUEL', '', s)
    return re.sub(r'\s+', '', s).replace('–','-').replace('—','-').replace('✓','').replace('*','')
# Compare text in bounded chapter segments, avoiding page headers and footers.
anchors = ['I. INTRODUCCIÓN', 'II. ASPECTOS GENERALES', 'III. CARACTERÍSTICAS GEOGRÁFICAS',
           'IV. CARACTERÍSTICAS DEMOGRÁFICAS', 'V. ANÁLISIS DE LOS DETERMINANTES',
           'VI. ANÁLISIS DE SALUD ENFERMEDAD', 'VII. VINCULACIÓN', 'VIII. ANÁLISIS',
           'IX. LÍNEAS DE ACCIÓN', 'X. CONCLUSIONES', 'XI. RECOMENDACIONES']
pt = '\n'.join(p['text'] for p in pages[5:])
wt = word[word.find('I. INTRODUCCIÓN', word.find('SIGLAS Y ACRÓNIMOS')+1):]
comparison = []
for i,a in enumerate(anchors):
    pstart, wstart = pt.find(a), wt.find(a)
    end = anchors[i+1] if i+1<len(anchors) else None
    ps = pt[pstart:pt.find(end,pstart+1) if end else None]
    ws = wt[wstart:wt.find(end,wstart+1) if end else None]
    # Numbers in both formats should remain identical; pagination is excluded.
    ps = re.sub(r'(?m)^\s*\d{1,2}\s*$', '', ps)
    ws = re.sub(r'(?m)^\s*\d{1,2}\s*$', '', ws)
    pn, wn = norm(ps), norm(ws)
    seq = difflib.SequenceMatcher(None, pn, wn)
    differences = [{'pdf':pn[x:y][:500], 'word':wn[u:v][:500]} for tag,x,y,u,v in seq.get_opcodes() if tag!='equal']
    comparison.append({'chapter':a,'pdf_chars':len(pn),'word_chars':len(wn),'similarity':round(seq.ratio(),5),'differences':differences})
inventory = []
for p in pages:
    labels = re.findall(r'(?m)^\s*((?:Tabla|Cuadro|Gráfico|Mapa)\s*\d+\.?.*)',p['text'])
    inventory.append({'page':p['page'],'printed_page':p['page']-3 if p['page']>=4 else None,
                      'chars':len(p['text']),'images':len(pdf[p['page']-1].get_images()),'labels':labels})
manifest = {'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in ROOT.iterdir() if p.suffix in ['.pdf','.doc']],
            'pdf_pages':len(pdf),'docx_2025_available':False,'comparison':comparison,'inventory':inventory}
(AUDIT/'source-audit.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Chapter comparison:',[(x['chapter'],x['similarity'],len(x['differences'])) for x in comparison])
print('Labels:',sum(len(x['labels']) for x in inventory),'Images:',sum(x['images'] for x in inventory))
params={'where':"NOMBPROV='SAN MIGUEL' AND NOMBDEP='CAJAMARCA'",'outFields':'IDDIST,NOMBDIST,NOMBPROV,NOMBDEP','outSR':'4326','f':'geojson','geometryPrecision':'5'}
url='https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioBase/MapServer/12/query?'+urllib.parse.urlencode(params)
b=urllib.request.urlopen(url,timeout=40).read(); geo=json.loads(b)
assert len(geo['features']) == 13, geo
assert all(f['properties']['IDDIST'].startswith('0611') for f in geo['features'])
(AUDIT/'districts-original.geojson').write_bytes(b)
(AUDIT/'geodata-source.json').write_text(json.dumps({'url':url,'publisher':'MINAM','retrieved':'2026-10-07','crs':'EPSG:4326','features':13,'sha256':hashlib.sha256(b).hexdigest(),'note':'Límites referenciales del servicio oficial MINAM. Antigüedad de la geometría no declarada. No acredita demarcación legal.'},ensure_ascii=False,indent=2),encoding='utf8')
print('Official district geometries:',[(f['properties']['IDDIST'],f['properties']['NOMBDIST']) for f in geo['features']])
