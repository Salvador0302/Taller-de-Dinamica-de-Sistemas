"""
Python model 'taller5_forrester.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 100,
    "time_step": lambda: 1,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Delincuentes arrestados",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "delitos_resueltos": 1,
        "tasa_de_delincuentes_arrestados": 1,
        "delincuentes_en_la_calle": 1,
    },
)
def delincuentes_arrestados():
    return (
        delitos_resueltos()
        * tasa_de_delincuentes_arrestados()
        * delincuentes_en_la_calle()
    )


@component.add(
    name="Delincuentes en la calle",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_delincuentes_en_la_calle": 1},
    other_deps={
        "_integ_delincuentes_en_la_calle": {
            "initial": {},
            "step": {
                "nuevos_delicuentes": 1,
                "delincuentes_arrestados": 1,
                "delincuentes_muertos": 1,
            },
        }
    },
)
def delincuentes_en_la_calle():
    return _integ_delincuentes_en_la_calle()


_integ_delincuentes_en_la_calle = Integ(
    lambda: nuevos_delicuentes() - delincuentes_arrestados() - delincuentes_muertos(),
    lambda: 50000,
    "_integ_delincuentes_en_la_calle",
)


@component.add(
    name="Delincuentes muertos",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"delincuentes_en_la_calle": 1, "tasa_de_muertes": 1},
)
def delincuentes_muertos():
    return delincuentes_en_la_calle() * tasa_de_muertes()


@component.add(
    name="Delitos resueltos",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"policias_en_servicio": 1},
)
def delitos_resueltos():
    return policias_en_servicio() / 1000


@component.add(
    name="discrepancia",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"objetivo": 1, "policias_en_servicio": 1},
)
def discrepancia():
    return objetivo() - policias_en_servicio()


@component.add(
    name="Fondos municipales",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"delincuentes_en_la_calle": 1},
)
def fondos_municipales():
    return delincuentes_en_la_calle() * 100


@component.add(
    name="Inmigrantes",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"inmigrantes_que_llegan": 1},
)
def inmigrantes():
    return inmigrantes_que_llegan()


@component.add(
    name="Inmigrantes desempleados",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_inmigrantes_desempleados": 1},
    other_deps={
        "_integ_inmigrantes_desempleados": {
            "initial": {},
            "step": {
                "nuevos_inmigrantes_desempleados": 1,
                "inmigrantes_que_obtienen_empleo": 1,
            },
        }
    },
)
def inmigrantes_desempleados():
    return _integ_inmigrantes_desempleados()


_integ_inmigrantes_desempleados = Integ(
    lambda: nuevos_inmigrantes_desempleados() - inmigrantes_que_obtienen_empleo(),
    lambda: 30000,
    "_integ_inmigrantes_desempleados",
)


@component.add(
    name="Inmigrantes que llegan",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"poblacion_inmigrante": 1, "tasa_de_inmigrantes": 1},
)
def inmigrantes_que_llegan():
    return poblacion_inmigrante() * tasa_de_inmigrantes()


@component.add(
    name="Inmigrantes que obtienen empleo",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "inmigrantes_desempleados": 1,
        "programas_de_integracion": 1,
        "tasa_de_inmigrantes_empleados": 1,
    },
)
def inmigrantes_que_obtienen_empleo():
    return (
        inmigrantes_desempleados()
        * programas_de_integracion()
        * tasa_de_inmigrantes_empleados()
    )


@component.add(
    name="Inmigrantes que se van",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"poblacion_inmigrante": 1, "tasa_de_emigrantes": 1},
)
def inmigrantes_que_se_van():
    return poblacion_inmigrante() * tasa_de_emigrantes()


@component.add(
    name="Nuevos delicuentes",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"inmigrantes_desempleados": 1, "tasa_de_nuevos_delincuentes": 1},
)
def nuevos_delicuentes():
    return inmigrantes_desempleados() * tasa_de_nuevos_delincuentes()


@component.add(
    name="Nuevos inmigrantes desempleados",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"inmigrantes": 1, "tasa_de_desempleo": 1},
)
def nuevos_inmigrantes_desempleados():
    return inmigrantes() * tasa_de_desempleo()


@component.add(name="objetivo", comp_type="Constant", comp_subtype="Normal")
def objetivo():
    return 30000


@component.add(
    name="Poblacion inmigrante",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_poblacion_inmigrante": 1},
    other_deps={
        "_integ_poblacion_inmigrante": {
            "initial": {},
            "step": {"inmigrantes_que_llegan": 1, "inmigrantes_que_se_van": 1},
        }
    },
)
def poblacion_inmigrante():
    return _integ_poblacion_inmigrante()


_integ_poblacion_inmigrante = Integ(
    lambda: inmigrantes_que_llegan() - inmigrantes_que_se_van(),
    lambda: 60000,
    "_integ_poblacion_inmigrante",
)


@component.add(
    name="Policias asignados",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"tasa_de_policias_contratados": 1, "discrepancia": 1},
)
def policias_asignados():
    return tasa_de_policias_contratados() * discrepancia()


@component.add(
    name="Policias en servicio",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_policias_en_servicio": 1},
    other_deps={
        "_integ_policias_en_servicio": {
            "initial": {},
            "step": {"policias_asignados": 1, "policias_retirados": 1},
        }
    },
)
def policias_en_servicio():
    return _integ_policias_en_servicio()


_integ_policias_en_servicio = Integ(
    lambda: policias_asignados() - policias_retirados(),
    lambda: 10000,
    "_integ_policias_en_servicio",
)


@component.add(
    name="Policias retirados",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"tasa_de_policias_retirados": 1, "policias_en_servicio": 1},
)
def policias_retirados():
    return tasa_de_policias_retirados() * policias_en_servicio()


@component.add(
    name="Programas de integración",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fondos_municipales": 1},
)
def programas_de_integracion():
    return fondos_municipales() / 6000


@component.add(
    name="tasa de delincuentes arrestados", comp_type="Constant", comp_subtype="Normal"
)
def tasa_de_delincuentes_arrestados():
    return 0.001


@component.add(name="tasa de desempleo", comp_type="Constant", comp_subtype="Normal")
def tasa_de_desempleo():
    return 0.14


@component.add(name="tasa de emigrantes", comp_type="Constant", comp_subtype="Normal")
def tasa_de_emigrantes():
    return 0.1


@component.add(name="tasa de inmigrantes", comp_type="Constant", comp_subtype="Normal")
def tasa_de_inmigrantes():
    return 0.12


@component.add(
    name="tasa de inmigrantes empleados", comp_type="Constant", comp_subtype="Normal"
)
def tasa_de_inmigrantes_empleados():
    return 0.001


@component.add(name="tasa de muertes", comp_type="Constant", comp_subtype="Normal")
def tasa_de_muertes():
    return 0.18


@component.add(
    name="tasa de nuevos delincuentes", comp_type="Constant", comp_subtype="Normal"
)
def tasa_de_nuevos_delincuentes():
    return 0.21


@component.add(
    name="tasa de policias contratados", comp_type="Constant", comp_subtype="Normal"
)
def tasa_de_policias_contratados():
    return 0.15


@component.add(
    name="tasa de policias retirados", comp_type="Constant", comp_subtype="Normal"
)
def tasa_de_policias_retirados():
    return 0.13
