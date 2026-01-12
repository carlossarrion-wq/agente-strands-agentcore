#!/usr/bin/env python3
"""
Script para invocar el agente remoto desplegado en AWS AgentCore

Este script usa el CLI de agentcore para invocar el agente.
Es la forma más sencilla y recomendada de invocar agentes remotos.
"""

import subprocess
import sys
import json
from typing import Optional

# Intentar importar la configuración del agente
try:
    from config_agent import AGENT_ARN, REGION
    DEFAULT_AGENT_ARN = AGENT_ARN
    DEFAULT_REGION = REGION
except ImportError:
    DEFAULT_AGENT_ARN = None
    DEFAULT_REGION = "eu-west-1"


def invoke_remote_agent(
    prompt: str,
    session_id: Optional[str] = None
):
    """
    Invoca el agente desplegado en AgentCore usando el CLI
    
    Args:
        prompt: Pregunta para el agente
        session_id: ID de sesión (opcional)
    """
    print("\n" + "="*80)
    print("🌐 INVOCANDO AGENTE REMOTO EN AWS AGENTCORE")
    print("="*80)
    print(f"🤖 Pregunta: {prompt}")
    print("="*80 + "\n")
    
    try:
        # Preparar el payload
        payload = json.dumps({"prompt": prompt})
        
        # Construir el comando
        cmd = ["agentcore", "invoke", payload]
        
        if session_id:
            cmd.extend(["--session-id", session_id])
        
        # Ejecutar el comando con streaming en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Leer y mostrar la salida en tiempo real
        full_output = ""
        for line in process.stdout:
            print(line, end='', flush=True)
            full_output += line
        
        # Esperar a que termine el proceso
        process.wait()
        
        # Mostrar errores si los hay
        stderr_output = process.stderr.read()
        if stderr_output:
            print("\n⚠️  Advertencias:", stderr_output)
        
        # Verificar el código de salida
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
        
        return full_output
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al invocar el agente:")
        print(f"Código de salida: {e.returncode}")
        if e.stdout:
            print(f"Salida: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        print("\n💡 Sugerencias:")
        print("1. Verifica que el agente esté desplegado: agentcore status")
        print("2. Verifica tus credenciales AWS: aws sts get-caller-identity")
        print("3. Asegúrate de estar en el directorio correcto del proyecto")
        return None
    except FileNotFoundError:
        print("\n❌ Error: No se encontró el comando 'agentcore'")
        print("\n💡 Instala el CLI de AgentCore:")
        print("   pip3 install bedrock-agentcore-starter-toolkit")
        return None
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        return None


def main():
    """Función principal con ejemplos de uso"""
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        # Usar el prompt de la línea de comandos
        prompt = " ".join(sys.argv[1:])
        invoke_remote_agent(prompt)
    else:
        # Ejecutar ejemplos predefinidos
        print("\n" + "="*80)
        print("🧪 EJEMPLOS DE INVOCACIÓN AL AGENTE REMOTO")
        print("="*80)
        
        # Ejemplo 1: Consulta AWS
        print("\n📝 Ejemplo 1: Consultar buckets S3")
        invoke_remote_agent(
            "Dame el listado de buckets S3 que tengo en mi entorno de AWS"
        )
        
        # Ejemplo 2: Pregunta general
        print("\n📝 Ejemplo 2: Pregunta general")
        invoke_remote_agent(
            "Explica qué es Python en 2 párrafos"
        )
        
        print("\n" + "="*80)
        print("💡 Uso desde línea de comandos:")
        print("   python3 invoke_remote_agent.py 'Tu pregunta aquí'")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
