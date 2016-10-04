from enum import Enum


class UpdateType(Enum):
    CHANGE = 1
    SET = 2
    FUNCTION = 3
    FUNCTION_RETURN = 4
    EVAL = 5
    EVAL_RETURN = 6


class DeferredUpdate(object):
    """
     Class to allow variables within an object to be updated at a later point (such as at the end of a time step)
      This is useful if the existing value is required by another object until the end of the time step.

    """

    def __init__(self, obj, var, value, update_type: UpdateType):
        self.obj = obj
        self.var = var
        self.value = value
        self.update_type = update_type

    def apply_update(self):
        """
            An object (obj)'s variable (var) is updated with the value (value) according to its 'UpdateType'
        """
        if self.update_type == UpdateType.CHANGE:
            # value is added
            self.obj[self.var] += self.value
        elif self.update_type == UpdateType.SET:
            # value replaces variable's value
            self.obj[self.var] = self.value
        elif self.update_type == UpdateType.FUNCTION:
            # uses a function to update variables
            self.value()
        elif self.update_type == UpdateType.FUNCTION_RETURN:
            # updates variable from a function's return value
            self.obj.var = self.value()
        elif self.update_type == UpdateType.EVAL:
            # evaluates a statement to update the value
            eval(self.value)
        elif self.update_type == UpdateType.EVAL_RETURN:
            # evaluates a statement and assigns result to variable
            self.obj.var = eval(self.value)
