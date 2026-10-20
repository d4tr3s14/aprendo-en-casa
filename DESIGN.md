---
name: qa-orchestrator · estilo Devin Desktop
version: 1.0
source: Extraído de https://devin.ai/desktop (maqueta HTML de la app de escritorio), 2026-10-02
description: Interfaz de herramienta de trabajo sobria, clara y densa. Neutros casi blancos, un solo acento azul, bordes de 1px muy suaves, tipografía pequeña (12–13px) y estados comunicados con puntos de color.
colors:
  light:
    bg-page: "#FCFCFC"          # fondo del área principal
    bg-wash: "#F8F8F8"          # fondo de la barra lateral
    bg-elevated: "#FFFFFF"      # tarjetas, paneles, segmento activo
    text-primary: "#191919"
    text-strong: "#000000"
    text-secondary: "rgba(25,25,25,0.56)"
    text-tertiary: "rgba(25,25,25,0.40)"
    border-primary: "rgba(0,0,0,0.08)"
    border-secondary: "rgba(0,0,0,0.06)"
    tint-strong: "rgba(0,0,0,0.08)"   # hover
    tint-soft: "rgba(0,0,0,0.06)"     # ítem activo, track de segmentos
    tint-faint: "rgba(0,0,0,0.04)"
    accent: "#317CFF"
    accent-tint: "rgba(51,125,244,0.10)"
    button-neutral: "#363636"   # botón primario oscuro
    green: "#00A558"
    green-tint: "rgba(62,237,155,0.20)"
    red: "#F53B3A"
    red-tint: "rgba(245,59,58,0.12)"
    orange: "#F58E3A"
    orange-tint: "rgba(245,142,58,0.12)"
    purple: "#956CDE"
    purple-tint: "rgba(149,108,222,0.12)"
  dark:
    bg-page: "#141414"
    bg-wash: "#191919"
    bg-elevated: "#1F1F1F"
    text-primary: "rgba(255,255,255,0.90)"
    text-strong: "#FFFFFF"
    text-secondary: "rgba(255,255,255,0.52)"
    text-tertiary: "rgba(255,255,255,0.40)"
    border-primary: "rgba(255,255,255,0.08)"
    border-secondary: "rgba(255,255,255,0.04)"
    tint-strong: "rgba(255,255,255,0.08)"
    tint-soft: "rgba(255,255,255,0.05)"
    tint-faint: "rgba(255,255,255,0.03)"
    accent: "#49B0FF"
    accent-fill: "#4489FF"
    accent-tint: "rgba(51,125,244,0.10)"
    button-neutral: "#F9F9F9"   # en oscuro el botón primario se invierte (claro con texto negro)
    green: "#00EC7E"
    green-tint: "rgba(0,236,126,0.08)"
    red: "#F53B3A"
    red-tint: "rgba(245,59,58,0.12)"
    orange: "#F58E3A"
    orange-tint: "rgba(245,142,58,0.08)"
    purple: "#956CDE"
    purple-tint: "rgba(149,108,222,0.12)"
typography:
  ui: "Inter, system-ui, sans-serif"
  mono: "'Geist Mono', 'IBM Plex Mono', ui-monospace, monospace"
  display: "Inter, system-ui, sans-serif"   # el sitio usa NB International Pro (comercial); Inter es el reemplazo libre
  scale:
    meta: { size: 12px, line: 16px, weight: 400 }      # "42m ago", "Working…", etiquetas de filtro
    meta-strong: { size: 12px, line: 16px, weight: 500 }
    body: { size: 13px, line: 18px, weight: 400 }      # texto de listas
    label: { size: 13px, line: 18px, weight: 500 }     # nav, títulos de tarjeta, encabezados de columna
    title: { size: 16px, line: 24px, weight: 500 }     # título de página/vista
    display: { size: 52px, line: 1.05, weight: 400, tracking: "-0.02em" }  # solo pantallas tipo portada
radius:
  xs: 6px        # ítems de nav, opción de segmento, botones
  sm: 8px        # tarjetas, track de segmentos
  md: 10px       # columnas del tablero
  lg: 12px       # paneles agrupados (grupo en sidebar)
  pill: 999px    # chips de filtro
  full: 9999px   # puntos de estado
