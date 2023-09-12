class TesterCtrl(object):
    """Mealy transducer.

    Internal states are integers, the current state
    is stored in the attribute "state".
    To take a transition, call method "move".

    The names of input variables are stored in the
    attribute "input_vars".

    Automatically generated by tulip.dumpsmach on 2023-09-11 19:56:41 UTC
    To learn more about TuLiP, visit http://tulip-control.org
    """
    def __init__(self):
        self.state = 2
        self.input_vars = ['z', 'x']

    def move(self, z, x):
        """Given inputs, take move and return outputs.

        @rtype: dict
        @return: dictionary with keys of the output variable names:
            ['env_z', 'env_x', 'I1', 'I2', 'I', 'target']
        """
        output = dict()
        if self.state == 0:
            if (z == 4) and (x == 0):
                self.state = 0

                output["env_z"] = 0
                output["env_x"] = 2
                output["I1"] = 0
                output["I2"] = 0
                output["I"] = 0
                output["target"] = 0
            elif (z == 4) and (x == 1):
                self.state = 1

                output["env_z"] = 0
                output["env_x"] = 2
                output["I1"] = 0
                output["I2"] = 0
                output["I"] = 0
                output["target"] = 0
            else:
                self._error(z, x)
        elif self.state == 1:
            if (z == 4) and (x == 0):
                self.state = 0

                output["env_z"] = 0
                output["env_x"] = 2
                output["I1"] = 0
                output["I2"] = 0
                output["I"] = 0
                output["target"] = 0
            elif (z == 4) and (x == 1):
                self.state = 1

                output["env_z"] = 0
                output["env_x"] = 2
                output["I1"] = 0
                output["I2"] = 0
                output["I"] = 0
                output["target"] = 0
            else:
                self._error(z, x)
        elif self.state == 2:
            if (z == 4) and (x == 0):
                self.state = 0

                output["env_z"] = 0
                output["env_x"] = 2
                output["I1"] = 0
                output["I2"] = 0
                output["I"] = 0
                output["target"] = 0
            else:
                self._error(z, x)
        else:
            raise Exception("Unrecognized internal state: " + str(self.state))
        return output

    def _error(self, z, x):
        raise ValueError("Unrecognized input: " + (
            "z = {z}; "
            "x = {x}; ").format(
                z=z,
                x=x))
