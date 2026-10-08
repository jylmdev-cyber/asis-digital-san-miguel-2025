# Cloudflare Pages Free: proyecto preparado

Esta guía prepara la publicación independiente en Cloudflare Pages. El código está en [GitHub](https://github.com/jylmdev-cyber/asis-digital-san-miguel-2025). La URL de Sites existente continúa disponible; todavía no se ha creado ni verificado una URL `pages.dev` para este proyecto.

## Conectar GitHub (recomendado)

1. Entrar a [Cloudflare Dashboard](https://dash.cloudflare.com/), elegir la cuenta institucional y abrir Workers & Pages → Create application → **Pages** → Import an existing Git repository.
2. Autorizar la integración GitHub para `jylmdev-cyber/asis-digital-san-miguel-2025` y seleccionar ese repositorio.
3. Elegir un nombre disponible. `asis-digital-san-miguel-2025` es una propuesta, no una reserva. Si se elige otro, ajustar `name` en `wrangler.jsonc` para que coincida.
4. Configurar los campos siguientes y guardar/desplegar.

| Campo | Valor |
|---|---|
| Rama de producción | `main` |
| Framework | Astro, salida estática |
| Root directory | Vacío / raíz del repositorio |
| Build command | `npm run build:pages` |
| Build output directory | `dist` |
| `NODE_VERSION` | `24` |
| `BASE_PATH` | `/` (también fijado por el script) |
| `SITE_URL` | URL HTTPS real del proyecto o dominio institucional |

**La raíz remota no es `web/`.** En el equipo la aplicación está en `C:/jimdev/asis-provincial/web`, pero esa carpeta constituye la raíz del repositorio GitHub. `package.json`, `src/` y `wrangler.jsonc` están directamente en la raíz remota.

Si aún no se conoce la URL, el primer build usa `CF_PAGES_URL`, que Cloudflare proporciona automáticamente. Tras obtener la dirección estable de producción, definir `SITE_URL` con esa URL y volver a desplegar. Así los enlaces canónicos, el sitemap y el QR apuntarán al dominio estable. Para previews puede dejarse `SITE_URL` vacío y usar la URL del despliegue suministrada por Cloudflare.

Los cambios en `main` se publican automáticamente una vez conectada la integración. No hacen falta claves de API para ese flujo. No crear Functions, Workers, D1, R2 ni un adaptador SSR: la aplicación entrega HTML y recursos estáticos.

## Archivos y comandos preparados

- `wrangler.jsonc`: nombre propuesto y carpeta `dist` para Pages.
- `.node-version`: Node 24; `package-lock.json` conserva las versiones instaladas.
- `scripts/build-pages.mjs`: compila con la URL elegida, genera QR/sitemap/robots y verifica el paquete.
- `public/_headers`: CSP, protección frente a framing y caché de un año para archivos con hash; datos/documentos/QR con revalidación.
- `scripts/validate-pages.mjs`: rechaza archivos privados/de desarrollo, enlaces simbólicos y tamaños/número superiores a Pages Free.

```powershell
npm ci
$env:SITE_URL = 'URL_HTTPS_REAL_ASIGNADA_POR_CLOUDFLARE'
npm run build:pages
npm run pages:dev
```

La dirección local se imprime en la terminal; el puerto configurado es 8788. `build:pages` exige una URL HTTPS de origen, sin ruta, credenciales, consulta ni fragmento. La generación del QR se hace dentro de `dist/`; conserva la copia fuente de Sites en `public/share/`.

## Publicación manual con Wrangler (alternativa)

Si se necesita Direct Upload, decidirlo antes de crear el proyecto: Cloudflare distingue proyectos Git y Direct Upload. Para mantenimiento continuo desde el repositorio, preferir la integración GitHub anterior.

```powershell
npx wrangler login
npx wrangler whoami
npx wrangler pages project create NOMBRE_REAL --production-branch main
$env:SITE_URL = 'URL_HTTPS_REAL_DEL_PROYECTO'
npm run build:pages
npm run pages:deploy -- --project-name NOMBRE_REAL --branch main
```

No ejecutar `project create` si el proyecto ya existe. Usar el nombre real elegido, incluyendo `name` en `wrangler.jsonc`. La sesión requiere que el propietario complete el login de Cloudflare; no enviar tokens por el chat ni guardarlos en Git. Un API token para automatización debe tener permisos Pages adecuados y almacenarse como secreto del proveedor, no en estos archivos.

## Condiciones Free comprobadas

Cloudflare publica 500 builds por mes, uno simultáneo, timeout de 20 minutos, máximo 20.000 archivos y 25 MiB por archivo. El paquete actual se comprueba en cada `build:pages`. Los límites de Functions son adicionales y este proyecto no las utiliza. El subdominio gratuito de Pages y HTTPS permiten compartir la plataforma sin comprar un dominio. Las condiciones pueden cambiar; comprobarlas antes de activar servicios adicionales.

## Comprobar la nueva publicación

Validación local realizada con Wrangler Pages: 29 archivos, 5,31 MiB totales y PDF máximo de 3,61 MiB; ocho rutas correctas y respuesta 404 para rutas inexistentes. Se comprobaron cabeceras CSP/caché, sitemap, robots, PDF y QR. Las pruebas de navegador cubrieron filtros, exportaciones CSV/PNG, mapa, búsqueda, modo oscuro y pantallas móviles/tablet: sin errores de ejecución ni infracciones detectadas por axe en las vistas examinadas. `npm run check` y las siete pruebas de datos pasaron. Estas verificaciones corresponden al emulador local; la URL pública de Cloudflare deberá comprobarse después de conectar la cuenta.

Confirmar el estado de despliegue exitoso y la URL entregada por Cloudflare; abrirla y verificar las ocho rutas directas, filtros, CSV/PNG, PDF, QR y metadatos. Comprobar `/robots.txt`, `/sitemap.xml`, cabeceras de seguridad y caché. Una ruta inexistente debe responder 404. No configurar un rewrite SPA a `index.html` porque cada sección tiene su HTML propio.

Si se añade un dominio, conectarlo desde Custom domains del proyecto Pages, establecer `SITE_URL` con ese origen y recompilar. Mantener el historial de GitHub y el rollback del proveedor.

## Referencias oficiales

Consulta: 7 de octubre de 2026. [Astro en Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-an-astro-site/), [build y variables](https://developers.cloudflare.com/pages/configuration/build-configuration/), [Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/), [Wrangler configuration](https://developers.cloudflare.com/pages/functions/wrangler-configuration/), [headers](https://developers.cloudflare.com/pages/configuration/headers/), [límites Free](https://developers.cloudflare.com/pages/platform/limits/).
