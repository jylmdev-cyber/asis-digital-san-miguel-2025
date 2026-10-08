"""Extract reviewed aggregates; never publish the private raw audit or clinical vignette."""
from pathlib import Path
import os
import json, re, hashlib, shutil
import pdfplumber
import pymupdf as fitz

ROOT=Path(os.environ.get('ASIS_SOURCE_DIR', str(Path(__file__).resolve().parents[2]))).resolve()
WEB=Path(__file__).resolve().parents[1]; OUT=WEB/'src/data'; PUBLIC=WEB/'public'
OUT.mkdir(parents=True,exist_ok=True); (PUBLIC/'data').mkdir(parents=True,exist_ok=True); (PUBLIC/'documents').mkdir(exist_ok=True)
pages=json.loads((ROOT/'audit/pdf-pages.json').read_text(encoding='utf8'))
audit=json.loads((ROOT/'audit/source-audit.json').read_text(encoding='utf8'))
pdf=pdfplumber.open(ROOT/'ASIS_RIS_SAN_MIGUEL_2025.pdf')
names=['San Miguel','Bolívar','Calquis','Catilluc','El Prado','La Florida','Llapa','Nanchoc','Niepos','San Gregorio','San Silvestre de Cochán','Tongod','Unión Agua Blanca']
ids=['061101','061102','061103','061104','061105','061106','061107','061108','061109','061110','061111','061112','061113']
def norm(x):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',x) if unicodedata.category(c)!='Mn').lower().strip()
districts=[{'id':i,'name':n,'micronetwork':('Nanchoc' if n in ['Bolívar','Nanchoc','San Gregorio'] else 'La Florida' if n in ['Niepos','La Florida'] else None)} for i,n in zip(ids,names)]
def canon(x):
    return next((n for n in names if norm(n)==norm(x.replace('\n',' '))),x.replace('\n',' '))
def number(x): return float(re.sub(r'\s+','',x).replace(',','.')) if '.' in x or ',' in x else int(re.sub(r'\s+','',x))
datasets=[]
def ds(id,title,page,table,year,source,columns,rows,note='',status='reviewed',module='demografia'):
    item={'id':id,'title':title,'module':module,'period':year,'unit':columns[1].get('unit','') if len(columns)>1 else '',
          'source':{'document':'ASIS_RIS_SAN_MIGUEL_2025.pdf','page':page,'printedPage':page-3,'table':table,'institution':source},
          'columns':columns,'rows':rows,'note':note,'status':status}
    datasets.append(item); return item
def col(key,label,unit='',numeric=False): return {'key':key,'label':label,'unit':unit,'numeric':numeric}
C=col
def table_rows(page,needle):
    tables=pdf.pages[page-1].extract_tables()
    tab=next((t for t in tables if any(needle in str(c) for row in t for c in row if c)),None)
    if tab is None:
        lines=pages[page-1]['text'].replace('San Silvestre de \nCochan','San Silvestre de Cochan').splitlines()
        rows=[['HEADER']]
        for line in lines:
            m=re.match(r'(.+?)\s+(\d[^a-zA-Z]*)$',line.strip())
            if m and (canon(m[1]) in names or m[1] in ['Total','Provincial']): rows.append([m[1]]+m[2].split())
        return rows
    return [[str(c).strip() for c in row if c is not None and str(c).strip()] for row in tab]

# Table 3 has non-standard borders; rows verified against rendered page 16.
pop=[]
for line in pages[15]['text'].splitlines():
    m=re.match(r'(.+?)\s+((?:\d+\s+){17}\d+)\s*$',line)
    if not m: continue
    name=canon(m[1]); vals=list(map(int,m[2].split()))
    for j,year in enumerate([2023,2024,2025]):
        v=vals[j*6:(j+1)*6]
        pop.append(dict(district=name,year=year,children=v[0],adolescents=v[1],youth=v[2],adults=v[3],older=v[4],total=v[5]))
