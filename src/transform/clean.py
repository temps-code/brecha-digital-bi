"""
Transform — Data Cleaning (Bronze → Silver)
Responsable: Juan Nicolás Flores Delgado (@Juan7139nf)

Limpia los CSV crudos de data/raw/:
  - Elimina o imputa valores NULL (5% introducido intencionalmente en seed.sql)
  - Normaliza mayúsculas/minúsculas mezcladas en nombres
  - Elimina espacios extra en campos de texto
  - Valida tipos de datos y rangos

Salida: data/processed/
"""
