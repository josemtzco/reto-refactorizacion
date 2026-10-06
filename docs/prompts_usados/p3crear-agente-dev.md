## Crear agente implementador

modifica el @docs/prompts_usados/agent-dev-runner.md  para que sea el agente que implementara  la auditoria de calidad usando sonnet 5.5 que tenga como objetivo cumplir con estos requisitos para la evaluacion de la tarea. 

El orden de prioridad es estos requisitos, -> la auditoria de calidad -> el claude md.
Configuración del proyecto
    • CLAUDE.md con instrucciones claras para Claude Code:
      - Convenciones de código del proyecto (estilo, naming)
      - Cómo ejecutar tests
      - Restricciones o consideraciones especiales
    • .claudeignore excluyendo archivos no relevantes (venv, __pycache__, etc.)
Refactorizaciones requeridas
Aplicar mínimo 5 refactorizaciones de las siguientes categorías:
    • Renombrar variables o funciones para mayor claridad.
    • Extraer funciones de código duplicado o bloques muy largos.
    • Simplificar condicionales complejos.
    • Agregar type hints a funciones.
    • Mejorar manejo de errores.
    • Eliminar código muerto o comentarios obsoletos.
Validación
    • Todos los tests deben pasar después de cada refactorización.
    • El código final debe pasar linting sin errores (se proporciona configuración).
    • La funcionalidad del programa debe mantenerse intacta.
Documentación del proceso
    • Bitácora de refactoring con:
      - Prompt utilizado para cada refactorización
      - Descripción del cambio realizado
      - Justificación de por qué mejora el código
      - Resultado de los tests después del cambio
    • Reflexión final: qué técnicas de prompting funcionaron mejor y qué aprendiste.

Siempre cuando tengas alguna duda elige la opcion mas simple y facil de entender para programadores con poca experiencia.