spacing: [2, 4, 6, 8, 10, 12, 16, 24, 32]
shadow:
  L1: "0 1px 2px 0 rgba(0,0,0,0.05)"                                   # tarjetas, segmento activo
  L2: "0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px 0 rgba(0,0,0,0.06)"
  ring: "0 0 3px 0 rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.08)"     # panel agrupado
  L3: "0 10px 15px -3px rgba(0,0,0,0.06)"                              # popovers, menús
  L4: "0 25px 50px -12px rgba(0,0,0,0.25)"                             # modales
---

# DESIGN.md — qa-orchestrator (inspirado en Devin Desktop)

## 1. Tema visual y atmósfera

Herramienta de trabajo, no página de marketing. Se siente como un editor de escritorio: tranquila, casi monocromática, con la información como protagonista. Casi todo es gris neutro sobre blanco roto; el color aparece **solo** para comunicar estado (un punto azul = en curso, check verde = listo, rojo = falla). Densidad media-alta: texto de 12–13px, filas de ~30px, mucho contenido visible sin scroll. Nada de degradados, ilustraciones ni sombras pesadas.

Principios:
- **Un solo acento** (azul `accent`). Si todo es azul, nada destaca.
- **Bordes en vez de sombras.** Separación con bordes de 1px a 6–8% de negro; sombras solo L1 en tarjetas.
- **Jerarquía por peso y opacidad del texto**, no por tamaño: primario 100%, secundario 56%, terciario 40%.
- **Estados con puntos de 8px** y texto meta pequeño, no con badges grandes de colores.

## 2. Paleta y roles

Usar los tokens del front matter como variables CSS (sección 9). Reglas:
- Fondo principal `bg-page`; barra lateral `bg-wash` (un tono más gris), separadas por un borde `border-primary`.
- Superficies que "flotan" (tarjetas, segmento activo, paneles agrupados): `bg-elevated` + borde `border-primary` + `shadow L1`.
- Hover de cualquier fila o botón fantasma: fondo `tint-strong`. Ítem seleccionado: `tint-soft`.
- Colores semánticos solo en texto, íconos o puntos; sus versiones `-tint` solo como fondo de chips de estado.

## 3. Tipografía

- Toda la UI en **Inter**. Monoespaciada (**Geist Mono**) para IDs de casos, nombres de suites, rutas, logs y duraciones.
- Tamaño base de la app: **13px** (no 16px). Metadatos 12px en `text-secondary`.
- Títulos de tarjeta y navegación: 13px peso 500. No usar negritas 700 en la app.
- Contadores junto a títulos (p. ej. "En ejecución 2"): mismo tamaño, color `text-secondary`, peso 400.

## 4. Layout

Estructura tipo ventana de escritorio:

