import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_user_spreadsheet_id(user_email: str) -> str:
    """
    Busca el spreadsheet_id del usuario autenticado en la hoja 'usuarios' 
    del archivo maestro 'usuarios_control_piscinas'.

    Args:
        user_email (str): Email autenticado por OAuth.

    Returns:
        str: El spreadsheet_id correspondiente al usuario.

    Raises:
        ValueError: Si el email no está autorizado o no está activo.
    """
    # Autenticación con cuenta de servicio
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)

    # Abrir el archivo maestro de usuarios
    MASTER_SPREADSHEET_ID = "1jzuCIUZ44MGJOSQoHWDXU0KBZIVsB5tKY4xEG-AAPUg"
    sheet = client.open_by_key(MASTER_SPREADSHEET_ID)
    worksheet = sheet.worksheet("usuarios")  # Asegúrate de que se llama así

    # Leer todos los registros
    records = worksheet.get_all_records()

    for row in records:
        email = row.get("email", "").strip().lower()
        spreadsheet_id = row.get("spreadsheet_id", "").strip()
        activo = row.get("activo", "").strip().lower()

        if user_email.strip().lower() == email:
            if activo in ["sí", "si", "true", "1"]:
                return spreadsheet_id
            else:
                raise ValueError(f"El usuario '{user_email}' no está activo.")

    raise ValueError(f"El usuario '{user_email}' no está autorizado.")
