from fastapi import APIRouter, HTTPException

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_code_generation import (
    router as acrobatics_code_generation_router,
)
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_phases import (
    AcrobaticsPhaseRouter,
)
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_phases_modifiers import AcrobaticsPhaseModifiers
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_requests import (
    FinalTimeMarginRequest,
    FinalTimeRequest,
    PreferredTwistSideRequest,
    SportTypeRequest,
)
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_responses import (
    FinalTimeMarginResponse,
    FinalTimeResponse,
    PreferredTwistSideResponse,
    SportTypeResponse,
)
from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_data import AcrobaticsOCPData
from bioptim_gui_api.acrobatics_ocp.misc.dynamics_updating import adapt_dynamics
from bioptim_gui_api.acrobatics_ocp.misc.enums import (
    Position,
    PreferredTwistSide,
    SportType,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp import GenericOCPBaseFieldRegistrar
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_constraints import GenericOCPConstraintRouter
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_objectives import GenericOCPObjectiveRouter
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_variables import (
    GenericControlVariableRouter,
    GenericStateVariableRouter,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_requests import DynamicsRequest


class AcrobaticsOCPBaseFieldRegistrar(GenericOCPBaseFieldRegistrar):
    def __init__(self, data):
        super().__init__(data)

    def register(self, route: APIRouter) -> None:
        super().register(route)

        # register additional endpoints
        self.register_put_final_time()
        self.register_put_final_time_margin()
        self.register_get_positions()
        self.register_get_sport_types()
        self.register_put_sport_type()
        self.register_get_preferred_twist_side()
        self.register_put_preferred_twist_side()
        self.register_get_dynamics()
        self.register_put_dynamics()

    def register_update_nb_phases(self) -> None:
        # disable the endpoint
        pass

    def register_put_final_time(self):
        @self.router.put("/final_time", response_model=FinalTimeResponse)
        def put_final_time(final_time: FinalTimeRequest):
            new_value = final_time.final_time
            if new_value < 0:
                raise HTTPException(status_code=400, detail="final_time must be positive")
            self.data.update_data("final_time", new_value)
            return FinalTimeResponse(final_time=new_value)

    def register_put_final_time_margin(self):
        @self.router.put("/final_time_margin", response_model=FinalTimeMarginResponse)
        def put_final_time_margin(final_time_margin: FinalTimeMarginRequest):
            new_value = final_time_margin.final_time_margin
            if new_value < 0:
                raise HTTPException(status_code=400, detail="final_time_margin must be positive")
            self.data.update_data("final_time_margin", new_value)
            return FinalTimeMarginResponse(final_time_margin=new_value)

    def register_get_positions(self):
        @self.router.get("/position", response_model=list)
        def get_position():
            return [side.capitalize() for side in Position]

    def register_get_sport_types(self):
        @self.router.get("/sport_type", response_model=list)
        def get_sport_type():
            return [side.capitalize() for side in SportType]

    def register_put_sport_type(self):
        @self.router.put("/sport_type", response_model=SportTypeResponse)
        def put_sport_type(sport_type: SportTypeRequest):
            new_value = sport_type.sport_type.value
            old_value = self.data.read_data("sport_type")

            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"sport_type is already {sport_type}",
                )

            self.data.update_data("sport_type", new_value)
            return SportTypeResponse(sport_type=new_value)

    def register_get_preferred_twist_side(self):
        @self.router.get("/preferred_twist_side", response_model=list)
        def get_preferred_twist_side():
            return [side.capitalize() for side in PreferredTwistSide]

    def register_put_preferred_twist_side(self):
        @self.router.put("/preferred_twist_side", response_model=PreferredTwistSideResponse)
        def put_preferred_twist_side(preferred_twist_side: PreferredTwistSideRequest):
            new_value = preferred_twist_side.preferred_twist_side.value
            old_value = self.data.read_data("preferred_twist_side")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"preferred_twist_side is already {preferred_twist_side}",
                )

            self.data.update_data("preferred_twist_side", new_value)
            return PreferredTwistSideResponse(preferred_twist_side=new_value)

    def register_get_dynamics(self):
        @self.router.get("/dynamics", response_model=list)
        def get_dynamics():
            return ["torque_driven", "joints_acceleration_driven"]

    def register_put_dynamics(self):
        @self.router.put("/dynamics", response_model=list)
        def put_dynamics(dynamics: DynamicsRequest):
            new_value = dynamics.dynamics
            old_value = self.data.read_data("dynamics")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"dynamics is already {old_value}",
                )

            self.data.update_data("dynamics", new_value)

            phases_info = self.data.read_data("phases_info")

            for phase in phases_info:
                adapt_dynamics(phase, new_value)

            self.data.update_data("phases_info", phases_info)
            return phases_info


router = APIRouter(
    prefix="/acrobatics",
    tags=["acrobatics"],
    responses={404: {"description": "Not found"}},
)
AcrobaticsOCPBaseFieldRegistrar(AcrobaticsOCPData).register(router)
AcrobaticsPhaseModifiers(AcrobaticsOCPData).register(router)

phase_router = APIRouter(
    prefix="/phases_info",
    responses={404: {"description": "Not found"}},
)
AcrobaticsPhaseRouter().register(phase_router)
GenericOCPObjectiveRouter(AcrobaticsOCPData).register(phase_router)
GenericOCPConstraintRouter(AcrobaticsOCPData).register(phase_router)
GenericControlVariableRouter(AcrobaticsOCPData).register(phase_router)
GenericStateVariableRouter(AcrobaticsOCPData).register(phase_router)

router.include_router(phase_router)

router.include_router(acrobatics_code_generation_router)