assert len(pop)==39
ds('poblacion','Población por distrito y curso de vida',16,'Cuadro 3',[2023,2024,2025],'OITE – Red San Miguel (2026)',[C('district','Distrito'),C('year','Año','año',True)]+[C(k,l,'habitantes',True) for k,l in [('children','Niños 0–11'),('adolescents','Adolescentes 12–17'),('youth','Jóvenes 18–29'),('adults','Adultos 30–59'),('older','Adultos mayores 60+'),('total','Total')]],pop,'Población de referencia del ASIS; no equivale a afiliados al SIS. Agrupaciones por curso de vida, no intervalos quinquenales.')
sex=[]
for r in table_rows(14,'Niños')[2:]:
    if len(r)==3: sex.append({'group':r[0],'male':number(r[1]),'female':number(r[2])})
ds('sexo-edad','Población por sexo y curso de vida',14,'Cuadro 2',2025,'ORE Cajamarca (2026)',[C('group','Curso de vida'),C('male','Masculino','habitantes',True),C('female','Femenino','habitantes',True)],sex,'La visualización usa cinco cursos de vida. La pirámide quinquenal del Gráfico 1 carece de tabla numérica recuperable.')
dynamic=[{'year':y,'births':b,'birthRate':7,'deaths':d,'deathRate':dr,'lifeExpectancy':le} for y,b,d,dr,le in [(2023,326,61,1,76.3),(2024,314,42,1,76.4),(2025,307,200,5,76.2)]]
ds('dinamica','Dinámica poblacional reportada',13,'Cuadro 1',[2023,2024,2025],'ORE Cajamarca (2026)',[C('year','Año','año',True),C('births','Nacimientos','nacimientos',True),C('birthRate','Natalidad','por 1.000 hab.',True),C('deaths','Defunciones','defunciones',True),C('deathRate','Mortalidad','por 1.000 hab.',True),C('lifeExpectancy','Esperanza de vida','años',True)],dynamic,'El título dice región Cajamarca, el texto refiere San Miguel. 200 defunciones discrepan de las 204 del Cuadro 39; 307 nacimientos discrepan de 795 nacidos vivos del Cuadro 46. No se calculan tendencias sanitarias a partir de esta tabla.', 'warning')
# SIS and district determinants remain exactly as reported, including flagged values.
sis=[]
for r in table_rows(17,'Bolívar')[1:]:
    if len(r)==4:
        for y,v in zip([2023,2024,2025],r[1:]): sis.append({'district':canon(r[0]),'year':y,'affiliates':number(v)})
ds('sis','Afiliación al Seguro Integral de Salud',17,'Tabla 2',[2023,2024,2025],'Unidad de Seguros – DIRESA Cajamarca (2026)',[C('district','Distrito'),C('year','Año','año',True),C('affiliates','Afiliaciones','afiliaciones',True)],sis,'Afiliación administrativa y población de referencia tienen universos distintos. No interpretar su razón como cobertura ni como población real.','warning')
specs=[('pobreza','Pobreza monetaria',18,'Tabla 3',2017),('analfabetismo','Analfabetismo',18,'Tabla 4',2017),('inasistencia','Inasistencia escolar',19,'Tabla 5',2017),('desempleo','Desempleo',20,'Tabla 6',2017),('dependencia','Dependencia económica de los hogares',21,'Tabla 7',2017),('densidad-estado','Densidad del Estado reportada',22,'Tabla 8',2017),('agua','Viviendas con acceso a agua potable',23,'Tabla 9',2017),('desague','Viviendas con acceso a desagüe',24,'Tabla 10',2017),('hacinamiento','Hacinamiento de los hogares',25,'Tabla 11',2017),('lena','Hogares que cocinan con leña o estiércol',26,'Tabla 12',2017),('migracion','Población migrante',27,'Tabla 13',2017),('emigracion','Población emigrante reportada',27,'Tabla 14',2017)]
for id,title,page,label,year in specs:
    raw=pages[page-1]['text']; raw=raw[raw.index(label+'.'):];raw=raw[:raw.index('Fuente:')]
    raw=raw.replace('San Silvestre de \nCochan','San Silvestre de Cochan').replace('San Silvestre de \nCochán','San Silvestre de Cochán')
    t=[]
    for line in raw.splitlines():
        m=re.match(r'(.+?)\s+(\d+[.,]?\d*)\s*$',line.strip())
        if m and (canon(m[1]) in names or m[1]=='Provincial'):t.append([m[1],m[2]])
    rows=[]
    for r in t:
        z=[str(c).strip() for c in r if c is not None and str(c).strip()]
        if len(z)==2 and re.fullmatch(r'\d+[.,]?\d*',z[1]): rows.append({'district':canon(z[0]),'value':number(z[1])})
    assert len(rows)==14,(id,rows)
    note='Línea base histórica de 2017; no representa una medición de 2025. Se conserva el valor provincial publicado, no un promedio simple de distritos.'
    status='historical'
    if id in ['inasistencia','dependencia']: note+=' El título menciona 2025, pero la fuente y el contexto remiten a 2017.'; status='warning'
    if id=='analfabetismo': note+=' El texto «casi 1 de cada 2» no corresponde al 12,7 % de la tabla.'
    if id=='densidad-estado': note+=' La unidad se publica como porcentaje, pero la escala parece un índice; pendiente de validación. No se representa como porcentaje en mapas.';status='warning'
    if id=='emigracion': note+=' Contiene valores superiores al 100 % sin definición de denominador; pendiente de validación. Se conserva en tabla, sin mapa ni gráfico de proporciones.';status='warning'
    ds(id,title,page,label,year,'Sistema de Información Distrital para la Gestión Pública (2017)',[C('district','Distrito'),C('value','Valor reportado','unidad pendiente' if id=='densidad-estado' else '%',True)],rows,note,status,'determinantes')
