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
        # Logo
        col_left, col_center, col_right = st.columns([18, 33, 49])
        with col_center:
            st.image("app/assets/banner.png", width=373)
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
logout_page = st.Page(
    logout,
    title="Salir",
    icon=":material/logout:",
)
productos_1 = st.Page(
    page="views/💾_Uploader_File.py",
    title="Carga de Datos",
)

productos_2 = st.Page(
    page="views/🏷️_Consulta_Stock.py",
    title="Consulta de Stock",
)

ventas_1 = st.Page(
    page="views/📊_Control_Ventas.py",
    title="Control de Ventas",
)
ventas_2 = st.Page(
    page="views/📈_Prediccion_Ventas.py",
    title="Predicción de Ventas",
)

admin = st.Page(
    page="views/💻_Pagina_Inicio.py",
    title="Home",
    default=(role == "Admin"),
)

# Agrupan las páginas en secciones para facilitar la navegación
account_pages = [logout_page]
admin_pages = [admin]
productos_pages = [productos_1, productos_2]
ventas_pages = [ventas_1, ventas_2]

# Configura la navegación dinámicamente según el rol del usuario
page_dict = {}
# Condicionales para la navegación
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages + productos_pages + ventas_pages
if len(page_dict) > 0:
    pg = st.navigation({"Cuenta": account_pages} | page_dict)
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
