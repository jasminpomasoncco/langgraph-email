# Agente de soporte automático por Gmail (LangGraph + GCP)

Un agente que lee correos entrantes automáticamente (sin intervención manual), los
clasifica, busca contexto relevante y redacta + envía una respuesta dentro del mismo
hilo de Gmail — corriendo como servicio en la nube con disparo programado.

## De qué trata

El flujo completo, end-to-end y sin intervención manual:

1. Lee el correo entrante más reciente desde Gmail.
2. Lo clasifica según su tipo o intención.
3. Busca contexto relevante (información de productos / base de conocimiento) mediante RAG.
4. Redacta una respuesta adecuada con un LLM.
5. Envía la respuesta dentro del hilo original de Gmail.

Todo esto se ejecuta como un servicio en la nube que se dispara de forma programada
en intervalos regulares, eliminando la ejecución manual.

## Herramientas más valiosas

- **LangGraph** — orquesta el flujo del agente como grafo de estados.
- **ChromaDB** — vector store para RAG (contexto de productos / conocimiento).
- **OpenAI API** — LLM para clasificación y generación de respuestas.
- **Gmail API (OAuth2)** — lectura y envío de correos en el hilo original.
- **Docker** — contenedorización del servicio (FastAPI + grafo).
- **Artifact Registry** — repositorio de imágenes Docker en GCP.
- **Cloud Run** — despliegue serverless con endpoint HTTP.
- **Secret Manager** (montado como volumen) — manejo seguro de credenciales OAuth.
- **Cloud Scheduler** — dispara el endpoint automáticamente en intervalos regulares,
  eliminando la ejecución manual.

## Historia de portafolio

Agente con LLM + RAG → contenedorizado → desplegado en Cloud Run → secretos manejados
de forma segura → ejecución automatizada end-to-end sin intervención manual.