# District health service matrices: blanks are zeros only when row sums reconcile.
for id,title,page,label,keys,labels in [
    ('legal','Saneamiento y título de propiedad',28,'Cuadro 4',['facilities','legalYes','legalNo','titleYes','titleNo'],['Establecimientos','Saneados','Sin saneamiento','Con título','Sin título']),
    ('infraestructura','Estado de la infraestructura',52,'Cuadro 28',['facilities','good','bad'],['Establecimientos','Buen estado','Mal estado']),
    ('internet','Conectividad de establecimientos',57,'Cuadro 31',['facilities','connected','disconnected','percent'],['Establecimientos','Con internet','Sin internet','Con internet (%)']),
    ('computo','Equipos de cómputo y categorías',56,'Cuadro 30',['facilities','i1','i2','i3','i4','cpu','monitors','printers','total'],['Establecimientos','I-1','I-2','I-3','I-4','CPU regulares','Monitores buenos','Impresoras malas','Total equipos'])]:
    t=next(t for t in pdf.pages[page-1].extract_tables() if any('Bolívar' in str(c) for r in t for c in r if c))
    rows=[]
    for r in t:
        if not r or canon(str(r[0] or '')) not in names: continue
        # Null cells are layout subdivisions. Actual empty string represents blank numeric cell.
        cells=[str(c).strip() for c in r if c is not None]
        if page in [28,52]: cells=[r[0]]+[str(r[j] or '0').strip() for j in ([3,6,9,12,15] if page==28 else [3,6,9])]
        vals=[number(v or '0') for v in cells[1:]]
        assert len(vals)==len(keys),(id,cells,vals)
        rows.append(dict(district=canon(cells[0]),**dict(zip(keys,vals))))
    assert len(rows)==13,(id,len(rows))
    note='Celdas vacías tratadas como cero únicamente en matrices exhaustivas cuyo total concuerda.'
    status='reviewed'
    if id=='computo': note+=' Categorías del Cuadro 30: 34 I-1, 8 I-2, 5 I-3 y 1 I-4; difieren del Cuadro 5 y del texto (32/10/5/1). Se usa el Cuadro 30 para el desglose distrital, pendiente de confirmación.';status='warning'
    ds(id,title,page,label,2025,'OITE – Red San Miguel' if page in [56,57] else 'Patrimonio – Red San Miguel',[C('district','Distrito')]+[C(k,l,'%' if k=='percent' else 'unidades',True) for k,l in zip(keys,labels)],rows,note,status,'servicios')
ambulances=[]
for r in table_rows(34,'Bolívar')[1:]:
    if len(r)==2: ambulances.append({'district':canon(r[0]),'ambulances':number(r[1])})
