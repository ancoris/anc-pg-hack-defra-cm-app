import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part


# Task instruction
INSTRUCTION_1 = """Correct the draft article according to the GOV.UK writing guide provided.
Tailor the content to the content-type specification provided.
Use the style guide as complementary rules.
Output in Markdown format, with only the revised draft article, without explanations or comments.
"""
INSTRUCTION_1_ALT = """Correct the draft article according to the instructions and the GOV.UK writing guide provided.
Tailor the content to the content-type specification provided.
Use the style guide as complementary rules.
Output in Markdown format, with only the revised draft article, without explanations or comments.
**Instructions (JSON):**
"""
INSTRUCTION_2 = "**GOV.UK writing guide (PDF):**"
INSTRUCTION_3 = "**Content-type specification (PDF):**"
INSTRUCTION_4 = "**Style Guide (PDF):**"
INSTRUCTION_5 = "**Draft Article (PDF):**"

WRITING_GUIDE_URI = "gs://anc-pg-hack-defra-cm.appspot.com/writing_for_gov_uk.pdf"
STYLE_GUIDE_URI = (
    "gs://anc-pg-hack-defra-cm.appspot.com/style_guide_defra style guide.pdf"
)


def get_model() -> GenerativeModel:
    return GenerativeModel("gemini-1.5-flash-002")


class Prompt:
    def __init__(
        self,
        source_material_gcs_uri,
        content_type_gcs_uri,
        additional_instructions=None,
    ):
        self.source_material = Part.from_uri(
            mime_type="application/pdf", uri=source_material_gcs_uri
        )
        self.style_guide = Part.from_uri(
            mime_type="application/pdf", uri=STYLE_GUIDE_URI
        )
        self.writing_guide = Part.from_uri(
            mime_type="application/pdf", uri=WRITING_GUIDE_URI
        )
        self.content_type_guide = Part.from_uri(
            mime_type="application/pdf", uri=content_type_gcs_uri
        )
        self.additional_instructions = additional_instructions
        self.string_prompt = None

    def get(self):
        prompt = None
        if self.additional_instructions:
            prompt = [INSTRUCTION_1_ALT, self.additional_instructions]
        else:
            prompt = [INSTRUCTION_1]

        self.string_prompt = [*prompt]
        prompt.extend(
            [
                INSTRUCTION_2,
                self.writing_guide,
                INSTRUCTION_3,
                self.content_type_guide,
                INSTRUCTION_4,
                self.style_guide,
                INSTRUCTION_5,
                self.source_material,
            ]
        )
        # self.string_prompt.extend(
        #     [
        #         INSTRUCTION_2,
        #         WRITING_GUIDE_URI.split("/")[-1],
        #         INSTRUCTION_3,
        #         self.content_type_guide.split("/")[-1],
        #         INSTRUCTION_4,
        #         self.style_guide.split("/")[-1],
        #         INSTRUCTION_5,
        #         self.source_material.split("/")[-1],
        #     ]
        # )
        self.string_prompt = ""
        print("prompt", prompt)
        print("string_prompt", self.string_prompt)
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
