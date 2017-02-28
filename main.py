"""
Details the various flask endpoints for processing and retrieving
command details as well as a swagger spec endpoint
"""

from multiprocessing import Process, Queue
import sys
import json
from flask import Flask, request, jsonify, Response
from flask_swagger import swagger

from db import session, engine
from base import Base, Command
from command_parser import get_valid_commands, process_command_output

app = Flask(__name__)


@app.route('/commands', methods=['GET'])
def get_command_output():
    """
    Returns as json the command details that have been processed
    ---
    tags: [commands]
    responses:
      200:
        description: Commands returned OK
      400:
        description: Commands not found
    """
    queue = Queue()

    commandList = process_command_output(queue)
    res = []
    # TODO: format the query result
    if commandList is not None:
        for command in commandList:
            res.append({"Command_string": command.command_string,
                   "length":command.length,
                   "duration":command.duration,
                   "output":command.output
                   })

        jres= Response(response=json.dumps(res), status=201, mimetype="application/json")
        jres.status_code = 200
    else:
        jres = Response(status=400)
    return jres


@app.route('/commands', methods=['POST'])
def process_commands():
    """
    Processes commmands from a command list
    ---
    tags: [commands]
    parameters:
      - name: filename
        in: formData
        description: filename of the commands text file to parse
        required: true
        type: string
    responses:
      200:
        description: Processing OK
    """

    temp_expns = request.get_json(force = True )
    filename = temp_expns['filename']
    file_data =  temp_expns['file_data']

    queue = Queue()
    status = get_valid_commands(queue, filename, file_data)

    """
    processes = [Process(target=process_command_output, args=(queue,))
                 for num in range(2)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    """

    if status is 200:
        jres = Response(status=200)
    else:
        jres = Response(status=400)
    return jres


@app.route('/database', methods=['POST'])
def make_db():
    """
    Creates database schema
    ---
    tags: [db]
    responses:
      200:
        description: DB Creation OK
    """
    Base.metadata.create_all(engine)
    return 'Database creation successful.'


@app.route('/database', methods=['DELETE'])
def drop_db():
    """
    Drops all db tables
    ---
    tags: [db]
    responses:
      200:
        description: DB table drop OK
    """
    Base.metadata.drop_all(engine)
    # if status is 200:
    #     jres = Response(status=200)
    # else:
    #     jres = Response(status=400)
    #
    # return jres

    return 'Database deletion successful.'


if __name__ == '__main__':
    """
    Starts up the flask server
    """
    port = 8080
    use_reloader = True

    # provides some configurable options
    for arg in sys.argv[1:]:
        if '--port' in arg:
            port = int(arg.split('=')[1])
        elif '--use_reloader' in arg:
            use_reloader = arg.split('=')[1] == 'true'

    app.run(port=port, debug=True, use_reloader=use_reloader)


# @app.route('/spec')
@app.route('/spec', methods=['GET'])
def swagger_spec():
    """
    Display the swagger formatted JSON API specification.
    ---
    tags: [docs]
    responses:
      200:
        description: OK status
    """
    spec = swagger(app)
    spec['info']['title'] = "Nervana cloud challenge API"
    spec['info']['description'] = ("Nervana's cloud challenge " +
                                   "for interns and full-time hires")
    spec['info']['license'] = {
        "name": "Nervana Proprietary License",
        "url": "http://www.nervanasys.com",
    }
    spec['info']['contact'] = {
        "name": "Nervana Systems",
        "url": "http://www.nervanasys.com",
        "email": "info@nervanasys.com",
    }
    spec['schemes'] = ['http']
    spec['tags'] = [
        {"name": "db", "description": "database actions (create, delete)"},
        {"name": "commands", "description": "process and retrieve commands"}
    ]
    return jsonify(spec)