ds('ambulancias','Ambulancias registradas por distrito',34,'Cuadro 10',2025,'Servicios de Salud – Red San Miguel',[C('district','Distrito'),C('ambulances','Ambulancias','unidades',True)],ambulances,'La ambulancia registrada en Tongod se reporta inoperativa desde 2024. Conteo patrimonial, no unidades operativas.','warning','servicios')
for id,page,label,title in [('rrhh-regimen',36,'Cuadro 12','Personal por grupo y régimen laboral'),('rrhh-asistencial',37,'Cuadro 13','Personal asistencial por cargo'),('rrhh-administrativo',38,'Cuadro 14','Personal administrativo por cargo')]:
    t=next(t for t in pdf.pages[page-1].extract_tables() if any('DL.' in str(c) for r in t for c in r if c))
    rows=[]
    for r in t[1:]:
        cells=[str(c).strip() for c in r if c is not None]
        if r[0]=='' and r[1]=='Total': cells=[str(c).strip() for c in r if c is not None and str(c).strip()]
        if len(cells)==6 and not any('DL.' in c for c in cells):
            try: rows.append(dict(group=cells[0].replace('\n',' '),**dict(zip(['appointed','cas','contract','other','total'],[number(x or '0') for x in cells[1:]]))))
            except ValueError: pass
    ds(id,title,page,label,2025,'Recursos Humanos – Red San Miguel',[C('group','Grupo')]+[C(k,l,'trabajadores',True) for k,l in [('appointed','DL. 276'),('cas','DL. 1057'),('contract','Locación'),('other','Otro'),('total','Total')]],rows,'Los totales de los cuadros 12, 13 y 14 no concilian entre sí por régimen. El Cuadro 14 registra dos ingenieros, aunque el texto declara cero. No sumar personal por cuadros sin confirmar universos.','warning','servicios')
# Morbidity and mortality tables preserve totals and published shares.
for id,page,label,title,module in [('morbilidad',58,'Cuadro 32','Causas de atención por morbilidad','epidemiologia'),('morbilidad-ninos',60,'Cuadro 33','Morbilidad en niños','epidemiologia'),('morbilidad-adolescentes',61,'Cuadro 34','Morbilidad en adolescentes','epidemiologia'),('morbilidad-jovenes',62,'Cuadro 35','Morbilidad en jóvenes','epidemiologia'),('morbilidad-adultos',63,'Cuadro 36','Morbilidad en adultos','epidemiologia'),('morbilidad-mayores',64,'Cuadro 37','Morbilidad en adultos mayores','epidemiologia'),('morbilidad-distritos',65,'Cuadro 38','Atenciones por distrito y sexo','epidemiologia'),('mortalidad',67,'Cuadro 39','Causas de defunción','epidemiologia'),('mortalidad-distritos',72,'Cuadro 45','Defunciones por distrito y sexo','epidemiologia')]:
    t=next(t for t in pdf.pages[page-1].extract_tables() if any('Femenino' in str(c) for r in t for c in r if c))
    rows=[]
    for r in t[1:]:
        cells=[str(c).strip().replace('\n',' ') for c in r if c is not None and str(c).strip()]
        if len(cells)!=5: continue
        try: rows.append(dict(**{'district' if 'distritos' in id else 'cause':canon(cells[0])},**dict(zip(['total','female','male','percent'],[number(x) for x in cells[1:]]))))
        except ValueError: pass
    assert len(rows)>10,(id,rows)
    note='Registros de atención, no personas únicas ni prevalencia.' if id.startswith('morbilidad') else 'Defunciones registradas; no una tasa de mortalidad.'
    status='reviewed'
    if id=='morbilidad':note+=' Se prioriza el Cuadro 32: el texto de p. 54 confunde 38.627 IRA con el total, invierte sexos y escribe 65,8 % para caries; la tabla reporta 6,8 %.';status='warning'
    if id=='mortalidad':note+=' El cuadro totaliza 204, mientras el Cuadro 1 publica 200. El texto de pp. 63–64 no concuerda con las causas ni con el 24,5 % de resto de enfermedades.';status='warning'
    ds(id,title,page,label,2025,'HIS MINSA' if id.startswith('morbilidad') else 'SINADEF / DIRESA Cajamarca',[C('district' if 'distritos' in id else 'cause','Distrito' if 'distritos' in id else 'Causa'),C('total','Total','atenciones' if id.startswith('morbilidad') else 'defunciones',True),C('female','Femenino','registros',True),C('male','Masculino','registros',True),C('percent','Participación','%',True)],rows,note,status,module)
