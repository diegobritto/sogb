from Constant import BLOCKS_SIZE, NUM_BLOCKS
from Inode import Inode
from Mensage import ARQUIVO_EH_DIRETORIO, ARQUIVO_MENSAGEM, ARQUIVO_NAO_ENCONTRADO, ARQUIVO_OU_DIRETORIO_NAO_EXISTE, CONTEUDO_EXCEDE_10_BLOCOS, EH_DIRETORIO, FALHA_AO_CRIAR_DIRETORIO, FALHA_AO_EXCLUIR_DIRETORIO_NAO_VAZIO, FALHA_REMOVER_ARQUIVO, FALHA_REMOVER_DIRETORIO, NAO_EH_DIRETORIO, PERMISSAO_ERRO_MESSAGEM, USUARIO_NAO_ENCONTRADO, USUARIO_SEM_PERMISSAO_LEITURA, USUARIO_SENHA_INVALIDO
from User import User
from Block import Block
from colorama import Fore, Style
from datetime import datetime
from UserManagement import UserManagement
class FileSystem:
    def __init__(self, maxBlocks):
        self.maxBlocks = maxBlocks
        self.blocks = NUM_BLOCKS
        self.blockSize = BLOCKS_SIZE
        self.inodes = {} 
        self.rootDirectoryPath = "/"
        self.diretorioAtual = self.rootDirectoryPath
        self.userManagement = UserManagement()
        self.mkdir(self.rootDirectoryPath) 

#region usuario

    def getUser(self, username):
        return self.userManagement.getUser(username)
    
    def adduser(self, username, password, userId, isAdmin):
        self.userManagement.adduser(username, password, userId, isAdmin)

    def rmuser(self, username):
        self.userManagement.rmuser(username)

    def lsuser(self):
        self.userManagement.lsuser()
    
    def login(self, username, password):
        for user in self.userManagement.users:
            if (user.username == username):
                if (user.password == password):
                    self.userManagement.currentUserId = user.userId
                    self.userManagement.currentUsername = user.username
                    return
                else:
                    print(USUARIO_SENHA_INVALIDO)
                    return
        print(USUARIO_SENHA_INVALIDO)

    def logout(self):
        self.userManagement.currentUserId = None
        self.userManagement.currentUsername = None

#endregion

#region validações
    def temPermissaoLeitura(self, inode):
        currentUser = self.getUser(self.userManagement.currentUsername)
        if (currentUser.isAdmin):
            return True
        
        inodepermissoes = inode.permissoes
        if (self.userManagement.currentUserId == inode.ownerId):
            if (inodepermissoes["user"]["read"]):
                return True
        elif (inodepermissoes["other"]["read"]):
            return True
        return False

    def temPermissaoEscrita(self, inode):
        currentUser = self.getUser(self.userManagement.currentUsername)
        if (currentUser.isAdmin):
            return True
        
        inodepermissoes = inode.permissoes
        if (self.userManagement.currentUserId == inode.idProprietario):
            if (inodepermissoes["user"]["write"]):
                return True
        elif (inodepermissoes["other"]["write"]):
            return True
        return False
   
    def diretorioEhRoot(self):
        return self.diretorioAtual == "/"
    
    def ehVazio(self, directoryPath):
        for path, inode in self.inodes.items():
            if path.startswith(directoryPath + "/"):
                return False
        return True

#endregion
 
