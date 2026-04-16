# ley-ar

CLI unificado para búsqueda en bases jurídicas argentinas:
- SAIJ
- JUBA (SCBA)
- CSJN (sumarios)
- JUSCABA (EJE API pública)

## Instalación

```bash
cd ley-ar
pip install -e .
```

## Uso

```bash
# Busca en todas las bases por defecto
ley search "prescripción adquisitiva"

# Filtrar por base(s)
ley search "phishing bancario" --db saij,juba

# Output JSON para scripts
ley search "daño moral" --db csjn --json

# Limitar resultados
ley search "responsabilidad civil" --limit 10

# Ver versión y bases disponibles
ley --version
ley status
```

## Notas

- Sin MCP/uvx: llamadas HTTP directas a APIs públicas.
- Salida con `rich` (tabla), JSON (`--json`) y texto (`--text`).
- Maneja errores por base y sigue con las restantes.
- `search` corre en paralelo usando `ThreadPoolExecutor`.