events=[('IRA notificadas',1857,65,'NOTIWEB / vigilancia del ASIS','episodios'),('Neumonías notificadas',232,65,'Vigilancia epidemiológica del ASIS','casos'),('Tuberculosis',4,83,'SIGTB','casos'),('Leishmaniasis cutánea',22,85,'NOTIWEB','casos'),('Dengue autóctono',0,85,'NOTIWEB','casos'),('Muertes maternas',0,74,'DGE / SINADEF','defunciones'),('Muertes perinatales',6,74,'DGE / SINADEF','defunciones'),('Cáncer (indicador territorial)',11,89,'HIS MINSA','casos'),('Diabetes (indicador territorial)',121,90,'HIS MINSA','casos'),('Hipertensión (indicador territorial)',498,91,'HIS MINSA','casos'),('Salud mental: casos tamizados',155,92,'HIS MINSA','casos tamizados')]
ds('vigilancia','Eventos e indicadores provinciales reportados',65,'Texto capítulos VI y VIII',2025,'Vigilancia epidemiológica / HIS MINSA',[C('event','Indicador'),C('value','Cantidad','según evento',True),C('unit','Unidad'),C('page','Página PDF','página',True),C('institution','Fuente')],[{'event':e,'value':v,'unit':u,'page':p,'institution':s} for e,v,p,s,u in events],'Cada registro conserva su propia página y fuente. Los universos de vigilancia, tamizaje y atenciones HIS son distintos; no sumarlos ni comparar como prevalencias.','reviewed','epidemiologia')
maternal=[{'year':y,'maternal':m,'perinatal':p,'liveBirths':b} for y,m,p,b in [(2023,0,1,660),(2024,1,3,740),(2025,0,6,795)]]
ds('materno-perinatal','Mortalidad materna y perinatal reportada',74,'Cuadro 46',[2023,2024,2025],'Cuantificador de Desigualdades – DGE / SINADEF',[C('year','Año','año',True),C('maternal','Maternas','defunciones',True),C('perinatal','Perinatales','defunciones',True),C('liveBirths','Nacidos vivos','nacidos vivos',True)],maternal,'Los 795 nacidos vivos discrepan de los 307 nacimientos del Cuadro 1. No se calcula RMM ni tasa perinatal sin validar el denominador.','warning','epidemiologia')
alt=[]
for line in pages[9]['text'].splitlines():
    m=re.match(r'(.+?)\s+(\d+)\s+m\.s\.n\.m',line.strip())
    if m and canon(m[1]) in names:alt.append({'district':canon(m[1]),'altitude':int(m[2])})
assert len(alt)==13
ds('altitud','Altitud de las capitales distritales',10,'Tabla 1',2022,'Atlas de Cajamarca (2022)',[C('district','Distrito'),C('altitude','Altitud','m s. n. m.',True)],alt,'El texto indica 2.650 m para San Miguel y la tabla 2.665 m. Se conserva la tabla, pendiente de validación.','warning','territorio')
# Validate sums, flag failures, preserve source values unchanged.
checks=[]
for d in datasets:
    rows=d['rows']; total=next((r for r in rows if norm(str(next(iter(r.values())))) in ['total','provincial','total provincial']),None)
    detail=[r for r in rows if r is not total]
    if total and 'year' not in total:
        for c in d['columns']:
            k=c['key']
            if c['numeric'] and k not in ['percent','value','year']:
                actual=sum(r[k] for r in detail)
                checks.append({'dataset':d['id'],'field':k,'sum':actual,'reported':total[k],'pass':actual==total[k]})
    if total and 'year' in total:
        for y in sorted(set(r['year'] for r in rows)):
            yr=[r for r in rows if r['year']==y];yt=next(r for r in yr if r['district']=='Total')
            actual=sum(r['affiliates'] for r in yr if r is not yt)
            checks.append({'dataset':d['id'],'field':'affiliates','year':y,'sum':actual,'reported':yt['affiliates'],'pass':actual==yt['affiliates']})
    for r in rows:
        if all(k in r for k in ['female','male','total']):
            assert r['female']+r['male']==r['total'],(d['id'],r)
