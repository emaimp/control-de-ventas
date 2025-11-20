import streamlit as st
import connection.db as _db

# Inicia el estado de sesión del usuario
if "user" not in st.session_state:
    st.session_state.user = None

AUTH_CREDENTIALS = st.secrets["pass"]

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
# Pagina de login
#
def login():
    # Menu
    login_1, login_2, login_3 = st.columns(3)
    with login_2:
        st.write("")
        st.write("") # Espacio
        st.write("")
        
        # Formulario para manejar el botón enviar
        with st.form(key="login_form"):
            
            # Logo de la empresa
            logo_1, logo_2, logo_3 = st.columns([27, 60, 13])
            with logo_2:
                st.write("") # Espacio
                st.image("app/assets/banner.png", width=250)
                st.write("") # Espacio
                st.write("") # Espacio
            
            # Entrada para el nombre de usuario
            username = st.text_input("Ingresa tu usuario", max_chars=20)
            st.write("") # Espacio
            # Entrada para la contraseña
            password = st.text_input(
                "Ingresa la contraseña", type="password", max_chars=10
            )
            st.write("") # Espacio
            
            # Botón de ingreso
            submit_button = st.form_submit_button("Entrar", type="primary", width="stretch")
            
            # Verificar si el usuario y la contraseña no están vacíos
            if username != "" and password != "":
                # Verificamos si el botón fue presionado o el formulario se envió
                if submit_button:
                    # Verificar la contraseña
                    if password == AUTH_CREDENTIALS.get(username, None):
                        st.session_state.user = username # Asigna el nombre de usuario a la sesión
                        st.success(f"Acceso concedido a {username}.")
                        st.rerun() # Reinicia la aplicación para reflejar el acceso
                    else:
                        st.error("Usuario o contraseña incorrectos.")
            elif submit_button:
                st.error("Por favor, ingresa tu usuario y contraseña.")
        
        # Badge de GitHub
        badge_1, badge_2, badge_3 = st.columns([40, 30, 30])
        with badge_2:
            """
            [![GitHub](
                https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github
                )](https://github.com/emaimp)
            """

# Pagina de logout
def logout():
    st.session_state.user = None
    st.rerun()
user = st.session_state.user # Variable para el usuario logueado

#
# Paginas
#
pages = {
    "Home": [
        st.Page(logout, title="Salir", icon=":material/logout:"),
        st.Page("views/💻_Pagina_Inicio.py", title="Inicio", default=True),
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

# Condicionales para la navegación
if st.session_state.user is not None:
    pg = st.navigation(pages)
else:
    pg = st.navigation([st.Page(login)])

# Inicializar base de datos después del login
if st.session_state.user is not None:
    try:
        _db.get_connection()
    except Exception as e:
        st.error(f"Error inicializando base de datos: {e}")
        st.stop()

pg.run() # Inicia la aplicación
