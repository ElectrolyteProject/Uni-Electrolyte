import sys
from pathlib import Path
from dp.launching.typing import BaseModel, Field, OutputDirectory,InputFilePath, Int,  Union, String, Literal, Field, Enum
from dp.launching.cli import SubParser,default_minimal_exception_handler,run_sp_and_exit,to_runner

from strategy import SCREENING_func,SEARCH_MOL_func,RECORD_DATASET_func
class Union_RECORD_DATASET(BaseModel):
    type: Literal["RECORD_DATASET"]
    mol_file: InputFilePath = Field(...,ftypes=["smi","sdf"],
                                    description="""CSV file or sdf file，
        the CSV file has 2 columns, "ID" and "smiles".
        In the sdf file, each conformation has "ID" tag and "smiles" tag . Each smiles and ID could only appear once
        and correspond to a unique conformation.""")
    model_property_map:String=Field(...,description="""
    json
    exp:
    {"g2gt":["Binding_energy_eV","Dielectric_constant_of_solvents_screening_condition","Viscosity_of_solvents_mPas",
    "LUMO_eV","HOMO_eV"]}
    """)

    fingerprint_list:String=Field(...,description="""
    json
    exp:
    ["g2gt"]
    """)


class Union_SCREENING(BaseModel):
    class SetOptional(String, Enum):
        option_i_1 = "StandardDataset"
        option_i_2 = "yourDataset"

    type: Literal["SCREENING"]
    dataset_name:SetOptional=Field( description="")
    Binding_energy_eV_screening_condition: String=Field( description="eg: 0~ , ~1 ,0~1 None")
    Dielectric_constant_of_solvents_screening_condition: String=Field( description=" eg: 0~ , ~1 ,0~1  None")
    Viscosity_of_solvents_mPas_screening_condition: String=Field( description="eg: 0~ , ~1 ,0~1  None")
    LUMO_eV_screening_condition :String=Field( description="eg: 0~ , ~1 ,0~1  None")
    HOMO_eV_screening_condition :String=Field( description="eg: 0~ , ~1 ,0~1  None")


class Union_SEARCH_MOL(BaseModel):
    type: Literal["SEARCH_MOL"]
    query_mol_file: InputFilePath = Field(...,ftypes=["CSV"],description="""
    CSV file or sdf file，
        the CSV file has 2 columns, "ID" and "smiles".
    """)


class Options(BaseModel):
    contact: Union[Union_RECORD_DATASET, Union_SCREENING,Union_SEARCH_MOL] = Field(discriminator="type")
    output_dir: OutputDirectory = Field(
        default="./output"
    )  # default will be override after online


class global_opt(Options, BaseModel):
    ...


def runner(opts:  global_opt) -> int:

    if opts.contact.type=="RECORD_DATASET":
        RECORD_DATASET_func(mol_file=opts.contact.mol_file)
    elif opts.contact.type=="SCREENING":
        SCREENING_func(dataset_name=opts.contact.dataset_name,
                       Binding_energy_eV_screening_condition=opts.contact.Binding_energy_eV_screening_condition,
                       Dielectric_constant_of_solvents_screening_condition=opts.contact.Dielectric_constant_of_solvents_screening_condition,
                       Viscosity_of_solvents_mPas_screening_condition=opts.contact.Viscosity_of_solvents_mPas_screening_condition,
                       LUMO_eV_screening_condition=opts.contact.LUMO_eV_screening_condition,
                       HOMO_eV_screening_condition=opts.contact.HOMO_eV_screening_condition)
    elif opts.contact.type=="SEARCH_MOL":
        SEARCH_MOL_func(query_mol_file=opts.contact.query_mol_file)
    else:
        raise Exception




    # output_dir = Path(opts.output_dir.get_path())
    # output_dir.mkdir(parents=True, exist_ok=True)
    # with (output_dir / 'z').open('w') as f:
    #     f.write(str(z))



def to_parser():
    return to_runner(
        global_opt,
        runner,
        version="0.1.0",
        exception_handler=default_minimal_exception_handler,
    )


if __name__ == '__main__':
    import sys
    #sys.argv=["","--json-config", r".\generated_schemas\config.json"]

    to_parser()(sys.argv[1:])
    # run_sp_and_exit(
    #     to_parser(),
    #     description="Example",
    #     version="0.1.0",
    #     exception_handler=default_minimal_exception_handler,
    # )