import json
import os

from fastapi import FastAPI

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics import router as acrobatics_router
from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_config import (
    DefaultAcrobaticsConfig,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp import router as generic_ocp_router
from bioptim_gui_api.generic_ocp.misc.generic_ocp_config import DefaultGenericOCPConfig
from bioptim_gui_api.load_existing.endpoints.load_existing import router as load_existing_router
from bioptim_gui_api.penalty.endpoints.penalty import router as penalty_router
from bioptim_gui_api.variables.endpoints.variables import router as variables_router

app = FastAPI()

app.include_router(acrobatics_router)
app.include_router(generic_ocp_router)

app.include_router(penalty_router)
app.include_router(variables_router)

app.include_router(load_existing_router)


@app.on_event("startup")
def startup_event():
    with open(DefaultAcrobaticsConfig.datafile, "w") as f:
        json.dump(DefaultAcrobaticsConfig.base_data, f)

    with open(DefaultGenericOCPConfig.datafile, "w") as f:
        json.dump(DefaultGenericOCPConfig.base_data, f)


@app.on_event("shutdown")
def shutdown_event():
    os.remove(DefaultAcrobaticsConfig.datafile)
    os.remove(DefaultGenericOCPConfig.datafile)
