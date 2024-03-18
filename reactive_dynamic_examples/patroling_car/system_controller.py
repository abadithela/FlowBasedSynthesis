class AgentCtrl(object):
    """Mealy transducer.

    Internal states are integers, the current state
    is stored in the attribute "state".
    To take a transition, call method "move".

    The names of input variables are stored in the
    attribute "input_vars".

    Automatically generated by tulip.dumpsmach on 2024-03-18 04:00:03 UTC
    To learn more about TuLiP, visit http://tulip-control.org
    """
    def __init__(self):
        self.state = 6
        self.input_vars = ['']

    def move(self, ):
        """Given inputs, take move and return outputs.

        @rtype: dict
        @return: dictionary with keys of the output variable names:
            ['x', 'z']
        """
        output = dict()
        if self.state == 0:
            if True:
                self.state = 1

                output["x"] = 5
                output["z"] = 4
        elif self.state == 1:
            if True:
                self.state = 2

                output["x"] = 5
                output["z"] = 3
        elif self.state == 2:
            if True:
                self.state = 3

                output["x"] = 5
                output["z"] = 2
        elif self.state == 3:
            if True:
                self.state = 4

                output["x"] = 5
                output["z"] = 1
        elif self.state == 4:
            if True:
                self.state = 5

                output["x"] = 5
                output["z"] = 0
        elif self.state == 5:
            if True:
                self.state = 5

                output["x"] = 5
                output["z"] = 0
        elif self.state == 6:
            if True:
                self.state = 0

                output["x"] = 5
                output["z"] = 5
        else:
            raise Exception("Unrecognized internal state: " + str(self.state))
        return output

    def _error(self, ):
        raise ValueError("Unrecognized input: " + ().format())