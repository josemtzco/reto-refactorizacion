# Plan de implementación — agente `dev-runner`

> Cómo poner a trabajar al agente `dev-runner`
> ([agent-dev-runner.md](agent-dev-runner.md)) sobre la auditoría
> ([auditoria-calidad.md](auditoria-calidad.md)), en **8 iteraciones de 3 fases**.
> Entre una iteración y otra se agregan a `CLAUDE.md` las aclaraciones de
> [docs/iteracion-claude.md](../iteracion-claude.md), para que el agente no tenga que
> adivinar en los puntos donde es fácil equivocarse.

## 1. Idea general

```text
Preparación ─► Iteración 1 ─► Checkpoint ─► Iteración 2 ─► … ─► Iteración 8 ─► Cierre
               (Paso 0,        (revisas tú,   (R4–R6)            (R22–R24)
                R1–R3)          se copian las
                                aclaraciones
                                a CLAUDE.md)
```

- Cada **iteración** = 3 fases de la auditoría = 3 commits `refactor(Rn): …`
  (+ 1 commit `docs:` con las aclaraciones de esa iteración).
- El agente **se detiene al terminar cada iteración** y entrega un reporte. Tú lo
  revisas y lanzas la siguiente. Así nunca hay más de 3 fases sin revisión humana y
  el contexto del agente se mantiene pequeño.
- Las aclaraciones van **antes** de las fases que explican: el bloque de la
  iteración N se copia a `CLAUDE.md` al empezar la iteración N (es decir, después
  de las 3 refactorizaciones anteriores).

| Iteración | Fases | Bloque de `iteracion-claude.md` | Prueba manual del menú |
|---|---|---|---|
| 1 | Paso 0, R1, R2, R3 | Iteración 1 | — |
| 2 | R4, R5, R6 | Iteración 2 | — |
| 3 | R7, R8, R9 | Iteración 3 | — |
| 4 | R10, R11, R12 | Iteración 4 | **Sí** (R10 toca `main.py`) |
| 5 | R13, R14, R15 | Iteración 5 | — |
| 6 | R16, R17, R18 | Iteración 6 | — |
| 7 | R19, R20, R21 | Iteración 7 | — |
| 8 | R22, R23, R24 + cierre (§7 del agente) | Iteración 8 | **Sí** (R23 reescribe el menú) |

## 2. Preparación (una sola vez, la haces tú)

1. **Dejar el árbol limpio.** El agente se detiene si encuentra cambios sin commit
   que no son suyos (§3 de `agent-dev-runner.md`). Hoy hay cambios pendientes
   (`CLAUDE.md`, `docs/`, `BITACORA_TEMPLATE.md` borrado). Haz commit de ellos:

   ```powershell
   git add -A
   git commit -m "docs: auditoría, agente dev-runner y plan de implementación"
   ```

2. **Registrar el agente en Claude Code.** Claude Code solo reconoce subagentes en
   `.claude/agents/`. Copia la definición (el archivo de `docs/` queda como
   documentación del proceso):

   ```powershell
   New-Item -ItemType Directory -Force .claude\agents
   Copy-Item docs\spec-driven-development\agent-dev-runner.md .claude\agents\dev-runner.md
   git add .claude\agents\dev-runner.md
   git commit -m "chore: registrar agente dev-runner"
   ```

   Comprueba con `/agents` que aparece `dev-runner`.

3. **Línea base confirmada** (ya medida el 2026-10-05):
   - `pytest`: **20 passed**.
   - `ruff check src`: **20 errores** (`UP009`×4, `SIM102`×3, `SIM115`×3, `C901`×2,
     `N802`×2, `SIM108`, `N816`, `SIM103`, `UP015`, `I001`, `F401`).

## 3. Cómo lanzar cada iteración

Desde Claude Code, en la raíz del repo, escribe (cambia `N`):

```text
Usa el agente dev-runner para ejecutar la iteración N de
docs/spec-driven-development/plan-implementacion.md.
```

El agente debe seguir, en este orden:

1. `git status` limpio; si no, se detiene.
2. **Checkpoint de aclaraciones:** copia el bloque "Iteración N" de
   `docs/iteracion-claude.md` al final de `CLAUDE.md`, dentro de la sección
   `## 6. Aclaraciones por iteración` (la crea en la iteración 1). Si en la
   iteración anterior anotó lecciones (paso 6), las agrega al bloque. Commit:
   `docs: aclaraciones de la iteración N en CLAUDE.md`.
