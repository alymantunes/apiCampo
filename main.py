from fastapi import FastAPI, APIRouter
from app.middleware.auth_middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module
from pathlib import Path
import pkgutil
import inspect
import logging
from typing import Optional, Set

logger = logging.getLogger("uvicorn.error")

def autodiscover_and_include_routers(
    app,  # type: FastAPI
    package="app.routes",  # type: str
    filename_prefix_if_missing=True,  # type: bool
    global_prefix=None,  # type: Optional[str]
    ignore_modules=None,  # type: Optional[Set[str]]
):
    """
    Importa todos os módulos em `package` e inclui qualquer APIRouter encontrado.
    Compatível com Python 3.6+ e pacotes sem __init__.py.

    - Ignora subpacotes e módulos iniciados por "_"
    - Se o router não tiver prefix, usa "/<nome-do-arquivo>" se filename_prefix_if_missing=True
    - Suporta múltiplos APIRouter por módulo
    - global_prefix é aplicado a todos os routers
    """
    if ignore_modules is None:
        ignore_modules = set()

    try:
        pkg = import_module(package)
    except Exception as e:
        logger.error("Não foi possível importar o pacote %s: %s", package, e)
        return

    # Tenta pegar caminhos do pacote (namespace ou regular)
    package_paths = []
    if hasattr(pkg, "__path__"):
        package_paths = list(pkg.__path__)
    elif hasattr(pkg, "__file__"):
        package_paths = [str(Path(pkg.__file__).parent)]
    else:
        logger.error("Pacote %s não possui __path__ nem __file__.", package)
        return

    # Itera sobre todos os módulos no(s) caminho(s) do pacote
    for _, modname, ispkg in sorted(pkgutil.iter_modules(package_paths), key=lambda x: x[1]):
        if ispkg or modname.startswith("_") or modname in ignore_modules:
            continue

        full_modname = "{}.{}".format(package, modname)
        try:
            module = import_module(full_modname)
        except Exception as e:
            logger.error("Falha ao importar %s: %s", full_modname, e)
            continue

        # Coleta todos os APIRouter no módulo
        routers = []
        if hasattr(module, "router") and isinstance(getattr(module, "router"), APIRouter):
            routers.append(getattr(module, "router"))
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, APIRouter) and obj not in routers:
                routers.append(obj)

        if not routers:
            logger.warning("Nenhum APIRouter encontrado em %s.", full_modname)
            continue

        # Inclui cada router
        for r in routers:
            r_prefix = getattr(r, "prefix", "") or ""
            if filename_prefix_if_missing and (r_prefix == "" or r_prefix == "/"):
                r_prefix = "/" + modname.replace("_", "-")
            final_prefix = (global_prefix or "") + r_prefix
            app.include_router(r, prefix=final_prefix)
            logger.info("Incluído %s com prefix '%s'", full_modname, final_prefix or "/")

# ----------------------------
# Criação da aplicação FastAPI
# ----------------------------
app = FastAPI()

# Middlewares
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto registro das rotas
autodiscover_and_include_routers(
    app,
    package="app.routes",
    filename_prefix_if_missing=True,
    global_prefix=None,       # ou "/api"
    ignore_modules=set(),     # ex.: {"experimental"}
)
