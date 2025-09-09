# api_client.py
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

try:
    # opcional: permite leer BACKEND_BASE_URL desde st.secrets si existe
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore


# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
def _get_base_url() -> str:
    """
    Resuelve la URL base del backend.
    - Primero mira la variable de entorno BACKEND_BASE_URL
    - Luego (si hay Streamlit) st.secrets["BACKEND_BASE_URL"]
    """
    url = os.getenv("BACKEND_BASE_URL")
    if not url and st is not None:
        try:
            url = st.secrets.get("BACKEND_BASE_URL")  # type: ignore[attr-defined]
        except Exception:
            url = url
    if not url:
        raise RuntimeError(
            "BACKEND_BASE_URL no configurada. "
            "Añádela en Variables del servicio o en .streamlit/secrets.toml"
        )
    return url.rstrip("/")


BASE_URL = _get_base_url()


# ---------------------------------------------------------------------
# Core request helper
# ---------------------------------------------------------------------
def _r(method: str, path: str, **kwargs) -> requests.Response:
    """
    Helper centralizado para llamar al backend.
    Lanza requests.HTTPError si el backend devuelve status >= 400.
    """
    url = f"{BASE_URL}{path}"
    resp = requests.request(method, url, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------
# Utilidades de adjuntos (Streamlit UploadedFile -> multipart/form-data)
# ---------------------------------------------------------------------
def _to_multipart_files(files: Optional[Iterable[Any]]) -> Optional[List[Tuple[str, Tuple[str, bytes, str]]]]:
    """
    Convierte una colección de ficheros (por ejemplo, st.file_uploader) en la
    tupla que espera requests para multipart/form-data.

    Devuelve:
      [('files', ('nombre.ext', b'contenido', 'mime/type')), ...]
    """
    if not files:
        return None

    out: List[Tuple[str, Tuple[str, bytes, str]]] = []
    for f in files:
        # Compat con Streamlit UploadedFile
        name = getattr(f, "name", "adjunto")
        mime = getattr(f, "type", "application/octet-stream") or "application/octet-stream"
        try:
            content = f.getbuffer()  # Streamlit
            if hasattr(content, "tobytes"):
                content = content.tobytes()
        except Exception:
            # Fallback genérico
            try:
                content = f.read()
            except Exception:
                content = b""
        out.append(("files", (name, content, mime)))
    return out


# ---------------------------------------------------------------------
# Bajas
#  - POST /bajas  -> crear
#  - GET  /bajas  -> listar por user_id
# ---------------------------------------------------------------------
def post_baja(
    *,
    user_id: str,
    usuario: str,
    tipo: str,
    fi: str,
    ff: Optional[str] = None,
    descripcion: Optional[str] = None,
    files: Optional[Iterable[Any]] = None,
) -> Dict[str, Any]:
    """
    Crea una baja (POST /bajas). El backend espera multipart/form-data
    (según tu Swagger).

    Params:
      user_id      : id del usuario
      usuario      : nombre/alias del usuario (si tu backend lo usa)
      tipo         : tipo de baja
      fi           : fecha_inicio (YYYY-MM-DD)
      ff           : fecha_fin (opcional, YYYY-MM-DD)
      descripcion  : texto opcional
      files        : iterable de UploadedFile (Streamlit) u objetos con .read()/.name/.type

    Return:
      dict con la respuesta del backend.
    """
    data = {
        "user_id": user_id,
        "usuario": usuario,
        "tipo": tipo,
        "fecha_inicio": fi,
    }
    if ff:
        data["fecha_fin"] = ff
    if descripcion:
        data["descripcion"] = descripcion

    mfiles = _to_multipart_files(files)

    resp = _r("POST", "/bajas", data=data, files=mfiles)
    try:
        return resp.json()
    except ValueError:
        return {"ok": True}


# Alias por si en alguna parte del código lo llamas 'crear_baja'
crear_baja = post_baja


def get_bajas(user_id: str) -> List[Dict[str, Any]]:
    """
    Lista las bajas de un usuario usando GET /bajas?user_id=...
    (Asegúrate de tener este endpoint implementado en el backend).
    """
    resp = _r("GET", "/bajas", params={"user_id": user_id})
    try:
        data = resp.json()
    except ValueError:
        return []

    # Soporta tanto lista directa como {"data": [...]}
    if isinstance(data, dict) and "data" in data:
        return list(data["data"])
    if isinstance(data, list):
        return data
    return [data]


# ---------------------------------------------------------------------
# Vacaciones (opcional, por si las usas también)
#  - POST /vacaciones
#  - GET  /vacaciones?user_id=...
#  Ajusta el body si tu backend espera otro formato.
# ---------------------------------------------------------------------
def post_vacacion(
    *,
    user_id: str,
    fecha_inicio: str,
    fecha_fin: str,
    descripcion: Optional[str] = None,
) -> Dict[str, Any]:
    payload = {
        "user_id": user_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    if descripcion:
        payload["descripcion"] = descripcion
    resp = _r("POST", "/vacaciones", json=payload)
    try:
        return resp.json()
    except ValueError:
        return {"ok": True}


def get_vacaciones(user_id: str) -> List[Dict[str, Any]]:
    resp = _r("GET", "/vacaciones", params={"user_id": user_id})
    try:
        data = resp.json()
    except ValueError:
        return []

    if isinstance(data, dict) and "data" in data:
        return list(data["data"])
    if isinstance(data, list):
        return data
    return [data]


