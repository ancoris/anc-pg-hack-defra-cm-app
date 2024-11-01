import base64
import json
from typing import Any

from firebase_admin import initialize_app
from firebase_functions import https_fn
from firebase_functions.options import CorsOptions
from content_generation_utils import Prompt, run_generation
from tagging_generation_utils import get_tagging
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting


def initialize_services():
    initialize_app()
    vertexai.init(project="anc-pg-hack-defra-cm", location="us-central1")


def get_generation_config() -> dict:
    return {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }


def get_safety_settings() -> list:
    return [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.OFF,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.OFF,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF,
        ),
    ]


def generate(
    statement: str,
    model: GenerativeModel,
    config: dict,
    safety_settings: list,
    fileUrl: str,
) -> str:
    document1 = Part.from_uri(
        mime_type="application/pdf",
        uri=fileUrl,
    )

    document1 = (
        Part.from_uri(
            mime_type="application/pdf",
            uri=fileUrl,
        )
        if fileUrl
        else None
    )
    params = [""" make this statement formal: """, statement]
    if document1:
        params.append(document1)
    response = model.generate_content(
        params,
        generation_config=config,
        safety_settings=safety_settings,
    )
    return response.text


@https_fn.on_call(
    memory=512,
    cors=CorsOptions(
        cors_origins=[
            "https://anc-pg-hack-defra-cm.web.app",
            "https://anc-pg-hack-defra-cm.firebaseapp.com",
            "http://localhost:5173",
            "http://localhost:5000",
        ],
        cors_methods=["GET", "POST", "OPTIONS"],
    ),
)
def generateDocuments(req: https_fn.CallableRequest) -> Any:
    print("START req.data: ", req.data)
    statement = req.data.get("request", "")
    fileUrl = req.data.get("fileUrl", "")
    contentType = req.data.get("contentType", "")

    prompt = Prompt(fileUrl, contentType, statement)
    # model = get_model()
    # config = get_generation_config()
    # safety_settings = get_safety_settings()
    # output = generate(statement, model, config, safety_settings, fileUrl)
    generated_draft = run_generation(prompt)
    tagging = get_tagging(fileUrl)
    return {
        "generated_draft": generated_draft,
        "prompt": prompt.string_prompt,
        "taxonomy": tagging,
    }


# Initialize services
initialize_services()
