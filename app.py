import customtkinter as ctk
from mongo import insert_app, conectar, mostrar_databases , mostrar_colecciones , set_collection , set_db , get_db
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

class Selector(ctk.CTkFrame , AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root , width= 0)
        self.buscar_databases()
        self.db_var = ctk.StringVar(value= "Databases")
        self.db_var.trace_add("write" , callback= self.definir_base)
        self.col_var = ctk.StringVar(value= "Coleccion")
        
    def definir_base(self, nose1 , nose2, nose3):
        """
        con sinceridad esos parametros no se que son
        """      
        set_db(self.db_var.get())
        
        self.buscar_colecciones(get_db())
        
        print("se ha definido una base")
        
    @async_handler
    async def buscar_colecciones(self, db):
        self.coleccion_selector.configure(values = await mostrar_colecciones(db), command = lambda x: set_collection(x))
        print("esto deberia correr")
        
        
    @async_handler
    async def buscar_databases(self):
        ctk.CTkOptionMenu(self , values= await mostrar_databases(), variable= self.db_var).pack( ipadx = 10, padx = 5 , pady = 5, anchor = "center")
        self.coleccion_selector = ctk.CTkOptionMenu(self , values= [], variable= self.col_var)
        self.coleccion_selector.pack( ipadx = 10, padx = 5 , pady = 5, anchor = "center")
        
        
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
            #Pestañas(self.master).place(anchor = "nw", relx = 0.15, rely = 0, relwidth = 0.85 , relheight = 1)
            #Selector(self.master).place(x = 0  , y = 0 , anchor = "nw" , relheight = 1)
            
            Selector(self.master).pack(side = "left", fill = "y" , padx = 10)
            Pestañas(self.master).pack(side = "left" , expand = True , fill = "both")
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
        self.boton.configure(state="disabled")
        
        self.progressb.place(relx = 0.5 , rely = 0.75 , relwidth = 0.5, anchor = "center")
        self.progressb.start()
        if await insert_app(documento):
            self.txtvar.set("DATO INGRESADO")
        else:
            self.txtvar.set("ERROR")
        self.progressb.stop()
        self.progressb.place_forget()
        self.boton.configure(state="normal")
                
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
        self.boton = ctk.CTkButton(self.tab("Insertar"), text= "Boton",
                              command= lambda: self.insertar(txt.get("0.0" , "end")) )
        self.boton.place(relx = 0.5 , rely= 0.83 , relwidth = 0.3,
                    anchor = "center")
        
        
        # labels
        label = ctk.CTkLabel(self.tab("Insertar"),
                             textvariable = self.txtvar)
        label.place(relx = 0.5 , rely = 0.9, anchor = "center")


App().async_mainloop()