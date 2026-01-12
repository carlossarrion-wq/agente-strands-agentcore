#!/usr/bin/env python3
"""
Script de prueba local para el agente AgentCore

Este script permite probar el agente localmente antes de desplegarlo.
"""

import asyncio
import json


async def test_agent_local():
    """Prueba el agente localmente sin desplegar"""
    
    # Importar el módulo del agente
    from agente_strands_agentcore import agent_invocation
    
    # Crear un contexto mock
    class MockContext:
        def __init__(self):
            self.session_id = "test-session-123"
    
    print("\n" + "="*80)
    print("🧪 PRUEBA LOCAL DEL AGENTE AGENTCORE")
    print("="*80)
    
    # Test 1: Listar buckets S3
    print("\n📝 Test 1: Listar buckets S3")
    print("-" * 80)
    
    payload1 = {
        "prompt": "Dame el listado de buckets S3 que tengo en mi entorno de AWS"
    }
    
    print(f"🤖 Pregunta: {payload1['prompt']}\n")
    print("💬 Respuesta: ", end="", flush=True)
    
    async for event in agent_invocation(payload1, MockContext()):
        if isinstance(event, dict) and 'data' in event:
            print(event['data'], end="", flush=True)
    
    print("\n" + "="*80)
    
    # Test 2: Pregunta general
    print("\n📝 Test 2: Pregunta general sobre Python")
    print("-" * 80)
    
    payload2 = {
        "prompt": "Explica qué es Python en 2 párrafos"
    }
    
    print(f"🤖 Pregunta: {payload2['prompt']}\n")
    print("💬 Respuesta: ", end="", flush=True)
    
    async for event in agent_invocation(payload2, MockContext()):
        if isinstance(event, dict) and 'data' in event:
            print(event['data'], end="", flush=True)
    
    print("\n" + "="*80)
    print("\n✅ Pruebas completadas exitosamente")


if __name__ == "__main__":
    asyncio.run(test_agent_local())
