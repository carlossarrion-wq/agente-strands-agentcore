# Agente Strands con AWS Bedrock AgentCore

Este proyecto contiene un agente inteligente que usa Strands integrado con AWS Bedrock AgentCore Runtime, con capacidades de streaming y herramientas AWS.

## 📁 Archivos del Proyecto

- **`agente_strands_streaming.py`**: Versión standalone del agente (sin AgentCore)
- **`agente_strands_agentcore.py`**: Versión integrada con AgentCore Runtime ⭐
- **`test_agentcore_local.py`**: Script para probar el agente localmente
- **`requirements.txt`**: Dependencias del proyecto
- **`README_VENV.md`**: Documentación del entorno virtual

## 🚀 Inicio Rápido

### 1. Activar el Entorno Virtual

```bash
cd "/Users/csarrion/Cline/ARQUITECTURA DE AGENTES/AWS Bedrock AgentCore/agente_strands_streaming"
source venv/bin/activate
```

### 2. Verificar Instalación

```bash
pip3 list | grep -E "strands|bedrock-agentcore"
```

Deberías ver:
- bedrock-agentcore: 1.1.4
- bedrock-agentcore-starter-toolkit: 0.2.5
- strands-agents: 1.21.0
- strands-agents-tools: 0.2.19

## 🧪 Pruebas Locales

### Opción 1: Prueba con Script de Test

```bash
python3 test_agentcore_local.py
```

Este script ejecuta dos pruebas:
1. Listar buckets S3 de AWS
2. Pregunta general sobre Python

### Opción 2: Ejecutar el Servidor Local

```bash
python3 agente_strands_agentcore.py
```

El servidor estará disponible en `http://localhost:8080`

Para probar con curl:

```bash
# Test 1: Listar buckets S3
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Dame el listado de buckets S3 que tengo en mi entorno de AWS"}'

# Test 2: Pregunta general
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explica qué es Python en 2 párrafos"}'
```

### Opción 3: Versión Standalone (sin AgentCore)

```bash
python3 agente_strands_streaming.py
```

## 🌐 Despliegue en AWS AgentCore

### Configurar el Agente

```bash
agentcore configure -e agente_strands_agentcore.py
```

Durante la configuración:
1. **Execution Role**: Presiona Enter para auto-crear
2. **ECR Repository**: Presiona Enter para auto-crear
3. **Requirements File**: Confirma `requirements.txt`
4. **OAuth Configuration**: Escribe `no`
5. **Request Header Allowlist**: Escribe `no`
6. **Memory Configuration**: Escribe `s` para saltar (opcional)

### Desplegar el Agente

```bash
agentcore deploy
```

Esto realizará:
- Build del contenedor Docker
- Push a Amazon ECR
- Despliegue en AgentCore Runtime
- Activación del endpoint con tracing

### Verificar el Estado

```bash
agentcore status
```

### Invocar el Agente Desplegado

```bash
# Invocar con el CLI
agentcore invoke '{"prompt": "Dame el listado de buckets S3 que tengo en mi entorno de AWS"}'

# Con session ID específico
SESSION_ID=$(python -c "import uuid; print(uuid.uuid4())")
agentcore invoke '{"prompt": "Dame el listado de buckets S3"}' --session-id $SESSION_ID
```

### Ver Logs

```bash
# Ver logs en tiempo real
agentcore status  # Copia el comando de logs que aparece

# Ejemplo:
aws logs tail /aws/bedrock-agentcore/runtimes/AGENT_ID-DEFAULT \
  --log-stream-name-prefix "YYYY/MM/DD/[runtime-logs]" \
  --follow
```

### Limpiar Recursos

```bash
agentcore destroy
```

## 🔧 Características del Agente

### Herramientas Disponibles

- **`use_aws`**: Herramienta universal para operaciones AWS
  - Listar buckets S3
  - Consultar instancias EC2
  - Obtener información de servicios AWS
  - Y cualquier operación de boto3

### Capacidades

- ✅ **Streaming en tiempo real**: Respuestas token por token
- ✅ **Herramientas AWS**: Acceso a recursos AWS mediante use_aws
- ✅ **Despliegue en producción**: Integración con AgentCore Runtime
- ✅ **Escalabilidad**: Gestión automática de contenedores
- ✅ **Observabilidad**: Logs y trazas con CloudWatch y X-Ray

## 📝 Ejemplos de Uso

### Consultas AWS

```python
payload = {
    "prompt": "Dame el listado de buckets S3 que tengo en mi entorno de AWS"
}
```

### Preguntas Generales

```python
payload = {
    "prompt": "Explica qué es Python en 2 párrafos"
}
```

### Preguntas Técnicas

```python
payload = {
    "prompt": "¿Cuáles son las diferencias entre async/await y threading en Python?"
}
```

## 🔐 Configuración de AWS

Asegúrate de tener configuradas tus credenciales de AWS:

```bash
aws configure
```

O mediante variables de entorno:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=eu-central-1
```

## 📚 Documentación Adicional

- [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Strands Documentation](https://github.com/awslabs/strands)
- [AgentCore Quickstart](https://aws.github.io/bedrock-agentcore-starter-toolkit/)

## 🐛 Troubleshooting

### Error: "No module named 'strands'"

```bash
pip3 install strands-agents strands-agents-tools
```

### Error: "No AWS credentials found"

```bash
aws configure
```

### Error al desplegar con agentcore

Verifica que tienes los permisos necesarios:
- AmazonBedrockAgentCoreFullAccess
- Permisos para crear roles IAM
- Permisos para ECR

## 📊 Comparación de Versiones

| Característica | Standalone | AgentCore |
|----------------|------------|-----------|
| Streaming | ✅ | ✅ |
| Herramientas AWS | ✅ | ✅ |
| Despliegue local | ✅ | ✅ |
| Despliegue producción | ❌ | ✅ |
| Escalabilidad automática | ❌ | ✅ |
| Observabilidad integrada | ❌ | ✅ |
| Gestión de memoria | ❌ | ✅ (opcional) |

## 🎯 Próximos Pasos

1. Probar el agente localmente con `test_agentcore_local.py`
2. Configurar y desplegar con `agentcore configure` y `agentcore deploy`
3. Monitorear el agente con CloudWatch y X-Ray
4. Añadir más herramientas según necesidades
5. Configurar memoria persistente (opcional)
