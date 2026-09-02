# yt-video · Miniaturas y títulos que se actualizan solos

Proyecto que actualiza automáticamente el título y la miniatura de uno o
varios vídeos de YouTube en función de una estadística (días desde la
publicación, visitas, likes...). Está pensado para ejecutarse **una vez por
invocación**, disparado por un `cron` externo — no hay servidor, no hay
interfaz gráfica, no gasta más cuota de la API que la imprescindible.

## Cómo funciona

1. `cron` ejecuta `main.py` cada X tiempo (ej: 1 vez al día).
2. Por cada vídeo señalado en `config.json`, el programa consulta la
   estadística elegida (`estadisticas/`).
3. Compara el valor con el último guardado en `almacenamiento/estado.json`.
4. Si **no ha cambiado**, no hace nada más (0 cuota extra).
5. Si **ha cambiado**, genera una miniatura nueva con Pillow
   (`miniatura/generador_miniatura.py`): fondo negro liso de 1280x720 con
   el texto de la estadística en blanco, centrado y a tamaño ajustado
   automáticamente, y actualiza título + miniatura en YouTube
   (`youtube/cliente_youtube.py`).

## Estructura

```
configuracion/   Carga de config.json
entidades/       Clase Video (los datos de cada vídeo señalado)
estadisticas/    Una clase por estadística (dias, visitas, likes) + fábrica
miniatura/       Generador de miniaturas con Pillow
youtube/         Autenticación OAuth2 y llamadas a la API
almacenamiento/  Guarda el último valor conocido de cada estadística
orquestador.py   Flujo principal que conecta todo lo anterior
main.py          Punto de entrada (lo que llama cron)
```

Añadir una estadística nueva (por ejemplo "suscriptores en el vídeo"):
crea `estadisticas/estadistica_suscriptores.py` heredando de
`ProveedorEstadistica` y regístrala en `fabrica_estadistica.py`. No hay que
tocar nada más.

## Configuración inicial

### 1. Instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Credenciales de Google Cloud

1. Entra en [Google Cloud Console](https://console.cloud.google.com/),
   crea un proyecto y activa **YouTube Data API v3**.
2. En "Credenciales" crea un **ID de cliente OAuth 2.0** de tipo
   "Aplicación de escritorio".
3. Descarga el JSON y guárdalo como `credenciales/client_secret.json`.

### 3. Clave de cifrado del token

`credenciales/token.json` se guarda siempre cifrado en disco. Genera tu
propia clave (una por proyecto, no la compartas ni la reutilices):

```bash
python -m seguridad.generar_clave
```

Copia la línea que imprime dentro de un fichero `secretos.env` en la raíz
del proyecto (usa `secretos.env.example` como plantilla). Ese fichero
**nunca** se sube a git.

### 4. Primera autenticación (hazlo en tu ordenador, no en el hosting)

La primera vez hace falta abrir un navegador para conceder permisos, así
que ejecuta el proyecto una vez en local:

```bash
python main.py
```

Se abrirá el navegador, aceptas permisos, y se genera
`credenciales/token.json` **ya cifrado** con la clave de `secretos.env`.
Sube ambos ficheros al hosting (`token.json` + `client_secret.json`), y
sube también `secretos.env` por un canal seguro (nunca dentro del propio
repositorio) — sin esa clave, el token guardado es inútil. Las siguientes
ejecuciones renuevan el token solas, sin volver a pedir navegador.

### 5. Rellenar `config.json`

- `id_video`: el ID del vídeo (lo que va después de `watch?v=` en la URL).
- `tipo_estadistica`: `dias`, `visitas` o `likes`.
- `plantilla_titulo` / `texto_miniatura`: usan `{valor}` como marcador,
  que se sustituye por el valor actual de la estadística.

### 6. Programar el cron

Cada ejecución del script cuesta muy poca cuota (una lectura +, si hay
cambio, un `update` de título y un `set` de miniatura ≈ 100 unidades por
vídeo actualizado, sobre una cuota diaria de 10.000). Con estadística
"días", una vez al día es más que suficiente:

```bash
crontab -e
```

```cron
# Todos los días a las 08:00
0 8 * * * cd /ruta/a/yt-video && /ruta/a/yt-video/.venv/bin/python main.py >> registro.log 2>&1
```

Si algún día cambias `tipo_estadistica` a `visitas` y quieres más
frecuencia, basta con ajustar la expresión cron (ej. `0 */6 * * *` para
cada 6 horas) — el propio programa ya evita gastar cuota si el valor no
ha cambiado entre ejecuciones.

## Seguridad de las credenciales

El ámbito de OAuth que necesita este proyecto para poder cambiar el título
y la miniatura (`videos.update` / `thumbnails.set`) es, por diseño de la
API de YouTube, el mismo que hace falta para **borrar vídeos**
(`videos.delete` exige exactamente los mismos ámbitos). No existe ningún
ámbito más restringido — así que `credenciales/token.json` se trata como
si fuera la contraseña de tu canal, con varias capas:

- **Cifrado en disco**: `token.json` nunca se guarda en texto plano.
  `seguridad/cifrador_token.py` lo cifra con la clave de `secretos.env`
  al guardarlo, y lo descifra solo en memoria justo antes de cada llamada
  a Google. Si alguien copia el fichero sin la clave, no sirve de nada.
- **La clave vive fuera del repositorio**: `secretos.env` está en
  `.gitignore` — nunca viaja junto al código. En el hosting, se sube por
  un canal aparte (o, mejor, como *secret* cifrado de la plataforma:
  GitHub Actions Secrets, variables de entorno del panel del VPS, etc.).
- **Permisos de fichero**: tanto `token.json` como `secretos.env` se
  guardan con `600` (solo tu usuario puede leerlos).
- **Revocación de emergencia**: si sospechas que algo se ha filtrado,
  revoca el acceso al instante desde
  [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
  — busca la app y quita el acceso. El token deja de funcionar en el momento,
  cifrado o no.
- Si despliegas en un hosting compartido con otros usuarios/procesos,
  revisa también los permisos de la carpeta `credenciales/` completa
  (`chmod 700`).

**Importante — lo que el cifrado NO resuelve**: si un atacante compromete
el propio proceso en ejecución (o el hosting completo, con acceso a la
variable de entorno `YT_VIDEO_CLAVE_CIFRADO`), puede descifrar el token
igual que lo hace tu script. El cifrado protege contra copias del disco,
backups filtrados o accesos que no llegan a comprometer también el
entorno de ejecución — no es una barrera mágica, es una capa más.