for y in [2023,2024,2025]:
    rows=[r for r in pop if r['year']==y]
    checks.append({'dataset':'poblacion','year':y,'sum':sum(r['total'] for r in rows),'reported':{2023:44692,2024:44219,2025:43651}[y],'pass':sum(r['total'] for r in rows)=={2023:44692,2024:44219,2025:43651}[y]})
    for r in rows: assert sum(r[k] for k in ['children','adolescents','youth','adults','older'])==r['total']
for c in checks:
    if not c['pass']:
        d=next(d for d in datasets if d['id']==c['dataset']); d['status']='warning';d['note']+=f" La suma de {c['field']} ({c['sum']}) no concuerda con el total impreso ({c['reported']})."

issues=[
 ('edition','Edición documental','Alta',1,'Portada 2025 y créditos 2026; el Word tiene nombre 2026 pero portada 2025.','Confirmar edición oficial; se presenta como ASIS 2025 por portada y periodos.'),
 ('docx','DOCX de 2025 no disponible','Media',1,'Solo se encontró un archivo Word binario .doc.','Solicitar versión oficial .docx; no renombrar ni asumir equivalencia.'),
 ('births','Denominadores de nacimientos','Alta',74,'307 nacimientos en Cuadro 1; 795 nacidos vivos en Cuadro 46 para 2025.','No calcular tasas maternas/perinatales.'),
 ('deaths','Defunciones provinciales','Alta',67,'200 en Cuadro 1; 204 en Cuadros 39 y 45.','Mostrar 204 como total del Cuadro 39 con advertencia; confirmar extracción SINADEF.'),
 ('morbidity','Morbilidad y distribución por sexo','Alta',57,'Narrativa: 38.627 como total, sexos invertidos y 65,8 % caries; Cuadro 32: 137.266 y 6,8 % caries.','Priorizar cuadro verificable, registrar discrepancia.'),
 ('mortalitytext','Interpretación de mortalidad','Alta',66,'Texto refiere 86,5 % resto; Cuadro 39 registra 24,5 %.','No reproducir conclusión narrativa como hallazgo validado.'),
 ('historical','Determinantes de 2017','Media',19,'Tablas 5 y 7 tienen título 2025, pero fuente 2017.','Rotular 2017 y mantener advertencia; actualizar con fuente oficial.'),
 ('emigration','Porcentajes superiores al 100 %','Alta',27,'Emigración: 150,4 % La Florida, 140,1 % El Prado, 140,6 % Niepos y 122,9 % San Gregorio.','Conservar en tabla; sin gráfico de composición ni interpretación de proporción.'),
 ('ide','Unidad del índice de densidad estatal','Alta',22,'0,44–0,65 publicados como porcentajes; escala y agregado requieren definición.','Mostrar unidad pendiente; excluir de mapas porcentuales.'),
 ('sis','Afiliados y población','Media',17,'56.670 afiliaciones frente a 43.651 habitantes en 2025.','Universos distintos; no derivar cobertura ni población real.'),
 ('categories','Categorías IPRESS','Alta',29,'Cuadro 5 y texto difieren del Cuadro 30 (34/8/5/1).','Usar Cuadro 30 con nota; solicitar padrón RENIPRESS fechado.'),
 ('staff','Personal no conciliado','Alta',38,'Cuadro 12 suma 366; cuadros 13 y 14 suman 342 + 24, pero las distribuciones por régimen no concilian. Texto niega ingenieros; tabla registra 2.','Confirmar universos en INFORHUS; no combinar cuadros por régimen.'),
 ('equipment','Equipamiento Unión Agua Blanca','Alta',51,'Narrativa: 73 equipos (48/25); Cuadro 27: 46.','Mantener inventarios detallados en documento; no publicar total consolidado como validado.'),
 ('ambulance','Ambulancia Tongod','Media',34,'El inventario incluye 1; narrativa declara inoperativa desde 2024.','Distinguir inventario de operatividad.'),
 ('privacy','Relato clínico identificable','Alta',73,'Relato de un evento individual con localidad, edad y antecedentes obstétricos.','Retirado de la copia pública y del índice; originales conservados localmente.'),
 ('maps','Georreferenciación de IPRESS','Media',8,'No hay tabla verificable de coordenadas de establecimientos. La latitud citada 78°59′48″ requiere revisión.','Usar límites referenciales oficiales MINAM; omitir puntos y solicitar padrón oficial.'),
 ('gradient','Gradientes sociales y causalidad','Alta',96,'Conclusiones causales y territoriales no concuerdan siempre con gráficos y texto; no hay microdatos ni denominadores de grupos.','Presentar asociaciones como hipótesis documentales; no inferir causalidad ni promediar grupos.'),
 ('numbering','Numeración duplicada','Baja',76,'Cuadro 46 aparece para mortalidad y vinculación; Cuadro 48 es imagen.','Usar identificador de dataset + página física.'),
 ('pyramid','Pirámide quinquenal sin tabla','Media',15,'Gráfico 1 incrustado; intervalos y valores no recuperables con fiabilidad.','Usar Cuadro 2 como distribución por curso de vida claramente rotulada.'),
]
quality=[dict(id=i,title=t,severity=s,page=p,evidence=e,action=a) for i,t,s,p,e,a in issues]
for c in checks:
    if not c['pass']:quality.append({'id':'sum-'+c['dataset']+'-'+c['field'],'title':'Total no conciliado: '+c['dataset'],'severity':'Alta','page':next(d['source']['page'] for d in datasets if d['id']==c['dataset']),'evidence':f"{c['field']}: suma {c['sum']}, total impreso {c['reported']}",'action':'Conservar valores; solicitar confirmación de la tabla.'})

