#!/usr/bin/env python3
"""
Agente Simple con Strands + Bedrock Runtime (Streaming Real)

Este agente usa Strands directamente con Bedrock Runtime API
para obtener streaming token-por-token en tiempo real.

Incluye herramientas AWS para consultar información del entorno.
"""

import asyncio
import logging
import os
from strands import Agent
from strands_tools.use_aws import use_aws

# Suprimir logs de Strands y boto3
logging.getLogger('strands').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Desactivar confirmación de herramientas para operaciones de lectura
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Configurar el agente con Claude Sonnet 4 y herramientas AWS
agent = Agent(
    model="eu.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt="""Eres un asistente útil especializado en AWS.
Respondes de forma clara y directa.
Tienes acceso a herramientas para consultar información de AWS.
Cuando te pidan información sobre recursos AWS, usa la herramienta use_aws.

Para listar buckets S3, usa:
- service_name: 's3'
- operation_name: 'list_buckets'
- parameters: {}""",
    tools=[use_aws]
)


async def chat_streaming(prompt: str):
    """
    Envía un prompt al agente y recibe respuesta en streaming
    
    Args:
        prompt: Pregunta o comando del usuario
    """
    print(f"\n🤖 Pregunta: {prompt}\n")
    print("💬 Respuesta: ", end="", flush=True)
    
    # Obtener stream del agente
    agent_stream = agent.stream_async(prompt)
    
    full_response = ""
    
    # Procesar eventos del stream en tiempo real
    async for event in agent_stream:
        # Solo extraer y mostrar el texto, sin debug info
        if isinstance(event, dict):
            # Extraer texto del evento
            if 'data' in event:
                text = event['data']
                print(text, end="", flush=True)
                full_response += text
            elif 'delta' in event and 'text' in event['delta']:
                text = event['delta']['text']
                print(text, end="", flush=True)
                full_response += text
        elif hasattr(event, 'data'):
            text = event.data
            print(text, end="", flush=True)
            full_response += text
        elif hasattr(event, 'text'):
            text = event.text
            print(text, end="", flush=True)
            full_response += text
    
    print("\n" + "="*80)  # Separador al final
    
    return full_response


async def main():
    """Función principal con ejemplos"""
    
    print("\n" + "="*80)
    print("🚀 AGENTE STRANDS CON STREAMING + HERRAMIENTAS AWS")
    print("="*80)
    
    # Ejemplo 1: Consulta AWS - Listar buckets S3
    await chat_streaming("Dame el listado de buckets S3 que tengo en mi entorno de AWS")
    
    # Ejemplo 2: Pregunta simple
    await chat_streaming("Explica qué es Python en 2 párrafos")
    
    # Ejemplo 3: Pregunta técnica
    await chat_streaming("¿Cuáles son las diferencias entre async/await y threading en Python?")
    
    print("\n✅ Todas las consultas completadas")


if __name__ == "__main__":
    # Ejecutar el agente
    asyncio.run(main())
