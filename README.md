# Aprendo en casa

Colección de actividades educativas interactivas hechas en familia, organizadas por
curso, semestre y asignatura. Se publican con GitHub Pages para poder usarlas desde
el celular o la tablet, sin instalar nada.

---

## 1. Publicar el sitio (una sola vez)

1. Crea un repositorio **público** en GitHub, por ejemplo `aprendo-en-casa`.
2. Sube el contenido de esta carpeta (no la carpeta, sino lo que hay **dentro**:
   `index.html` debe quedar en la raíz del repositorio).
3. Entra a **Settings → Pages**.
4. En *Source* elige **Deploy from a branch**, rama `main`, carpeta `/ (root)`, y guarda.
5. Espera 1 o 2 minutos. El sitio queda en:

```
https://TU-USUARIO.github.io/aprendo-en-casa/
```

> Reemplaza `TU-USUARIO` por tu nombre de usuario de GitHub.

### Dejarlo como app en el iPhone

Abre esa dirección en **Safari** → botón Compartir → **Añadir a pantalla de inicio**.
Queda un ícono igual que una app y se abre a pantalla completa.

---

## 2. Estructura

```
├─ index.html            Portada: el menú que usa la niña
├─ actividades.json      Catálogo de todas las actividades
├─ plantilla/base.html   Esqueleto para crear actividades nuevas
└─ 1-basico/
   ├─ semestre-1/
   │  ├─ ciencias-naturales/
   │  ├─ lenguaje/
   │  ├─ matematica/
   │  └─ historia/
   └─ semestre-2/ ...
```

Para el año siguiente basta con agregar `2-basico/` al lado, con la misma forma.
Nada de lo anterior se mueve ni se rompe.

---

## 3. Agregar una actividad nueva

1. Copia `plantilla/base.html` a la carpeta que corresponda y renómbralo.
   Ejemplo: `1-basico/semestre-1/matematica/sumar-hasta-20.html`
2. Edita en el archivo: el título, el texto de la pregunta y el arreglo `PREGUNTAS`.
3. Agrega la entrada en `actividades.json`, dentro de `"actividades"`:

```json
{
  "id": "mat-sumar-hasta-20",
  "titulo": "Suma y gana",
  "curso": "1-basico",
  "semestre": 1,
  "asignatura": "matematica",
  "objetivo": "Sumar números hasta el 20 de forma aditiva.",
  "archivo": "1-basico/semestre-1/matematica/sumar-hasta-20.html",
  "emoji": "🔢",
  "fecha": "2026-09-05"
}
```

4. Sube los cambios. La portada se actualiza sola.

---

## 4. Reglas del proyecto

**Técnicas**
- Una actividad = **un solo archivo HTML** con CSS y JS adentro, sin librerías externas.
  Así funciona sin internet y se puede enviar por correo a la profesora.
- Nombres de archivos y carpetas en minúscula, sin tildes, sin ñ, sin espacios.
  Usa guiones: `clasificar-animales.html`, nunca `Clasificación Animales.html`.
- Pensado para pantalla táctil: se juega **tocando**, nunca arrastrando.
- Narración por voz en español con botón para silenciar.

**Pedagógicas**
- El error nunca castiga: se puede reintentar con una pista amable.
- Cada acierto entrega un dato breve que ella pueda repetir en su evaluación.
- Máximo 8 a 10 ítems por nivel.
- Siempre termina con un logro visible.

**Privacidad**
El repositorio es público. No incluir nombre completo de la niña, colegio,
nombres de profesores, fotos ni ningún dato personal.

---

## 5. Contenido actual

| Curso | Semestre | Asignatura | Actividad |
|---|---|---|---|
| 1° Básico | 1 | Ciencias Naturales | Expedición Animal — clasificar animales por movimiento y cubierta corporal |
