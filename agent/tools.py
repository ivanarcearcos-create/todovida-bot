# agent/tools.py — Herramientas del agente TodoVida
# Generado por AgentKit

"""
Herramientas específicas para TodoVida.
Cubren los casos de uso: confirmación de pedidos, validación de dirección,
atención de ventas y soporte al cliente.
"""

import os
import re
import yaml
import logging
from datetime import datetime

logger = logging.getLogger("agentkit")


def cargar_info_negocio() -> dict:
    """Carga la información del negocio desde business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """Retorna el horario de atención del negocio."""
    info = cargar_info_negocio()
    return {
        "horario": info.get("negocio", {}).get("horario", "24/7"),
        "esta_abierto": True,  # TodoVida atiende 24/7
    }


def validar_direccion_espana(direccion: str) -> dict:
    """
    Valida que una dirección de España esté completa.
    Comprueba que tenga calle, número y código postal.

    Args:
        direccion: Texto con la dirección del cliente

    Returns:
        Dict con 'valida' (bool), 'campos_faltantes' (list) y 'sugerencia' (str)
    """
    campos_faltantes = []

    # Verificar código postal español (5 dígitos)
    tiene_cp = bool(re.search(r'\b\d{5}\b', direccion))
    if not tiene_cp:
        campos_faltantes.append("código postal")

    # Verificar que haya número de calle (dígito en la dirección)
    tiene_numero = bool(re.search(r'\b\d+\b', direccion))
    if not tiene_numero:
        campos_faltantes.append("número de calle")

    # Verificar longitud mínima (una dirección completa tiene cierta longitud)
    if len(direccion.strip()) < 15:
        campos_faltantes.append("dirección completa")

    valida = len(campos_faltantes) == 0

    sugerencia = ""
    if not valida:
        sugerencia = f"Parece que falta: {', '.join(campos_faltantes)}. Por favor incluye la dirección completa con calle, número, piso (si aplica), ciudad y código postal."

    return {
        "valida": valida,
        "campos_faltantes": campos_faltantes,
        "sugerencia": sugerencia
    }


def generar_confirmacion_pedido(nombre_cliente: str, direccion: str) -> str:
    """
    Genera un mensaje de confirmación de pedido para enviar al cliente.

    Args:
        nombre_cliente: Nombre del cliente
        direccion: Dirección de envío confirmada

    Returns:
        Mensaje de confirmación listo para enviar
    """
    return (
        f"¡Perfecto, {nombre_cliente}! 🎉 Tu pedido de Gomitas de Gordolobo está confirmado.\n\n"
        f"📦 Lo enviaremos a:\n{direccion}\n\n"
        f"💳 Recuerda que es pago contra entrega — pagas cuando lo recibas.\n"
        f"🚀 Recibirás tu pedido en 2-4 días hábiles.\n\n"
        f"¿Tienes alguna duda más? ¡Estoy aquí para ayudarte! 💚"
    )


def registrar_pedido_confirmado(telefono: str, direccion: str) -> dict:
    """
    Registra un pedido como confirmado (log local).
    En producción esto podría conectarse a un CRM o base de datos.

    Args:
        telefono: Número de teléfono del cliente
        direccion: Dirección de envío confirmada

    Returns:
        Dict con el resultado del registro
    """
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"PEDIDO CONFIRMADO — Tel: {telefono} | Dirección: {direccion} | Hora: {timestamp}")
    return {
        "confirmado": True,
        "telefono": telefono,
        "direccion": direccion,
        "timestamp": timestamp
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca información relevante en los archivos de /knowledge.
    Retorna el contenido más relevante encontrado.
    """
    resultados = []
    knowledge_dir = "knowledge"

    if not os.path.exists(knowledge_dir):
        return "No hay archivos de conocimiento disponibles."

    for archivo in os.listdir(knowledge_dir):
        ruta = os.path.join(knowledge_dir, archivo)
        if archivo.startswith(".") or not os.path.isfile(ruta):
            continue
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                if consulta.lower() in contenido.lower():
                    resultados.append(f"[{archivo}]: {contenido[:500]}")
        except (UnicodeDecodeError, IOError):
            continue

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontré información específica sobre eso en mis archivos."
