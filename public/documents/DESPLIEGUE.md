# Alojamiento y publicación

Comparación verificada el **7 de octubre de 2026** en documentación oficial. Los planes pueden cambiar; consultar otra vez antes de migrar.

| Servicio | Compatibilidad y plan gratuito | Límites relevantes | Subdominio / HTTPS / GitHub automático | Ventajas y limitaciones |
|---|---|---|---|---|
| Cloudflare Pages | Astro estático, Vite/React y Nuxt prerenderizado; plan Free | 500 builds/mes, 1 simultáneo, timeout 20 min, 20.000 archivos, 25 MiB/archivo | `pages.dev`; HTTPS; integración GitHub | CDN y encabezados; buena opción institucional estática. Funciones tienen cuotas separadas; verificar política y cuenta institucional |
| GitHub Pages | `dist/` estático; gratis en repositorios públicos | Sitio máximo 1 GB, tráfico blando 100 GB/mes, timeout 10 min; 10 builds/h blando salvo workflow Actions propio | `github.io`; HTTPS; GitHub Actions | Código y publicación juntos; subruta necesita BASE_PATH, no encabezados personalizados. No sirve para SaaS/comercio ni transacciones sensibles |
| Netlify Free | Astro y otros frameworks; plan gratuito | 300 créditos/mes compartidos: deploy producción 15, tráfico 20/GB, solicitudes 2/10.000 | `netlify.app`; HTTPS; GitHub | Configuración sencilla y previews. El presupuesto incluye descargas del PDF; al agotarse se pausan los proyectos del equipo hasta restablecer créditos |
| Vercel Hobby | Astro estático, React y Nuxt; Hobby gratuito | Restringido a uso personal no comercial; 100 GB Fast Data Transfer, 1.000.000 CDN requests; sin compra de uso adicional en Hobby | `vercel.app`; HTTPS; GitHub | Buen flujo de previews, pero **no asumir elegibilidad del uso institucional**; comprobar términos antes de elegir |

Fuentes: [Cloudflare límites](https://developers.cloudflare.com/pages/platform/limits/), [Cloudflare integración GitHub](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/), [GitHub límites](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [GitHub HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https), [Netlify planes](https://www.netlify.com/pricing/), [Netlify créditos](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/), [Vercel Hobby](https://vercel.com/docs/plans/hobby).

**Recomendación:** Cloudflare Pages para una cuenta institucional que busque alojamiento estático gratuito e independiente. GitHub Pages es alternativa sencilla. La instalación realizada en esta sesión utiliza el servicio **Sites conectado a la cuenta del propietario**, con subdominio `chatgpt.site`; no se presenta como una cuenta Cloudflare Pages contratada ni se garantiza que las condiciones de Sites sean iguales a Free de Cloudflare.

## Instalación publicada

URL configurada: [ASIS Digital San Miguel](https://asis-digital-san-miguel-2025.jimdev.chatgpt.site).

Sites utiliza `.openai/hosting.json` con `static.directory: dist`. El código fuente exacto se envía antes de guardar cada versión; solo se despliega una versión guardada. La confirmación de éxito y URL procede del estado nativo del despliegue. No publicar credenciales de escritura en comandos, archivos o historial.

## Cloudflare Pages

1. Conectar el repositorio GitHub desde Workers & Pages → Pages → importar repositorio.
2. Elegir Astro; comando `npm run build`; salida `dist`; Node.js 24.
3. Definir `SITE_URL=https://nombre.pages.dev`, `BASE_PATH=/` y rama `main`.
4. Desplegar y comprobar la URL entregada, HTTPS, rutas directas, PDF y filtros.
5. Cada push a `main` genera la versión; mantener rollback y propiedad institucional.

No se necesita base de datos ni funciones. `_headers` se copia a `dist/`. No activar SSR.

## GitHub Pages

El repositorio contiene un workflow manual `pages.yml`. Activar Settings → Pages → GitHub Actions y ejecutar el workflow. Para despliegue continuo, añadir el evento `push` a `main` después de elegir ese alojamiento como destino.

El workflow determina el subdirectorio desde el nombre del repositorio y construye con `SITE_URL=https://PROPIETARIO.github.io` y `BASE_PATH=/REPOSITORIO/`. Astro genera los enlaces a datos, gráficos, PDF y rutas con ese prefijo. Un dominio propio requiere `BASE_PATH=/` y su `SITE_URL` correspondiente. El workflow CI comprueba cada push sin cambiar la audiencia ni publicar en otro proveedor.

## Netlify y Vercel

Importar el repositorio, usar `npm run build` y `dist`, Node.js 24, `BASE_PATH=/`, `SITE_URL` con la URL que asigne el proveedor. `netlify.toml` incluye esos parámetros de build; Vercel detecta Astro o puede usar `vercel.json`. Revisar los créditos y la elegibilidad de Hobby respectivamente. No crear redirects SPA: existen páginas HTML por sección.

## Revisión después de cada versión

Verificar enlaces por sección y filtros compartidos, descargas de datos, número de páginas del PDF derivado, ausencia de texto sensible, HTTPS y metadatos. Conservar una versión anterior y registrar fuentes/periodo/observaciones junto a cada cambio. No sustituir un archivo anual silenciosamente ni registrar claves en el repositorio.
