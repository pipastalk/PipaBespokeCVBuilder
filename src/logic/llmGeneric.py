
import enum
from enum import Enum
import os
class LLMModels(Enum):
    #TODO add more models and verify which ones we can use.
    Gemeni = "gemini-3-flash-preview"

class LLMConfig:
    def __init__(self, system_prompt: str, model_name: LLMModels):
        self._system_prompt = system_prompt
        self._model_name = model_name
        self.__available_tools = [] #TODO build related models, get_file/write_file etc
        self.request_counter = 0
    def set_system_prompt(self, system_prompt: str):#sets the system prompt for the LLM
        self._system_prompt = system_prompt
    def get_system_prompt(self):    #gets the system prompt for the LLM
        return self._system_prompt
    def set_llm_model(self, model_name: LLMModels): #sets the LLM model to be used
        self._model_name = model_name
    def get_llm_model(self):    #gets the LLM model to be used
        return self._model_name
    def genereate_config(self):
        raise NotImplementedError("method genereate_config() must be implemented by subclasses")
    def get_response(self, contents: str):
        raise NotImplementedError("method get_response() must be implemented by subclasses")
    def set_api_key(self):
        raise NotImplementedError("method set_api_key() must be implemented by subclasses")
    def generate_llm_client(self, model_name: LLMModels): #subclasses should use model_name.value to generate the client
        raise NotImplementedError("method generate_client() must be implemented by subclasses")
    def send_llm_request(self, contents: str):
        pass 
        #TODO this sends a request to the LLM asking it a question.
    def set_input_file(self, file_path: str):
        pass
        #TODO this sets a file to be included in the LLM request
    def set_output_file_path(self, file_path: str):
        pass 
        #TODO this sets a filepath for the LLM to write to / to copy any
    def set_contents(self, input, source_path = None): #sets the contents for the LLM request, input is the question and source_path is for supporting files
        contents = {"text": input, "files": []}
        if not input and not source_path:
            raise ValueError("No input or source path was provided")
        def contents_to_input(input):
            contents["text"] = input
        def contents_to_file(source_path):
            if not os.path.exists(source_path):
                raise ValueError("The provided source path does not exist")
            contents["files"].append(source_path)
        if input:
            contents_to_input(input)
        if source_path:
            contents_to_file(source_path)
        self.contents = contents
    def prompt(self):
        raise NotImplementedError("method prompt() must be implemented by subclasses")

class GeminiLLM(LLMConfig):
    from google import genai
    from google.genai import types
    def __init__(self, system_prompt: str, model_name: LLMModels):
        super().__init__(system_prompt, model_name)

    def genereate_config(self): #Sets tools llm can use and
        self.config = types.GenerateContentConfig(
            tools=[self.__available_models], 
            system_instruction=self._system_prompt
        )
    def get_response(self, contents: str):
        response = client.models.generate_content(
        model=self.__available_models[self._model_name.value],
        contents=messages,
        config=config
    )
    def generate_llm_client(self, model_name: LLMModels):
        client = genai.Client() 