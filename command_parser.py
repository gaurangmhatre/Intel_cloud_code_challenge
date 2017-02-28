import subprocess
import time
import os
from db import session, engine
from base import Base, Command
from subprocess import STDOUT

"""
Handles the work of validating and processing command input.
"""


def get_valid_commands(queue, fi, file_data):
    # TODO: efficiently evaluate commands


    # File processing for getting COMMAND LIST and VALID COMMANDS

    script_dir = os.path.dirname(__file__)
    path = os.path.join(script_dir, fi)
    try:
        with open(path, "r") as fh:
           CommandLine = fh.readlines()
    except IOError as err:
        CommandLine = file_data

    commandList=[]
    validList=[]

    for line in CommandLine:
        if '[COMMAND LIST]' in line:
            commandFlag = True
            validFlag = False
        elif '[VALID COMMANDS]' in line:
            commandFlag = False
            validFlag = True

        if '[COMMAND LIST]' not in line and '[VALID COMMANDS]' not in line and line.rstrip() != '':
            if commandFlag :
                commandList.append(line.rstrip())
            elif validFlag :
                validList.append(line.rstrip())

    #Get all the valid commands
    validCommandsFromInput = set(commandList) & set(validList)

    for command in validCommandsFromInput:
        try:
            start = time.time()
            #commandResult = subprocess.check_output(command, shell=True)
            commandResult = subprocess.check_output(command, shell=True, stderr=STDOUT, timeout=1 )
            CommandTimeTaken = (time.time() - start)


            CommandString = command
            commandLength = len(command)
            print(commandResult)
            print(CommandString)
            print(commandLength)
            print(CommandTimeTaken)

            # Check if the commad is already in Table
            flag = session.query(Command).filter_by(output=commandResult).first()

            if flag:
                print('Command : "', command, '" is alredy in commands table')
            else:
                ed_commands = Command(CommandString, commandLength, CommandTimeTaken, commandResult)
                session.add(ed_commands)
                session.commit()
        except subprocess.CalledProcessError as err:
            print('Handling CalledProcessError: ', err, ' for command: ', command)
            continue
        except subprocess.TimeoutExpired as err:
            print('Handling TimeoutExpired: ', err, ' for command: ', command)
            continue
    return 200


def process_command_output(queue):
    # TODO: run the command and put its data in the db
    # commandList = session.query(Command).get(1)
    commandList = session.query(Command).all()

    return commandList


