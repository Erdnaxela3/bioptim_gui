from fastapi import APIRouter, HTTPException

import bioptim_gui_api.acrobatics_ocp.acrobatics_code_generation as acrobatics_code_generation
import bioptim_gui_api.acrobatics_ocp.acrobatics_phases as acrobatics_somersaults
from bioptim_gui_api.acrobatics_ocp.acrobatics_responses import *
from bioptim_gui_api.acrobatics_ocp.acrobatics_utils import *

router = APIRouter(
    prefix="/acrobatics",
    tags=["acrobatics"],
    responses={404: {"description": "Not found"}},
)
router.include_router(
    acrobatics_somersaults.router,
    prefix="/phases_info",
    responses={404: {"description": "Not found"}},
)
router.include_router(acrobatics_code_generation.router)


@router.get("/", response_model=dict)
def get_acrobatics_data():
    data = read_acrobatics_data()
    return data


@router.put("/nb_somersaults", response_model=dict)
def update_nb_somersaults(nb_somersaults: NbSomersaultsRequest):
    nb_max_somersaults = 5
    old_value = read_acrobatics_data("nb_somersaults")
    new_value = nb_somersaults.nb_somersaults
    if new_value < 0 or new_value > nb_max_somersaults:
        raise HTTPException(status_code=400, detail="nb_somersaults must be positive")

    if new_value > old_value:
        add_somersault_info(new_value - old_value)
    elif new_value < old_value:
        remove_somersault_info(old_value - new_value)

    # if new_value == 1:
    #     update_acrobatics_data("position", Position.STRAIGHT.value)

    update_acrobatics_data("nb_somersaults", new_value)

    data = read_acrobatics_data()
    nb_somersaults = data["nb_somersaults"]
    position = data["position"]
    half_twists = data["nb_half_twists"]

    new_phase_names = acrobatics_phase_names(nb_somersaults, position, half_twists)
    nb_phases = len(new_phase_names)

    new_phases = [
        config.DefaultAcrobaticsConfig.default_phases_info.copy()
        for _ in range(nb_phases)
    ]
    for i in range(nb_phases):
        new_phases[i]["phase_name"] = new_phase_names[i]

    data["phases_info"] = new_phases

    update_acrobatics_data("phases_info", new_phases)

    return data


@router.put(
    "/nb_half_twists/{somersault_index}",
    response_model=list,
)
def put_nb_half_twist(somersault_index: int, half_twists_request: NbHalfTwistsRequest):
    if half_twists_request.nb_half_twists < 0:
        raise HTTPException(
            status_code=400, detail="nb_half_twists must be positive or zero"
        )
    half_twists = read_acrobatics_data("nb_half_twists")
    half_twists[somersault_index] = half_twists_request.nb_half_twists
    update_acrobatics_data("nb_half_twists", half_twists)

    data = read_acrobatics_data()
    nb_somersaults = data["nb_somersaults"]
    position = data["position"]
    half_twists = data["nb_half_twists"]

    new_phase_names = acrobatics_phase_names(nb_somersaults, position, half_twists)
    nb_phases = len(new_phase_names)

    new_phases = [
        config.DefaultAcrobaticsConfig.default_phases_info.copy()
        for _ in range(nb_phases)
    ]
    for i in range(nb_phases):
        new_phases[i]["phase_name"] = new_phase_names[i]

    data["phases_info"] = new_phases
    update_acrobatics_data("phases_info", new_phases)

    phases_info = read_acrobatics_data("phases_info")
    return phases_info


@router.put("/model_path", response_model=ModelPathResponse)
def put_model_path(model_path: ModelPathRequest):
    update_acrobatics_data("model_path", model_path.model_path)
    return ModelPathResponse(model_path=model_path.model_path)


@router.put("/final_time", response_model=FinalTimeResponse)
def put_final_time(final_time: FinalTimeRequest):
    new_value = final_time.final_time
    if new_value < 0:
        raise HTTPException(status_code=400, detail="final_time must be positive")
    update_acrobatics_data("final_time", new_value)
    return FinalTimeResponse(final_time=new_value)


@router.put("/final_time_margin", response_model=FinalTimeMarginResponse)
def put_final_time_margin(final_time_margin: FinalTimeMarginRequest):
    new_value = final_time_margin.final_time_margin
    if new_value < 0:
        raise HTTPException(
            status_code=400, detail="final_time_margin must be positive"
        )
    update_acrobatics_data("final_time_margin", new_value)
    return FinalTimeMarginResponse(final_time_margin=new_value)


@router.get("/position", response_model=list)
def get_position():
    # TODO implement with frontend
    # nb_somersaults = read_acrobatics_data("nb_somersaults")
    # if nb_somersaults == 1:
    #     return [Position.STRAIGHT.capitalize()]
    return [side.capitalize() for side in Position]


@router.put("/position", response_model=PositionResponse)
def put_position(position: PositionRequest):
    new_value = position.position.value
    old_value = read_acrobatics_data("position")

    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"position is already {position}",
        )

    # TODO update phases

    update_acrobatics_data("position", new_value)
    return PositionResponse(position=new_value)


@router.get("/sport_type", response_model=list)
def put_sport_type():
    return [side.capitalize() for side in SportType]


@router.put("/sport_type", response_model=SportTypeResponse)
def put_sport_type(sport_type: SportTypeRequest):
    new_value = sport_type.sport_type.value
    old_value = read_acrobatics_data("sport_type")

    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"sport_type is already {sport_type}",
        )

    update_acrobatics_data("sport_type", new_value)
    return SportTypeResponse(sport_type=new_value)


@router.get("/preferred_twist_side", response_model=list)
def get_preferred_twist_side():
    return [side.capitalize() for side in PreferredTwistSide]


@router.put("/preferred_twist_side", response_model=PreferredTwistSideResponse)
def put_preferred_twist_side(preferred_twist_side: PreferredTwistSideRequest):
    new_value = preferred_twist_side.preferred_twist_side.value
    old_value = read_acrobatics_data("preferred_twist_side")
    if old_value == new_value:
        raise HTTPException(
            status_code=304,
            detail=f"preferred_twist_side is already {preferred_twist_side}",
        )

    update_acrobatics_data("preferred_twist_side", new_value)
    return PreferredTwistSideResponse(preferred_twist_side=new_value)
