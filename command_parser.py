import subprocess
import time
import json
from db import session, engine
from base import Base, Command


"""
Handles the work of validating and processing command input.
"""


def get_valid_commands(queue, fi):
    # TODO: efficiently evaluate commands

    # File processing for getting COMMAND LIST and VALID COMMANDS
    with open("/home/gaurang/Downloads/GitRepo/IntelCode/MySolution/Intel_cloud_code_challenge/"+fi, "r") as fh:
       CommandLine = fh.readlines()

    commandList=[]
    validList=[]

    for line in CommandLine:
        if '[COMMAND LIST]' in line:
            commandFlag = True
            validFlag = False
        elif '[VALID COMMANDS]' in line:
            commandFlag = False
            validFlag = True

        if '[COMMAND LIST]' not in line and '[VALID COMMANDS]' not in line and line.rstrip() <> '':
            if commandFlag :
                commandList.append(line.rstrip())
            elif validFlag :
                validList.append(line.rstrip())

    #Get all the valid commands
    validCommandsFromInput = set(commandList) & set(validList)

    for command in validCommandsFromInput:
        start = time.time()
        commandResult = subprocess.check_output(command, shell=True)
        CommandTimeTaken = (time.time() - start)

        CommandString = command
        commandLength = len(command)
        print commandResult
        print CommandString
        print commandLength
        print CommandTimeTaken

        # Check if the commad is already in Table
        flag = session.query(Command).filter_by(output=commandResult).first()

        if flag:
            print 'same query'
        else:
            ed_commands = Command(CommandString, commandLength, CommandTimeTaken, commandResult)
            session.add(ed_commands)
            session.commit()

    return 200


def process_command_output(queue):
    # TODO: run the command and put its data in the db
    # commandList = session.query(Command).get(1)
    commandList = session.query(Command).all()

    return commandList


