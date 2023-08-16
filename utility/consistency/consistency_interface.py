from __future__ import print_function
from cosmosis.datablock import option_section, names
import consistency
import numpy as np


def setup(options):
    verbose = options.get_bool(option_section, "verbose", default=False)
    cosmomc_theta = options.get_bool(option_section, "cosmomc_theta", default=False)
    relations_file = options.get_string(
        option_section, "relations_file", default="")
    extra_relations = options.get_string(option_section, "extra_relations", default="")
    cons = consistency.cosmology_consistency(verbose, relations_file, cosmomc_theta, extra_relations)
    return cons


def execute(block, config):
    cons = config
    cosmo = names.cosmological_parameters

    # Create dict of all parameters that we have already
    known_parameters = {}
    for param in cons.parameters:
        if '___' in param:
            section, lookup_param = param.split('___')
        else:
            section = cosmo
            lookup_param = param
        if block.has_value(section, lookup_param):
            known_parameters[param] = block[section, lookup_param]

    if cons.verbose:
        print("Consistency relation input parameters:", ', '.join(list(known_parameters.keys())))

    # Run the consistency checker/parameter filler-inner.
    try:
        filled_parameters = cons(known_parameters)
    # There are two possible simpler errors:
    # too many/inconsistent parameters, or not enough.
    except consistency.UnderSpecifiedModel as error:
        print("\nYou did not set enough cosmological parameters")
        print("to be able to deduce the rest of them:")
        print(error)
        return 1
    except consistency.OverSpecifiedModel as error:
        if error.first_error == "over":
            print("\nYou set inconsistent cosmological parameters.")
        else:
            print("\nYou either did not set enough cosmological parameters, or")
            print("set inconsistent ones.  We tried adding omega_nu=0 and/or")
            print("omega_K=0 but that made it inconsistent.")
        if cons.verbose:
            print("See above for more information.")
        else:
            print("Run with verbose=T in the section for the consistency module")
            print("for more information.")
        print("Final error (may or may not be useful) was:")
        print("    ", error, "\n")
        return 2

    # Annoyingly this does not fit elsewhere
    if block.has_value(cosmo, "log1e10As"):
        block[cosmo, "A_s"] = np.exp(block[cosmo, 'log1e10As']) * 1.0e-10
    elif block.has_value(cosmo, "A_s_1e9"):
        block[cosmo, "A_s"] = block[cosmo, "A_s_1e9"] * 1e-9

    # Set or replace the new values
    for param, value in list(filled_parameters.items()):
        if '___' in param:
            section, param = param.split('___')
        else:
            section = cosmo
        block[section, param] = value

    if block.has_value(cosmo, "S_8") and block.has_value(cosmo, "omega_m"):
        sigma_8 = block[cosmo, "S_8"] / (block[cosmo, "omega_m"] / 0.3)**0.5

        if block.has_value(cosmo, "sigma_8"):
            sigma8_check = block[cosmo, 'sigma_8']
            if not np.isclose(sigma_8, sigma8_check):
                raise ValueError("Inconsistent values of sigma_8 and S_8.")
        elif cons.verbose:
            print(f"Calculated sigma_8 = {sigma_8} from S_8/(Omega_m/0.3)**0.5")

        block[cosmo, "sigma_8"] = sigma_8

    block.save_to_file('debug_output/consistency_bf_block.txt', clobber=True)

    return 0
