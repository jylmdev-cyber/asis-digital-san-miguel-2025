# Verificación realizada y límites

Revisión del 7 de octubre de 2026 (hora de Perú). La coincidencia documental y aritmética no certifica la exactitud de los registros de salud originales.

## Datos y privacidad

Siete pruebas automatizadas verifican procedencia/periodo/unidades, población distrital por año y curso de vida, sumas de morbilidad/mortalidad y sexo, inventarios de servicios, tratamiento de periodos históricos/valores ambiguos, correspondencia de geodata y ausencia de relato clínico en el índice público. Los cotejos declarados en `asis.json` pasan.

La extracción verifica además que los marcadores del relato individual no aparecen en el texto recuperable del PDF derivado. Se inspeccionó visualmente su página 73 tras la redacción efectiva. Se revisaron páginas de tablas, mapas y una hoja de contacto de imágenes. No se publica el Word, PDF original ni auditoría bruta.

## Aplicación

`npm run check`: TypeScript y comprobación Astro. `npm test`: 7 pruebas. `npm run build`: ocho secciones y página 404 estáticas. Playwright en Chrome comprobó las ocho rutas, filtros de distrito/periodo, CSV con fuente, exclusión de gráficos para emigración inconsistente, búsqueda/Escape, cambio de tema, PNG con procedencia, selección de polígonos, navegación móvil y ausencia de desbordamiento a 390 y 768 píxeles.

Axe detectó **cero incidencias** en las ocho rutas de modo claro, tablero oscuro y tablero móvil, con reglas WCAG 2 A/AA, 2.1 y 2.2 AA disponibles. Se corrigieron contraste, señalización de enlaces y tamaño/espaciado de objetivos detectados. Esto no equivale a una certificación WCAG: faltan revisión humana integral, tecnologías de asistencia y auditoría de todos los estados/zoom.

Las capturas del prototipo fueron inspeccionadas; existen tablas alternativas para gráficos y tablas territoriales para el mapa. Las animaciones respetan `prefers-reduced-motion`. El script QA registra fallos de ejecución y resultados en `qa/`, que no se sube al repositorio.

## Rendimiento y publicación

HTML prerenderizado por capítulo, tipografía local, gráficos bajo demanda, índice de búsqueda diferido y GeoJSON local. No hay llamadas a servicios sanitarios ni mapas de teselas en el navegador. ECharts, React y Leaflet implican JavaScript de cliente; en equipos modestos conviene vigilar su coste de carga. Core Web Vitals requiere medición de campo con tráfico real: no se declara una puntuación ni un cumplimiento sin esa evidencia.

Metadatos title/description/canonical/Open Graph/Twitter, idioma español y favicon. No se añadió analítica ni rastreadores. Los encabezados CSP y otras políticas se entregan en `_headers`; comprobar su aplicación cuando se migra de proveedor. El despliegue se verifica con un estado nativo `succeeded` y URL de producción. GitHub CI repite tipado, pruebas y build sobre cada push.

## Medición de laboratorio

Lighthouse sobre el build estático local, perfil móvil simulado: rendimiento 98/100, accesibilidad 100/100, SEO 100/100, buenas prácticas 81/100. LCP 2,1 s; FCP 1,8 s; CLS 0; TBT 10 ms. La prueba usa HTTP local, por lo que falla la comprobación HTTPS. Se excluyó una solicitud externa inyectada por el entorno de seguridad del equipo, ajena a los recursos de la aplicación. Son resultados de una ejecución local, sin medición de INP ni tráfico de campo; no representan una garantía de rendimiento en Internet.
