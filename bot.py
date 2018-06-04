import flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import json
import os
from alexa import AlexaRequest
import requests
import time
from neo4j.v1 import GraphDatabase

app = flask.Flask(__name__)
CORS(app,resources={r"/*": {"origins": "*"}})

driver = GraphDatabase.driver(os.environ['NEO4J_URL'])
session = driver.session()

@app.route("/alexa", methods=['GET','POST'])
def alexa():
    data = request.get_json(force=True)
    alexaRequest = AlexaRequest(data)

    if alexaRequest.LAUNCH_REQUEST == alexaRequest.getRequestType():
        return jsonify(alexaRequest.buildResponse('Welcome to Linkathon', False))
    elif alexaRequest.getIntent() == 'subjectCount':
        return jsonify(handleSubjectCount(alexaRequest))
    elif alexaRequest.getIntent() == 'subjectQuery':
        return jsonify(handleSubjectQuery(alexaRequest))
    

    return jsonify(alexaRequest.buildResponse())

def handleSubjectCount(alexaRequest):
    q = "MATCH (n:studySubject) RETURN count(n) AS c"
    result = list(session.run(q))

    return alexaRequest.buildResponse('There are ' + str(result[0]['c']) + ' subjects', True)

def handleSubjectQuery(alexaRequest):
    q = "MATCH (n:studySubject) WHERE n.%s %s toInteger(%s) RETURN count(n) AS c"
    slots = alexaRequest.getSlots()
    operator = slots['operator']['value']
    operatorF = ''
    if operator == 'greater than':
        operatorF = '>'
    else:
        operatorF = '<'
    
    query = q % (slots['column']['value'], operatorF, slots['val']['value'])
    print(query)
    result = list(session.run(query))
    c = result[0]['c']

    response = 'There are %d subjects having %s %s %s' % (c, slots['column']['value'], operator, slots['val']['value'])
    
    return alexaRequest.buildResponse(response, True) 



if __name__ == "__main__":
    app.run(host="0.0.0.0")