import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part


PROJECT_ID = "anc-pg-hack-defra-cm"
LOCATION = "europe-west2"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Task instruction
INSTRUCTION_1 = """Your task is to tag the article provided.
Tag the article based on the summary provided.
Generate the tag from the taxonomy provided (JSON).
Output the tag by linking levels of taxonomy with a ">" (e.g. Fruit > Apple > Red Apple).
Output only ONE tag, without any explanations.
When in doubt return "".
**Taxonomy (JSON):**
{
    "Environment": {
        "Rural and countryside": {
            "Boats and waterways": {},
            "Countryside": {
                "Access to the countryside": {},
                "Parks, trails and nature reserves": {}
            },
            "Forests and woodland": {},
            "Rural development and land management": {
                "Commons and greens": {},
                "Pollution": {},
                "Protected sites": {},
                "Weeds and invasive, non-native plants": {},
                "Hedgerows": {},
                "Farming": {},
                "Contaminated land": {},
                "Economic growth in rural areas": {},
                "Rural economy and community": {}
            }
        },
        "Pollution and environmental quality": {},
        "River maintenance, flooding and coastal erosion": {},
        "Wildlife, animals, biodiversity and ecosystems": {
            "Biodiversity and ecosystems": {},
            "Wildlife and animal welfare": {},
            "Animal and plant health": {},
            "Protected sites and species": {
                "Marine sites and species": {},
                "Land sites": {},
                "Land species": {}
            },
            "Wildlife and habitat conservation": {
                "Birds": {},
                "Fish and shellfish": {},
                "Plants": {},
                "Invertebrates": {},
                "Reptiles and amphibians": {},
                "Mammals": {}
            },
            "Pets": {},
            "Animal welfare": {}
        },
        "Food and farming": {
            "Food and farming industry": {},
            "Common Agricultural Policy reform": {},
            "Keeping farmed animals": {
                "Cattle deaths": {},
                "Deer farming": {},
                "Pig identification, registration and movements": {},
                "Shows, fairs and markets": {},
                "Veterinary medicines": {},
                "Poultry registration": {},
                "Sheep and goats identification, registration and movements": {},
                "Import and export of farmed animals": {},
                "Cattle identification, registration and movements": {},
                "Reporting disease and disease outbreaks": {},
                "Bovine tuberculosis (bovine TB)": {}
            },
            "Producing and distributing food": {
                "Crops and horticulture": {},
                "Food labelling and safety": {},
                "Import, export and distribution of food": {},
                "Meat production": {},
                "Dairy and milk production": {},
                "Sugar": {},
                "Egg production and marketing": {}
            },
            "Farming and food grants and payments": {
                "Intervention schemes": {},
                "Rural grants and payments": {
                    "Basic Payment Scheme (BPS)": {},
                    "Common Agricultural Policy (CAP) reform": {},
                    "Cross-compliance": {},
                    "Rural development": {},
                    "Online applications and payments": {},
                    "Countryside stewardship": {}
                },
                "School milk scheme": {},
                "Private storage aid": {}
            }
        }
    }
}
"""
INSTRUCTION_2 = "**Article:**"


def get_prompt(source_material_gcs_uri):
    source_material = Part.from_uri(
        mime_type="application/pdf", uri=source_material_gcs_uri
    )

    return [INSTRUCTION_1, INSTRUCTION_2, source_material]


def generate_draft(prompt):
    model = GenerativeModel("gemini-1.5-pro-002")
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

    responses = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )

    try:
        result = responses.text.lstrip("```json\n").rstrip("\n```").replace('\\"', '"')
        return result
    except Exception as e:
        return "Tag not found."


def get_tagging(source_material_gcs_uri):
    prompt = get_prompt(source_material_gcs_uri)
    result = generate_draft(prompt)

    return result


if __name__ == "__main__":
    additional_instructions = """{
"voice": "use the active voice",
"title": "use sentence case: capitalize just the first letter of the first word in the title and use lowercase for the rest words",
"audience": "write for a reading age of 10",
"headings": "use ONLY statement form in headings",
"bullet points": "use lowercase at the start of any bullet point, for example, '*use lowercase' instead of '*Use lowercase'"
}
"""
    prompt = get_prompt(
        source_material_gcs_uri="gs://content_draft_generation/bluetongue_content_example/source_Guidance for accessing free testing Ver2.0 DRAFT.pdf",  # User uploaad
        writing_guide_gcs_uri="gs://content_draft_generation/guidance_policies/writing_for_gov_uk.pdf",  # Hodecode
        content_type_gcs_uri="gs://content_draft_generation/guidance_policies/example content type - detailed guide.pdf",  # Hodecode depending on content type dropdown
        style_guide_gcs_uri="gs://content_draft_generation/style_guide/defra style guide.pdf",  # Hodecode
        additional_instructions=additional_instructions,  # Free-text input from frontend
    )
    result = generate_draft(prompt)

    print(result)
