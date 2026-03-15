MILESTONE 
    0. MANUAL uploads YAML of user's CV Resources
        [COMPLETED] 
            Examples created with AI / Personal
            data_ingestion tooling created for user data
            spell data injestion right
            build a user object to store the CV data against
            put verification of data before a user is built
            refactor data_ingestion parse/validates to use generics
            create slug id's for projects, skills, qualifications,hobbies,people
            convert lists to dicts for better lookups (skills etc)
            add logger to generic class so all can use it
            refactor code so searches for id can be done by the schema class not by the data_ingestion tools directly
            create unit testing suit for User
        ---
        [TODO]
            [low] refactor code to use getattr instead of registry_map/configs
            [high]create unit testing suit for data_ingestion [ACTIVE]
            
        ---
____________________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    1. MANUAL upload of advert
        [COMPLETED]
        ---
        [TODO]
            Build advert path ingest
                determine type (webpage,pdf,docx)
                convert advert path and put into a yaml file
                    build data structure for this
            build check if advert has already been applied for
        ---
_____________________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    2. LLM: Inject: job advert text + all skills titles
        Prompt: "Return skills from the list relevant to this job"
        [COMPLETED]
        ---
        [TODO]
            Build litellm function to support uploading file
            Build tool to get Skills from user object and a format in which the llm likes it being uploaded (maybe pydantic?)
            Build unit test
            Build flexible verification of responses
                checking that skills were not halucinated              
        ---
_____________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    3. APP cross references skills in response with Skills table
        [COMPLETED]
        ---
        [TODO]
            PRIOIRTY research Pydantic
            build search function for skills
        ---
_________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    3.1 APP gives Skills objects that match along with titles of placements/projects that are linked       
        [COMPLETED]
        ---
        [TODO]
        ---
            give each skill/project/placement a unique ID to assist in cross referencing 
            build tooling to return projects and placements and skills 
_____________________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    3.2 LLM Inject job advert and skills and placements objects and generate a list of CV options
        [COMPLETED]
        ---
        [TODO]
            ensure a good data format to limit token use for these prompts
            fine tune the amount of responses/prompts needed
        ---
            A:Prompt:
            Write 3 personal statement tailored to the job advert
            B:Prompt:
            Write 3 blurbs for each of the Placements tailored to the job advert.
            C:Prompt:
            Match these blurbs together with the Personal statements and give a ranking of each combo
            Boots Suggestion Prompt:
                "Select the top 3 projects/placements that best prove the required skills, and write one high-impact achievement bullet for each."
            Return as yaml, docx or pdf
_____________________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    4. APP Parse response and present/export for user
        [COMPLETED]
        ---
        [TODO]
        ---
_____________________________________________________________________
            |                       |                       |
            |                       |                       |
____________V_______________________V_______________________V_________
    7. MANUAL user inserts into their templates
        [COMPLETED]
        ---
        [TODO]
        ---