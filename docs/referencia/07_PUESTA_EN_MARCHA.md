# Puesta en marcha local

## Requisitos y contexto

La aplicación se ha construido en este entorno con Node 24.22.3; `package.json` admite Node >=22.13.0. Utiliza una versión compatible con el lockfile. En Windows puede trabajarse con PowerShell o WSL; los comandos Node incluidos evitan depender de Bash para el arranque normal.

El código original utiliza Vinext sobre Workers: `next.config.ts` y la estructura App Router no significan que baste con ejecutar `next dev`. El comando de desarrollo es el de `package.json`.

## Primera instalación

Desde la carpeta extraída:

```sh
cd proyecto
npm ci
npm run setup:local
npm run build
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_fine_randall_flagg.sql
npm run db:seed:local
npm run dev
```

- `setup:local` crea un perfil portable y un usuario/contraseña nuevos solo para desarrollo. La contraseña temporal se muestra una vez en el terminal; se guarda su derivación, no el texto, en `.dev.vars`.
- Si `.dev.vars` ya existe, no se sobrescribe. Para elegir credenciales propias, edítalas mediante un procedimiento local seguro y recalcula la derivación que espera el servidor.
- El comando SQL inicial se ejecuta una sola vez sobre una base vacía. No vuelvas a ejecutar una migración ya aplicada. Para cambios futuros sigue el historial de migraciones.
- `db:seed:local` importa el contenido publicado solo si no existe `content.main`. No sobrescribe contenido local previo.
- El servidor de desarrollo portable suele usar `http://localhost:5173`; utiliza la URL exacta que imprima el comando.
- Abre `/admin` e inicia sesión con las credenciales locales recién generadas. `/pantallas/admin` es una vista de diseño sin guardado.

## Variables del administrador

| Variable | Uso |
|---|---|
| `ADMIN_USERNAME` | Usuario del panel |
| `ADMIN_PASSWORD_SALT` | Salt de texto utilizado por PBKDF2 |
| `ADMIN_PASSWORD_HASH` | Derivación hexadecimal PBKDF2-SHA256, 100000 iteraciones, 32 bytes |

El script genera estos valores de forma compatible con `app/api/login/route.ts`. El alojamiento de producción debe configurarlos como secretos del entorno. No se incluyen los valores de la propuesta publicada.

## Verificación y ejecución compilada

```sh
npm run typecheck
npm run test:solidario
npm run test:clasificaciones
npm run build
npm start
```

La prueba solidaria ejecuta los handlers reales con SQLite en memoria y almacenamiento simulado; no cobra, no llama a una pasarela ni modifica producción. El resto de pruebas heredadas se explica en `08_ESTADO_Y_PENDIENTES.md`.

## Alojamiento independiente

Esta copia no lleva el identificador del Site existente. Para Cloudflare propio habrá que provisionar D1 y R2, configurar bindings `DB`/`BUCKET`, aplicar migraciones y secretos y revisar el proceso de despliegue del Worker generado. El paquete no crea esos recursos ni modifica DNS.

Para otro backend, adaptar `lib/server.ts`, las rutas, el almacenamiento y la autenticación; mantener los contratos de producto. La interfaz no debe depender de una cuenta de ChatGPT para ser pública en el dominio definitivo.

## Problemas habituales

- «No se ha podido cargar contenido»: comprueba el binding `DB` y que se aplicó la migración local.
- Login no configurado: revisa `.dev.vars`, reinicia el servidor y utiliza las credenciales locales, no las de ChatGPT.
- Cookie de sesión: el diseño actual usa `Secure`; verifica un navegador que trate loopback como contexto local confiable o usa HTTPS local. No elimines `Secure` de producción para resolver una limitación de desarrollo.
- Subidas fallidas: confirma `BUCKET`, formato permitido y límite de 10 MB.
- Enlaces solidarios inactivos: es correcto si el evento está cerrado o la URL específica está vacía.
- Un álbum histórico vacío en la galería propia: sus fotos siguen en el álbum externo; no hay que inventar una importación que no se ha realizado.
