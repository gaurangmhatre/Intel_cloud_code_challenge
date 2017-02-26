import subprocess
import time
from db import session, engine
from base import Base, Command

"""
Handles the work of validating and processing command input.
"""


def get_valid_commands(queue, fi):
    # TODO: efficiently evaluate commands

    # File processing for getting COMMAND LIST and VALID COMMANDS
    with open("/home/gaurang/Downloads/GitRepo/IntelCode/MySolution/Intel_cloud_code_challenge/commands.txt", "r") as fh:
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

    #commandResult = subprocess.check_output('ps -ef | '+command, shell=True)

    # c = conn.cursor()
    # for item in my_list:

    for command in validCommandsFromInput:
        start = time.time()
        commandResult = subprocess.check_output('ps -ef | '+command, shell=True)
        CommandTimeTaken = (time.time() - start)

        CommandString = command
        commandLength = len(command)
        print commandResult
        print CommandString
        print commandLength
        print CommandTimeTaken

        ed_commands= Command(CommandString,commandLength, CommandTimeTaken,commandResult)
        session.add(ed_commands)
    session.commit()


    queue.put(command)


def process_command_output(queue):
    # TODO: run the command and put its data in the db

    command = queue.get()


