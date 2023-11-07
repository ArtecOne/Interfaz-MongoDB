import customtkinter as ctk
from mongo import insert_app, conectar
from async_tkinter_loop import async_handler
from async_tkinter_loop.mixins import AsyncCTk


class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        
        
        self.title("Cluster Admin")
        self.geometry("900x600")
        self.minsize(600,600)
        
        self.login = Login(self)
        self.login.place(anchor = "n", relx = 0.5 , rely = 0,
                         relwidth = 1 , relheight = 1)
        
        self.tabs = Pestañas(self)
        self.tabs.place(anchor = "n", relx = 0.5, rely = 0,
                        relwidth = 1 , relheight = 1)
        
        self.login.lift(aboveThis=self.tabs)

class Login(ctk.CTkFrame , AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.user_var = ctk.StringVar(value= "ingresa tu uri")
        self.alert_var = ctk.StringVar()
        self.inicio()
    
    @async_handler
    async def log_in(self):        
        if await conectar(self.user_var.get()):
            self.destroy()
        else:
            self.alert_var.set("revisa tu Connection string")
    
    def inicio(self):
        input_user = ctk.CTkEntry(self, textvariable= self.user_var)
        input_user.place(relx = 0.5 , rely = 0.4, anchor = "center",
                         relwidth = 0.3 , relheight = 0.1)
                
        ingresar_but = ctk.CTkButton(self, text= "ingresar" , command= lambda: self.log_in())
        ingresar_but.place(relx = 0.5 , rely = 0.55, anchor = "center",
                           relwidth = 0.3 , relheight = 0.1)
        
        alert_label = ctk.CTkLabel(self, textvariable = self.alert_var, text_color= "red")
        alert_label.place(relx = 0.5, rely = 0.65 , anchor = "center")

class Pestañas(ctk.CTkTabview, AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.add("Insertar")
        self.txtvar = ctk.StringVar()
        
        self.add("Buscar")
        self.add("Borrar")
        self.add("Actualizar")
        self.pestaña1()
    
    @async_handler   
    async def insertar(self, documento):
        self.progressb.place(relx = 0.5 , rely = 0.75 , relwidth = 0.5, anchor = "center")
        self.progressb.start()
        if await insert_app(documento):
            self.txtvar.set("DATO INGRESADO")
        else:
            self.txtvar.set("ERROR")
        self.progressb.stop()
        self.progressb.place_forget()
                
    def pestaña1 (self):
        # letras encabezado
        header = ctk.CTkLabel(self.tab("Insertar"),
                              text= "Debe colocar la clave entre comillas sino no se creará",
                              font= ctk.CTkFont("monospace", 14))
        header.place(relx = 0.5 , rely = 0.1 , anchor = "center")
        
        
        # caja de texto
        txt = ctk.CTkTextbox(self.tab("Insertar"))
        txt.place(anchor = "center" , relx = 0.5 , rely = 0.45,
                  relwidth = 0.5 , relheight = 0.5)
        
        
        # barra de progreso
        self.progressb = ctk.CTkProgressBar(self.tab("Insertar"),
                                       orientation= "horizontal",
                                       mode= "indeterminate",
                                       )
        
        
        # botones
        boton = ctk.CTkButton(self.tab("Insertar"), text= "Boton",
                              command= lambda: self.insertar(txt.get("0.0" , "end")) )
        boton.place(relx = 0.5 , rely= 0.83 , relwidth = 0.3,
                    anchor = "center")
        
        
        # labels
        label = ctk.CTkLabel(self.tab("Insertar"),
                             textvariable = self.txtvar)
        label.place(relx = 0.5 , rely = 0.9, anchor = "center")
        
App().async_mainloop()