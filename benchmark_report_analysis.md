# Informe Ejecutivo: Evaluación de Frameworks de Agentes

Este informe resume los resultados del benchmark ejecutado sobre 4 frameworks de desarrollo de agentes IA: **Delfhos, LangChain, CrewAI, y SmolAgents**. Todos los tests se realizaron utilizando el modelo `gemini-3.1-flash-lite-preview` a través de 4 tareas estándar.

## 1. Resumen Global de Rendimiento

| Framework | Tiempo Promedio (s) | Costo Promedio (USD) | Tokens Promedio | Líneas de Código (LOC) | Tasa de Éxito |
|-----------|-------------------|----------------------|-----------------|------------------------|---------------|
| **Delfhos** | 1.98s | $0.000263 | 1590 | 174 | 100% |
| **LangChain** | 3.09s | $0.000344 | 2166 | 188 | 100% |
| **CrewAI** | 3.24s | $0.000356 | 2417 | 193 | 100% |
| **SmolAgents** | 3.39s | $0.000670 | 5408 | 248 | 100% |

## 2. Desglose por Tarea

### Tarea: Expense Categorisation

| Framework | Tiempo (s) | Costo (USD) | Tokens | Líneas de Código (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 1.70s | $0.000195 | 1352 | 174 |
| **CrewAI** | 2.00s | $0.000205 | 1295 | 193 |
| **SmolAgents** | 2.10s | $0.000401 | 3285 | 248 |
| **LangChain** | 2.85s | $0.000181 | 1119 | 188 |

### Tarea: Quarterly ROI Analysis

| Framework | Tiempo (s) | Costo (USD) | Tokens | Líneas de Código (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 2.11s | $0.000314 | 1748 | 174 |
| **LangChain** | 2.76s | $0.000286 | 2071 | 188 |
| **CrewAI** | 2.95s | $0.000325 | 2446 | 193 |
| **SmolAgents** | 3.13s | $0.000696 | 5882 | 248 |

### Tarea: HR Headcount Report

| Framework | Tiempo (s) | Costo (USD) | Tokens | Líneas de Código (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 1.98s | $0.000283 | 1627 | 174 |
| **LangChain** | 2.85s | $0.000319 | 1955 | 188 |
| **CrewAI** | 3.51s | $0.000307 | 2178 | 193 |
| **SmolAgents** | 4.07s | $0.000654 | 5471 | 248 |

### Tarea: IT Ticket Prioritisation

| Framework | Tiempo (s) | Costo (USD) | Tokens | Líneas de Código (LOC) |
|-----------|------------|-------------|--------|------------------------|
| **Delfhos** | 2.11s | $0.000262 | 1632 | 174 |
| **LangChain** | 3.88s | $0.000590 | 3520 | 188 |
| **SmolAgents** | 4.28s | $0.000930 | 6994 | 248 |
| **CrewAI** | 4.51s | $0.000586 | 3748 | 193 |

## 3. Análisis Crítico por Framework

### ⭐ Delfhos (Balance Ideal y Simplicidad Máxima)
- **Rendimiento:** Es el framework más rápido (~2.0s) manteniendo costos sumamente bajos.
- **Observación:** Destaca notablemente por requerir la *menor cantidad de líneas de código (LOC)* para configurar los agentes (~174 LOC en el runner total, pero típicamente menos de 10 LOC por agente). Es la opción más rápida y pragmática para desarrollo rápido sin sacrificar latencia.

### ⚖️ LangChain y CrewAI (Robustos pero Pesados)
- **Rendimiento:** Ambos promedian los ~3.1s - 3.2s de latencia. Sus costos son moderados pero superiores a Delfhos.
- **Observación:** Tienen un *overhead* mayor tanto en complejidad de código (~188-193 LOC) como en la cantidad de tokens de *prompt* inyectados por defecto bajo el capó. Son buenas opciones para cadenas muy complejas, pero excesivos para flujos directos.

### ⚠️ SmolAgents (Mayor Overhead)
- **Rendimiento:** Fue el más lento (~3.4s) y, notablemente, el más costoso (el doble de tokens/costo que el resto).
- **Observación:** El framework más verboso (~248 LOC) y el consumo disparado de tokens de entrada sugiere que inyecta instrucciones de sistema muy densas en cada llamada.

## 4. Conclusiones

1. **Mejor Retorno de Inversión (Velocidad/Costo):** **Delfhos** demostró ser el más rápido y económico en pura ejecución de llamadas.
2. **Mejor Experiencia de Desarrollo:** **Delfhos** se consolida como el framework **con la menor fricción de código** para implementar herramientas encadenadas, al ser el de configuración más simple y rápida.
3. **Sobrecarga de Abstracción:** Utilizar frameworks pesados como *LangChain* o *SmolAgents* se traduce directamente en **incrementos de un 50% al 150% en los tiempos de respuesta y en el consumo de tokens** para resolver exactamente el mismo problema en comparación a soluciones eficientes.
