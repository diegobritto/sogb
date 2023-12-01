import os
from Constant import MAX_BLOCK
from FileSystem import FileSystem
from Mensage import COMANDO_NAO_RECONHECIDO, USUARIO_LOGIN

if __name__ == "__main__":
    fileSystem = FileSystem(MAX_BLOCK) # Maximum block count

    commandsDictionary = {
        "adduser": lambda fileSystem, args: fileSystem.adduser(args[0], args[1], args[2], False),
        "cat": lambda fileSystem, args: fileSystem.cat(args[0]),
        "cd": lambda fileSystem, args: fileSystem.cd(args[0]),
        "chmod": lambda fileSystem, args: fileSystem.chmod(args[0], args[1]),
        "chown": lambda fileSystem, args: fileSystem.chown(args[0], args[1]),
        "clear": lambda fileSystem, args: os.system('clear' if os.name == 'posix' else 'cls'),
        "format": lambda fileSystem, _: fileSystem.format(),
        "help": lambda fileSystem, args: fileSystem.help(),
        "ls": lambda fileSystem, args: fileSystem.ls(),
        "lsuser": lambda fileSystem, args: fileSystem.lsuser(),
        "login": lambda fileSystem, args: fileSystem.login(args[0], args[1]),
        "logout": lambda fileSystem, args: fileSystem.logout(),
        "mkdir": lambda fileSystem, args: fileSystem.mkdir(args[0]),
        "rmdir": lambda fileSystem, args: fileSystem.rmdir(args[0]),
        "rm": lambda fileSystem, args: fileSystem.rm(args[0]),
        "rmuser": lambda fileSystem, args: fileSystem.rmuser(args[0]),
        "stat": lambda fileSystem, args: fileSystem.stat(args[0]),
        "touch": lambda fileSystem, args: fileSystem.touch(args[0]),
        "write": lambda fileSystem, args: fileSystem.escreveConteudo(args[0], ' '.join(args[1:])),
    }
    while True:
        if (fileSystem.userManagement.currentUserId is None):
            userInput = input(USUARIO_LOGIN)
            userInput = str("login "+userInput)
        else:
            userInput = input(fileSystem.userManagement.currentUsername + ":" + fileSystem.diretorioAtual + "$ ")

        inputParts = userInput.split()
        inputCommand = inputParts[0] if len(inputParts) > 0 else None
        commandArgs = inputParts[1:]

        if (inputCommand == "exit"):
            break

        if (fileSystem.userManagement.currentUserId is None):
            if (inputCommand == "login"):
                fileSystem.login(commandArgs[0], commandArgs[1])
        else:
            if (inputCommand in commandsDictionary):
                commandsDictionary[inputCommand](fileSystem, commandArgs)
            else:
                print(COMANDO_NAO_RECONHECIDO)