3. Lee `CLAUDE.md` completo (ya con el bloque nuevo), la auditoría y `src/`.
4. Ejecuta las 3 fases de la iteración con el ciclo de §5 de `agent-dev-runner.md`
   (tests → ruff → salida de referencia → bitácora → commit), una fase por commit.
5. Verifica que el número de errores de ruff coincida con la tabla de §4. Si no
   coincide pero bajó y todo está verde, sigue y lo explica en el reporte.
6. **Se detiene** y entrega el reporte de la iteración:
   - fases hechas y hashes de commit;
   - pytest / ruff / referencia después de cada fase;
   - dudas o sorpresas → las escribe como "Lecciones de la iteración N" al final
     del bloque "Iteración N+1" de `docs/iteracion-claude.md` (van en el commit del
     checkpoint siguiente).

**Prioridad si algo choca:** rúbrica → auditoría → `CLAUDE.md` (incluidas las
aclaraciones). Las aclaraciones **no cambian** la auditoría: la detallan. La única
excepción es cuando seguir la auditoría al pie de la letra cambiaría el
comportamiento: ahí manda la regla inviolable "no cambiar el comportamiento
observable", y la aclaración lo dice explícitamente.

## 4. Errores de ruff esperados después de cada fase

Sirve para detectar a simple vista una fase que hizo de más o de menos.

| Fase | Errores | Qué desaparece |
|---|---|---|
| inicio | 20 | — |
| R1 | 16 | `UP009` ×4 |
| R2 | 15 | `I001` |
| R3 | 12 | `N802` + `SIM115` de `reporteViejoCSV`, `F401` (`import os` en `reportes`) |
| R4–R7 | 12 | — (cambios de nombres y constantes) |
| R8 | 9 | `SIM115` ×2, `UP015` |
| R9 | 9 | — |
| R10 | 7 | `N802` y `SIM103` de `hayArchivo` |
| R11–R16 | 7 | — |
| R17 | 6 | `N816` |
| R18 | 4 | `SIM108` y, probablemente, `C901` de `registrar_venta` (12 → 10) |
| R19 | 1 | `SIM102` ×3 |
| R20–R22 | 1 | — (solo queda `C901` de `menu`) |
| R23 | 0 | `C901` de `menu` |
| R24 | 0 | `All checks passed!` |

Regla dura: el número **nunca sube** respecto a la fase anterior.

## 5. Lo que haces tú en cada checkpoint (5 minutos)

1. Lee el reporte del agente y `git log --oneline -5`.
2. Abre la bitácora y revisa que las 3 filas nuevas sean cortas y tengan la
   categoría de la rúbrica.
3. Corre tú mismo:

   ```powershell
   .venv\Scripts\python -m pytest
   .venv\Scripts\python -m ruff check src --statistics
   ```

4. Iteraciones 4 y 8: prueba el menú a mano
   (`.venv\Scripts\python src\main.py`): opciones 1 a 7 con datos válidos e
   inválidos, una opción inexistente y, al final, `8`. Después
   `git restore datos_ejemplo.json`.
5. Si algo no te convence, dilo antes de lanzar la siguiente iteración; si quieres
   añadir una aclaración, escríbela en el bloque siguiente de
   `docs/iteracion-claude.md`.

## 6. Cuándo se detiene el agente antes de tiempo

- `git status` no está limpio al empezar.
- Un test falla **antes** de tocar nada (línea base rota).
- Una fase sigue en rojo tras **dos intentos** (revierte con `git restore src` y
  reporta).
- La salida de referencia cambia y no sabe explicar por qué.
- Para pasar algo tendría que tocar `tests/`, `pyproject.toml`,
  `scripts/referencia_base.txt` o usar `# noqa`.

En todos los casos: no hace commit, deja el árbol limpio y explica qué pasó.

## 7. Cierre (al final de la iteración 8)

Lo define §7 de `agent-dev-runner.md`: pytest verde, ruff en cero, revisión de
`CLAUDE.md` y `.claudeignore`, `docs/reflexion.md` con "Datos para la reflexión" y
reporte final. Además, en el cierre el agente revisa que la sección
`## 6. Aclaraciones por iteración` de `CLAUDE.md` siga siendo cierta con el código
final (p. ej. nombres ya renombrados) y la resume o corrige en el commit `docs:`.

Pendiente para ti al final: escribir la reflexión, completar la matrícula en la
bitácora y guardar los prompts usados en `docs/prompts_usados/`.
