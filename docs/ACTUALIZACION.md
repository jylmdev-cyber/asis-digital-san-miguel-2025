# Actualización y mantenimiento

## Cambiar datos de una edición

1. Conservar los originales fuera del repositorio público y registrar archivo, fecha, hash y edición. Diferenciar año de publicación y periodo de medición.
2. Revisar todo el material, tablas y objetos incrustados. Comparar versiones disponibles; no resolver diferencias por intuición ni copiar un total narrativo si contradice su tabla.
3. Editar `src/data/asis.json` mediante extracción revisada. Mantener esquema, unidad, universo, numerador/denominador cuando se conozcan, periodo y página física. Registrar faltantes y observaciones.
4. Actualizar el espejo `public/data/asis.json` y el índice sanitizado `source-pages.json`. Incorporar un PDF público derivado si los originales contienen relatos individuales. No subir fuentes internas sin autorización.
5. Ejecutar `npm run check`, `npm test`, `npm run build`. Ajustar los totales esperados de pruebas únicamente con evidencia del nuevo documento y revisión registrada.
6. Revisar gráficos, tablas y filtros en navegador; comprobar modo oscuro, móvil, teclado, CSV, PNG y PDF. Ejecutar QA en la URL local correcta.
7. Actualizar diagnóstico, notas y fecha de revisión; publicar la misma revisión del código que produjo `dist/`. Conservar rollback y resumen de cambios.

No sobrescribir retrospectivamente una fuente anual sin anotarlo. No reemplazar un faltante por cero. No promediar porcentajes territoriales sin denominadores. No usar atenciones como pacientes únicos ni calcular cobertura SIS con otra población.

## Reproducir la extracción de estos originales

Los scripts son específicos del documento auditado; no constituyen un extractor universal. Requieren Python 3.11 o posterior y, para Word `.doc`, Windows con Microsoft Word instalado. Los datos incluidos permiten ejecutar la aplicación sin estos programas ni los originales.

```powershell
python -m pip install -r scripts/requirements-audit.txt
$env:ASIS_SOURCE_DIR = 'C:/ruta/privada/con/originales'
python scripts/prepare_sources.py
./scripts/export_word.ps1 -SourceDirectory $env:ASIS_SOURCE_DIR
python scripts/review_sources.py
python scripts/extract_data.py
npm test
```

El directorio privado contiene `ASIS_RIS_SAN_MIGUEL_2025.pdf` y `ASIS_RED_SAN_MIGUEL_2026_FINAL.doc`. La carpeta `audit/` se escribe allí y debe quedar fuera del control de versiones. Si no está disponible Word, conservar los datos ya revisados y declarar que la comparación no se pudo repetir. No convertir cambiando la extensión a DOCX.

`review_sources.py` compara texto normalizado, inventaría rótulos y obtiene límites MINAM. `extract_data.py` obtiene tablas revisadas, aplica cotejos de sumas, genera los JSON y elimina el párrafo individual del PDF. Revise visualmente la página PDF 73 después de cada ejecución; una fuente modificada puede cambiar las posiciones y exigir adaptar la redacción. Los rangos de dependencias Python son de compatibilidad, no un entorno congelado: conservar versiones efectivas junto a cada nueva auditoría.

## Incorporar ASIS 2026 y posteriores

Guardar conjuntos por edición (`src/data/editions/2026.json`, por ejemplo), crear un registro de ediciones disponibles y parametrizar rutas/metadatos/portada/filtros. La edición actual ya separa datos, componentes y fuentes, pero todavía tiene una edición activa fija. Un selector solo debe habilitar años cuyos datos y documentos hayan pasado la revisión; no crear una serie interpolada.

Los periodos medidos pueden seguir siendo anteriores al año del ASIS. Cada indicador mantiene su periodo real. Comparar entre ediciones exige igualdad de definición, universo y cobertura; anotar cambios de metodología.

## Actualizar cartografía y establecimientos

Conservar fecha de recuperación, URL oficial, CRS, códigos UBIGEO, hash y carácter referencial. Verificar los 13 distritos y la correspondencia de valores. Nunca dibujar límites o coordenadas aproximados como oficiales. Las capas IPRESS requieren padrón oficial fechado de RIS/RENIPRESS, sin datos de pacientes, y revisión de código/categoría/microrred/latitud/longitud/estado. Incorporar cada punto solo tras cotejar su ubicación.

## Operación

Revisar alertas de cuotas del alojamiento, dependencias, enlaces y renovación de dominio si se añade uno. No se contrata dominio ni plan de pago en esta instalación. Las actualizaciones sanitarias necesitan un responsable institucional; no activar un refresco automático que publique datos sin validación.
