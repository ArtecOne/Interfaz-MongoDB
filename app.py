import asyncio
import customtkinter as ctk

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
        self.add("Buscar")
        self.add("Borrar")
        self.add("Actualizar")
        self.pestaña1()
    
    def pestaña1 (self):
        txt = ctk.CTkTextbox(self.tab("Insertar"))
        txt.place(anchor = "center" , relx = 0.5 , rely = 0.35,
                  relwidth = 0.5 , relheight = 0.5)

App()