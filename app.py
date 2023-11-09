import customtkinter as ctk
from mongo import insert_app, conectar, mostrar_databases , mostrar_colecciones , set_collection , set_db , get_db, search_app, delete_app
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
    def __init__(self, root , online = True):
        super().__init__(master= root , width= 0)
        
        if not online:
            self.buscar_databases_offline()
        else:
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
    
    def buscar_databases_offline(self):
        ctk.CTkOptionMenu(self , values= ["data1" , "data2" , "data3"]).pack( ipadx = 10, padx = 5 , pady = 5, anchor = "center")
        self.coleccion_selector = ctk.CTkOptionMenu(self , values= ["col1" , "col2" , "col3"])
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
    
    @async_handler
    async def debug_log_in(self):
        self.destroy()
        Selector(self.master , False).pack(side = "left", fill = "y" , padx = 5)
        Pestañas(self.master).pack(side = "left" , expand = True , fill = "both", padx = 5)
    
    def inicio(self):
        input_user = ctk.CTkEntry(self, textvariable= self.user_var)
        input_user.place(relx = 0.5 , rely = 0.4, anchor = "center",
                         relwidth = 0.3 , relheight = 0.1)
                
        ingresar_but = ctk.CTkButton(self, text= "ingresar" , command= lambda: self.log_in)
        ingresar_but.place(relx = 0.5 , rely = 0.55, anchor = "center",
                           relwidth = 0.3 , relheight = 0.1)
        
        alert_label = ctk.CTkLabel(self, textvariable = self.alert_var, text_color= "red")
        alert_label.place(relx = 0.5, rely = 0.65 , anchor = "center")
        
        debug_ingresar = ctk.CTkButton(self , text= "debug" , command= self.debug_log_in)
        debug_ingresar.place(x = 0 , y = 0 , anchor = "nw")
    
    
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
        self.pestaña3()

    @async_handler   
    async def insertar(self, documento , funcion):
        funcion(True) 
        match documento:
            case None:
                self.txtvar.set("ERROR")
                funcion(False)
            case _:
                self.txtvar.set("DATO INGRESADO") and funcion(False) if await insert_app(documento) else self.txtvar.set("ERROR") and funcion(False)
    
    @async_handler
    async def buscar(self, funcion):
        funcion(True)
        data = await search_app(self.clave_var.get() , self.valor_var.get())
        match data:
            case False:
                funcion(False , "Selecciona una Database y una Colection")
            case []:
                funcion(False , "Sin Datos")
            case _:
                self.ventanita = VentanaBusquedaSup(self.tab("Buscar"), data)
                self.ventanita.bind("<Destroy>" , func= lambda ev: funcion(False , ""))
    
    @async_handler
    async def borrar(self , funcion):
        funcion(True)
        data = await delete_app(self.clave_var.get() , self.valor_var.get())
        match data:
            case True:
                print("bien")
                funcion(False , "datos eliminados")
            case False:
                print("bien 2")
                funcion(False , "error")
    
    @async_handler
    async def actualizar(self , funcion):
        pass
        
          
    ####pestaña 1  
                
    def pestaña1 (self):
        PestañaInsertar().crearse(self.tab("Insertar"), self.txtvar, self.insertar)
    
    ####pestaña2

    def pestaña2 (self):
        PestañaBuscar().crearse(self.tab("Buscar") , self.clave_var , self.valor_var , self.alerta_busc_var , self.buscar)
    
    ####pestaña3
    
    def pestaña3(self):
        PestañaBorrar().crearse(self.tab("Borrar"), self.clave_var , self.valor_var , self.alerta_busc_var , self.borrar)
        
class PestañaInsertar():
    def switch_boton_y_barra(self, booleano):
        if booleano:
            self.boton.configure(state="disabled")
            self.progressb.place(relx = 0.5 , rely = 0.75 , relwidth = 0.5, anchor = "center")
            self.progressb.start()
        else:
            self.progressb.stop()
            self.progressb.place_forget()
            self.boton.configure(state="normal")
    
    def crearse(self, root, txtvar, insertar):
        # letras encabezado
        header = ctk.CTkLabel(root,
                              text= "Debe colocar la clave entre comillas sino no se creará",
                              font= ctk.CTkFont("monospace", 14))
        header.place(relx = 0.5 , rely = 0.1 , anchor = "center")
        
        # caja de texto
        txt = ctk.CTkTextbox(root)
        txt.place(anchor = "center" , relx = 0.5 , rely = 0.45,
                  relwidth = 0.5 , relheight = 0.5)
        
        
        # barra de progreso
        self.progressb = ctk.CTkProgressBar(root,
                                       orientation= "horizontal",
                                       mode= "indeterminate",
                                       )
        
        # botones
        self.boton = ctk.CTkButton(root, text= "Boton",
                              command= lambda: insertar(txt.get("0.0" , "end") if txt.get("0.0" , "end").isprintable() else None, self.switch_boton_y_barra))
        self.boton.place(relx = 0.5 , rely= 0.83 , relwidth = 0.3,
                    anchor = "center")
        
        # labels
        label = ctk.CTkLabel(root,
                             textvariable = txtvar)
        label.place(relx = 0.5 , rely = 0.9, anchor = "center")

