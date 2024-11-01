import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part


# Task instruction
INSTRUCTION_1 = """Correct the draft article according to the instructions and the GOV.UK writing guide provided.
Tailor the content to the content-type specification provided.
Use the style guide as complementary rules.
Output in Markdown format, with only the revised draft article, without explanations or comments.
"""
INSTRUCTION_1_ALT = """Correct the draft article according to the instructions and the GOV.UK writing guide provided.
Tailor the content to the content-type specification provided.
Use the style guide and acceptance criteria as complementary guide.
Output in Markdown format, with only the revised draft article, without explanations or comments.
"""
INSTRUCTION_2 = """**Instructions (JSON):**
{
"voice": "use the active voice",
"title": "use sentence case: capitalize just the first letter of the first word in the title and use lowercase for the rest words",
"audience": "write for a reading age of 10",
"headings": "use ONLY statement form in headings",
"bullet points": "use lowercase at the start of any bullet point, for example, '*use lowercase' instead of '*Use lowercase'"
}
"""
INSTRUCTION_3 = "**GOV.UK writing guide (PDF):**"
INSTRUCTION_4 = "**Content-type specification (PDF):**"
INSTRUCTION_5 = "**Style Guide (PDF):**"
INSTRUCTION_6 = "**Acceptance criteria (TEXT):**"
INSTRUCTION_7 = "**Draft Article (PDF):**"

WRITING_GUIDE_URI = "gs://anc-pg-hack-defra-cm.appspot.com/writing_for_gov_uk.pdf"
STYLE_GUIDE_URI = (
    "gs://anc-pg-hack-defra-cm.appspot.com/style_guide_defra style guide.pdf"
)


def get_model() -> GenerativeModel:
    return GenerativeModel("gemini-1.5-pro-002")


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
            prompt = [
                INSTRUCTION_1_ALT,
                INSTRUCTION_2,
                INSTRUCTION_3,
                self.writing_guide,
                INSTRUCTION_4,
                self.content_type_guide,
                INSTRUCTION_5,
                self.style_guide,
                INSTRUCTION_6,
                self.additional_instructions,
                INSTRUCTION_7,
                self.source_material,
            ]
        else:
            prompt = [
                INSTRUCTION_1,
                INSTRUCTION_2,
                INSTRUCTION_3,
                self.writing_guide,
                INSTRUCTION_4,
                self.content_type_guide,
                INSTRUCTION_5,
                self.style_guide,
                INSTRUCTION_7,
                self.source_material,
            ]

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
