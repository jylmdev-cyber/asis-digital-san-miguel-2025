# Propuesta técnica y decisiones

## Comparación

| Opción | Rendimiento y SEO | Interactividad y mantenimiento | Despliegue estático | Decisión |
|---|---|---|---|---|
| Nuxt 4 + Vue 3 + TypeScript + Tailwind | Prerenderizado disponible; adecuado para aplicaciones Vue | Componentes y convenciones completas; útil con equipos Vue o futuros servicios | Generar/prerenderizar todas las rutas; no requerir funciones del servidor | Viable, pero añade convenciones innecesarias para esta edición cerrada |
| React + Vite + TypeScript + Tailwind | Bundle rápido; una SPA necesita resolver HTML de cada ruta, SEO y rutas directas | Excelente ecosistema de visualización; filtros complejos sencillos | Muy compatible; el alojamiento debe resolver rutas de la SPA o usar hash | Viable; exige trabajo adicional para HTML indexable por capítulo |
| Astro + componentes React + TypeScript | HTML prerenderizado por sección; interactividad en cliente y recursos diferidos | Componentes reutilizables; datos independientes; permite ampliar por edición | `astro build` produce `dist/`, sin servidor | **Seleccionada** |

Referencias: [Nuxt deployment](https://nuxt.com/docs/4.x/getting-started/deployment), [Vite static deploy](https://vite.dev/guide/static-deploy.html), [Astro islands](https://docs.astro.build/en/concepts/islands/). Consulta: 7 de octubre de 2026.

La solución usa Astro para ocho rutas de contenido y React para el observatorio de cada ruta. No se afirma que cada tarjeta sea una isla independiente: el componente `Observatory` se hidrata completo; las bibliotecas de gráficos, mapas y el índice documental se cargan aparte. Esto facilita filtros sincronizados con la URL y conserva HTML inicial con contenidos principales. Una siguiente optimización, si el uso de red móvil lo requiere, es dividir ese componente por sección.

CSS propio con variables sustituye Tailwind: ocho módulos comparten un sistema pequeño y coherente, sin añadir una dependencia de estilos. TypeScript comprueba props y utilidades; el JSON se valida mediante pruebas de unidades, sumas y procedencia. Las dependencias exactas están fijadas en el lockfile.

## Flujo

```text
PDF/Word privados → extracción y comparación local → revisión de tablas y alertas
                     ↓
JSON agregado + PDF derivado + límites MINAM → pruebas → Astro build
                     ↓
HTML por capítulo + React + recursos diferidos → CDN estática con HTTPS
```

ECharts comunica comparaciones con barras de base cero y distribución por sexo/curso de vida. No se presenta esa distribución como una pirámide quinquenal. Chart.js sería suficiente para barras sencillas, pero ECharts aporta leyendas, exportación y soporte de opciones uniformes; D3 no se necesita para las visualizaciones disponibles. Leaflet usa 13 polígonos locales del MINAM sin teselas ni APIs externas en tiempo de ejecución.

Cada conjunto contiene `id`, `title`, `module`, `period`, `unit`, `columns`, `rows`, `source`, `note` y `status`. La fuente incluye documento, página física, página impresa, etiqueta del cuadro e institución declarada. Cada descarga CSV incorpora esos campos. La fila provincial se separa de los distritos para evitar doble conteo. Los valores nulos se conservan como faltantes.

## Navegación

| Ruta | Contenido y límites |
|---|---|
| `/` | Población, IPRESS, atenciones, defunciones, problemas y acceso a capítulos |
| `/territorio/` | Distritos, altitudes y cartografía oficial referencial |
| `/demografia/` | Población 2023–2025, sexo/curso 2025, comparación territorial y SIS |
| `/epidemiologia/` | Morbilidad, mortalidad, vigilancia y eventos materno/perinatales, con universos diferenciados |
| `/determinantes/` | Línea social histórica 2017; indicadores dudosos solo en tabla |
| `/servicios/` | Categorías, recursos humanos, infraestructura, saneamiento, conectividad y capacidad documentada |
| `/prioridades/` | Síntesis de problemas y acciones del cuadro original, sin puntuaciones creadas |
| `/biblioteca/` | PDF derivado, índice del documento, fuentes, glosario, descargas y observaciones |

Los parámetros `distrito`, `microrred`, `periodo`, `indicador` y `curso` conservan el estado cuando corresponde. La búsqueda combina rutas, títulos de conjuntos y texto del PDF público. Los datos se filtran solo en dimensiones existentes; no se imputan causas provinciales a un distrito.

## Seguridad y continuidad

Sin autenticación ni datos del paciente. Exportación CSV protegida contra interpretación de fórmulas en texto. Enlaces externos seguros; encabezados de seguridad para proveedores compatibles. La CSP permite estilos/scripts inline necesarios para Astro, sin `eval`, plugins ni framing. El archivo `_headers` depende del proveedor: GitHub Pages no lo interpreta.

Las ediciones futuras reutilizan componentes y esquema; antes de introducir un selector multianual hay que agregar archivos completos por edición, un registro de ediciones y parametrizar los valores 2025 de portada, metadatos y filtros. Esta versión no simula datos 2026/2027 ni un selector operativo para años inexistentes. El procedimiento está en la guía de actualización.
