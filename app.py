import customtkinter as ctk
from mongo import insert_app, conectar, mostrar_databases , mostrar_colecciones , set_collection , set_db , get_db, search_app, delete_app, update_app
from async_tkinter_loop import async_handler
from async_tkinter_loop.mixins import AsyncCTk
import os
import sys
import dotenv

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        
        
        self.title("Cluster Admin")
        self.iconbitmap(resource_path("6959203.ico"))
        self.geometry("900x600")
        self.minsize(600,600)
        
        self.login = Login(self)
        self.login.place(anchor = "n", relx = 0.5 , rely = 0,
                         relwidth = 1 , relheight = 1)

class Selector(ctk.CTkFrame , AsyncCTk):
    def __init__(self, root , online = True):
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
        ctk.CTkOptionMenu(self , values= await mostrar_databases(), variable= self.db_var , font= ctk.CTkFont("motiva sans", 12)).pack( ipadx = 10, padx = 5 , pady = 5, anchor = "center")
        self.coleccion_selector = ctk.CTkOptionMenu(self , values= [], variable= self.col_var)
        self.coleccion_selector.pack( ipadx = 10, padx = 5 , pady = 5, anchor = "center")
        
class Login(ctk.CTkFrame , AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.user_var = ctk.StringVar()
        self.alert_var = ctk.StringVar()
        self.inicio()
        self.reciente()
    
    @async_handler
    async def log_in(self, uri = None):
        
        if not uri:
            dire = dotenv.find_dotenv()
            uri = dotenv.get_key(dire, "secret")
        
        if await conectar(uri):
            self.destroy()
            Selector(self.master).pack(side = "left", fill = "y" , padx = 5)
            Pestañas(self.master).pack(side = "left" , expand = True , fill = "both", padx = 5)
            
            with open("./.env", "a+"):
                dotenv.set_key("./.env" ,  "secret" , uri)

        else:
            self.alert_var.set("revisa tu Connection string \n y que tengas los permisos necesarios")
    
    def inicio(self):
        label = ctk.CTkLabel(self, text= "Ingrese URI" , font= ctk.CTkFont("motiva sans", 14))
        label.place(relx = 0.5, rely = 0.3 , anchor = "center")
        
        input_user = ctk.CTkEntry(self, textvariable= self.user_var)
        input_user.place(relx = 0.5 , rely = 0.4, anchor = "center",
                         relwidth = 0.3 , relheight = 0.1)
                
        ingresar_but = ctk.CTkButton(self, text= "ingresar" , font= ctk.CTkFont("motiva sans", 14), command= lambda : self.log_in(self.user_var.get()))
        ingresar_but.place(relx = 0.5 , rely = 0.55, anchor = "center",
                           relwidth = 0.3 , relheight = 0.1)
        
        alert_label = ctk.CTkLabel(self, textvariable = self.alert_var, text_color= "red" , font= ctk.CTkFont("motiva sans", 12))
        alert_label.place(relx = 0.5, rely = 0.65 , anchor = "center")
    
    
    def reciente(self):
        dire = dotenv.find_dotenv()
        if dire:
            if dotenv.get_key(dire , "secret") != "null":
                boton_reciente = ctk.CTkButton(self , text= "Usar Sesion Reciente", fg_color = "green", command= self.log_in)
                boton_reciente.place(relx = 0.5, rely = 0.72 , anchor = "center")

class Pestañas(ctk.CTkTabview, AsyncCTk):
    def __init__(self, root):
        super().__init__(master= root)
        
        self.add("Insertar")
        self.txtvar = ctk.StringVar()
        
        self.add("Buscar")
        self.add("Borrar")
        self.add("Actualizar")
        self.clave_var = ctk.StringVar()
        self.alerta_busc_var = ctk.StringVar()

        self.pestaña1()
        self.pestaña2()
        self.pestaña3()
        self.pestaña4()

    @async_handler   
    async def insertar(self, documento , funcion):
        funcion(True) 
        self.txtvar.set("DATO INGRESADO") , funcion() if await insert_app(documento) else self.txtvar.set("ERROR") , funcion()
    
    @async_handler
    async def buscar(self, funcion):
        funcion(True)
        data = await search_app(self.clave_var.get())
        match data:
            case False:
                funcion(False , "Selecciona una Database y una Colection")
            case []:
                funcion(False , "Sin Datos")
            case "t":
                funcion(False , "Escriba algo")
            case _:
                self.ventanita = VentanaBusquedaSup(self.tab("Buscar"), data)
                self.ventanita.bind("<Destroy>" , func= lambda ev: funcion(False))
    
    @async_handler
    async def borrar(self , funcion):
        funcion(True)
        
        
        data = await search_app(self.clave_var.get())
        if data == False or data == []:
            funcion(False , "Sin Datos que borrar")
            return None
        
        ven = VentanaBorrarSup(self.tab("Borrar"))
        if not ven.Esperar():
            funcion(False)
            ven.destroy()
            return None
        
        ven.destroy()    
        
        data = await delete_app(self.clave_var.get())
        if data:
            funcion(False , f"datos eliminados : {data}")
        else:
            funcion(False , "error")
    
    @async_handler
    async def actualizar(self , funcion, new_doc , switch):
        funcion(True)
        
        data = await update_app(self.clave_var.get() , new_doc , switch)
        if data:
            funcion(False, "Se ha editado la Coleccion")
        else:
            funcion(False, "Error, revise su query y documento")
        
          
    ####pestaña 1  
                
    def pestaña1 (self):
        PestañaInsertar().crearse(self.tab("Insertar"), self.txtvar, self.insertar)
    
    ####pestaña2

    def pestaña2 (self):
        PestañaBuscar().crearse(self.tab("Buscar") , self.clave_var  , self.alerta_busc_var , self.buscar)
    
    ####pestaña3
    
    def pestaña3(self):
        PestañaBorrar().crearse(self.tab("Borrar"), self.clave_var , self.alerta_busc_var , self.borrar)
        
    ####pestaña4
    
    def pestaña4(self):
        PestañaActualizar().crearse(self.tab("Actualizar") ,self.clave_var , self.alerta_busc_var , self.actualizar)
        
class PestañaInsertar():
    def switch_boton_y_barra(self, booleano = False):
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
                              font= ctk.CTkFont("motiva sans", 18, "bold"))
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
        self.boton = ctk.CTkButton(root, text= "Insertar",
                              command= lambda: insertar(txt.get("0.0" , "end") , self.switch_boton_y_barra))
        self.boton.place(relx = 0.5 , rely= 0.83 , relwidth = 0.3,
                    anchor = "center")
        
        # Alerta
        label = ctk.CTkLabel(root, textvariable = txtvar , font= ctk.CTkFont("motiva sans", 12))
        label.place(relx = 0.5 , rely = 0.9, anchor = "center")

