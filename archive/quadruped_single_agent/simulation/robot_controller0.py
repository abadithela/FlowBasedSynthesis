class AgentCtrl(object):
    """Mealy transducer.

    Internal states are integers, the current state
    is stored in the attribute "state".
    To take a transition, call method "move".

    The names of input variables are stored in the
    attribute "input_vars".

    Automatically generated by tulip.dumpsmach on 2023-09-20 21:01:06 UTC
    To learn more about TuLiP, visit http://tulip-control.org
    """
    def __init__(self):
        self.state = 48
        self.input_vars = ['env_z', 'env_x']

    def move(self, env_z, env_x):
        """Given inputs, take move and return outputs.

        @rtype: dict
        @return: dictionary with keys of the output variable names:
            ['z', 'x']
        """
        output = dict()
        if self.state == 0:
            if (env_z == 4) and (env_x == 2):
                self.state = 0

                output["z"] = 4
                output["x"] = 0
            elif (env_z == 3) and (env_x == 2):
                self.state = 1

                output["z"] = 4
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 1:
            if (env_z == 4) and (env_x == 2):
                self.state = 2

                output["z"] = 4
                output["x"] = 1
            elif (env_z == 2) and (env_x == 2):
                self.state = 3

                output["z"] = 4
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 4

                output["z"] = 4
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 2:
            if (env_z == 4) and (env_x == 2):
                self.state = 2

                output["z"] = 4
                output["x"] = 1
            elif (env_z == 3) and (env_x == 2):
                self.state = 4

                output["z"] = 4
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 3:
            if (env_z == 2) and (env_x == 2):
                self.state = 3

                output["z"] = 4
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 45

                output["z"] = 4
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 6

                output["z"] = 4
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 4:
            if (env_z == 4) and (env_x == 2):
                self.state = 5

                output["z"] = 4
                output["x"] = 3
            elif (env_z == 2) and (env_x == 2):
                self.state = 3

                output["z"] = 4
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 6

                output["z"] = 4
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 5:
            if (env_z == 4) and (env_x == 2):
                self.state = 9

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 8

                output["z"] = 4
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 6:
            if (env_z == 4) and (env_x == 2):
                self.state = 5

                output["z"] = 4
                output["x"] = 3
            elif (env_z == 2) and (env_x == 2):
                self.state = 7

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 8

                output["z"] = 4
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 7:
            if (env_z == 2) and (env_x == 2):
                self.state = 7

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 43

                output["z"] = 3
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 10

                output["z"] = 3
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 8:
            if (env_z == 4) and (env_x == 2):
                self.state = 9

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 2) and (env_x == 2):
                self.state = 7

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 10

                output["z"] = 3
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 9:
            if (env_z == 4) and (env_x == 2):
                self.state = 9

                output["z"] = 4
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 10

                output["z"] = 3
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 10:
            if (env_z == 4) and (env_x == 2):
                self.state = 11

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 2) and (env_x == 2):
                self.state = 12

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 13

                output["z"] = 2
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 11:
            if (env_z == 4) and (env_x == 2):
                self.state = 11

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 14

                output["z"] = 2
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 12:
            if (env_z == 2) and (env_x == 2):
                self.state = 12

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 42

                output["z"] = 2
                output["x"] = 3
            elif (env_z == 3) and (env_x == 2):
                self.state = 14

                output["z"] = 2
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 13:
            if (env_z == 4) and (env_x == 2):
                self.state = 11

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 2) and (env_x == 2):
                self.state = 12

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 14

                output["z"] = 2
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 14:
            if (env_z == 4) and (env_x == 2):
                self.state = 15

                output["z"] = 2
                output["x"] = 2
            elif (env_z == 2) and (env_x == 2):
                self.state = 16

                output["z"] = 2
                output["x"] = 3
            elif (env_z == 3) and (env_x == 2):
                self.state = 17

                output["z"] = 2
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 15:
            if (env_z == 4) and (env_x == 2):
                self.state = 15

                output["z"] = 2
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 19

                output["z"] = 1
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 16:
            if (env_z == 2) and (env_x == 2):
                self.state = 16

                output["z"] = 2
                output["x"] = 3
            elif (env_z == 1) and (env_x == 2):
                self.state = 30

                output["z"] = 2
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 17

                output["z"] = 2
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 17:
            if (env_z == 4) and (env_x == 2):
                self.state = 15

                output["z"] = 2
                output["x"] = 2
            elif (env_z == 2) and (env_x == 2):
                self.state = 18

                output["z"] = 1
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 19

                output["z"] = 1
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 18:
            if (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 29

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 21

                output["z"] = 0
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 19:
            if (env_z == 4) and (env_x == 2):
                self.state = 20

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 2) and (env_x == 2):
                self.state = 18

                output["z"] = 1
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 21

                output["z"] = 0
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 20:
            if (env_z == 4) and (env_x == 2):
                self.state = 20

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 23

                output["z"] = 0
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 21:
            if (env_z == 4) and (env_x == 2):
                self.state = 20

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 23

                output["z"] = 0
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 22:
            if (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 28

                output["z"] = 0
                output["x"] = 3
            elif (env_z == 3) and (env_x == 2):
                self.state = 23

                output["z"] = 0
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 23:
            if (env_z == 4) and (env_x == 2):
                self.state = 24

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 2) and (env_x == 2):
                self.state = 25

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 26

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 24:
            if (env_z == 4) and (env_x == 2):
                self.state = 24

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 26

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 25:
            if (env_z == 2) and (env_x == 2):
                self.state = 25

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 27

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 26

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 26:
            if (env_z == 4) and (env_x == 2):
                self.state = 24

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 2) and (env_x == 2):
                self.state = 25

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 3) and (env_x == 2):
                self.state = 26

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 27:
            if (env_z == 2) and (env_x == 2):
                self.state = 25

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 27

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 28:
            if (env_z == 2) and (env_x == 2):
                self.state = 25

                output["z"] = 0
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 27

                output["z"] = 0
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 29:
            if (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 28

                output["z"] = 0
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 30:
            if (env_z == 2) and (env_x == 2):
                self.state = 18

                output["z"] = 1
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 31

                output["z"] = 2
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 31:
            if (env_z == 2) and (env_x == 2):
                self.state = 32

                output["z"] = 2
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 33

                output["z"] = 2
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        elif self.state == 32:
            if (env_z == 2) and (env_x == 2):
                self.state = 32

                output["z"] = 2
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 34

                output["z"] = 1
                output["x"] = 0
            elif (env_z == 3) and (env_x == 2):
                self.state = 39

                output["z"] = 1
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        elif self.state == 33:
            if (env_z == 2) and (env_x == 2):
                self.state = 32

                output["z"] = 2
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 34

                output["z"] = 1
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        elif self.state == 34:
            if (env_z == 2) and (env_x == 2):
                self.state = 35

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 36

                output["z"] = 0
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        elif self.state == 35:
            if (env_z == 2) and (env_x == 2):
                self.state = 35

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 37

                output["z"] = 0
                output["x"] = 1
            elif (env_z == 3) and (env_x == 2):
                self.state = 38

                output["z"] = 0
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 36:
            if (env_z == 2) and (env_x == 2):
                self.state = 35

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 1) and (env_x == 2):
                self.state = 37

                output["z"] = 0
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 37:
            if (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 29

                output["z"] = 0
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 38:
            if (env_z == 4) and (env_x == 2):
                self.state = 20

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 2) and (env_x == 2):
                self.state = 22

                output["z"] = 0
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 21

                output["z"] = 0
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 39:
            if (env_z == 4) and (env_x == 2):
                self.state = 40

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 2) and (env_x == 2):
                self.state = 35

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 3) and (env_x == 2):
                self.state = 41

                output["z"] = 0
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        elif self.state == 40:
            if (env_z == 4) and (env_x == 2):
                self.state = 40

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 3) and (env_x == 2):
                self.state = 38

                output["z"] = 0
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 41:
            if (env_z == 4) and (env_x == 2):
                self.state = 40

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 2) and (env_x == 2):
                self.state = 35

                output["z"] = 0
                output["x"] = 0
            elif (env_z == 3) and (env_x == 2):
                self.state = 38

                output["z"] = 0
                output["x"] = 1
            else:
                self._error(env_z, env_x)
        elif self.state == 42:
            if (env_z == 2) and (env_x == 2):
                self.state = 16

                output["z"] = 2
                output["x"] = 3
            elif (env_z == 1) and (env_x == 2):
                self.state = 30

                output["z"] = 2
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 43:
            if (env_z == 2) and (env_x == 2):
                self.state = 12

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 44

                output["z"] = 2
                output["x"] = 4
            else:
                self._error(env_z, env_x)
        elif self.state == 44:
            if (env_z == 2) and (env_x == 2):
                self.state = 12

                output["z"] = 2
                output["x"] = 4
            elif (env_z == 1) and (env_x == 2):
                self.state = 42

                output["z"] = 2
                output["x"] = 3
            else:
                self._error(env_z, env_x)
        elif self.state == 45:
            if (env_z == 2) and (env_x == 2):
                self.state = 46

                output["z"] = 3
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 47

                output["z"] = 3
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 46:
            if (env_z == 2) and (env_x == 2):
                self.state = 46

                output["z"] = 3
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 30

                output["z"] = 2
                output["x"] = 2
            elif (env_z == 3) and (env_x == 2):
                self.state = 17

                output["z"] = 2
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 47:
            if (env_z == 2) and (env_x == 2):
                self.state = 46

                output["z"] = 3
                output["x"] = 2
            elif (env_z == 1) and (env_x == 2):
                self.state = 30

                output["z"] = 2
                output["x"] = 2
            else:
                self._error(env_z, env_x)
        elif self.state == 48:
            if (env_z == 4) and (env_x == 2):
                self.state = 0

                output["z"] = 4
                output["x"] = 0
            else:
                self._error(env_z, env_x)
        else:
            raise Exception("Unrecognized internal state: " + str(self.state))
        return output

    def _error(self, env_z, env_x):
        raise ValueError("Unrecognized input: " + (
            "env_z = {env_z}; "
            "env_x = {env_x}; ").format(
                env_z=env_z,
                env_x=env_x))