import streamlit as st

# -----------------------------------------------------------------------------------
# Iniciar los roles
if "role" not in st.session_state:
    st.session_state.role = None
ROLES = ["Inicio", "Producto", "Ventas"]
# Contraseñas
ROLE_PASSWORDS = st.secrets["pass"]
# -----------------------------------------------------------------------------------
# Hacer que el set_page_config no se ejecute
if "page_config" not in st.session_state:
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state.page_config = True


# -----------------------------------------------------------------------------------
# Pagina login de roles
def login():
    # -------------------------------------------------------------------------------
    # Cargar styles.css
    with open("config/styles.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    # -------------------------------------------------------------------------------
    # Menu
    colmenu1, colmenu2, colmenu3 = st.columns(3)
    with colmenu2:
        st.image("assets/banner.png", width=745)
        # Formulario para manejar el botón enviar
        with st.form(key="login_form"):
            # Selección del rol
            role = st.selectbox("Elige un usuario", ROLES)
            st.write("")  # Espacio
            # Entrada para la contraseña
            password = st.text_input(
                "Ingresa la contraseña", type="password", max_chars=10
            )
            st.write("")  # Espacio
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
                        st.rerun()  # Reinicia la aplicación para reflejar el acceso
                    else:
                        st.error("Contraseña incorrecta.")
        """
        [![GitHub](
            https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github
            )](https://github.com/emaimp)
        """


# -----------------------------------------------------------------------------------
# Pagina de logout
def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role
# -----------------------------------------------------------------------------------
# Paginas
logout_page = st.Page(
    logout,
    title="Salir",
    icon=":material/logout:",
)
productos_1 = st.Page(
    page="pages/🏷️_Consulta_Stock.py",
    title="Consulta",
    default=(role == "Producto"),
)
productos_2 = st.Page(
    page="pages/📅_Registro_Ventas.py",
    title="Registro",
)
ventas_1 = st.Page(
    page="pages/📊_Control_Ventas.py",
    title="Control",
    default=(role == "Ventas"),
)
ventas_2 = st.Page(
    page="pages/📈_Prediccion_Ventas.py",
    title="Predicción",
)
admin = st.Page(
    page="pages/💻_Pagina_Inicio.py",
    title="Info",
    default=(role == "Inicio"),
)
# -----------------------------------------------------------------------------------
account_pages = [logout_page]  # Pagina login
admin_pages = [admin]  # Pagina inicio
productos_pages = [productos_1, productos_2]  # Pagina producto
ventas_pages = [ventas_1, ventas_2]  # Pagina ventas
# -----------------------------------------------------------------------------------
page_dict = {}
# Condicionales para la navegación
if st.session_state.role == "Inicio":
    page_dict["Inicio"] = admin_pages
if st.session_state.role in ["Producto", "Inicio"]:
    page_dict["Producto"] = productos_pages
if st.session_state.role in ["Ventas", "Inicio"]:
    page_dict["Ventas"] = ventas_pages
if len(page_dict) > 0:
    pg = st.navigation({"Cuenta": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])
pg.run()
# -----------------------------------------------------------------------------------
