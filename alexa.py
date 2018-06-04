import json
import os

class AlexaRequest():

    INTENT_REQUEST = "IntentRequest"
    LAUNCH_REQUEST = "LaunchRequest"

    def __init__(self, request):
        self.sessionId = request['session']['sessionId']
        self.userId = request['session']['user']['userId']
        self.requestType = request['request']['type']
        self.attributes = request['session']['attributes'] if 'attributes' in request['session'] else {}
        req = request['request']
        if 'intent' in req:
            self.intent = req['intent']['name']
            self.slots = req['intent']['slots'] if 'slots' in req['intent'] else []
        else:
            self.intent = ""
        self.dialogState = req['dialogState'] if 'dialogState' in req else None
    

    def buildResponse(self, message=None, shouldEndSession=True, attributes=None, directives=None):
        session_attributes = {} if attributes is None else attributes
        should_end_session = shouldEndSession
        card_title = "Brain Buddy"
        reprompt_text = ""
        speech_output = "Hmm, Linkathon had an issue." if message is None else message

        return self.build_response(session_attributes, self.build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, directives))
    
    def getIntent(self):
        return self.intent
    
    def getSlots(self):
        return self.slots
    
    def getAttributes(self):
        return self.attributes
    
    def getRequestType(self):
        return self.requestType
    
    def getDialogState(self):
        return self.dialogState


    def build_speechlet_response(self, title, outputText, reprompt_text, should_end_session, directives=None):
        directivesValue = [] if directives is None else [{"type":directives}]
        output = {}
        output['cards'] = {
                "type": "Simple",
                "title": title,
                "content": outputText
            }
        output['directives'] = directivesValue
        if directives is None:
            output['outputSpeech'] = {
                "type": "PlainText",
                "text": outputText
            }
            output['reprompt'] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": reprompt_text
                }
            }
        output['shouldEndSession'] = should_end_session
        return output

    def build_response(self, session_attributes, speechlet_response):
        return {
            "version": "1.0",
            "sessionAttributes": session_attributes,
            "response": speechlet_response
    }
    

