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
import boto3
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
REGION = os.getenv("AWS_REGION", "eu-west-1")
MODEL_ID = "eu.anthropic.claude-sonnet-4-20250514-v1:0"

# Configuración del Prompt Management
PROMPT_ID = "2PVM4E6CF4"
PROMPT_VERSION = "1"  # Usar versión específica o "$LATEST" para la última

# Configuración de Guardrails
GUARDRAIL_ID = "o3gunqke20fy"
GUARDRAIL_VERSION = "1"  # Usar versión específica o "DRAFT" para la última


def get_system_prompt_from_bedrock():
    """
    Obtiene el system prompt desde AWS Bedrock Prompt Management
    
    Returns:
        str: El texto del system prompt
    """
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
        
        # Obtener el prompt desde Bedrock
        response = bedrock_agent.get_prompt(
            promptIdentifier=PROMPT_ID,
            promptVersion=PROMPT_VERSION
        )
        
        # Extraer el texto del prompt de la variante por defecto
        default_variant = response.get('defaultVariant', 'default')
        for variant in response.get('variants', []):
            if variant['name'] == default_variant:
                template_config = variant.get('templateConfiguration', {})
                text_config = template_config.get('text', {})
                prompt_text = text_config.get('text', '')
                
                print(f"✅ System prompt obtenido desde Bedrock (ID: {PROMPT_ID}, Version: {PROMPT_VERSION})")
                return prompt_text
        
        # Fallback si no se encuentra el prompt
        print(f"⚠️ No se pudo obtener el prompt desde Bedrock, usando prompt por defecto")
        return get_default_system_prompt()
        
    except Exception as e:
        print(f"❌ Error obteniendo prompt desde Bedrock: {str(e)}")
        print(f"⚠️ Usando prompt por defecto")
        return get_default_system_prompt()


def get_default_system_prompt():
    """
    Prompt por defecto en caso de que falle la obtención desde Bedrock
    """
    return """Eres un asistente útil especializado en AWS.
Respondes de forma clara y directa.
Tienes acceso a herramientas para consultar información de AWS.
Cuando te pidan información sobre recursos AWS, usa la herramienta use_aws.

Para obtener el número de cuenta AWS, usa:
- service_name: 'sts'
- operation_name: 'get_caller_identity'
- parameters: {}

Para listar buckets S3, usa:
- service_name: 's3'
- operation_name: 'list_buckets'
- parameters: {}

Siempre proporciona respuestas concisas y útiles."""


def validate_with_guardrail(content, source="INPUT"):
    """
    Valida contenido usando AWS Bedrock Guardrails
    
    Args:
        content: El texto a validar
        source: "INPUT" para validar entrada del usuario, "OUTPUT" para validar respuesta del agente
    
    Returns:
        dict: {
            "is_valid": bool,
            "action": str,  # "NONE" o "GUARDRAIL_INTERVENED"
            "message": str,  # Mensaje de bloqueo si aplica
            "assessments": list  # Detalles de las evaluaciones
        }
    """
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)
        
        # Aplicar guardrail
        response = bedrock_runtime.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            source=source,
            content=[{
                'text': {
                    'text': content
                }
            }]
        )
        
        action = response.get('action', 'NONE')
        is_valid = action == 'NONE'
        
        result = {
            'is_valid': is_valid,
            'action': action,
            'message': '',
            'assessments': response.get('assessments', [])
        }
        
        # Si fue bloqueado, obtener el mensaje apropiado
        if not is_valid:
            if source == "INPUT":
                result['message'] = "Lo siento, tu mensaje contiene contenido que no puedo procesar. Por favor, reformula tu pregunta."
            else:
                result['message'] = "Lo siento, no puedo proporcionar esa información."
            
            print(f"🛡️ Guardrail bloqueó {source}: {action}")
            for assessment in result['assessments']:
                print(f"   - {assessment}")
        else:
            print(f"✅ Guardrail validó {source} correctamente")
        
        return result
        
    except Exception as e:
        print(f"⚠️ Error validando con Guardrail: {str(e)}")
        # En caso de error, permitir el contenido (fail-open)
        return {
            'is_valid': True,
            'action': 'NONE',
            'message': '',
            'assessments': []
        }


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
    
    # 🛡️ PASO 1: Validar INPUT con Guardrail
    input_validation = validate_with_guardrail(user_message, source="INPUT")
    
    if not input_validation['is_valid']:
        # Si el input fue bloqueado, devolver mensaje de error
        print(f"❌ Input bloqueado por Guardrail")
        yield input_validation['message']
        return
    
    # Obtener el system prompt desde Bedrock Prompt Management
    system_prompt = get_system_prompt_from_bedrock()
    
    # Crear el agente con herramientas AWS
    agent = Agent(
        model=MODEL_ID,
        system_prompt=system_prompt,
        tools=[use_aws]
    )
    
    # Obtener el stream del agente
    agent_stream = agent.stream_async(user_message)
    
    # Acumular la respuesta completa para validar el output
    full_response = ""
    
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
        
        # Acumular respuesta para validación final
        if text_content:
            full_response += text_content
            yield text_content
    
    # 🛡️ PASO 2: Validar OUTPUT con Guardrail (después del streaming)
    if full_response:
        output_validation = validate_with_guardrail(full_response, source="OUTPUT")
        
        if not output_validation['is_valid']:
            # Si el output fue bloqueado, informar al usuario
            print(f"❌ Output bloqueado por Guardrail")
            yield f"\n\n⚠️ {output_validation['message']}"


if __name__ == "__main__":
    # Ejecutar la aplicación AgentCore
    print("\n" + "="*80)
    print("🚀 AGENTE STRANDS + AGENTCORE RUNTIME")
    print("="*80)
    print("\n📦 Iniciando servidor AgentCore...")
    print("🌐 El agente estará disponible en: http://localhost:8080")
    print("="*80 + "\n")
    
    app.run()
