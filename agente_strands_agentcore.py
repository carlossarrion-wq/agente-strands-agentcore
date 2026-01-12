#!/usr/bin/env python3
"""
Agente Strands con AWS Bedrock AgentCore Runtime

Este agente usa Strands integrado con AgentCore Runtime para:
- Streaming en tiempo real
- Herramientas AWS (use_aws)
- Despliegue en producción con AgentCore

Para desplegar: agentcore deploy
"""

import os
import logging
from strands import Agent
from strands_tools.use_aws import use_aws
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Suprimir logs verbosos
logging.getLogger('strands').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Desactivar confirmación de herramientas para operaciones de lectura
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Crear la aplicación AgentCore
app = BedrockAgentCoreApp()

# Configuración del modelo y región
REGION = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID = "eu.anthropic.claude-sonnet-4-20250514-v1:0"


@app.entrypoint
async def agent_invocation(payload, context):
    """
    Handler principal para invocaciones del agente con streaming
    
    Args:
        payload: Diccionario con el prompt del usuario
        context: Contexto de ejecución de AgentCore
    """
    # Extraer el prompt del payload
    user_message = payload.get("prompt", "No se proporcionó ningún prompt")
    
    # Obtener session_id del contexto para aislamiento
    session_id = getattr(context, 'session_id', 'default')
    
    print(f"📝 Contexto de sesión: {session_id}")
    print(f"🤖 Procesando mensaje: {user_message}")
    
    # Crear el agente con herramientas AWS
    agent = Agent(
        model=MODEL_ID,
        system_prompt="""Eres un asistente útil especializado en AWS.
Respondes de forma clara y directa.
Tienes acceso a herramientas para consultar información de AWS.
Cuando te pidan información sobre recursos AWS, usa la herramienta use_aws.

Para listar buckets S3, usa:
- service_name: 's3'
- operation_name: 'list_buckets'
- parameters: {}

Siempre proporciona respuestas concisas y útiles.""",
        tools=[use_aws]
    )
    
    # Obtener el stream del agente
    agent_stream = agent.stream_async(user_message)
    
    # Procesar y enviar eventos de streaming - SOLO TEXTO
    async for event in agent_stream:
        # Extraer SOLO el texto del evento, sin metadata
        text_content = None
        
        if isinstance(event, dict):
            # Extraer texto de diferentes formatos de evento
            if 'data' in event and isinstance(event['data'], str):
                text_content = event['data']
            elif 'delta' in event and isinstance(event['delta'], dict):
                if 'text' in event['delta']:
                    text_content = event['delta']['text']
        elif hasattr(event, 'data') and isinstance(event.data, str):
            text_content = event.data
        elif hasattr(event, 'text') and isinstance(event.text, str):
            text_content = event.text
        
        # Solo enviar si hay texto válido
        if text_content:
            yield text_content


if __name__ == "__main__":
    # Ejecutar la aplicación AgentCore
    print("\n" + "="*80)
    print("🚀 AGENTE STRANDS + AGENTCORE RUNTIME")
    print("="*80)
    print("\n📦 Iniciando servidor AgentCore...")
    print("🌐 El agente estará disponible en: http://localhost:8080")
    print("="*80 + "\n")
    
    app.run()
