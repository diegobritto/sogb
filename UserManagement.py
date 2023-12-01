from Constant import PASSWORD_ADMIN, USERNAME_ADMIN
from Mensage import APENAS_ADMIN_PODE_ADICIONAR_NOVO_USUARIO, APENAS_ADMIN_PODE_REMOVER_USUARIO, NOME_USUARIO_EXISTENTE, USUARIO_COM_ESSE_ID_JA_EXISTE, USUARIO_CRIADO_COM_SUCESSO, USUARIO_NAO_ENCONTRADO, USUARIO_REMOVIDO_COM_SUCESSO, USUARIO_ROOT_NAO_PODE_SER_REMOVIDO
from User import User


class UserManagement:
    def __init__(self):
        self.users = []
        self.currentUserId = None
        self.currentUsername = None
        self.adduser(USERNAME_ADMIN, PASSWORD_ADMIN, "0", True)

    def adduser(self, username, password, userId, isAdmin):
        currentUser = self.getUser(self.currentUsername)
        if (currentUser != None and not currentUser.isAdmin):
            print(APENAS_ADMIN_PODE_ADICIONAR_NOVO_USUARIO)
            return
        
        for user in self.users:
            if (user.username == username):
                print(NOME_USUARIO_EXISTENTE)
                return
            if (user.userId == userId):
                print(USUARIO_COM_ESSE_ID_JA_EXISTE)
                return
        newUser = User(username, userId, password, isAdmin)
        self.users.append(newUser)
        if (userId != "0"):
            print(USUARIO_CRIADO_COM_SUCESSO)
    
    def rmuser(self, username):
        currentUser = self.getUser(self.currentUsername)
        if (currentUser != None and not currentUser.isAdmin):
            print(APENAS_ADMIN_PODE_REMOVER_USUARIO)
            return
        
        if (username == USERNAME_ADMIN):
            print(USUARIO_ROOT_NAO_PODE_SER_REMOVIDO)
            return

        for user in self.users:
            if (user.username == username):
                self.users.remove(user)
                print(USUARIO_REMOVIDO_COM_SUCESSO)
                return
        print(USUARIO_NAO_ENCONTRADO)

    def lsuser(self):
        for user in self.users:
            print(user.username + " Uid: " + user.userId)
  
    def getUser(self, username):
        for user in self.users:
            if (user.username == username):
                return user
        return None
