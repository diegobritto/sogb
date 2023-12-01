from datetime import datetime

from Mensage import INFO_ARQUIVO, INFO_DIRETORIO

class Inode:
    def __init__(self, idProprietario, ehDiretorio):
        self.idProprietario = idProprietario
        self.dataCriacao = datetime.now()
        self.dataAcessoUltimo = self.dataCriacao
        self.dataModificacaoUltima = self.dataCriacao
        self.permissoes = {
            "user": {"read": True, "write": True, "execute": False},
            "group": {"read": True, "write": False, "execute": False},
            "other": {"read": True, "write": False, "execute": False},
        }   
        self.ehDiretorio = ehDiretorio
        self.tamanho = 0
        self.blocos = [None] * 10
        self.contagemBlocos = 0
        self.blocoIndiretoSimples = None

    def informacoesInode(self):
        if (self.ehDiretorio):
            return str(INFO_DIRETORIO.format(self.tamanho, self.contagemBlocos, self.formatarStringPermissao(), self.idProprietario, self.dataAcessoUltimo, self.dataModificacaoUltima, self.dataCriacao))
        else:
            return INFO_ARQUIVO.format(
                self.tamanho,
                self.contagemBlocos,
                'arquivo regular' if self.tamanho != 0 else 'arquivo regular vazio',
                self.formatarStringPermissao(), 
                self.idProprietario, 
                self.dataAcessoUltimo,
                self.dataModificacaoUltima, 
                self.dataCriacao
            )
        
    def formatarStringPermissao(self):
        stringPermissao = "-"
        for escopo, permissao in self.permissoes.items():
            stringPermissao += "r" if permissao["read"] else "-"
            stringPermissao += "w" if permissao["write"] else "-"
            stringPermissao += "x" if permissao["execute"] else "-"
        return stringPermissao
