import streamlit as st
import connection.db as _db

# Iniciar los roles
if "role" not in st.session_state:
    st.session_state.role = None

ROLES = ["Admin"]
ROLE_PASSWORDS = st.secrets["pass"]

#
# Hacer que el set_page_config no se ejecute
#
if "page_config" not in st.session_state:
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state.page_config = True

#
# Pagina login de roles
#
def login():

    # Cargar styles.css
    with open("app/config/styles.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Menu
    col_menu1, col_menu2, col_menu3 = st.columns(3)
    with col_menu2:
        
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("") # Espacio
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        
        # Título de la empresa
        col_title1, col_title2, col_title3 = st.columns([11, 82, 7])
        with col_title2:
            st.markdown('<h4 style="text-align:center; font-size: 2em;">Electrodomésticos S.A</h4>', unsafe_allow_html=True)
            st.write("") # Espacio
        
        # Formulario para manejar el botón enviar
        with st.form(key="login_form"):
            # Selección del rol
            role = st.selectbox("Elige un usuario", ROLES)
            st.write("") # Espacio
            # Entrada para la contraseña
            password = st.text_input(
                "Ingresa la contraseña", type="password", max_chars=10
            )
            st.write("") # Espacio
            
            # Botón de ingreso
            submit_button = st.form_submit_button("Entrar")
            
            # Verificar si la contraseña no esta vacía
            if password != "":
                # Verificamos si el botón fue presionado o el formulario se envió
                if submit_button:
                    # Verificar la contraseña
                    if password == ROLE_PASSWORDS.get(role, None):
                        st.session_state.role = role
                        st.success(f"Acceso concedido como {role}")
                        st.rerun() # Reinicia la aplicación para reflejar el acceso
                    else:
                        st.error("Contraseña incorrecta.")
        """
        [![GitHub](
            https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github
            )](https://github.com/emaimp)
        """

# Pagina de logout
def logout():
    st.session_state.role = None
    st.rerun()
role = st.session_state.role

#
# Paginas
#
pages = {
    "Home": [
        st.Page("views/💻_Pagina_Inicio.py", title="Inicio", default=(role == "Admin")),
        st.Page(logout, title="Cerrar Sesión", icon=":material/logout:"),
    ],
    "Productos": [
        st.Page("views/💾_Uploader_File.py", title="Carga de Datos"),
        st.Page("views/🏷️_Consulta_Stock.py", title="Consulta de Stock"),
    ],
    "Ventas": [
        st.Page("views/📊_Control_Ventas.py", title="Control de Ventas"),
        st.Page("views/📈_Prediccion_Ventas.py", title="Predicción de Ventas"),
    ],

}

# Configura la navegación dinámicamente según el rol del usuario
page_dict = {}
# Condicionales para la navegación
if st.session_state.role == "Admin":
    page_dict["Admin"] = pages
if len(page_dict) > 0:
    pg = st.navigation(pages, position="top")
else:
    pg = st.navigation([st.Page(login)])

# Inicializar base de datos después del login
if st.session_state.role is not None:
    try:
        _db.get_connection()
    except Exception as e:
        st.error(f"Error inicializando base de datos: {e}")
        st.stop()

pg.run()
