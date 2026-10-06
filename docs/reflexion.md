# Reflexión final

*El uso del ai tiene muchas posibilidades en este caso sea para corregir un proyecot ya existente pero usando- los prompts en orden y estructurados puedes mejorar muchisimo la calidad de los resultados, apesar de que nada es determinista de igual manera se puede notar un gran cambio en los resutlados positivamente, siempre tomando encuenta que la experiencia de la persona usandolo tiene un peso muy importante para verificar los resultados del AI. *

## Datos para la reflexión

Hechos medidos o registrados en el repositorio. Lo que no consta en los registros
queda marcado como "pendiente".

**Errores de ruff**

- Al inicio (línea base): 20 errores.
- Al final (después de R24): 0 errores, `All checks passed!`.
- Camino registrado en la bitácora: 20 → 16 (R1) → 15 (R2) → 12 (R3) → 9 (R8) →
  7 (R10) → 6 (R17) → 4 (R18) → 1 (R19) → 0 (R23).

**Pruebas**

- 20 tests en verde antes y después de cada fase (R1–R24).
- Salida de referencia idéntica en cada fase, con la comparación contra
  `scripts/referencia_base.txt`.

**Fases que fallaron al primer intento y cambios revertidos**

- Iteración 8 (R22–R24): ninguna fase falló y no se revirtió nada.
- Iteraciones 1 a 7: pendiente (no hay constancia de fallos en la bitácora ni en los
  reportes de iteración; confirmar con el historial de la conversación).

**Riesgo que detectaron las pruebas de comportamiento y no los tests**

- En R20 (iteración 7) la validación de `cantidad` pasó de `cantidad > 0` a
  `cantidad <= 0` invertido. Con `NaN`, el original rechazaba la cantidad
  (`NaN > 0` es falso) y la versión nueva la aceptaba (`NaN <= 0` también es falso).
  Ni los 20 tests ni la salida de referencia lo detectaron (la referencia no incluye
  `NaN`). Se encontró al revisar el código y se corrigió en R22 con
  `cantidad is None or not cantidad > 0` en `registrar_venta` y `cotizar`. Se
  comprobó a mano que ambos regresan `None` con `"cantidad invalida"`.
- Otros riesgos que la referencia vigila y los tests no (según `CLAUDE.md`): `0`
  contra `0.0` en el descuento (R18), `codigo in (None, "")` con el código `0` (R15),
  el empate en `mas_vendidos` (R13) y los bytes no UTF-8 en `cargar_datos` (R9).
  No consta en los registros que alguno de estos haya fallado: pendiente.

**Sorpresas de proceso**

- El aviso de git `LF → CRLF` es solo `autocrlf`, sin efecto en el código.
- La prueba manual del menú (opciones 1 a 7, opción inválida y `8`) no la pudo hacer
  el agente: R23 se validó con la prueba por `subprocess` de la salida de referencia.
  Pendiente que la haga el alumno.

**Resultado de la refactorización**

- `registrar_venta` quedó dividida en `_descuento_por_volumen`, `_aplica_vip`,
  `_calcular_montos` y `_construir_ticket`; `menu` en siete funciones `_opcion_*` y el
  diccionario `OPCIONES`.
- Categorías de la rúbrica cubiertas: renombrar, extraer funciones, simplificar
  condicionales, type hints, manejo de errores y código muerto.