```
┌──────────── sidebar 280–300px (bg-wash) ────────────┬────────────── main (bg-page) ──────────────┐
│ [Segmentado: Ejecución | Casos]          🔍  ⊟       │ ←  →  Título de la vista                    │  ← barra 48px, borde inferior
│ + Nueva ejecución                                     │ [Tablero | Lista]                           │
│ ▣ Ejecuciones   (activo: tint-soft)                   │ (Estado ▾) (Proyecto ▾) (Ambiente ▾) …      │  ← chips pill
│                                                       ├─────────────────────────────────────────────┤
│ Proyectos                          🔍 ≡ +             │ Columna     Columna      Columna            │
│  Nombre de ejecución              ●                   │ ┌───────┐   ┌───────┐    ┌───────┐          │
│  meta · 42 min                                        │ │tarjeta│   │tarjeta│    │tarjeta│          │
│ ┌ Grupo (panel elevado r12) ─────── ˅ ┐               │ └───────┘   └───────┘    └───────┘          │
│ │ ítems…                               │              │                                              │
└───────────────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

- Barra superior del main: alto 48px, padding `10px 16px`, borde inferior `border-primary`.
- Padding interno de la sidebar: `0 8px`; ítems con padding `6px 8px`.
- Columnas del tablero: ancho ~262–280px, padding 8px, radio 10px, gap entre tarjetas 8px.

## 5. Componentes

**Ítem de navegación (sidebar)**
- Padding `6px 8px`, radio 6px, texto 13/18 peso 500, ícono 16px a la izquierda con gap 8px.
- Hover `tint-strong`; activo `tint-soft`. Sin borde.

**Control segmentado (Agent | Editor, Tablero | Lista)**
- Track: fondo `tint-soft`, padding 1px, radio 7–8px.
- Opción: padding `0 10px`, alto 22–26px, texto 12–13px peso 500 en `text-secondary`.
- Opción activa: fondo `bg-elevated`, borde `border-primary`, `shadow L1`, radio 6px, texto `text-primary`.

**Chip de filtro**
- Radio pill, borde 1px `border-primary`, fondo transparente, alto 28px, padding `0 8px 0 12px`.
- Texto 12px peso 500 `text-secondary` + chevron ˅. Con filtro aplicado: texto `text-primary` y valor visible ("Estado: Fallido").

**Encabezado de columna**
- Ícono de estado + nombre (13px, 500) + contador (`text-secondary`) + menú "⋯" alineado a la derecha. Padding `0 6px`, alto 28px.

**Tarjeta**
- Fondo `bg-elevated`, borde `border-primary`, radio 8px, padding `10px 12px`, `shadow L1`, gap interno 8px.
- Línea opcional superior: contexto/grupo en 13px `text-secondary`.
- Título 13px peso 500, máximo 2 líneas.
- Punto de estado 8px arriba a la derecha.
- Pie: ícono 12px + meta 12px `text-secondary` ("Ejecutando…", "hace 42 min").
- Hover: borde `rgba(0,0,0,0.12)`. Sin elevación extra.

**Fila de lista (sidebar o vista Lista)**
- Padding `6px 8px`, radio 6px. Línea 1: título 13px + punto de estado a la derecha. Línea 2: meta 12px `text-secondary` con separadores "·".

**Panel agrupado**
- Fondo `bg-elevated`, radio 12px, padding 2px, sombra `ring`. Encabezado con nombre del grupo en `text-secondary` y chevron para colapsar.

**Botones**
- Primario: fondo `button-neutral`, texto blanco, 13px peso 500, alto 32px, padding `0 12px`, radio 6px.
- Secundario: fondo `bg-elevated`, borde `border-primary`, `shadow L1`.
- Fantasma / ícono: sin fondo, 28×28, radio 6px, hover `tint-strong`, íconos 16px en `text-secondary`.
- Destructivo: texto `red`, hover `red-tint`. Nunca un botón rojo sólido salvo confirmación final.

**Indicadores de estado**
- Punto 8px redondo. En curso: `accent`, con animación suave de opacidad o shimmer en el texto "Ejecutando…".
- Check verde, X roja e íconos de línea de 14–16px para estados finales.

**Íconos**
- Línea (stroke 1.5px), 16px en UI y 12–14px en meta. Recomendado: Lucide.

## 6. Mapeo al dominio QA

| Concepto Devin | En qa-orchestrator |
|---|---|
| Sessions (tablero Running / Waiting for review / Done) | Ejecuciones agrupadas por estado |
| Spaces | Proyectos o PMOs |
| Grupo colapsable en sidebar | Suite o ciclo de pruebas |
| Tarjeta de sesión | Ejecución o caso de prueba |
| Filtros Status / Space / Pull request / Agent | Estado / Proyecto / Ambiente / Responsable |

Colores de estado de pruebas (siempre como punto, ícono o texto; fondo tint solo en chips):

| Estado | Color | Ícono |
|---|---|---|
| Pendiente / No ejecutado | `text-tertiary` | círculo vacío |
| En ejecución | `accent` | punto + "Ejecutando…" |
| Exitoso | `green` | check |
| Fallido | `red` | X |
| Bloqueado | `orange` | candado o ⚠ |
| En revisión / Re-test | `purple` | ojo o ↻ |

Para gráficos del jefe de proyecto (avance, tendencias), usar los mismos colores semánticos y la regla de un acento: barras en `accent`, comparativas en grises.

## 7. Movimiento

- Transiciones de 120–160ms `ease-out` en hover, segmentos y colapsables. Nada de rebotes.
- Estado "en curso": pulso lento de opacidad (1.5s) en el punto, o shimmer en el texto.

## 8. Qué NO hacer

- No usar fondos de color plenos en tarjetas ni encabezados.
- No mezclar varios acentos (azul + morado + verde decorativo).
- No subir el texto base a 15–16px dentro de la app.
- No usar sombras grandes en tarjetas; solo modales y menús llevan L3/L4.
- No poner badges grandes con texto en mayúsculas para estados.
- No usar radios grandes (>12px) salvo chips pill y puntos.

## 9. Tokens CSS listos para copiar

```css
:root {
  --bg-page:#FCFCFC; --bg-wash:#F8F8F8; --bg-elevated:#FFFFFF;
  --text-primary:#191919; --text-strong:#000;
  --text-secondary:rgba(25,25,25,.56); --text-tertiary:rgba(25,25,25,.40);
  --border-primary:rgba(0,0,0,.08); --border-secondary:rgba(0,0,0,.06);
  --tint-strong:rgba(0,0,0,.08); --tint-soft:rgba(0,0,0,.06); --tint-faint:rgba(0,0,0,.04);
  --accent:#317CFF; --accent-tint:rgba(51,125,244,.10); --button-neutral:#363636; --button-neutral-text:#FFF;
  --green:#00A558; --green-tint:rgba(62,237,155,.20);
  --red:#F53B3A; --red-tint:rgba(245,59,58,.12);
  --orange:#F58E3A; --orange-tint:rgba(245,142,58,.12);
  --purple:#956CDE; --purple-tint:rgba(149,108,222,.12);
  --font-ui:Inter, system-ui, sans-serif;
  --font-mono:'Geist Mono','IBM Plex Mono',ui-monospace,monospace;
  --r-xs:6px; --r-sm:8px; --r-md:10px; --r-lg:12px; --r-pill:999px;
  --shadow-L1:0 1px 2px 0 rgba(0,0,0,.05);
  --shadow-L2:0 1px 3px 0 rgba(0,0,0,.06),0 1px 2px 0 rgba(0,0,0,.06);
  --shadow-ring:0 0 3px 0 rgba(0,0,0,.06),0 0 0 .5px rgba(0,0,0,.08);
  --shadow-L3:0 10px 15px -3px rgba(0,0,0,.06);
  --shadow-L4:0 25px 50px -12px rgba(0,0,0,.25);
}
[data-theme="dark"] {
  --bg-page:#141414; --bg-wash:#191919; --bg-elevated:#1F1F1F;
  --text-primary:rgba(255,255,255,.90); --text-strong:#FFF;
  --text-secondary:rgba(255,255,255,.52); --text-tertiary:rgba(255,255,255,.40);
  --border-primary:rgba(255,255,255,.08); --border-secondary:rgba(255,255,255,.04);
  --tint-strong:rgba(255,255,255,.08); --tint-soft:rgba(255,255,255,.05); --tint-faint:rgba(255,255,255,.03);
  --accent:#49B0FF; --button-neutral:#F9F9F9; --button-neutral-text:#000;
  --green:#00EC7E; --green-tint:rgba(0,236,126,.08); --orange-tint:rgba(245,142,58,.08);
  --shadow-L1:0 1px 2px 0 rgba(0,0,0,.20);
  --shadow-L3:0 10px 15px -3px rgba(0,0,0,.64);
  --shadow-L4:0 25px 50px -12px rgba(0,0,0,.50);
}
body { background:var(--bg-page); color:var(--text-primary); font:400 13px/18px var(--font-ui); }
```

## 10. Instrucciones para el agente

1. Lee este archivo completo antes de tocar el front.
2. Crea `tokens.css` con la sección 9 e impórtalo primero; reemplaza colores, tamaños y sombras hardcodeados por las variables.
3. No modifiques endpoints, contratos de la API (FastAPI) ni la lógica de negocio: solo HTML, CSS y JS de presentación.
4. Rediseña una vista a la vez, empezando por el tablero de ejecuciones, y muestra el resultado antes de seguir.
5. Mantén la paridad funcional: cada botón, filtro y acción existente debe seguir disponible.
