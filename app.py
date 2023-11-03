import asyncio
import customtkinter as ctk
from jsontest import crear_jjson

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Cluster Admin")
        self.geometry("900x600")
        self.minsize(600,600)
        
        self.tabs = Pestañas(self)
        self.tabs.place(anchor = "n", relx = 0.5, rely = 0,
                        relwidth = 1 , relheight = 1)
        
        self.mainloop()

class Pestañas(ctk.CTkTabview):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.add("Insertar")
        self.txtvar = ctk.StringVar()
        
        self.add("Buscar")
        self.add("Borrar")
        self.add("Actualizar")
        self.pestaña1()
        
    def insertar(self, documento):
        if crear_jjson(documento):
            self.txtvar.set("DATO INGRESADO")
        else:
            self.txtvar.set("ERROR")
            
        #self.after(5 , self.stop_pb()) fix
    
    def pestaña1 (self):
        header = ctk.CTkLabel(self.tab("Insertar"),
                              text= "Debe colocar la clave entre comillas sino no se creará",
                              font= ctk.CTkFont("monospace", 14))
        header.place(relx = 0.5 , rely = 0.1 , anchor = "center")
        
        txt = ctk.CTkTextbox(self.tab("Insertar"))
        txt.place(anchor = "center" , relx = 0.5 , rely = 0.45,
                  relwidth = 0.5 , relheight = 0.5)
        
        progressb = ctk.CTkProgressBar(self.tab("Insertar"),
                                       orientation= "horizontal",
                                       mode= "indeterminate",
                                       )
        progressb.place(relx = 0.5 , rely = 0.75 , relwidth = 0.5,
                        anchor = "center")
        self.start_pb = lambda : progressb.start()
        self.stop_pb = lambda : progressb.stop() or progressb.set(0)
        
        boton = ctk.CTkButton(self.tab("Insertar"), text= "Boton",
                              command= lambda: self.insertar(txt.get("0.0", "end")) or self.start_pb())
        boton.place(relx = 0.5 , rely= 0.83 , relwidth = 0.3,
                    anchor = "center")
        
        label = ctk.CTkLabel(self.tab("Insertar"),
                             textvariable = self.txtvar)
        label.place(relx = 0.5 , rely = 0.9, anchor = "center")
        
App()