class PestañaBuscar():
    def switch_boton_alerta(self , booleano , argumento = ""):
        if booleano:
            self.boton_buscar.configure(state = "disabled")
        else:
            self.boton_buscar.configure(state = "normal")
            self.alerta_var.set(argumento)
            
    
    def crearse(self , root , clave_var , alerta_var, buscar):
        self.alerta_var = alerta_var
        
        # header
        consejo = ctk.CTkLabel(root, text= "{} para buscar toda la coleccion \n {'key' , value} buscar donde el valor sea igual", font= ctk.CTkFont("monospace" , 18, "bold"))
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # buscar
        
        entry_key = ctk.CTkEntry(root, textvariable= clave_var)
        entry_key.place(relx = 0.5 , rely = 0.4 , anchor = "center", relheight = 0.12, relwidth = 0.4)
        
        # boton
        self.boton_buscar = ctk.CTkButton(root, text= "Buscar" , command= lambda: buscar(self.switch_boton_alerta))
        self.boton_buscar.place(relx = 0.5 , rely = 0.52, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(root , font= ctk.CTkFont("motiva sans" , 12) , textvariable = alerta_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.6)

class PestañaBorrar():
    def switch_boton_alerta(self , booleano , argumento = ""):
        if booleano:
            self.boton_borrar.configure(state = "disabled")
        else:
            self.boton_borrar.configure(state = "normal")
            self.alerta_var.set(argumento)
    
    def crearse(self , root, clave_var, alerta_var , borrar):
        self.alerta_var = alerta_var
        
        consejo = ctk.CTkLabel(root, text= "{} borrar toda la coleccion \n {'key' : value} para borrar donde el valor sea igual", font= ctk.CTkFont("monospace" , 18, "bold"))
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # buscar y borrar
        
        entry_key = ctk.CTkEntry(root, textvariable= clave_var)
        entry_key.place(relx = 0.5 , rely = 0.4 , anchor = "center", relheight = 0.12, relwidth = 0.4)
        
        # boton
        self.boton_borrar = ctk.CTkButton(root, text= "Borrar" , command= lambda: borrar(self.switch_boton_alerta))
        self.boton_borrar.place(relx = 0.5 , rely = 0.52, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(root , font= ctk.CTkFont("motiva sans" , 12) , textvariable = alerta_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.6)
        
class PestañaActualizar():
    def switch_boton_alerta(self, booleano, argumento = ""):
        if booleano:
            self.boton_actualizar.configure(state = "disabled")
        else:
            self.boton_actualizar.configure(state = "normal")
            self.alerta_var.set(argumento)
    
    
    
    def crearse(self, root , clave_var , alerta_var , actualizar):
        switch_var = ctk.StringVar(value= "u")
        self.alerta_var = alerta_var
        new_doc = ctk.StringVar()
        
        # header
        consejo = ctk.CTkLabel(root, text= "haga una query {'key' , value} \n reemplace el archivo encontrado por otro documento {'key' , value} \n o actualicelo", font= ctk.CTkFont("monospace" , 18, "bold"),
                               height= 35 , width= 10, corner_radius= 10)
        consejo.place(relx = 0.5 , rely = 0.2, anchor = "center")
        
        # switch
        
        switch = ctk.CTkSwitch(root , text= "Update / Replace" , progress_color= "green", variable= switch_var, onvalue= "r" , offvalue= "u")
        switch.place(rely = 0.4 , relx = 0.24 , anchor = "e")
        
        # entries
        
        entry_search = ctk.CTkEntry(root, textvariable= clave_var)
        entry_search.place(relx = 0.5 , rely = 0.4 , anchor = "center", relheight = 0.1, relwidth = 0.5)
        
        entry_doc = ctk.CTkEntry(root, textvariable= new_doc)
        entry_doc.place(relx = 0.5 , rely = 0.55 , anchor = "center", relheight = 0.1, relwidth = 0.5)
        
        # boton
        self.boton_actualizar = ctk.CTkButton(root, text= "Buscar" , command= lambda: actualizar(self.switch_boton_alerta , new_doc.get(), switch_var.get()))
        self.boton_actualizar.place(relx = 0.5 , rely = 0.7, anchor = "center")
        
        # alerta
        self.alerta_busc = ctk.CTkLabel(root , font= ctk.CTkFont("motiva sans" , 12) , textvariable = alerta_var , text_color= "red")
        self.alerta_busc.place(anchor = "center" , relx = 0.5 , rely = 0.65)    

class VentanaBusquedaSup(ctk.CTkToplevel , AsyncCTk):
    def __init__(self , root, data):
        super().__init__(master = root)
        self.title = "Query Result"
        self.geometry("600x600")
        self.visualizar(data)
        self.focus()
        
    def view(self , doc : dict , root):
        frame = ctk.CTkFrame(root)
        
        for key , value in doc.items():
            ctk.CTkLabel(frame, text= key, font= ctk.CTkFont("motiva sans" , 14), text_color= "green").pack(side = "left" , padx = 10)
            ctk.CTkLabel(frame, text= value, font= ctk.CTkFont("motiva sans" , 14), text_color= "white").pack(side = "left" , padx = 10)

        return frame
        
    def visualizar(self , datos : list = None):
        
        print(datos)
        main_frame = ctk.CTkScrollableFrame(self)
        
        for dicc in datos:
            self.view(dicc, main_frame).pack(anchor = "w")
            
        main_frame.pack(padx = 5 , pady = 5 , expand = True , fill = "both")

class VentanaBorrarSup(ctk.CTkToplevel , AsyncCTk):
    def __init__(self , root):
        super().__init__(master = root)
        self.title = "Confirmar"
        self.resizable(False, False)
        self.focus()
        self.confirmar = ctk.BooleanVar()
    
    def Esperar(self):
        
        texto = ctk.CTkLabel(self , text= "Quiere Eliminar los datos??", font= ctk.CTkFont("motiva sans" , 16, "bold"))
        texto.pack(expand = True , fill = "both" , padx = 3 , pady = 2)
        
        boton_si = ctk.CTkButton(self ,  height = 50 , width= 200 , text= "SI" , fg_color= "green" , hover_color= "#006400", font= ctk.CTkFont("motiva sans" , 12, "bold") , command= lambda: self.confirmar.set(True))
        boton_si.pack(expand = True, pady = 2, anchor = "center")
        
        boton_no = ctk.CTkButton(self , height= 50 , width= 200 , text= "NO" , fg_color= "red" , hover_color= "#8B0000", font= ctk.CTkFont("motiva sans" , 12, "bold") , command= lambda: self.confirmar.set(False))
        boton_no.pack(expand = True, pady = 2, anchor = "center")
        
        self.wait_variable(self.confirmar)
        
        return self.confirmar.get()
        


App().async_mainloop()