
from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
chatbot_bp = Blueprint('chatbot', __name__)

# Configuración para OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_openrouter_client():
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)


from flask_login import current_user

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    if not request.json or 'message' not in request.json:
        return jsonify({"error": "Missing 'message' in request"}), 400

    client = _get_openrouter_client()
    if not client:
        return jsonify({"error": "API key not configured"}), 500

    # Obtener contexto del usuario

    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        nombre = getattr(current_user, 'nombre_completo', 'Usuario')
        roles = current_user.get_roles() if hasattr(current_user, 'get_roles') else []
        rol = roles[0] if roles else 'usuario'
        grado = ''
        seccion = ''
        if rol == 'estudiante' and hasattr(current_user, 'estudiante') and current_user.estudiante:
            grado = getattr(current_user.estudiante, 'grado_id', '')
            seccion = getattr(current_user.estudiante, 'seccion', '')
        contexto = (
            "Eres el asistente virtual de soporte del SistemaColegio. "
            "Tu objetivo es ayudar a los usuarios a entender y usar las funcionalidades del sistema escolar, responder dudas sobre el uso de la plataforma, navegación, registro, consulta de notas, ejercicios, contenidos y roles. "
            f"El usuario es {nombre}, rol: {rol}, grado: {grado}, seccion: {seccion}. "
            "Responde de forma clara y útil, guiando al usuario sobre cómo aprovechar el sistema. "
        )
    else:
        contexto = (
            "Eres el asistente virtual de soporte del SistemaColegio. "
            "Tu objetivo es ayudar a los usuarios a entender y usar las funcionalidades del sistema escolar, responder dudas sobre el uso de la plataforma, navegación, registro, consulta de notas, ejercicios, contenidos y roles. "
            "Responde de forma clara y útil, guiando al usuario sobre cómo aprovechar el sistema. "
        )

    mensaje_final = contexto + request.json['message']

    try:
        chat = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "user", "content": mensaje_final}
            ]
        )
        reply = chat.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500