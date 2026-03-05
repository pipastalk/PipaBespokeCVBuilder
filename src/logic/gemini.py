import litellm
from litellm import completion
import os
from enum import Enum
from dotenv import load_dotenv
class llmRole(Enum):
    SYSTEM = "system"
    USER = "user"
class supportedModels(Enum):
    Gemini = "gemini/gemini-2.5-flash"
class geminiReasoningLevel(Enum): #https://docs.litellm.ai/docs/providers/gemini#gemini-3-models---thinking_level-parameter
    LOW = "low"
    HIGH = "high"

class GeminiLLM:
    def request_response(self, model_name : supportedModels , access_role : llmRole, content_struct):
        load_dotenv()
        api_key = os.environ['GEMINI_API_KEY']
        contents = content_struct["text"] #TODO File input not handled yet
        messages = [{"role": access_role.value, "content": contents}]
        response = completion(
            model = model_name.value,
            messages = messages
        )
        return response
    def build_contents(self, text_input, file_input = None):
        #Expected content_struct format: {"text": "some text", "file_paths": ["path/to/jobadvert.pdf", "path/to/cv_template.pdf"]}
        contents = {"file_paths": []}
        if not text_input:
            raise ValueError("No text input was provided")
        contents["text"] = text_input
        if file_input:
            #TODO not handled by liteLLM yet
            pass
            if not os.path.exists(file_input):
                raise ValueError("The provided source path does not exist")
            contents["file_paths"].append(file_input)
        return contents
    def get_reply_from_response(self, response):
        reply = response.choices[0].message.content
        return reply


def test_gemini():        
    gemini = GeminiLLM()
    content_struct = gemini.build_contents(
        text_input="count to 5 and then stop",
        file_input=None
    )
    response = gemini.request_response(
        model_name = supportedModels.Gemini,
        access_role = llmRole.USER,
        content_struct = content_struct
    )
    reply = gemini.get_reply_from_response(response)
    print("Gemini's reply: ", reply)
if __name__ == "__main__":
    test_gemini()