#region comandos
    def format(self):
        self.__init__(self.maxBlocks)

    def touch(self, fileName):
        filePath = self.getCaminhoCompleto(fileName)
        if (filePath in self.inodes):
            self.inodes[filePath].dataAcessoUltimo = datetime.now()
            self.inodes[filePath].dataModificacaoUltima = datetime.now()
        else:
            newInode = Inode(self.userManagement.currentUserId, False)
            self.inodes[filePath] = newInode

    def escreveConteudo(self, fileName, data):
        filePath = self.getCaminhoCompleto(fileName)
        if (filePath in self.inodes):
            inode = self.inodes.get(filePath)
            if (inode.ehDiretorio):
                print(ARQUIVO_EH_DIRETORIO.format(fileName))
                return
            
            if (not self.temPermissaoEscrita(inode)):
                print(PERMISSAO_ERRO_MESSAGEM.format(fileName))
                return
            bytesData = bytearray(data, 'utf-8')
            bytesCount = len(bytesData)
            inode.blocos = [None] * 10 
            inode.tamanho = bytesCount
            self.blocks -= inode.contagemBlocos
            inode.contagemBlocos = 0
            for byte in range(0, bytesCount, self.blockSize):
                inode.contagemBlocos += 1
                if (inode.contagemBlocos > 10):
                    print (CONTEUDO_EXCEDE_10_BLOCOS.format(str(self.blockSize)))
                    inode.contagemBlocos = 0
                    inode.blocos = [None] * 10 
                    break

                newBlock = Block(self.blockSize)
                newBlock.write(bytesData[byte:byte + self.blockSize])
                inode.blocos.append(newBlock)
            
            self.blocks += inode.contagemBlocos
            inode.dataModificacaoUltima = datetime.now()
        else:
            print(ARQUIVO_NAO_ENCONTRADO)

    def cat(self, fileName):
        filePath = self.getCaminhoCompleto(fileName)
        if (filePath in self.inodes):
            inode = self.inodes.get(filePath)
            if (inode.ehDiretorio):
                print(EH_DIRETORIO.format(fileName))
                return
            
            if (not self.temPermissaoLeitura(inode)):
                print(USUARIO_SEM_PERMISSAO_LEITURA.format(fileName))
                return

            fileContent = ""
            for block in inode.blocos:
                if (block != None):
                    fileContent += block.read().decode('utf-8')
            print(fileContent)
        else:
            print(ARQUIVO_NAO_ENCONTRADO)

    def rm(self, fileName):
        filePath = self.getCaminhoCompleto(fileName)
        if (filePath in self.inodes):
            if (not self.inodes[filePath].ehDiretorio):
                self.inodes.pop(filePath)
            else:
                print(FALHA_REMOVER_ARQUIVO.format(fileName))
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)

    def chown(self, newOwnerName, fileDirectoryName):
        newOwner = self.getUser(newOwnerName)
        if (newOwner == None):
            print(USUARIO_NAO_ENCONTRADO)
            return
        
        fileDirectoryPath = self.getCaminhoCompleto(fileDirectoryName)
        if (fileDirectoryPath in self.inodes):
                inode = self.inodes.get(fileDirectoryPath)
                inode.ownerId = newOwner.userId
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)

    def chmod(self, permissoes, fileDirectoryName):
        fileDirectoryPath = self.getCaminhoCompleto(fileDirectoryName)

        if (fileDirectoryPath in self.inodes):
            permissoesDictionary = {
                "0": [False, False, False], # ---
                "1": [False, False, True],  # --x
                "2": [False, True, False],  # -w-
                "3": [False, True, True],   # -wx
                "4": [True, False, False],  # r--
                "5": [True, False, True],   # r-x
                "6": [True, True, False],   # rw-
                "7": [True, True, True]     # rwx
            }
            
            permissoesChars = list(permissoes) 

            # Garante que o chmod tenha permissão para usuário, grupo e outros (000 - três caracteres)
            for i in range (len(permissoesChars), 3, 1):
                permissoesChars.append('0')
        
            
            permissionUser = permissoesDictionary.get(permissoesChars[0])
            permissionGroup = permissoesDictionary.get(permissoesChars[1])
            permissionOther = permissoesDictionary.get(permissoesChars[2])

            self.inodes[fileDirectoryPath].permissoes["user"] = {
                "read": permissionUser[0],
                "write": permissionUser[1],
                "execute": permissionUser[2]
            }

            self.inodes[fileDirectoryPath].permissoes["group"] = {
                "read": permissionGroup[0],
                "write": permissionGroup[1],
                "execute": permissionGroup[2]
            }

            self.inodes[fileDirectoryPath].permissoes["other"] = {
                "read": permissionOther[0],
                "write": permissionOther[1],
                "execute": permissionOther[2]
            }
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)

    def mkdir(self, directoryName):
        directoryPath = self.getCaminhoCompleto(directoryName)
        if (directoryPath in self.inodes):
            if (self.inodes[directoryPath].ehDiretorio):
                print (FALHA_AO_CRIAR_DIRETORIO.format(directoryName))
                return
            
        newInode = self.criaInode()
        newInode.blocos.append(Block(self.blockSize))
        newInode.contagemBlocos += 1
        self.blocks += 1
        self.inodes[directoryPath] = newInode

    def criaInode(self):
        if (self.userManagement.currentUserId != None):
            return Inode(self.userManagement.currentUserId, True)
        else:
            return Inode(0, True)

    def rmdir(self, directoryName):
        directoryPath = self.getCaminhoCompleto(directoryName)
        if (directoryPath in self.inodes):
            inode = self.inodes[directoryPath]
            if (inode.ehDiretorio):
                if (self.ehVazio(directoryPath)):
                    self.blocks -= inode.contagemBlocos
                    self.inodes.pop(directoryPath)
                else:
                    print(FALHA_AO_EXCLUIR_DIRETORIO_NAO_VAZIO.format(directoryName))
            else:
                print(FALHA_REMOVER_DIRETORIO.format(directoryName))
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)
    
    def cd(self, changeToDirectoryName):
        directoryPath = self.getCaminhoCompleto(changeToDirectoryName)
            
        if (changeToDirectoryName == ".."):
            if (not self.diretorioEhRoot):
                directory = self.diretorioAtual.split("/")
                if (len(directory) > 2):
                    self.diretorioAtual = "/".join(directory[:-1])
                else:
                    self.diretorioAtual = "/"
            else:
                self.diretorioAtual = "/"
        elif (directoryPath in self.inodes):
            if (self.inodes[directoryPath].ehDiretorio):
                self.diretorioAtual += "/" + changeToDirectoryName if not self.diretorioEhRoot else changeToDirectoryName
            else:
                print(NAO_EH_DIRETORIO.format(changeToDirectoryName))
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)

    def ls(self):
        diretorioAtualCaminho = self.diretorioAtual + ("/" if not self.diretorioEhRoot else "")
        for diretorioCaminhoArquivo, inode in self.inodes.items():
            # Verifica se o item está dentro do diretório atual
            if diretorioCaminhoArquivo.startswith(diretorioAtualCaminho) and diretorioCaminhoArquivo != diretorioAtualCaminho:
                # Obtém o caminho relativo ao diretório atual
                caminhoRelativo = diretorioCaminhoArquivo[len(diretorioAtualCaminho):]
                # Verifica se o caminho relativo não contém mais barras (é um item direto no diretório atual)
                if "/" not in caminhoRelativo:
                    if self.inodes[diretorioCaminhoArquivo].ehDiretorio:
                        print(Fore.BLUE + " "+caminhoRelativo, end=" ")
                        print(Style.RESET_ALL, end = "")
                    else:
                        print(caminhoRelativo+ " ", end=" ")
        print()
    

    def stat(self, fileName):
        filePath = self.getCaminhoCompleto(fileName)
        if (filePath in self.inodes):
            print(ARQUIVO_MENSAGEM.format(fileName))
            print(self.inodes[filePath].informacoesInode())
        else:
            print(ARQUIVO_OU_DIRETORIO_NAO_EXISTE)

    def getCaminhoCompleto(self, directoryFileName):
        if (directoryFileName == "/"):
            return directoryFileName
        
        if (self.diretorioEhRoot):
            directoryPath = self.diretorioAtual + directoryFileName
        else:
            directoryPath = self.diretorioAtual + "/" + directoryFileName
        return directoryPath

    def help(self):
        textoAjuda = "Comandos:\n"
        textoAjuda += "\nadduser 'nomeUsuario' 'senha' 'idUsuario':\n    Adiciona um novo usuário com o nome de usuário, senha e ID de usuário especificados.\n"
        textoAjuda += "\ncat 'nomeArquivo':\n    Exibe o conteúdo do arquivo especificado.\n"
        textoAjuda += "\ncd 'nomeDiretorio':\n    Altera o diretório atual para o especificado.\n"
        textoAjuda += "\nchmod 'permissões' 'nomeArquivoOuDiretorio':\n    Altera as permissões do arquivo ou diretório usando dígitos 4 (leitura), 2 (escrita) e 1 (execução) para proprietário, grupo e outros.\n"
        textoAjuda += "\n    Exemplo: 'chmod 754 nomeArquivo123' define permissões de leitura, escrita e execução para o proprietário (7), leitura e execução para o grupo (5) e leitura para os outros (4).\n"
        textoAjuda += "\nformat:\n    Formata o sistema de arquivos, apagando todos os arquivos, diretórios e usuários.\n"
        textoAjuda += "\nhelp:\n    Exibe esta mensagem de ajuda.\n"
        textoAjuda += "\nls:\n    Lista arquivos e diretórios no diretório atual.\n"
        textoAjuda += "\nlogin 'nomeUsuario' 'senha':\n    Faz login no sistema com o nome de usuário e senha especificados.\n"
        textoAjuda += "\nlogout:\n    Faz logout do usuário atual do sistema.\n"
        textoAjuda += "\mkdir 'nomeDiretorio':\n    Cria um novo diretório com o nome especificado.\n"
        textoAjuda += "\nrm 'nomeArquivo':\n    Remove o arquivo especificado.\n"
        textoAjuda += "\nrmuser 'nomeUsuario':\n    Remove um usuário com o nome de usuário especificado.\n"
        textoAjuda += "\nrmdir 'nomeDiretorio':\n    Remove o diretório especificado.\n"
        textoAjuda += "\nstat 'nomeArquivoOuDiretorio':\n    Exibe informações sobre o arquivo ou diretório especificado, como ID do proprietário, permissões, tamanho e datas.\n"
        textoAjuda += "\ntouch 'nomeArquivo':\n    Cria um arquivo vazio ou atualiza os tempos de acesso e modificação para o tempo atual.\n"
        textoAjuda += "\nwrite 'nomeArquivo' 'conteudo':\n    Escreve o conteúdo no arquivo especificado.\n"

        print(textoAjuda)


#endregion

