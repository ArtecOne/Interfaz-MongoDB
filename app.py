import customtkinter as ctk
from mongo import insert_app, conectar, mostrar_databases , mostrar_colecciones , set_collection , set_db , get_db, search_app
from async_tkinter_loop import async_handler
from async_tkinter_loop.mixins import AsyncCTk
import os
import dotenv


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
        self.reciente()
    
    @async_handler
    async def log_in(self):
        dire = dotenv.find_dotenv()
        
        if dire:
            uri = dotenv.get_key(dire, "secret")
        else:
            uri = self.user_var.get()
        
        if await conectar(uri):
            self.destroy()
            Selector(self.master).pack(side = "left", fill = "y" , padx = 5)
            Pestañas(self.master).pack(side = "left" , expand = True , fill = "both", padx = 5)
            
            with open("./.env", "a+"):
                dotenv.set_key("./.env" ,  "secret" , uri)

        else:
            self.alert_var.set("revisa tu Connection string")
    
    def inicio(self):
        input_user = ctk.CTkEntry(self, textvariable= self.user_var)
        input_user.place(relx = 0.5 , rely = 0.4, anchor = "center",
                         relwidth = 0.3 , relheight = 0.1)
                
        ingresar_but = ctk.CTkButton(self, text= "ingresar" , command= lambda: self.log_in)
        ingresar_but.place(relx = 0.5 , rely = 0.55, anchor = "center",
                           relwidth = 0.3 , relheight = 0.1)
        
        alert_label = ctk.CTkLabel(self, textvariable = self.alert_var, text_color= "red")
        alert_label.place(relx = 0.5, rely = 0.65 , anchor = "center")
    
    
    def reciente(self):
        if dotenv.find_dotenv():
            boton_reciente = ctk.CTkButton(self , text= "Usar Sesion Reciente", fg_color = "green", command= self.log_in)
            boton_reciente.place(relx = 0.5, rely = 0.72 , anchor = "center")

class Pestañas(ctk.CTkTabview, AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.add("Insertar")
        self.txtvar = ctk.StringVar()
        
        self.add("Buscar")
        self.clave_var = ctk.StringVar()
        self.valor_var = ctk.StringVar()
        self.alerta_busc_var = ctk.StringVar()
        
        self.add("Borrar")
        self.add("Actualizar")
        self.pestaña1()
        self.pestaña2()
    
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
    
    @async_handler
    async def buscar(self):
        self.boton_buscar.configure(state = "disabled")
        data = await search_app(self.clave_var.get() , self.valor_var.get())
        match data:
            case False:
                self.boton_buscar.configure(state = "normal")
                self.alerta_busc_var.set("Seleccione una Database y una Coleccion")
            case []:
                self.boton_buscar.configure(state = "normal")
                self.alerta_busc_var.set("Sin Datos")
            case _:
                self.ventanita = VentanaBusqueda(self.tab("Buscar"), data)
                self.ventanita.bind("<Destroy>" , func= lambda ev: self.boton_buscar.configure(state = "normal"))
            
        
                
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
    
    def pestaña2 (self):
        consejo = ctk.CTkLabel(self.tab("Buscar"), text= "vacie las cajas para buscar toda la coleccion", font= ctk.CTkFont("monospace" , 18))
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # buscar
        clave_txt = ctk.CTkLabel(self.tab("Buscar"), text= "clave", font= ctk.CTkFont("monospace" , 14))
        clave_txt.place(relx = 0.4 , rely = 0.32 , anchor = "center")
        
        entry_key = ctk.CTkEntry(self.tab("Buscar"), textvariable= self.clave_var)
        entry_key.place(relx = 0.48 , rely = 0.4 , anchor = "e", relheight = 0.12, relwidth = 0.15)
        
        valor_txt = ctk.CTkLabel(self.tab("Buscar"), text= "valor", font= ctk.CTkFont("monospace" , 14))
        valor_txt.place(relx = 0.595 , rely = 0.32 , anchor = "center")
        
        entry_val = ctk.CTkEntry(self.tab("Buscar"), textvariable= self.valor_var)
        entry_val.place(relx = 0.52 , rely = 0.4 , anchor = "w", relheight = 0.12 , relwidth = 0.15)
        
        # boton
        self.boton_buscar = ctk.CTkButton(self.tab("Buscar"), text= "Buscar" , command= self.buscar)
        self.boton_buscar.place(relx = 0.5 , rely = 0.52, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(self.tab("Buscar") , font= ctk.CTkFont("monospace" , 14) , textvariable = self.alerta_busc_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.6)


class VentanaBusqueda(ctk.CTkToplevel , AsyncCTk):
    def __init__(self , root, data):
        super().__init__(master = root)
        self.geometry("600x600")
        self.visualizar(data)
        
    def view(self , doc : tuple , root):
        frame = ctk.CTkFrame(root)
        
        sw = True
        
        for val in doc:
            ctk.CTkLabel(frame, text= val, font= ctk.CTkFont("monospace" , 14), text_color= "green" if sw == True else "white").pack(side = "left" , padx = 10)
            sw = not sw

        return frame
        
    def visualizar(self , datos : list = None):
        
        print(datos)
        main_frame = ctk.CTkScrollableFrame(self)
        
        for tup in datos:
            self.view(tup, main_frame).pack()
            
        main_frame.pack(padx = 5 , pady = 5 , expand = True , fill = "both")


App().async_mainloop()