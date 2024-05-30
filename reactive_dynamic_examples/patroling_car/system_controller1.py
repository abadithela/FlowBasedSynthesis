class AgentCtrl(object):
    """Mealy transducer.

    Internal states are integers, the current state
    is stored in the attribute "state".
    To take a transition, call method "move".

    The names of input variables are stored in the
    attribute "input_vars".

    Automatically generated by tulip.dumpsmach on 2024-04-06 03:54:42 UTC
    To learn more about TuLiP, visit http://tulip-control.org
    """
    def __init__(self):
        self.state = 6
        self.input_vars = ['']

    def move(self, ):
        """Given inputs, take move and return outputs.

        @rtype: dict
        @return: dictionary with keys of the output variable names:
            ['x', 'z', 'f']
        """
        output = dict()
        if self.state == 0:
            if True:
                self.state = 1

                output["x"] = 4
                output["z"] = 5
                output["f"] = 9
        elif self.state == 1:
            if True:
                self.state = 2

                output["x"] = 3
                output["z"] = 5
                output["f"] = 8
        elif self.state == 2:
            if True:
                self.state = 3

                output["x"] = 2
                output["z"] = 5
                output["f"] = 7
        elif self.state == 3:
            if True:
                self.state = 4

                output["x"] = 1
                output["z"] = 5
                output["f"] = 6
        elif self.state == 4:
            if True:
                self.state = 5

                output["x"] = 0
                output["z"] = 5
                output["f"] = 5
        elif self.state == 5:
            if True:
                self.state = 5

                output["x"] = 0
                output["z"] = 5
                output["f"] = 5
        elif self.state == 6:
            if True:
                self.state = 0

                output["x"] = 5
                output["z"] = 5
                output["f"] = 10
        else:
            raise Exception("Unrecognized internal state: " + str(self.state))
        return output

    def _error(self, ):
        raise ValueError("Unrecognized input: " + ().format())
