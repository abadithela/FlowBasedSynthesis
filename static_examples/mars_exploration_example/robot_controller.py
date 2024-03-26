class AgentCtrl(object):
    """Mealy transducer.

    Internal states are integers, the current state
    is stored in the attribute "state".
    To take a transition, call method "move".

    The names of input variables are stored in the
    attribute "input_vars".

    Automatically generated by tulip.dumpsmach on 2024-03-20 20:19:33 UTC
    To learn more about TuLiP, visit http://tulip-control.org
    """
    def __init__(self):
        self.state = 26
        self.input_vars = ['']

    def move(self, ):
        """Given inputs, take move and return outputs.

        @rtype: dict
        @return: dictionary with keys of the output variable names:
            ['x', 'z', 'f', 'icedrop', 'rockdrop']
        """
        output = dict()
        if self.state == 0:
            if True:
                self.state = 1

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 0
                output["z"] = 4
                output["f"] = 9
        elif self.state == 1:
            if True:
                self.state = 2

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 1
                output["z"] = 4
                output["f"] = 8
        elif self.state == 2:
            if True:
                self.state = 3

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 2
                output["z"] = 4
                output["f"] = 7
        elif self.state == 3:
            if True:
                self.state = 4

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 3
                output["z"] = 4
                output["f"] = 6
        elif self.state == 4:
            if True:
                self.state = 5

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 4
                output["f"] = 5
        elif self.state == 5:
            if True:
                self.state = 6

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 3
                output["f"] = 4
        elif self.state == 6:
            if True:
                self.state = 7

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 2
                output["f"] = 3
        elif self.state == 7:
            if True:
                self.state = 8

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 1
                output["f"] = 2
        elif self.state == 8:
            if True:
                self.state = 9

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 0
                output["f"] = 1
        elif self.state == 9:
            if True:
                self.state = 10

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 5
                output["z"] = 0
                output["f"] = 10
        elif self.state == 10:
            if True:
                self.state = 11

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 0
                output["f"] = 9
        elif self.state == 11:
            if True:
                self.state = 12

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 1
                output["f"] = 8
        elif self.state == 12:
            if True:
                self.state = 13

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 4
                output["z"] = 2
                output["f"] = 7
        elif self.state == 13:
            if True:
                self.state = 14

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 3
                output["z"] = 2
                output["f"] = 6
        elif self.state == 14:
            if True:
                self.state = 15

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 2
                output["z"] = 2
                output["f"] = 5
        elif self.state == 15:
            if True:
                self.state = 16

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 2
                output["z"] = 3
                output["f"] = 4
        elif self.state == 16:
            if True:
                self.state = 17

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 3
                output["z"] = 3
                output["f"] = 10
        elif self.state == 17:
            if True:
                self.state = 18

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 2
                output["z"] = 3
                output["f"] = 9
        elif self.state == 18:
            if True:
                self.state = 19

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 1
                output["z"] = 3
                output["f"] = 8
        elif self.state == 19:
            if True:
                self.state = 20

                output["icedrop"] = False
                output["rockdrop"] = False
                output["x"] = 0
                output["z"] = 3
                output["f"] = 7
        elif self.state == 20:
            if True:
                self.state = 21

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 2
                output["f"] = 6
        elif self.state == 21:
            if True:
                self.state = 22

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 1
                output["f"] = 5
        elif self.state == 22:
            if True:
                self.state = 23

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 0
                output["f"] = 4
        elif self.state == 23:
            if True:
                self.state = 24

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 0
                output["f"] = 4
        elif self.state == 24:
            if True:
                self.state = 25

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 0
                output["f"] = 4
        elif self.state == 25:
            if True:
                self.state = 23

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 0
                output["f"] = 4
        elif self.state == 26:
            if True:
                self.state = 0

                output["icedrop"] = True
                output["rockdrop"] = True
                output["x"] = 0
                output["z"] = 5
                output["f"] = 10
        else:
            raise Exception("Unrecognized internal state: " + str(self.state))
        return output

    def _error(self, ):
        raise ValueError("Unrecognized input: " + ().format())