# Remove the entire clinical vignette at content level (not a white overlay).
safe=fitz.open(ROOT/'ASIS_RIS_SAN_MIGUEL_2025.pdf'); p=safe[72]
start=p.search_for('En cuanto la presentación')[0]
end=p.search_for('En tanto, los casos')[0]
rect=fitz.Rect(70,start.y0-2,p.rect.width-60,end.y0-12)
p.add_redact_annot(rect,fill=(1,1,1))
p.apply_redactions()
p.insert_textbox(rect,'Copia pública: se retiró el relato clínico individual para proteger la privacidad. Los indicadores agregados se conservan. El original permanece en el archivo local.',fontsize=11,fontname='helv',color=(.1,.25,.3))
safe.set_metadata({'title':'ASIS San Miguel 2025 - copia pública con relato clínico retirado','author':'Red de Salud San Miguel; adaptación digital','subject':'Copia pública derivada; sin validación institucional adicional'})
safe.save(PUBLIC/'documents/ASIS_SAN_MIGUEL_2025_PUBLICO.pdf',garbage=4,deflate=True)
reopen=fitz.open(PUBLIC/'documents/ASIS_SAN_MIGUEL_2025_PUBLICO.pdf')
alltext='\n'.join(p.get_text() for p in reopen)
assert all(x not in alltext for x in ['shock hipovolémico','ruptura uterina'])
publicpages=[{'page':i+1,'text':p.get_text()} for i,p in enumerate(reopen)]
(PUBLIC/'data/source-pages.json').write_text(json.dumps(publicpages,ensure_ascii=False),encoding='utf8')
reopen[72].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(ROOT/'audit/renders/page-73-public.png')
geo=json.loads((ROOT/'audit/districts-original.geojson').read_text(encoding='utf8'))
for f in geo['features']: f['properties']['name']=next(d['name'] for d in districts if d['id']==f['properties']['IDDIST'])
(PUBLIC/'data/districts.geojson').write_text(json.dumps(geo,ensure_ascii=False,separators=(',',':')),encoding='utf8')
geosource=json.loads((ROOT/'audit/geodata-source.json').read_text(encoding='utf8'))
data={'edition':2025,'reviewedAt':'2026-10-07','districts':districts,'datasets':datasets,'quality':quality,'checks':checks,'inventory':audit['inventory'],'files':audit['files'],'geosource':geosource,'summary':{'pdfPages':97,'documentLabels':sum(len(p['labels']) for p in audit['inventory']),'embeddedImages':sum(p['images'] for p in audit['inventory']),'docxAvailable':False,'comparison':'El Word .doc con nombre 2026 también lleva portada 2025. Los capítulos I, VII, VIII, IX, X y XI coinciden en texto normalizado; otros difieren por extracción de tablas, espacios y cifras incrustadas. No se acredita equivalencia de imágenes.'}}
(OUT/'asis.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(PUBLIC/'data/asis.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Datasets',len(datasets),'Rows',sum(len(d['rows']) for d in datasets),'Issues',len(quality),'Failed sums',[c for c in checks if not c['pass']])
