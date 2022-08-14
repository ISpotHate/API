# API Endpoint
/
The ISpotHate API, hosted at [ispothate.eastus.cloudapp.azure.com:8000](http://ispothate.eastus.cloudapp.azure.com:8000). 

Documentation: http://ispothate.eastus.cloudapp.azure.com:8000/docs

Redoc Documentation: http://ispothate.eastus.cloudapp.azure.com:8000/redoc

Features: 
- /ishate -> Returns the confidence of HATE speech or NON_HATE speech
- /ishomophobia -> Returns a boolean result of whether the text is homophobia or not
- /isswearing -> Returns a boolean result of whether the text contains a curse word/offensive speech, and censors the text and returns it
- /sentiment -> Returns the sentiment of the text (negative, neutral, or positive)
- /intent -> Returns the intent of the text (confidence of speech being targeted, aggressive, or hateful)
- /toxicity -> Returns whether the speech is toxic or not, as well as other labels (toxicity, severe_toxicity, obscene, threat, insult, identity_attack, sexual_explicit)
- /returnlabels -> Returns every label (from above methods)

Want to add more features? Either [install the API and run it locally](SETUP.md) or (add your own model)[ADDMODEL.md]
