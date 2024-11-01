import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part


# Task instruction
INSTRUCTION_1 = """Correct the draft article according to the style guide. Output only the revised draft article, without explanations or comments.
**Style Guide (PDF):**
"""
INSTRUCTION_1_ALT_PART_1 = """Correct the draft article according to the instructions and refer to the style guide as complementary instructions. Output only the revised draft article, without explanations or comments.
**Instructions:**
"""
INSTRUCTION_1_ALT_PART_2 = "**Style Guide (PDF):**"
INSTRUCTION_2 = "**Draft Article (PDF):**"


def get_model() -> GenerativeModel:
    return GenerativeModel("gemini-1.5-flash-002")


class Prompt:
    def __init__(
        self, source_material_gcs_uri, style_guide_gcs_uri, additional_instructions=None
    ):
        self.source_material = Part.from_uri(
            mime_type="application/pdf", uri=source_material_gcs_uri
        )
        self.style_guide = Part.from_uri(
            mime_type="application/pdf", uri=style_guide_gcs_uri
        )
        self.additional_instructions = additional_instructions
        self.string_prompt = None

    def get(self):
        prompt = None
        if self.additional_instructions:
            prompt = [
                INSTRUCTION_1_ALT_PART_1,
                self.additional_instructions,
                INSTRUCTION_1_ALT_PART_2,
            ]
        else:
            prompt = [INSTRUCTION_1]

        prompt.extend([self.style_guide, INSTRUCTION_2, self.source_material])
        self.string_prompt = [
            item.uri if hasattr(item, "uri") else item for item in prompt
        ]
        print("prompt", prompt)
        print("prompt string_prompt", self.string_prompt)
        return prompt


def get_prompt(
    source_material_gcs_uri, style_guide_gcs_uri, additional_instructions=None
):

    source_material = Part.from_uri(
        mime_type="application/pdf", uri=source_material_gcs_uri
    )
    style_guide = Part.from_uri(mime_type="application/pdf", uri=style_guide_gcs_uri)
    prompt = None
    if additional_instructions:
        prompt = [
            INSTRUCTION_1_ALT_PART_1,
            additional_instructions,
            INSTRUCTION_1_ALT_PART_2,
        ]
    else:
        prompt = [INSTRUCTION_1]

    print("pre prompt", prompt)
    prompt.extend([style_guide, INSTRUCTION_2, source_material]),
    print("post prompt", prompt)
    return prompt


def generate_draft(prompt):
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    }
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
        "top_p": 0.99,
    }
    model = get_model()
    print(f"start generating content")
    responses = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )

    result = responses.text.lstrip("```json\n").rstrip("\n```").replace('\\"', '"')

    return result


def run_generation(prompt: Prompt):
    prompt_array = prompt.get()
    print("prompt_array", prompt_array)
    result = generate_draft(prompt_array)
    return result


if __name__ == "__main__":
    # Source material GCS URI
    source_material_gcs_uri = (
        "gs://example_docs/source_Guidance for accessing free testing Ver2.0 DRAFT.pdf"
    )

    # Style guide GCS URI
    style_guide_gcs_uri = "gs://example_docs/defra style guide.pdf"

    prompt = get_prompt(source_material_gcs_uri, style_guide_gcs_uri, "")
    result = generate_draft(prompt)
