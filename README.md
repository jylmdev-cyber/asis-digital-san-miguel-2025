# ASIS Digital 2025 | RIS San Miguel

Observatorio estático que convierte el ASIS en ocho secciones navegables, con gráficos, cartografía, tablas, búsqueda y referencias a la fuente. Adaptación digital pendiente de validación institucional.

[Abrir plataforma](https://asis-digital-san-miguel-2025.jimdev.chatgpt.site) · [Código fuente](https://github.com/jylmdev-cyber/asis-digital-san-miguel-2025)

La información publicada incluye **36 conjuntos de datos, 515 filas y 19 observaciones de calidad**. Los determinantes sociales conservan el año 2017; la población tiene series 2023–2025. Se usan agregados del PDF y límites referenciales oficiales del MINAM. Los indicadores sanitarios representan sus universos documentados, sin calcular tasas con denominadores inconsistentes.

## Ejecutar

Node.js 24 o posterior. El archivo `package-lock.json` fija las versiones de la instalación verificada.

```sh
npm ci
npm run dev
npm run check
npm test
npm run build
npm run preview
```

Abra la dirección que imprima Astro. Para comprobar el navegador, instale Chrome y ejecute `npm run qa`, usando `QA_URL` con la dirección local real; el valor predeterminado de esta instalación es `http://127.0.0.1:4322/`. También puede instalar Chromium con `npx playwright install chromium` y cambiar el canal del script.

## Entregables

- [Diagnóstico e inventario documental](docs/DIAGNOSTICO.md).
- [Comparación y arquitectura recomendada](docs/ARQUITECTURA.md).
- [Diseño y prototipo](docs/PROTOTIPO.md).
- Aplicación funcional: `src/`, `public/`, `tests/`.
- [Guía de actualización](docs/ACTUALIZACION.md) y [validación](docs/VALIDACION.md).
- [Comparación de alojamiento y despliegue gratuito](docs/DESPLIEGUE.md).
- [Plan priorizado y alcance](docs/PLAN.md).

## Estructura

```text
src/pages/             Rutas HTML estáticas y metadatos
src/components/        Dashboard, gráficos, mapa, tablas
src/data/asis.json     Datos, unidades, periodos, fuentes y observaciones
src/lib/data.ts        Tipos, filtros, formatos y exportación CSV
src/styles/            Temas, responsive, impresión y movimiento reducido
public/data/           JSON público, índice de páginas y GeoJSON MINAM
public/documents/      Copia PDF pública con relato individual retirado
scripts/               Extracción reproducible y pruebas de navegador
tests/                 Conciliación y trazabilidad de agregados
docs/                  Diagnóstico, decisiones y mantenimiento
.openai/hosting.json   Destino de Sites y carpeta estática dist
```

Astro + React + TypeScript, ECharts y Leaflet. CSS con variables de diseño; no servidor, base de datos, telemetría ni credenciales del visitante. Los gráficos se cargan al aproximarse al área visible; el índice completo se solicita cuando se abre la búsqueda.

## Fuentes y publicación

El PDF original de 97 páginas se encuentra en el directorio de trabajo del propietario y **no se incluye en este repositorio**. Tampoco se publica el archivo Word binario `ASIS_RED_SAN_MIGUEL_2026_FINAL.doc` ni el texto bruto de auditoría. No se encontró el DOCX solicitado. La biblioteca explica las diferencias de edición y ofrece una **copia derivada**, con el párrafo de un caso individual retirado de la página PDF 73. Los agregados se conservan.

El código QR para compartir se encuentra en `public/share/` y en la biblioteca. Puede regenerarse con `node scripts/generate-qr.mjs` después de fijar `SITE_URL`.

La interfaz permite filtros solo cuando el conjunto tiene esa dimensión. La pertenencia a microrred está verificada parcialmente para Nanchoc y La Florida. No se dispone de coordenadas verificadas de IPRESS ni padrón nominal completo: no se inventan puntos ni asignaciones territoriales.

El estado de publicación se confirma mediante el servicio de despliegue. La plataforma puede migrarse a cualquier alojamiento estático usando `dist/`; vea la guía de despliegue. El uso y redistribución institucional de los documentos debe conservar sus fuentes y condiciones de autorización.