class PestañaBuscar():
    def switch_boton_alerta(self , booleano , argumento = ""):
        if booleano:
            self.boton_buscar.configure(state = "disabled")
        else:
            self.boton_buscar.configure(state = "normal")
            self.alerta_var.set(argumento)
            
    
    def crearse(self , root , clave_var , valor_var, alerta_var, buscar):
        self.alerta_var = alerta_var
        
        consejo = ctk.CTkLabel(root, text= "vacie las cajas para buscar toda la coleccion", font= ctk.CTkFont("monospace" , 18))
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # buscar
        clave_txt = ctk.CTkLabel(root, text= "clave", font= ctk.CTkFont("monospace" , 14))
        clave_txt.place(relx = 0.4 , rely = 0.32 , anchor = "center")
        
        entry_key = ctk.CTkEntry(root, textvariable= clave_var)
        entry_key.place(relx = 0.48 , rely = 0.4 , anchor = "e", relheight = 0.12, relwidth = 0.15)
        
        valor_txt = ctk.CTkLabel(root, text= "valor", font= ctk.CTkFont("monospace" , 14))
        valor_txt.place(relx = 0.595 , rely = 0.32 , anchor = "center")
        
        entry_val = ctk.CTkEntry(root, textvariable= valor_var)
        entry_val.place(relx = 0.52 , rely = 0.4 , anchor = "w", relheight = 0.12 , relwidth = 0.15)
        
        # boton
        self.boton_buscar = ctk.CTkButton(root, text= "Buscar" , command= lambda: buscar(self.switch_boton_alerta))
        self.boton_buscar.place(relx = 0.5 , rely = 0.52, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(root , font= ctk.CTkFont("monospace" , 14) , textvariable = alerta_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.6)

class PestañaBorrar():
    def switch_boton_alerta(self , booleano , argumento = ""):
        if booleano:
            self.boton_borrar.configure(state = "disabled")
        else:
            self.boton_borrar.configure(state = "normal")
            self.alerta_var.set(argumento)
    
    def crearse(self , root, clave_var, valor_var , alerta_var , borrar):
        self.alerta_var = alerta_var
        
        consejo = ctk.CTkLabel(root, text= "vacie las cajas para borrar toda la coleccion", font= ctk.CTkFont("monospace" , 18))
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # buscar y borrar
        clave_txt = ctk.CTkLabel(root, text= "clave", font= ctk.CTkFont("monospace" , 14))
        clave_txt.place(relx = 0.4 , rely = 0.32 , anchor = "center")
        
        entry_key = ctk.CTkEntry(root, textvariable= clave_var)
        entry_key.place(relx = 0.48 , rely = 0.4 , anchor = "e", relheight = 0.12, relwidth = 0.15)
        
        valor_txt = ctk.CTkLabel(root, text= "valor", font= ctk.CTkFont("monospace" , 14))
        valor_txt.place(relx = 0.595 , rely = 0.32 , anchor = "center")
        
        entry_val = ctk.CTkEntry(root, textvariable= valor_var)
        entry_val.place(relx = 0.52 , rely = 0.4 , anchor = "w", relheight = 0.12 , relwidth = 0.15)
        
        # boton
        self.boton_borrar = ctk.CTkButton(root, text= "Buscar" , command= lambda: borrar(self.switch_boton_alerta))
        self.boton_borrar.place(relx = 0.5 , rely = 0.52, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(root , font= ctk.CTkFont("monospace" , 14) , textvariable = alerta_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.6)
        
class PestañaActualizar():
    def crearse(root , clave_var , valor_var , alerta_var , actualizar):
        pass

class VentanaBusquedaSup(ctk.CTkToplevel , AsyncCTk):
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