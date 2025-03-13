# simple-google-oidc-server
Servidor con Flask que se autentica con el OAuth2 de Google y logea cosas a la consola. Es un ejemplillo que me hice para mi charla del t3chf3st 2025, _"Qué pasa cuando pinchas en "Login con..."?_. Crear un _service provider_ me daba la posibilidad de enseñar el flujo desde el punto de vista de la aplicación, así que preparé esto rápidamente. La mayoría del código es _boilerplate_ para sacarme los logs que luego enseño en la presentación, y la aplicación en sí no hace nada, ni es tampoco ejemplo de nada en particular, más allá de dejar constancia de que no me he inventado las capturas de pantalla que enseño :P

## Prerequisitos
Necesitas crear una aplicación de OAuth en Google, y luego añadir tu `CLIENT_ID` y `CLIENT_SECRET` en un fichero `.env`.
Y tener Python instalado, claro.

## Instalación

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para arrancar el servidor:
`python app.py`

Y estará activo en `localhost:3000`.
